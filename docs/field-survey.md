# Field survey

Routers we manage or own, checked since 21 November 2026, by model and firmware. Counts only: no
owner, network or device is identified. The check is still running; this page is updated as
batches finish.

Last updated: 2026-11-22 10:47 UTC.

## The result so far

**Of 183 routers we have reached, 152 show the attack of 20 November, an older
backdoor, or both. 31 show nothing.** GL.iNet's published indicator (a `crond -i /tmp/.log`
process) was not running on any of them.

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
| GL-AXT1800 | 4.8.4 beta | 2 | 0 | 0 | 0 | 0 | 2 |
| GL-IPQ5332/AP-MI01.2 | 4.8.7 | 1 | 0 | 0 | 1 | 0 | 0 |
| GL-IPQ5332/AP-MI01.6 | 4.8.4 | 1 | 0 | 0 | 1 | 0 | 0 |
| GL-IPQ5332/AP-MI01.6 | 4.9.0 | 1 | 0 | 0 | 1 | 0 | 0 |
| GL-IPQ5332/AP-MI04.1-C2 | 4.7.3 | 1 | 0 | 0 | 0 | 0 | 1 |
| GL-IPQ5332/AP-MI04.1-C2 | 4.8.1 | 3 | 0 | 0 | 3 | 0 | 0 |
| GL-IPQ5332/AP-MI04.1-C2 | 4.8.3 | 1 | 0 | 0 | 1 | 0 | 0 |
| GL-MT2500 | 4.7.0 | 2 | 0 | 2 | 0 | 0 | 0 |
| GL-MT2500 | 4.7.4 | 7 | 0 | 7 | 0 | 0 | 0 |
| GL-MT2500 | 4.7.13 | 9 | 0 | 8 | 1 | 0 | 0 |
| GL-MT2500 | 4.9.0 | 1 | 0 | 0 | 1 | 0 | 0 |
| GL-MT3000 | 4.7.4 | 10 | 0 | 9 | 1 | 0 | 0 |
| GL-MT3000 | 4.8.0 | 3 | 0 | 3 | 0 | 0 | 0 |
| GL-MT3000 | 4.8.1 | 17 | 0 | 3 | 14 | 0 | 0 |
| GL-MT3000 | 4.8.2 | 2 | 0 | 0 | 2 | 0 | 0 |
| GL-MT3000 | 4.9.0 | 6 | 0 | 0 | 6 | 0 | 0 |
| GL-MT3000 | 4.11.0 | 5 | 0 | 1 | 0 | 3 | 1 |
| GL-MT3600BE | 4.8.5 | 2 | 0 | 0 | 2 | 0 | 0 |
| GL-MT3600BE | 4.9.0 | 3 | 0 | 0 | 1 | 0 | 2 |
| GL-MT3600BE | 4.9.1 | 2 | 0 | 0 | 2 | 0 | 0 |
| GL-MT5000 | 4.8.6 | 5 | 0 | 0 | 5 | 0 | 0 |
| GL-MT5000 | 4.9.0 | 13 | 0 | 0 | 13 | 0 | 0 |
| GL-MT6000 | 4.7.0 | 1 | 0 | 1 | 0 | 0 | 0 |
| GL-MT6000 | 4.7.7 | 6 | 0 | 5 | 0 | 1 | 0 |
| GL-MT6000 | 4.8.1 | 1 | 0 | 0 | 0 | 0 | 1 |
| GL-MT6000 | 4.8.2 | 5 | 0 | 0 | 5 | 0 | 0 |
| GL-MT6000 | 4.8.3 | 12 | 0 | 3 | 8 | 0 | 1 |
| GL-MT6000 | 4.8.4 | 1 | 0 | 0 | 1 | 0 | 0 |
| GL-MT6000 | 4.9.0 | 4 | 0 | 1 | 3 | 0 | 0 |
| GL-MT6000 | 4.9.1 | 5 | 4 | 0 | 1 | 0 | 0 |
| GL-MT6000 | 4.11.0 | 1 | 0 | 0 | 0 | 1 | 0 |
| **All routers** | | **183** | **24** | **47** | **81** | **18** | **13** |
| GL-RM1 (KVM) | 1.10.1 | 1 | 0 | 0 | 0 | 0 | 1 |

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
