# Field survey

Routers we manage or own, checked since 21 November 2026, by model and firmware. Counts only: no
owner, network or device is identified. The check is still running; this page is updated as
batches finish.

Last updated: 2026-11-23 08:39 UTC (first sweep); second sweep added 2026-11-27.

## The result so far

**Of 216 routers we have reached, 175 show the attack of 20 November, an older
backdoor, or both. 41 show nothing.** GL.iNet's published indicator (a `crond -i /tmp/.log`
process) was not running on any of them.

*Updated 27 November 2026: totals of both sweeps. After the first sweep this read: of 199
routers, 166 with a sign and 33 with nothing. The table below is the first sweep; the second is
in [its own section](#second-sweep-26-november-2026).*

This is not a random sample. They are routers we manage or own, almost all with GoodCloud
switched on, and only those that were online when we checked.

## By model and firmware

| Model | Firmware | Checked | Remote shell | Older backdoor | Attacker's command ran, nothing else found | Nothing found, running since before 20 Nov | Nothing found, but restarted since |
|---|---|---|---|---|---|---|---|
| GL-AX1800 | 4.6.8 | 2 | 0 | 0 | 0 | 1 | 1 |
| GL-AX1800 | 4.7.0 | 1 | 0 | 1 | 0 | 0 | 0 |
| GL-AX1800 | 4.8.3 | 3 | 0 | 1 | 2 | 0 | 0 |
| GL-AXT1800 | 4.6.8 | 1 | 0 | 0 | 0 | 0 | 1 |
| GL-AXT1800 | 4.6.11 | 13 | 0 | 0 | 0 | 11 | 2 |
| GL-AXT1800 | 4.7.0 | 2 | 0 | 2 | 0 | 0 | 0 |
| GL-AXT1800 | 4.8.2 | 14 | 11 | 0 | 2 | 0 | 1 |
| GL-AXT1800 | 4.8.3 | 14 | 9 | 0 | 4 | 1 | 0 |
| GL-AXT1800 | 4.8.4 | 2 | 0 | 0 | 1 | 0 | 1 |
| GL-BE10000 | 4.8.6 | 1 | 0 | 0 | 1 | 0 | 0 |
| GL-BE3600 | 4.7.3 | 1 | 0 | 0 | 0 | 0 | 1 |
| GL-BE3600 | 4.8.1 | 3 | 0 | 0 | 3 | 0 | 0 |
| GL-BE3600 | 4.8.3 | 1 | 0 | 0 | 1 | 0 | 0 |
| GL-BE6500 | 4.8.7 | 1 | 0 | 0 | 1 | 0 | 0 |
| GL-BE9300 | 4.8.4 | 1 | 0 | 0 | 1 | 0 | 0 |
| GL-BE9300 | 4.9.0 | 1 | 0 | 0 | 1 | 0 | 0 |
| GL-E5800 | 4.10.0 | 2 | 0 | 0 | 0 | 0 | 2 |
| GL-MT2500 | 4.7.0 | 2 | 0 | 2 | 0 | 0 | 0 |
| GL-MT2500 | 4.7.4 | 7 | 0 | 7 | 0 | 0 | 0 |
| GL-MT2500 | 4.7.13 | 11 | 0 | 10 | 1 | 0 | 0 |
| GL-MT2500 | 4.9.0 | 1 | 0 | 0 | 1 | 0 | 0 |
| GL-MT3000 | 4.7.4 | 10 | 0 | 9 | 1 | 0 | 0 |
| GL-MT3000 | 4.8.0 | 3 | 0 | 3 | 0 | 0 | 0 |
| GL-MT3000 | 4.8.1 | 17 | 0 | 3 | 14 | 0 | 0 |
| GL-MT3000 | 4.8.2 | 2 | 0 | 0 | 2 | 0 | 0 |
| GL-MT3000 | 4.9.0 | 6 | 0 | 0 | 6 | 0 | 0 |
| GL-MT3000 | 4.11.0 | 6 | 0 | 1 | 0 | 3 | 2 |
| GL-MT3600BE | 4.8.5 | 2 | 0 | 0 | 2 | 0 | 0 |
| GL-MT3600BE | 4.9.0 | 6 | 0 | 0 | 4 | 0 | 2 |
| GL-MT3600BE | 4.9.1 | 2 | 0 | 0 | 2 | 0 | 0 |
| GL-MT5000 | 4.8.6 | 6 | 0 | 0 | 6 | 0 | 0 |
| GL-MT5000 | 4.9.0 | 17 | 0 | 0 | 17 | 0 | 0 |
| GL-MT6000 | 4.7.0 | 1 | 0 | 1 | 0 | 0 | 0 |
| GL-MT6000 | 4.7.7 | 6 | 0 | 5 | 0 | 1 | 0 |
| GL-MT6000 | 4.8.1 | 1 | 0 | 0 | 0 | 0 | 1 |
| GL-MT6000 | 4.8.2 | 5 | 0 | 0 | 5 | 0 | 0 |
| GL-MT6000 | 4.8.3 | 13 | 0 | 3 | 9 | 0 | 1 |
| GL-MT6000 | 4.8.4 | 1 | 0 | 0 | 1 | 0 | 0 |
| GL-MT6000 | 4.9.0 | 5 | 0 | 1 | 4 | 0 | 0 |
| GL-MT6000 | 4.9.1 | 5 | 4 | 0 | 1 | 0 | 0 |
| GL-MT6000 | 4.11.0 | 1 | 0 | 0 | 0 | 1 | 0 |
| **All routers** | | **199** | **24** | **49** | **93** | **18** | **15** |
| GL-RM1 (KVM) | 1.10.1 | 1 | 0 | 0 | 0 | 0 | 1 |

## Second sweep, 26 November 2026

*Added 27 November 2026.* We went through the same routers again on 26 November. The table
above is the first sweep and is left as it was.

**202 routers answered. 185 of them had been checked before; 17 had not.**

What the 17 newly reached routers showed:

| State on 26 November | Routers |
|---|---|
| Older backdoor installed and running | 2 (a GL-AXT1800 on 4.7.0 and a GL-MT2500 on 4.7.13) |
| Remote shell of 20 November still running | 1 (a GL-AXT1800 on 4.8.2) |
| Attacker's command ran, nothing else found | 6 |
| Nothing found | 8 |

With the first sweep that makes **216 routers reached, 175 of them with the attack of
20 November, the older backdoor, or both**: a remote shell on 25, the older backdoor on 51, the
attacker's command and nothing else on 99.

What the 185 rechecked routers showed:

- **Nothing had come back.** Of the 49 routers from which we removed the older backdoor, 48
  answered: its three places were as in the firmware and none of its processes was running on any
  of them. No remote shell was running on any router where we had ended one. The vendor cloud had
  not been switched on again on any router where we had switched it off.
- **Almost nobody had upgraded.** 3 of the 185 were on a newer firmware than on 22 November, all
  three on a second-round fixed build (two GL-MT6000 on 4.11.2, one GL-AXT1800 on 4.8.5). The
  other 182 were on the same firmware as before.
- **More than half had not been restarted since the attack:** 115 of the 202. A router that has
  not been restarted or upgraded still holds whatever was started on it on 20 November.

**The remote shell found on 26 November** was on a router that had not been restarted since
September. Its loop had been started on 20 November 2026 at about 21:40 UTC and was still running
six days later, retrying its connection to `170.39.226.219`; the attempt in the router's
connection table was unanswered. We saved its memory, ended it and switched the vendor cloud off.

**The two newly found backdoored routers** carry the same build as the other 49: the same two
server names and settings in the loader, each with its own identifier. Their files are dated
9 December 2025 and 28 February 2026. Both were removed after the evidence was saved.

**Against GoodCloud's own log.** Of the 210 devices that answered the attacker in the
[device log of our own account](goodcloud-device-log.md), the second sweep reached 162.

Not reached on 26 November: the routers that were offline or whose network we could not join. A
router we could not reach may be in any of the states above.

## What the columns mean

Each sign is described in the README under
[The signs, and what each one means](../README.md#the-signs-and-what-each-one-means).

- **Remote shell**: an interactive root shell to `170.39.226.219`, running when we checked.
  See [details](router-reverse-shell.md).
- **Older backdoor**: the changed start-up script and `/bin/ulogd` described in finding R-11,
  installed and running. Most of these routers also show the attacker's command of 20 November.
- **Attacker's command ran, nothing else found**: the firewall rule that the command leaves, or,
  on a router restarted since, the state file its handler writes (findings R-14, R-15, R-17).
  The command ran as root. We found no shell, pipe or backdoor on these.
- **Nothing found, but restarted since**: cannot be cleared for 20 November, because a restart
  removes the rule, the pipe and the shell.

Method: the process list and connections, the named pipe `/tmp/f`, the firewall rule, the state
file `/etc/mp_ip_mapping_info`, the start-up script and keep list compared with the firmware's own
copies, and the "gl-helper" files, as described in the [README](../README.md#check-a-device).

Contributions use the same idea: see [CONTRIBUTING.md](../CONTRIBUTING.md).
