#!/usr/bin/env python3
# decrypt_ujaild_strings.py - find and decrypt the hidden strings of the GL.iNet "ujaild"
# second-stage backdoor, without running it.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Usage: python3 -I decrypt_ujaild_strings.py <elf> [key-text]
#
# The implant keeps some strings (its server URL and the GL hardware/firmware paths) as lowercase
# hex text that is RC4-encrypted. The RC4 key is itself a plain string in the program's read-only
# data; its default value is below and is the same in both known builds. Go stores string data
# without terminators, so string boundaries are not visible in the bytes. This tool therefore takes
# every maximal run of lowercase hex digits (length >= 8) in .rodata, tries each start offset in the
# first few characters of the run, RC4-decrypts to the end of the run, and keeps the longest
# all-printable prefix (at least 4 bytes). A random 4-byte plaintext is printable by chance with
# probability about (98/256)^4 = 0.02 per candidate, so hits under 10 bytes are marked SHORT and
# need a code reference before they count. Every result is printed with its file offset and the
# ciphertext text, so each one can be checked by hand.
#
# Exits non-zero if the file has no .rodata or if the key text is not present in the file (a key
# that is not in the binary cannot be the binary's key, and the run would be meaningless).
#
# Standard library only. The input file is only read.
import re
import struct
import sys

DEFAULT_KEY = 'github.com/google/uuid'
PRINTABLE = set(range(0x20, 0x7f)) | {0x09, 0x0a, 0x0d}


def die(msg):
    sys.stderr.write('decrypt_ujaild_strings: ERROR: %s\n' % msg)
    sys.exit(2)


def rc4(key, data):
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) & 0xff
        s[i], s[j] = s[j], s[i]
    i = j = 0
    out = bytearray()
    for c in data:
        i = (i + 1) & 0xff
        j = (j + s[i]) & 0xff
        s[i], s[j] = s[j], s[i]
        out.append(c ^ s[(s[i] + s[j]) & 0xff])
    return bytes(out)


def rodata(b):
    shoff, = struct.unpack_from('<Q', b, 0x28)
    shentsize, shnum, shstrndx = struct.unpack_from('<HHH', b, 0x3a)
    hdrs = [struct.unpack_from('<IIQQQQIIQQ', b, shoff + i * shentsize) for i in range(shnum)]
    stroff = hdrs[shstrndx][4]
    for h in hdrs:
        name = b[stroff + h[0]:b.index(b'\0', stroff + h[0])]
        if name == b'.rodata':
            return h[4], h[5]
    die('no .rodata section')


def scan(b, key, maxshift=6):
    off, size = rodata(b)
    region = b[off:off + size]
    hits = []
    for m in re.finditer(rb'[0-9a-f]{8,}', region):
        run = m.group(0)
        # Start candidates: the first few characters of the run, and, because encrypted strings
        # can sit back to back, the end of every hit and the few characters before it (the
        # printable-prefix rule can overrun a boundary by a byte or two).
        todo = list(range(0, min(maxshift, len(run) - 8) + 1))
        done = set()
        while todo:
            shift = todo.pop(0)
            if shift in done or shift < 0 or len(run) - shift < 8:
                continue
            done.add(shift)
            # RC4 is a stream cipher, so decrypting the whole rest of the run once gives every
            # prefix's plaintext; the candidate is the longest all-printable prefix.
            usable = (len(run) - shift) // 2 * 2
            pt = rc4(key, bytes.fromhex(run[shift:shift + usable].decode()))
            n = 0
            while n < len(pt) and pt[n] in PRINTABLE:
                n += 1
            if n >= 4:
                hits.append((off + m.start() + shift, run[shift:shift + 2 * n].decode(), pt[:n]))
                end = shift + 2 * n
                todo.extend([end, end - 2, end - 4, end - 6])
    return hits


def main():
    if len(sys.argv) < 2:
        die('usage: decrypt_ujaild_strings.py <elf> [key-text]')
    b = open(sys.argv[1], 'rb').read()
    key = (sys.argv[2] if len(sys.argv) > 2 else DEFAULT_KEY).encode()
    kpos = b.find(key)
    if kpos < 0:
        die('key text %r not found in %s' % (key, sys.argv[1]))
    print('# key %r found at file offset 0x%x' % (key.decode(), kpos))
    seen = set()
    for pos, ct, pt in scan(b, key):
        if pos in seen:
            continue
        seen.add(pos)
        flag = 'SHORT' if len(pt) < 10 else 'ok'
        print('0x%06x\t%s\t%d\t%s\t%r' % (pos, flag, len(pt), ct, pt.decode('ascii')))


if __name__ == '__main__':
    main()
