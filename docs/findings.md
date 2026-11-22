# Findings

One row per finding. "How it is known" uses four labels:

- **GL statement**: said by GL.iNet or its staff, with a link.
- **Verified**: checked first-hand by the named party, with the method.
- **Reported**: posted by someone else and not reproduced here.
- **Unconfirmed**: a single claim with no supporting evidence yet.

Times are UTC. Add rows through a pull request or an issue; see [CONTRIBUTING.md](../CONTRIBUTING.md).

## What GL.iNet has said

| ID | Finding | How it is known | Source |
|---|---|---|---|
| G‑1 | A vulnerability in GL.iNet's cloud remote management services was exploited to install malicious software on some routers and KVM devices. | GL statement | [Notice](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056), as read 2026-11-22 07:12 (marked "Last updated November 21, 2026") |
| G‑2 | The attack path has been blocked; devices cannot be newly infected through it. This does not clean devices already infected. | GL statement | Same |
| G‑3 | Indicator: a running process containing `crond -i /tmp/.log`. | GL statement | Same |
| G‑4 | Stable firmware with fixes for routers and KVMs is scheduled for 2026-11-22. KVM beta builds are available: 1.10.2 for RM1, RM1V2, RM1PE, RM4PE, RM10, RM10RC; 1.8.6 for RMQ1. | GL statement | Same |
| G‑5 | `netstat` may have been replaced on an infected device, and running it starts the malware. | GL statement (staff) | [Router check thread, post 41](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/41) |
| G‑6 | An anonymous report from an infected device shows `netstat` was replaced. | Reported by a forum user | [Router check thread, post 48](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/48) |

## Routers

| ID | Finding | How it is known | Source |
|---|---|---|---|
| R‑1 | A root remote shell (`/bin/sh -i` joined to `nc 170.39.226.219 <port>` through a named pipe `/tmp/f`) was running on a GL-AXT1800, firmware 4.8.3, with GoodCloud on. It started at 21:40:24 on 2026-11-20. | Verified by RemoteToHome: process list, `/proc`, `netstat` on the router, 2026-11-21 15:25 | [Details](router-reverse-shell.md) |
| R‑2 | Two more GL-AXT1800 routers on 4.8.3 had the same shell to the same address on other ports; one started at about 21:40 on 2026-11-20. | Reported | [Posts 10](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/10) and [22](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/22) |
| R‑3 | The shell command is appended to an `iptables` rule for the chain `SDWAN_IP_MAPPING`. The GoodCloud client on the router (package `gl-sdk4-cloud`) builds that rule from values in a cloud message and passes it to the shell without validating them. | Verified by RemoteToHome: read the client code from the affected router. Not confirmed by GL.iNet. | [Details](router-reverse-shell.md) |
| R‑4 | That code runs whether or not AstroWarp / SD-WAN is enabled. It was disabled on the affected router. | Verified by RemoteToHome: code and the router's configuration | Same |
| R‑5 | The same code is present in GL-AXT1800 4.8.4 (beta built 2026-11-11) and GL-MT3000 4.11.0 (built 2026-09-24). The earliest firmware in which we find it is GL-MT3000 4.7.0, released 2024-12-05; the GL-MT3000 4.6.9 and GL-AXT1800 4.6.11 images do not have it. | Verified by RemoteToHome: read the client code from both; the official images for the earlier versions | Same |
| R‑6 | The GoodCloud client on the router only starts when GoodCloud is enabled on the device. | Verified by RemoteToHome: the client's start script on AXT1800 4.8.4 | |
| R‑7 | The shell is not persistent. No file in the router's writable storage changed in that period except the client's own state file, and the shell is gone after a reboot. | Verified by RemoteToHome (file change times on the affected router); reboot behaviour Reported in post 22 | [Details](router-reverse-shell.md) |
| R‑8 | The named pipe `/tmp/f` stays after the shell is stopped and until the next reboot. Its timestamp is the last data it carried. | Verified by RemoteToHome on the affected router; timestamp meaning tested on a different Linux system | Same |
| R‑9 | GL.iNet's indicator process (G-3) was not present on the router in R-1. | Verified by RemoteToHome | Same |
| R‑10 | GL.iNet's firmware listing holds stable router firmware dated 22 and 23 November 2026 for GL-AXT1800 (4.8.4), GL-MT3000 (4.11.1), GL-MT6000 (4.11.1), GL-MT5000 (4.9.1), GL-BE9300 (4.10.2), GL-BE14000 (4.9.3), GL-E5800 (4.10.3), GL-X2000 (4.7.14) and GL-MG1300 (4.11.1). At 2026-11-22 21:34 there was none yet for GL-AX1800, GL-MT2500 or GL-MT3600BE. (At 06:20 that day there was none for any router.) | Verified by RemoteToHome: the listing as copied by our [firmware mirror](https://gl-fw.remotetohome.io/) | |
| R‑11 | An older, separate backdoor: lines added at the top of the startup script `/etc/init.d/urandom_seed`, a file `/bin/ulogd`, and an added line in `/lib/upgrade/keep.d/netifd` so that both survive upgrades. We found it installed and running on 49 routers we manage: GL-MT2500 (4.7.0, 4.7.4, 4.7.13); GL-MT3000 (4.7.4, 4.8.0, 4.8.1, 4.11.0); GL-MT6000 (4.7.0, 4.7.7, 4.8.3, 4.9.0); GL-AX1800 (4.7.0, 4.8.3); GL-AXT1800 (4.7.0). On the 40 whose clock gave a real date, the files are dated from 2025-09-15 to 2026-05-24. The indicator in G-3 was not present on any of them. On three other routers we checked earlier (AXT1800 4.8.3 and 4.8.4 beta, MT3000 4.11.0) both files are identical to the firmware image. | Reported by forum users, with dates from September and October 2025. Verified by RemoteToHome on 2026-11-22: files compared with the firmware's own copies in `/rom`, process list | Notice thread, posts [26](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/26) and [58](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/58); [forum topic](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097); [field survey](field-survey.md) |
| R‑12 | A GL-MT3000 on 4.11.0 with GoodCloud connected, not rebooted since 19 November, showed none of the indicators. | Reported | [Router check thread, post 47](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/47) |
| R‑13 | The same shell was still running on 23 more routers when we checked them on 2026-11-22: GL-AXT1800 (firmware 4.8.2 and 4.8.3) and GL-MT6000 (firmware 4.9.1). On the GL-MT6000 routers the shell was not connected; its loop was retrying against the address every few seconds. None had been restarted. On the first, three shells had started at 20:46:35, 21:17:27 and 21:39:45 on 2026-11-20; on the second, one at 21:39:47. | Verified by RemoteToHome on routers we manage: process list and `/proc` | [Field survey](field-survey.md) |
| R‑14 | The handler in R-3 ends by writing `/etc/mp_ip_mapping_info`. An empty copy of that file written on or after 2026-11-20, on a router that does not use AstroWarp, shows the handler ran. It survives a restart; the firewall rule does not. | Verified by RemoteToHome: client code, and the file on affected routers | |
| R‑15 | Routers that show the rule but no shell also ran a command from the attacker as root. We recovered the cloud message from the client's memory on seven routers (GL-MT3000 and GL-MT5000 on 4.9.0, GL-MT3600BE on 4.8.5 and 4.9.0). It is the same on all seven apart from a device identifier. It looks for the folders in K-1 (`/etc/config/.gl`, `/etc/glinet/.cache`) and sends the result to `170.39.226.219`. | Verified by RemoteToHome on routers we manage. The same message recovered from a GL-BE9300 is Reported by another owner | |
| R‑16 | Fragments of the same folder check, typed by hand, were in the memory of two of the three shells on one router in R-13. | Verified by RemoteToHome: memory of the shell processes, saved before the shells were ended | |
| R‑17 | The rule from R-3 was present on routers of seven models that we manage: GL-AXT1800, GL-AX1800, GL-MT2500, GL-MT3000, GL-MT5000, GL-MT6000 and GL-MT3600BE, on firmware from 4.7.4 to 4.9.0. | Verified by RemoteToHome, 2026-11-21 and 2026-11-22; the check of our routers is still running | [Field survey](field-survey.md) |
| R‑18 | The backdoor in R-11 was installed in batches, on routers in unrelated networks. The file dates fall on 15 September 2025; 13 October 2025; 7, 9, 12, 14, 16, 17, 19, 20, 21 and 29 December 2025; 1 January 2026; 6, 7 and 27 February 2026; 1, 28 and 29 March 2026; 21, 23 and 24 May 2026. On 20 December 2025 it reached 11 routers on 11 different networks, six of them within 14 minutes. 44 of the 49 routers have no public address on their WAN port, so they are not directly reachable from the internet. Each of the 38 we could check was bound to GoodCloud before its install date, and each runs a build of the cloud package later than the one in which the code in R-3 first appears. How it was installed is not known. | Verified by RemoteToHome on routers we manage: file change times, WAN address, cloud binding time and package version read on each router. Not confirmed by GL.iNet | [Field survey](field-survey.md) |
| R‑19 | In GL-MT3000 4.11.1 (cloud package build git-2026.323) the AstroWarp module of the cloud client is the file that changed in substance against 4.11.0 (git-2026.240). It gained a parameter validator with messages for `virtual_ip_info`, `connection_info` and `global_ip_set` and patterns that accept only address characters. The `iptables` format string from R-3 is still there; its inputs are now checked first. | Verified by RemoteToHome: both official images, each matching its published checksum, compared file by file and by readable text, not by instruction listing. A differently built fix in GL-BE14000 4.9.3, covering eight cloud commands, is Reported by Admon | |
| R‑20 | The same firmware adds a package `gl-sdk4-system-check` with a script that runs once at the first start after the update. It restores `/etc/init.d/urandom_seed` from `/rom` whenever the two differ (the file changed by the backdoor in R-11). Only if `/etc/config/.gl` exists, it also removes that folder, one line in `/etc/rc.local` and three scheduled-task lines that point into `/etc/glinet/.cache`. It does not remove `/bin/ulogd`, `/usr/bin/monitord`, the keep-list line or `/etc/glinet/.cache` itself. | Verified by RemoteToHome: the script read in full (46 lines). What still runs after it has not been tested | |
| R‑21 | One further weakness in the cloud client, separate from the handler in R-3, is not addressed in GL-MT3000 4.11.1: the component involved is byte for byte the same as in 4.11.0. It is being reported to GL.iNet and is not described here. | Verified by RemoteToHome: checksums of the component in both images | |

## The remote address

| ID | Finding | How it is known | Source |
|---|---|---|---|
| A‑1 | `170.39.226.219` has reverse DNS `aa27e2db.ewr.customer.misaka.io` and sits in `170.39.226.0/24`, registered to Misaka Network, Inc., with no customer reassignment recorded. | Verified by RemoteToHome: DNS and ARIN registration data, 2026-11-21 | [Details](attacker-infrastructure.md) |
| A‑2 | The range is routed by AS917. | Verified by RemoteToHome: RIPEstat, 2026-11-21 | Same |
| A‑3 | The only earlier public trace is a passive-DNS record of `szlsntvpnxxx04.top` on this address on 2022-01-22. No record in GreyNoise or Shodan InternetDB. | Verified by RemoteToHome: those services' public lookups, 2026-11-21 | Same |
| A‑4 | An abuse report was sent to the provider's abuse contact on 2026-11-21 at 17:24, copied to GL.iNet. The provider replied at about 20:54 the same day: server suspended, customer notified, data preserved, no flow records for that site, further details only on legal request (Provider statement, not checked by us). | RemoteToHome | Same |
| A‑5 | Two further addresses, `66.245.219.252` and `65.20.71.131`, in the network logs of a compromised GL-RM1 KVM and in the installer script that KVM downloaded on 2026-11-19 (K-9). We searched everything we saved from routers for both: 73 state captures that include the connection table, and the check output of every router reached. No match. The address in A-1 appears in 23 of those captures. | Reported; our search Verified by RemoteToHome, 2026-11-22 | [BleepingComputer, 22 November 2026](https://www.bleepingcomputer.com/news/security/hackers-exploit-glinet-cloud-flaw-to-infect-routers-kvm-devices/) |

## KVMs

| ID | Finding | How it is known | Source |
|---|---|---|---|
| K‑1 | RM1PE firmware 1.10.2 adds a boot-time cleanup. If any of `etc/glinet/.cache/gl-helper`, `etc/glinet/.cache/gb`, `etc/config/.gl/gl-helper`, `etc/config/.gl/gb` exists in the writable layer, it deletes `etc/glinet/.cache`, `etc/config/.gl`, `etc/rc.local`, `etc/crontabs/root` and `usr/bin/netstat` there. | Verified by Admon and by RemoteToHome: official image, compared with 1.10.1 | [Details](kvm-firmware.md) |
| K‑2 | RM1 firmware 1.10.2 has no such cleanup. | Verified by RemoteToHome: official image | Same |
| K‑3 | RM1V2 firmware 1.10.2 has no such cleanup. | Verified by Admon | [His README](https://github.com/admonstrator/glinet-csa-2026-01#-firmware-notes) |
| K‑4 | 1.10.2 makes the cloud remote terminal always use TLS with a fixed certificate authority. In 1.10.1 a cloud-supplied setting could switch TLS off. | Verified by Admon (RM1PE, RM1V2) and RemoteToHome (RM1PE, RM1; TLS seen on the wire on an RM1) | [Details](kvm-firmware.md) |
| K‑5 | On an RM1, upgrading to 1.10.2 with settings kept rebuilds the writable layer from a fixed list. Files outside the list are dropped. The list includes the password file, `/root/.ssh`, the SSH host keys and everything under `/etc/kvmd/user`. | Verified by RemoteToHome on a test RM1, with marker files | Same |
| K‑6 | KVM firmware runs any script named `S??*` in `/etc/kvmd/user/scripts` at boot, and that directory is inside the list in K-5. | Verified by RemoteToHome by reading the firmware. Whether a script there survives an upgrade has not been tested. | Same |
| K‑7 | RM1 1.10.2 leaves SSH switched off after the upgrade. `/etc/init.d/S50dropbear enable` in the web terminal turns it back on. | Verified by RemoteToHome on a test RM1 | Same |
| K‑8 | An RM10 on 1.11.3 beta whose owner says the cloud service was not in use "appears infected". No details given yet. | Reported | [Router check thread, post 45](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/45) |
| K‑9 | The installer on that KVM is a script named `ni.sh`. As described by the publication that examined a copy: it recognises many GL.iNet router and KVM models, downloads programs named `gl-helper` and `gb`, sets itself to start again after a reboot, can run its process under the name `crond -i /tmp/.log` (the indicator in G-3), replaces `netstat` with a script that hides its own connections (G-5), and can add SSH keys. | Reported | [BleepingComputer, 22 November 2026](https://www.bleepingcomputer.com/news/security/hackers-exploit-glinet-cloud-flaw-to-infect-routers-kvm-devices/) |

## Not yet known

1. Whether any router was made to contact an address other than `170.39.226.219`. Two more
   are reported for KVMs (A-5); we have not found them on a router.
2. Whether devices with the cloud service enabled but not bound to an account were reachable.
3. Whether the fixed firmware of every model carries the same fix. We read one (R-19); another is
   reported to be built differently.
4. What the process in G-3 does on a router. For KVMs it is reported to be the installer's own
   process under another name (K-9).
5. How the older backdoor in R-11 was installed.
6. How many devices were reached. Our own count is in the [field survey](field-survey.md).
