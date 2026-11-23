# The older backdoor: the second stage (`ujaild`)

This page describes the second stage of the older GL.iNet router backdoor — the program the loader
downloads and runs in memory. It is written for two readers: a router owner who wants to know what
it means, and a researcher who wants enough detail to find the same thing on their own sample.

All of this comes from static analysis only. No sample was ever run, and nothing was downloaded from
any address in the malware. We examined the program files and the saved process memory from routers
we manage or own, then removed the malware from them.

## In short, for an owner

The loader on an infected router fetches a second program, starts it under the name
`/usr/sbin/ujaild`, and immediately deletes the file — so the program runs from memory and leaves
nothing on disk to find. On start it reads the router's GL identity (model, serial and MAC address,
firmware version) and "checks in" over an encrypted web connection to a fixed server, then waits for
orders.

Once it is running, whoever controls that server can run any command on the router, write any file
to it, or drop a file and run it — and can turn the router into a **doorway into the home or office
network behind it** (a proxy the operator can send traffic through). Anything the router can reach,
they can reach.

On the routers whose memory we captured, the program had **only ever checked in** — we found no
command and no proxying in the memory of any of them at the time we captured it. The infections are
not new: on one router the program had been checking in since **23 May 2026**.

If you run a GL.iNet router, the detection section at the end lists exactly what to look for.

## The samples

We recovered the program from 49 routers. There are two builds:

| Build | SHA-256 | Size (bytes) | Routers |
|---|---|---|---|
| A | `311b5767e7d63e7dbdc1476c36608b8d7ef729c8bbcc64ded63b9470396351d6` | 6,815,892 | 42 |
| B | `53736d5db721a358bec5b9ddf6056df73b36fc5330300342c42f866a05191432` | 6,750,356 | 7 |

**How it is known — Verified** (we hashed every copy): 51 copies of the file exist across the 49
routers; all 51 hash to one of the two values above (44 to build A, 7 to build B). The two extra
files are a second capture of the same program on two routers, byte-for-byte identical to the first.
So there are 49 distinct routers and two builds. The affected models were GL-MT2500, GL-MT3000,
GL-MT6000, GL-AXT1800 and GL-AX1800; firmware versions ranged from 4.7.0 to 4.11.0.

A forum user reported build A's size and hash in
[post 22](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/22);
our hashing confirms it and adds the second, smaller build B.

## What the two builds are

**How it is known — Verified** (`readelf`, and a Python reader of the Go function table, on one copy
of each build):

- 64-bit ARM (`AArch64`) ELF executables, statically linked, stripped, entry point `0x8bce0`.
- Written in Go. Both carry a Go build-info header (`\xff Go buildinf:`) but the Go version string
  in it has been blanked to `unknown`.
- Obfuscated with [garble](https://github.com/burrowers/garble): the Go function-table magic number
  is `0x26364a1c`, which is not any released Go value — garble replaces it with a value derived from
  its build seed. Both builds carry the **same** magic, which means (Inferred) they were obfuscated
  with the same seed or in the same build environment.
- Both contain a `.go.fipsinfo` section, which only appears in programs built with Go 1.24 or later
  (Inferred lower bound; the exact version is Not determined, because garble blanked it).
- No separate packer (no UPX or similar); garble is the only obfuscation.

The two builds differ only in a few things: the server they contact (below), a build stamp, how
often they check in, and a small size/function-count difference (build A has 6,598 functions, build
B 6,594). Everything else — the encryption key, the GL paths, the web path `/v1/gl/instance`, the
internal data structures, the error messages — is identical.

### Recovering the original names

garble renames every identifier to random text, so the disassembly shows names like `D1ZuDQRPg`.
But the program uses Go's JSON encoder, which works by reflection, so garble had to keep a table
mapping each obfuscated name back to the original. That table is in the program's data, as 1,016
pairs. Reading it (Verified) gives back the developer's own type and field names, which is where the
structure in the next sections comes from.

### The build stamps

**Verified.** Each build stores a plain decimal stamp, the only 8-digit `25xxxxxx` value in its
data, which it reports at check-in as `BuildVersion`:

| Build | Server | Build stamp |
|---|---|---|
| A | `up.adguardns.com` / `up.adguardns.org` | `25120821` |
| B | `up.adsanalypro.com` | `25101510` |

**Inferred reading.** Read as year-month-day-hour, `25120821` is 8 December 2025 (hour 21) and
`25101510` is 15 October 2025 (hour 10). This reading is supported by a forum user who reported in
[post 18](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/18)
that the `adguardns` names were registered on 8 December 2025 — the same date as build A's stamp.
Treat it as a reading, not a fact: what is certain is that build A's stamp is the higher of the two.

Note that the stamp order does not match what the memory shows: build A (higher stamp) has the
long check-in histories, while on the seven routers with build B the program had started only
recently (check-in counters of 7 or less, server dates from 15 November 2026; see the memory
section). The counter starts again whenever the program is started again, so a low counter says
when this copy was started, not when the router was first infected. Those seven are the same
seven routers that carry the larger, three-server loader.

## What it can do

The program is a general-purpose remote-control tool. The operator's server sends it a numbered
command (`TaskOp`) and an argument block; the program carries out the task and returns the result at
its next check-in. The task types, read from the program's own data structures (Verified, from the
recovered names on build A), are:

| Task | Fields (original names) | What it does |
|---|---|---|
| `TaskExecReq` | `File, Args, Dir, Timeout, AutoKill, Environments` | Run any program, with chosen arguments, working directory, environment and timeout |
| `TaskWriteReq` | `RFile, Content, Position, Base64` | Write any file, to any path, at a chosen byte offset, content optionally base64-decoded |
| `TaskWriteExecReq` | (combines the two above) | Write a file, then run it |
| `TaskForwardReq` | `Enabled, Addr, UserAgent, RetryWait` | Turn on the proxy / network pivot (below) |

The check-in itself is a structure called `InstanceReq`, which carries a `Forwarding` on/off flag, a
`Sleep` interval, and the result of any finished task. The server's reply, `InstanceRsp`, carries an
assigned `InstanceID`, the next `Sleep` interval, the next task, and an `Exit` flag that tells the
program to shut down. Two plain error strings in the program, `` unknown message type `%c` `` and
`unknown op: %v`, confirm this message-type and command-number design.

Each capability below is marked **Present** (the code or data structure for it is there),
**Not found** (we searched for the usual signs and found none — the terms we searched are listed),
or **Unclear**. A library being built into the program only shows the library is present, not that
the feature is used; we keep that distinction.

| Capability | Status | Evidence |
|---|---|---|
| Run commands remotely | **Present** | `TaskExecReq` structure; Go `os/exec` is built in |
| Write any file | **Present** | `TaskWriteReq` structure (path, offset, base64) |
| Drop a file and run it | **Present** | `TaskWriteExecReq` structure |
| Proxy / network pivot (SOCKS5) | **Present** (capability); **not seen used** | `TaskForwardReq` structure + `Forwarding` flag; the `yamux` stream-multiplexing library and the SOCKS5 handshake string `socks5 want cmd` are built in. See note below |
| Transport | **Present**: HTTPS over HTTP/2 | the `crypto/tls` and HTTP/2 libraries are built in; the server URL is `https://…/v1/gl/instance` |
| QUIC | **Not found** | no QUIC library; terms searched: `quic-go`, `quic` |
| WebSocket as the channel | **Unclear** | the word `websocket` appears but with no WebSocket library and no sign it is the server channel |
| Self-update inside this stage | **Unclear** | no updater code; the `Exit` flag stops the program and the loader re-downloads it, which has the same effect |
| Change VPN config (WireGuard / `wg` / UCI) | **Not found** | terms searched: `wireguard`, `wg0`, `wg `, `uci`, `/etc/config` — the few stray matches are coincidental fragments inside unrelated text |
| Read `/etc/shadow`, steal SSH keys | **Not found** | terms searched: `/etc/shadow`, `authorized_keys`, `.ssh`, `dropbear`, `ssh-` |
| Change the firewall | **Not found** | terms searched: `iptables`, `nftables`, `nft` |
| Capture traffic | **Not found** | terms searched: `tcpdump`, `pcap`, `/proc/net` |
| Harvest credentials | **Not found** (no dedicated code) | the only `/etc/passwd` use is the standard Go call that reads the current user name for the check-in |
| Tamper with logs | **Not found** | terms searched: `logread`, `syslog`, `/var/log`, `logd`, `wtmp`, `history` |
| Scan the network | **Not found** | the `scan` matches are all standard-library text, not a scanner |

**The proxy, in more detail (Inferred mechanism).** When the operator sends a forward task, the
program dials out to the address in `TaskForwardReq.Addr` using the given user-agent, opens a
multiplexed session (the `yamux` library), and serves a SOCKS5 proxy over it. The effect is a proxy
into the network behind the router, reachable by the operator. A forum user reported the `yamux` and
`socks5` strings in
[post 2](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/2);
our reading confirms them and ties them to the `TaskForwardReq` structure and the `Forwarding` flag.

So beyond run-command, write-file, drop-and-run and the proxy, there is no router-specific logic in
this program. Anything more is done by the operator through the generic run-command task.

## The embedded configuration, and how to decrypt it

The server address and the GL paths are not stored in plain text. They are kept as lowercase-hex
text and decrypted at run time with RC4 and a fixed key — the key is itself a plain string in the
program:

```
github.com/google/uuid
```

**Verified** (we decrypted these from both builds with that key). The decrypted values:

| Decrypted value | Note |
|---|---|
| `/proc/gl-hw-info/model` | GL hardware file |
| `/proc/gl-hw-info/device_sn` | GL hardware file (serial) |
| `/proc/gl-hw-info/device_mac` | GL hardware file (MAC) |
| `/etc/glversion` | GL firmware version file |
| `https://up.adguardns.com/v1/gl/instance` | build A server |
| `https://up.adguardns.org/v1/gl/instance` | build A server |
| `https://up.adsanalypro.com/v1/gl/instance` | build B server |

To find them in a sample, these are the first bytes of the hex ciphertext (the same in both builds,
because the key and the plain text are the same):

| Ciphertext prefix | Decrypts to |
|---|---|
| `0329bd5c9c72cd95433933c6dfe3a8089d` | the common start of the three `/proc/gl-hw-info/` paths |
| `033cbb50d03ac68f0b233782d9e3` | `/etc/glversion` |
| `442dbb438c6785d61b216a8ad2` | `https://up.ad` (the common start of every server URL) |

The script [`tools/ujaild/decrypt_ujaild_strings.py`](../tools/ujaild/decrypt_ujaild_strings.py)
does the whole job: it finds the key in the file, then finds and RC4-decrypts the hidden strings.
It prints short chance matches too, marked `SHORT`; the real ones are marked `ok`.

**The server `up.adsanalypro.com` (build B) has not been reported elsewhere.** It is a new address
found in this analysis. The older-wave names reported during the incident
(`cdn.lede-openproject.org`, `cdn.adxinsight.com`, `cdn.openwrt-project.org`, and the `cdn.adguardns`
names) do **not** appear in either second-stage build.

Everything else the program needs — how often to check in, its assigned id, and any task — arrives
in the server's reply. The program is started as `/usr/sbin/ujaild` with no command-line arguments,
and it takes no configuration from the command line or the environment.

## What the saved memory shows

We scanned the saved process memory of 47 routers (two of the 49 had no memory capture). The scan
reads only the program's own protocol fields; it reads no owner data. The results:

| Build / server | Routers with memory | Servers actually contacted | Check-in counter (highest) | Server date range | Check-in interval (seconds) |
|---|---|---|---|---|---|
| A / `adguardns` | 40 | `up.adguardns.com`, `up.adguardns.org` | 366 | 23 May 2026 to 22 November 2026 | 7,200 and 43,200 |
| B / `adsanalypro` | 7 | `up.adsanalypro.com` | 7 | 15 November 2026 to 22 November 2026 | 3,600 and 86,400 |

**How it is known — Verified.**

- **Which server was actually contacted.** A build stores its server URL as a decrypted constant
  that appears on the heap a fixed small number of times (two per address). An address the program
  actually talked to appears far more often, because every check-in and reply adds more copies. By
  that measure: of the 40 build-A memory images, 10 had contacted `up.adguardns.com` only, 15
  `up.adguardns.org` only, and 15 both; all 7 build-B images had contacted `up.adsanalypro.com`. The
  two campaigns' addresses never mix on one router.
- **The check-in counter and dates.** The highest check-in counter seen was 366, on one GL-MT2500
  (firmware 4.7.13); the earliest server date retained in any image was 23 May 2026, on that same
  router — so that router had been checking in for about six months. The dates are the server's own
  responses, kept in the program's memory.
- **No tasking, no proxying.** We found **no task and no forwarding** in the memory of any of the 47
  routers at the time of capture. A task is only counted when a command number or an argument,
  result or file-content field carries a real value; the bare field-name labels that the JSON
  encoder leaves in memory were not counted (they are present whether or not any command was ever
  sent). The `Forwarding` flag was never found set to on.

**What this does and does not prove (an honest limit).** Process memory holds only what the program
still kept at the moment we captured it. Our scan would have found a task or a result that was still
in memory; it would **not** have seen a command that ran and whose traces the program had already
discarded. So this is strong evidence that these routers were waiting, not being actively used — but
it is not proof that no command was ever sent to any of them.

## How it identifies the router

At each check-in the program sends a block of identity fields (Verified from the structure and from
the memory): the operating system and processor type; the firmware version (from `/etc/glversion`);
the host name and user name; the MAC address(es) (from `/proc/gl-hw-info/device_mac`); its own
command line; a process id; and two identifiers, `UniqueID` and `UniqueID2`. `UniqueID` is
(Inferred) derived from the GL hardware serial and/or MAC; given the program includes a UUID
library, `UniqueID2` is (Inferred) a generated UUID. The exact derivation is Not determined. The
per-router values themselves are owner data and are not published here.

In short, the program reads GL.iNet-specific files to fingerprint the device, so it was written
specifically for GL.iNet routers.

## Detection

### On a live router

- A running process named **`/usr/sbin/ujaild`** whose program file has been **deleted** — on Linux,
  `/proc/<pid>/exe` points to `/tmp/ujaild (deleted)`. It is started by the loader, which shows
  in the process list as `/usr/bin/monitord /var/run/monitord.pid` and is described on
  [the loader page](older-backdoor-loader.md).
- Outbound HTTPS to **`up.adguardns.com`**, **`up.adguardns.org`** or **`up.adsanalypro.com`**, to
  the path `/v1/gl/instance`, at long intervals (1, 2, 12 or 24 hours).
- *Added 23 November 2026.* The text **`__DAEMON_STAGE=`** in the process's environment
  (`/proc/<pid>/environ`). **Reported** by an owner who saw
  `__DAEMON_STAGE=2/…` on an infected GL-MT6000
  ([issue 14](https://github.com/admonstrator/glinet-csa-2026-01/issues/14) of the community
  script's repository) and explained by infinisec, who traced it to the library the program uses
  to put itself in the background
  ([issue 24](https://github.com/admonstrator/glinet-csa-2026-01/issues/24)). **Verified by us**
  as far as the files go: the text `__DAEMON_STAGE` is in both builds we hold, once in each. We
  did not save the environment of a running copy, so we have not seen the variable set. This
  mark does not depend on the program's name or on its servers.

### In a file or in memory (stable markers, the same in both builds)

- The RC4 ciphertext constants above (`0329bd5c…`, `033cbb50…`, `442dbb43…`) — stable because the
  key and plain text are fixed.
- *Added 23 November 2026.* Use the short server prefix above, not a longer one. A 40-character
  prefix, `442dbb438c6785d61b216a8ad2eabb06c0120007`, has been proposed elsewhere as a mark
  ([issue 24](https://github.com/admonstrator/glinet-csa-2026-01/issues/24)). It covers the two
  `up.adguardns` addresses only: it is in build A (twice) and **not in build B**, the build on 7
  of our routers that uses `up.adsanalypro.com`. The 26-character prefix `442dbb438c6785d61b216a8ad2`
  and the hardware-path prefix `0329bd5c…` are in both. **Verified** by byte search in both files.
- The recovered names `TaskForwardReq`, `TaskWriteExecReq`, `InstanceFields`, `UniqueID2`,
  `RetryWait`, `AutoKill`, and the strings `` unknown message type `%c` `` and `unknown op: %v`.
- The Go build-info header `\xff Go buildinf:` with the function-table magic `0x26364a1c`.
- In memory: the decrypted path `/v1/gl/instance` together with the check-in fields
  `"BuildVersion":"25`, `"UniqueID2":"`, `"InstanceID":` and the `/proc/gl-hw-info/` paths.

Two YARA rules, one for a file on disk and one for process memory, are in
[`tools/ujaild/ujaild.yar`](../tools/ujaild/ujaild.yar). We had no `yara` program at hand, so we
checked the rules' conditions with our own byte search: the file rule matches both builds and
not the loader or ordinary programs; the memory rule matches all 47 memory images. Please test
them with `yara` itself before relying on them.

## Limits

- Static analysis only: nothing was executed, and nothing in the malware was contacted.
- The Go toolchain version, the meaning of the build stamps, the derivation of the two unique
  identifiers, and the command numbers used for each task are Not determined (no task was ever
  issued on the routers we examined, so no command number was observed).
- The memory limit above: absence of tasking in memory is not proof none was ever sent.

## Credits

The following were first reported by forum users in the topic
[Found other malware while looking for 11-20 evidence](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097);
our analysis confirms and extends them:

- The `yamux` and `socks5` strings: acs, [post 2](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/2).
- The `adguardns` names registered on 8 December 2025: rdizzie, [post 18](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/18).
- Build A's size and SHA-256: HubertCumberdale, [post 22](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/22).

*Added 23 November 2026. Part of [the incident pages](../README.md). Times are UTC.*
