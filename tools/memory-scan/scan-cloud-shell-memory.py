#!/usr/bin/env python3
# scan-cloud-shell-memory.py
#
# Recover the GL.iNet cloud "virtual_ip_info" attack messages and the reverse-shell activity of the
# 20 November 2026 GoodCloud incident from saved process-memory images, offline. It reads the
# writable-memory image of the cloud client (gl-cloud) and of the reverse-shell processes, finds the
# attacker messages and classifies them, and lists what was typed into the shells. It executes
# nothing it finds and contacts no network. Run it with an isolated interpreter:
#
#     python3 -I scan-cloud-shell-memory.py --raw <dir-of-images> --json out.json [--strings <dir>]
#
# Each image <name>.mem is paired with a <name>.index describing the memory regions, in this format:
#
#     region <start-hex>-<end-hex> <length-decimal>        (one line per region, in order)
#     cmdline: <process command line>                      (optional metadata lines)
#     now_utc: YYYY-MM-DD HH:MM:SS
#     proc_start_ticks: <int>     uptime_s: <float>         (for a process start time, USER_HZ 100)
#
# A cloud-client image is a file named glcloud.mem; a reverse-shell image is named pid-<n>.mem or
# shell-pid-<n>.mem. The region lengths must sum to the file size, or the image is reported as an
# error rather than scanned; an empty image is reported as "not scanned", never as "nothing found".
#
# This tool reads the plain frame type (0x02). On some models (GL-MT3000 among them) the cloud
# client receives messages in a second frame type, 0x32, which this tool does not read: such
# frames are counted and reported as "not decoded". Everything else -- the plain frame, the plain
# JSON request, the device's re-encoded copy, the reverse-shell process memory and the text state
# captures -- is handled in full. All text printed or written is masked for owner data (see mask()).
#
# SPDX-License-Identifier: GPL-3.0-or-later
import argparse
import hashlib
import json
import os
import re
import sys


# --------------------------------------------------------------------------------------------
# Masking. Applied to every string that leaves this program. Device identifiers, MAC addresses and
# every IPv4 address that is not loopback, a wildcard or one of the two attacker addresses are
# replaced; the attacker's own values are kept so a reader can act on them.
# --------------------------------------------------------------------------------------------
KEEP_IP = {'127.0.0.1', '0.0.0.0', '255.255.255.255', '66.245.219.252'}
ATTACKER_NET = re.compile(r'^170\.39\.226\.\d+$')
IDS = set()  # 12-hex device identifiers learnt from topics and survey tags; masked wherever seen


def learn_ids(img):
    for m in re.finditer(rb'/([0-9a-fA-F]{12})/(?:command|attribute)/', img):
        IDS.add(m.group(1).decode().lower())
    for m in re.finditer(rb'MKX([0-9a-fA-F]{12})', img):
        IDS.add(m.group(1).decode().lower())


_IDRE = None
_IDN = -1


def mask(s):
    if isinstance(s, bytes):
        s = s.decode('latin1')
    global _IDRE, _IDN
    if _IDN != len(IDS):
        if IDS:
            frags = sorted({i[k:k + n] for i in IDS for n in range(5, 12) for k in range(0, 13 - n)},
                           key=len, reverse=True)
            _IDRE = (re.compile('|'.join(sorted(IDS)), re.I),
                     re.compile(r'(?<![0-9a-fA-F])(?:%s)(?![0-9a-fA-F])' % '|'.join(frags), re.I))
        else:
            _IDRE = None
        _IDN = len(IDS)
    if _IDRE:
        s = _IDRE[0].sub('<id>', s)
        s = _IDRE[1].sub('<id>', s)
    s = re.sub(r'(?i)(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}', '<mac>', s)
    s = re.sub(r'[0-9a-fA-F]{12,}', lambda m: '<num>' if m.group().isdigit() else '<id>', s)
    s = re.sub(r'(?<![0-9a-fA-F])(?=[0-9a-fA-F]*[a-fA-F])[0-9a-fA-F]{6,11}(?![0-9a-fA-F])', '<hex>', s)

    def ip(m):
        v = m.group()
        return v if v in KEEP_IP or ATTACKER_NET.match(v) else '<ip>'
    s = re.sub(r'(?<![\d.])\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?![\d.])', ip, s)
    # private-range runs, including copies corrupted by interspersed non-printables: collapse to
    # <ip> so an owner LAN address can never leak even in a damaged remnant.
    s = re.sub(r'(?<![\d.])(?:10|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)[\d.]{0,16}', '<ip>', s)
    s = re.sub(r'(?<![\d.])\d{1,3}(?:\.\d{1,3}){4,5}(?![\d])', '<ip>', s)
    s = re.sub(r'HOSTNAME=[^\x00-\x1f\x7f-\xff]*', 'HOSTNAME=<host>', s)
    s = re.sub(r'(?<![A-Za-z0-9])zt[a-z0-9]{8}(?![a-z0-9])', '<zt-iface>', s)
    return re.sub(r'[^\x20-\x7e]', '.', s)


# --------------------------------------------------------------------------------------------
# Image loading
# --------------------------------------------------------------------------------------------
class Unreadable(Exception):
    pass


def load(mem):
    idx = mem[:-4] + '.index'
    if not os.path.isfile(idx):
        raise Unreadable('%s: no index file' % mem)
    text = open(idx, encoding='latin1').read()
    meta = {}
    for k in ('now_utc', 'cmdline', 'proc_start_ticks', 'uptime_s', 'RESULT'):
        m = re.search(r'^%s: ?(.*)$' % k, text, re.M)
        meta[k] = m.group(1).strip() if m else None
    regs, off = [], 0
    for m in re.finditer(r'^region ([0-9a-f]+)-([0-9a-f]+) (\d+)', text, re.M):
        regs.append((off, int(m.group(1), 16), int(m.group(3))))
        off += int(m.group(3))
    size = os.path.getsize(mem)
    if size == 0:
        return None, regs, meta, 'empty image; index says: %s' % meta.get('RESULT')
    img = open(mem, 'rb').read()
    if off != size:
        raise Unreadable('%s: index regions sum to %d, file is %d' % (mem, off, size))
    return img, regs, meta, None


def addr(regs, o):
    for fo, va, n in regs:
        if fo <= o < fo + n:
            return va + (o - fo)
    return None


# --------------------------------------------------------------------------------------------
# Cloud client scan (plain forms only; type-0x32 frames are counted, not decoded)
# --------------------------------------------------------------------------------------------
MSG = re.compile(rb'\{"id": ?1, ?"astrowarp": ?\{"virtual_ip_info": ?\{"data": ?\[.{0,4000}?\}\]\}\}\}', re.S)
FRAME = re.compile(rb'GL([\x02\x32])(...)', re.S)
TOPIC = re.compile(rb'/sys/[a-z0-9_.-]{1,40}/[0-9a-zA-Z_.-]{1,40}/[0-9a-fA-F]{12}/'
                   rb'(?:command|attribute)/[A-Za-z0-9_/]{1,80}')
PRINT_RUN = re.compile(rb'[\x09\x0a\x0d\x20-\x7e]{4,}')
IND = {
    'attacker-net': rb'170\.39\.226\.\d{1,3}',
    'ip-semicolon': rb'127\.0\.0\.1;',
    'mkfifo': rb'mkfifo',
    'tmp-f': rb'/tmp/f\b',
    'pkill': rb'(?<![A-Za-z_])pkill',
    'sdwan-cmd': rb'SDWAN_IP_MAPPING -d',
    'survey-marker': rb'===[SLCE]===',
    'nc-target': rb'(?<![A-Za-z_])nc (?:-w \d+ )?[0-9.]+ \d+',
    'reply-vii-empty': rb'"virtual_ip_info":\[\]',
    'reply-astrowarp-empty': rb'"astrowarp":\[\]',
    'download': rb'(?<![A-Za-z_])(?:wget|curl|tftp) ',
    'gl-dirs': rb'/etc/config/\.gl|/etc/glinet/\.cache',
    'wake': rb'wake\?m=|:8899/',
    'procwalk': rb'for d in /proc/',
    'other-server': rb'66\.245\.219\.252',
}
IND_RE = {k: re.compile(v) for k, v in IND.items()}


def balanced_json(buf, start):
    depth, i, ins, esc = 0, start, False, False
    while i < len(buf) and i - start < 20000:
        c = buf[i]
        if ins:
            if esc:
                esc = False
            elif c == 0x5c:
                esc = True
            elif c == 0x22:
                ins = False
        else:
            if c == 0x22:
                ins = True
            elif c == 0x7b:
                depth += 1
            elif c == 0x7d:
                depth -= 1
                if depth == 0:
                    return buf[start:i + 1]
        if c < 0x09 or (0x0d < c < 0x20) or c > 0x7e:
            return None
        i += 1
    return None


# Catalogue of the known message families. Applied to masked text; returns the entries it matches.
def classify(t):
    e = []
    if '===S===' in t or '===C===' in t or '===L===' in t or 'glinet/.cache' in t \
            or 'glinet\\/.cache' in t:
        e.append('C1-survey-401')
    elif 'nc -w 6 170.39.226.219 50000' in t:
        e.append('C3-survey-short-w6')
    elif 'head -30' in t and 'LL<id>' in t:
        e.append('C2-survey-short')
    if 'rm -f /tmp/f;mkfifo /tmp/f' in t or 'rm -f \\/tmp\\/f;mkfifo' in t \
            or 'cat /tmp/f|/bin/sh -i' in t or '/bin/sh -i 2>&1|nc 170.39.226.219' in t \
            or '\\/bin\\/sh -i 2>&1|nc 170.39.226.219' in t:
        e.append('C4-reverse-shell')
    if 'pkill -9 -f' in t:
        e.append('C5-kill-pkill')
    if 'for d in /proc/[0-9]*' in t or re.search(
            r'\$d\\?/cmdline 2>\\?/dev\\?/null && kill -9 \$p 2>\\?/dev\\?/null; done', t):
        e.append('C6-kill-procwalk')
    if re.search(r'\*\|\*\\?"cat', t) or 'esac; ' in t:
        e.append('C7-kill-case')
    if 'wake?m=KK_' in t or 'wake.m=KK' in t or re.search(r'virtualIp\\?": ?\\?";wget', t):
        e.append('C8-wake-wget')
    if '"virtual_ip_info":[]' in t:
        e.append('R1-reply-vii-empty')
    if '"astrowarp":[]' in t:
        e.append('R2-reply-astrowarp-empty')
    return e


NC_PORT = re.compile(r'nc (?:-w \d+ )?(170\.39\.226\.\d+) (\d+)')


def scan_cloud(img, regs):
    res = {'plain': [], 'vii_objects': [], 'frames': {}, 'indicators': [], 'entries': [],
           'nc_targets': set()}

    def add(norm, off):
        for c in classify(norm):
            res['entries'].append({'entry': c, 'off': off})

    for m in MSG.finditer(img):
        n = mask(m.group())
        res['plain'].append({'off': m.start(), 'norm': n})
        add(n, m.start())
    seen = set()
    for m in re.finditer(rb'virtual_ip_info', img):
        for st in range(m.start() - 1, max(0, m.start() - 400), -1):
            if img[st] == 0x7b and st not in seen:
                j = balanced_json(img, st)
                if j and b'virtual_ip_info' in j:
                    try:
                        json.loads(j)
                    except ValueError:
                        continue
                    seen.add(st)
                    n = mask(j)
                    res['vii_objects'].append({'off': st, 'norm': n})
                    add(n, st)
    for m in FRAME.finditer(img):
        t = m.group(1)[0]
        pre = img[max(0, m.start() - 200):m.start()]
        tm = list(TOPIC.finditer(pre))
        if not tm or len(pre) - tm[-1].end() > 4:
            continue
        if t == 0x02:
            ln = int.from_bytes(m.group(2)[1:3], 'big')
            body = img[m.end():m.end() + ln]
            if body[:1] == b'{':
                n = mask(body)
                add(n, m.start())
                res['frames']['0x02 plain'] = res['frames'].get('0x02 plain', 0) + 1
        else:
            res['frames']['0x32 (not decoded)'] = \
                res['frames'].get('0x32 (not decoded)', 0) + 1
    for r in PRINT_RUN.finditer(img):
        run = r.group()
        hits = [k for k, rx in IND_RE.items() if rx.search(run)]
        if hits:
            m = mask(run[:1500])
            if not m.startswith('{"id": 1, "astrowarp"'):
                add(m, r.start())
            res['indicators'].append({'off': r.start(), 'hits': hits, 'raw': m})
        for mt in NC_PORT.finditer(run.decode('latin1', 'replace')):
            res['nc_targets'].add('%s:%s' % (mt.group(1), mt.group(2)))
    res['nc_targets'] = sorted(res['nc_targets'])
    return res


# --------------------------------------------------------------------------------------------
# Reverse-shell process scan
# --------------------------------------------------------------------------------------------
TYPED_SURVEY = (b'echo ===S===; ls -ld /etc/config/.gl 2>&1; echo ===L===; '
                b'ls -la /etc/config/.gl 2>&1 | head -40; echo ===E===')
CMDWORDS = re.compile(
    rb'cat /etc/|(?<![A-Za-z_])uci |(?<![A-Za-z_])wget|(?<![A-Za-z_])curl|(?<![A-Za-z_])tftp'
    rb'|(?<![A-Za-z_])nc |chmod|(?<![A-Za-z_])ls |uname|iptables|(?<![A-Za-z_])rm |base64'
    rb'|/etc/shadow|authorized_keys|/tmp/|mkfifo|170\.39\.226|===[SLCE]===|(?<![A-Za-z_])cat ')
SHELL_RUN = re.compile(rb'[\x09\x0a\x0d\x20-\x7e]{3,}')


def scan_shell(img, regs):
    stack_i = len(regs) - 1
    runs = []
    for r in SHELL_RUN.finditer(img):
        o = r.start()
        region = next((i for i, (fo, va, n) in enumerate(regs) if fo <= o < fo + n), None)
        runs.append({'off': o, 'stack': region == stack_i, 'raw': r.group()})
    f = {'typed_survey': img.count(TYPED_SURVEY),
         'folder_absent_output': img.count(b'.gl: No such file or directory'),
         'dot_lp': img.count(b'/tmp/.l'),
         'banner': bool(re.search(rb'BusyBox v[0-9.]+', img)),
         'prompt': bool(re.search(rb'[~/] # ', img)),
         'cmd_runs': [mask(x['raw'][:2000]) for x in runs if CMDWORDS.search(x['raw'])]}
    return f


# --------------------------------------------------------------------------------------------
STATE_IND = re.compile(r'127\.0\.0\.1;|170\.39\.226\.|/tmp/f\b|mkfifo|/tmp/\.lp|66\.245\.219\.252'
                       r'|wake\?m=|pkill -9|for d in /proc|SDWAN_IP_MAPPING -d|/bin/sh -i')


def scan_state(path):
    hits = []
    for n, line in enumerate(open(path, encoding='latin1').read().splitlines(), 1):
        if STATE_IND.search(line):
            hits.append({'line': n, 'raw': mask(line[:600])})
    return hits


def main():
    ap = argparse.ArgumentParser(description='Offline scanner for the GL.iNet cloud virtual_ip_info '
                                             'attack messages and reverse-shell memory.')
    ap.add_argument('--raw', required=True, help='directory tree of <name>.mem + <name>.index images')
    ap.add_argument('--json', required=True, help='write the full masked result here')
    ap.add_argument('--strings', help='optional directory for per-shell masked string dumps')
    a = ap.parse_args()

    cloud, shells, states, errors = [], [], [], []
    for root, dirs, files in os.walk(a.raw):
        # never descend into sample folders marked do-not-run (they hold live malware samples)
        dirs[:] = sorted(d for d in dirs if 'DO-NOT-RUN' not in d)
        for fn in sorted(files):
            p = os.path.join(root, fn)
            if fn == 'glcloud.mem':
                cloud.append(p)
            elif re.fullmatch(r'(?:shell-)?pid-\d+\.mem', fn):
                shells.append(p)
            elif fn.endswith('.txt'):
                states.append(p)

    for p in cloud:
        if os.path.getsize(p):
            learn_ids(open(p, 'rb').read())
    print('device identifiers learnt for masking: %d' % len(IDS))

    out = {'cloud': [], 'shell': [], 'state': [], 'not_scanned': [], 'errors': []}
    for p in cloud:
        rel = os.path.relpath(p, a.raw)
        try:
            img, regs, meta, why = load(p)
        except Unreadable as e:
            out['errors'].append(str(e))
            errors.append(rel)
            print('ERROR (cloud, not scanned):', e, file=sys.stderr)
            continue
        if img is None:
            out['not_scanned'].append({'file': rel, 'why': why})
            print('NOT SCANNED %s: %s' % (rel, why))
            continue
        r = scan_cloud(img, regs)
        r.update(file=rel, sha256=hashlib.sha256(img).hexdigest())
        out['cloud'].append(r)
        ent = sorted({e['entry'] for e in r['entries']})
        print('%s: entries %s; frames %s; nc %s' % (rel, ent, r['frames'], r['nc_targets']))

    for p in shells:
        rel = os.path.relpath(p, a.raw)
        try:
            img, regs, meta, why = load(p)
        except Unreadable as e:
            out['errors'].append(str(e))
            errors.append(rel)
            print('ERROR (shell, not scanned):', e, file=sys.stderr)
            continue
        if img is None:
            out['not_scanned'].append({'file': rel, 'why': why})
            print('NOT SCANNED %s: %s' % (rel, why))
            continue
        f = scan_shell(img, regs)
        rec = {'file': rel, 'sha256': hashlib.sha256(img).hexdigest(),
               'cmdline': mask(meta['cmdline'] or ''), 'flags': f}
        out['shell'].append(rec)
        print('%s [%s]: typed_survey %d, folder_absent %d, other_cmd_runs %d, /tmp/.l %d'
              % (rel, rec['cmdline'][:48], f['typed_survey'], f['folder_absent_output'],
                 len(f['cmd_runs']), f['dot_lp']))
        if a.strings:
            os.makedirs(a.strings, exist_ok=True)
            sp = os.path.join(a.strings, rel.replace('/', '__') + '.txt')
            with open(sp, 'w') as fh:
                for run in SHELL_RUN.finditer(img):
                    fh.write('%08x %s\n' % (run.start(), mask(run.group())))

    for p in states:
        out['state'].append({'file': os.path.relpath(p, a.raw), 'hits': scan_state(p)})

    json.dump(out, open(a.json, 'w'), indent=1)
    print('\nTOTAL: cloud scanned %d, shell scanned %d, not scanned %d, errors %d, state files %d'
          % (len(out['cloud']), len(out['shell']), len(out['not_scanned']), len(errors),
             len(states)))
    if errors:
        print('ERRORS: %s' % ', '.join(errors), file=sys.stderr)
        sys.exit(3)


if __name__ == '__main__':
    main()
