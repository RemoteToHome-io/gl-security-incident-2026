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
| G-1 | A vulnerability in GL.iNet's cloud remote management services was exploited to install malicious software on some routers and KVM devices. | GL statement | [Notice](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056), version of 2026-11-21 16:00 |
| G-2 | The attack path has been blocked; devices cannot be newly infected through it. This does not clean devices already infected. | GL statement | Same |
| G-3 | Indicator: a running process containing `crond -i /tmp/.log`. | GL statement | Same |
| G-4 | Stable firmware with fixes for routers and KVMs is scheduled for 2026-11-22. KVM beta builds are available: 1.10.2 for RM1, RM1V2, RM1PE, RM4PE, RM10, RM10RC; 1.8.6 for RMQ1. | GL statement | Same |
| G-5 | `netstat` may have been replaced on an infected device, and running it starts the malware. | GL statement (staff) | [Router check thread, post 41](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/41) |
| G-6 | An anonymous report from an infected device shows `netstat` was replaced. | Reported by a forum user | [Router check thread, post 48](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/48) |

## Routers

| ID | Finding | How it is known | Source |
|---|---|---|---|
| R-1 | A root remote shell (`/bin/sh -i` joined to `nc 170.39.226.219 <port>` through a named pipe `/tmp/f`) was running on a GL-AXT1800, firmware 4.8.3, with GoodCloud on. It started at 21:40:24 on 2026-11-20. | Verified by RemoteToHome: process list, `/proc`, `netstat` on the router, 2026-11-21 15:25 | [Details](router-reverse-shell.md) |
| R-2 | Two more GL-AXT1800 routers on 4.8.3 had the same shell to the same address on other ports; one started at about 21:40 on 2026-11-20. | Reported | [Posts 10](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/10) and [22](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/22) |
| R-3 | The shell command is appended to an `iptables` rule for the chain `SDWAN_IP_MAPPING`. The GoodCloud client on the router (package `gl-sdk4-cloud`) builds that rule from values in a cloud message and passes it to the shell without validating them. | Verified by RemoteToHome: read the client code from the affected router. Not confirmed by GL.iNet. | [Details](router-reverse-shell.md) |
| R-4 | That code runs whether or not AstroWarp / SD-WAN is enabled. It was disabled on the affected router. | Verified by RemoteToHome: code and the router's configuration | Same |
| R-5 | The same code is present in GL-AXT1800 4.8.4 (beta built 2026-11-11) and GL-MT3000 4.11.0 (built 2026-09-24). | Verified by RemoteToHome: read the client code from both | Same |
| R-6 | The GoodCloud client on the router only starts when GoodCloud is enabled on the device. | Verified by RemoteToHome: the client's start script on AXT1800 4.8.4 | |
| R-7 | The shell is not persistent. No file in the router's writable storage changed in that period except the client's own state file, and the shell is gone after a reboot. | Verified by RemoteToHome (file change times on the affected router); reboot behaviour Reported in post 22 | [Details](router-reverse-shell.md) |
| R-8 | The named pipe `/tmp/f` stays after the shell is stopped and until the next reboot. Its timestamp is the last data it carried. | Verified by RemoteToHome on the affected router; timestamp meaning tested on a different Linux system | Same |
| R-9 | GL.iNet's indicator process (G-3) was not present on the router in R-1. | Verified by RemoteToHome | Same |
| R-10 | No router firmware containing a fix had been published by 2026-11-21 16:00. | Verified by RemoteToHome: GL.iNet's firmware listing for eight models; see also G-4 | |
| R-11 | A startup script `/etc/init.d/urandom_seed` was overwritten on some routers as early as September 2025, surviving upgrades through a modified `/lib/upgrade/keep.d/netifd`. | Unconfirmed: one forum post with no evidence attached; a second user says they see the same. On three routers we checked (AXT1800 4.8.3 and 4.8.4 beta, MT3000 4.11.0) both files are identical to the firmware image. | Notice thread, posts [26](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/26) and [58](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056/58) |
| R-12 | A GL-MT3000 on 4.11.0 with GoodCloud connected, not rebooted since 19 November, showed none of the indicators. | Reported | [Router check thread, post 47](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/47) |

## The remote address

| ID | Finding | How it is known | Source |
|---|---|---|---|
| A-1 | `170.39.226.219` has reverse DNS `aa27e2db.ewr.customer.misaka.io` and sits in `170.39.226.0/24`, registered to Misaka Network, Inc., with no customer reassignment recorded. | Verified by RemoteToHome: DNS and ARIN registration data, 2026-11-21 | [Details](attacker-infrastructure.md) |
| A-2 | The range is routed by AS917. | Verified by RemoteToHome: RIPEstat, 2026-11-21 | Same |
| A-3 | The only earlier public trace is a passive-DNS record of `szlsntvpnxxx04.top` on this address on 2022-01-22. No record in GreyNoise or Shodan InternetDB. | Verified by RemoteToHome: those services' public lookups, 2026-11-21 | Same |
| A-4 | An abuse report was sent to the provider's abuse contact on 2026-11-21 at 17:24, copied to GL.iNet. The provider replied at about 20:54 the same day: server suspended, customer notified, data preserved, no flow records for that site, further details only on legal request (Provider statement, not checked by us). | RemoteToHome | Same |

## KVMs

| ID | Finding | How it is known | Source |
|---|---|---|---|
| K-1 | RM1PE firmware 1.10.2 adds a boot-time cleanup. If any of `etc/glinet/.cache/gl-helper`, `etc/glinet/.cache/gb`, `etc/config/.gl/gl-helper`, `etc/config/.gl/gb` exists in the writable layer, it deletes `etc/glinet/.cache`, `etc/config/.gl`, `etc/rc.local`, `etc/crontabs/root` and `usr/bin/netstat` there. | Verified by Admon and by RemoteToHome: official image, compared with 1.10.1 | [Details](kvm-firmware.md) |
| K-2 | RM1 firmware 1.10.2 has no such cleanup. | Verified by RemoteToHome: official image | Same |
| K-3 | RM1V2 firmware 1.10.2 has no such cleanup. | Verified by Admon | [His README](https://github.com/admonstrator/glinet-csa-2026-01#-firmware-notes) |
| K-4 | 1.10.2 makes the cloud remote terminal always use TLS with a fixed certificate authority. In 1.10.1 a cloud-supplied setting could switch TLS off. | Verified by Admon (RM1PE, RM1V2) and RemoteToHome (RM1PE, RM1; TLS seen on the wire on an RM1) | [Details](kvm-firmware.md) |
| K-5 | On an RM1, upgrading to 1.10.2 with settings kept rebuilds the writable layer from a fixed list. Files outside the list are dropped. The list includes the password file, `/root/.ssh`, the SSH host keys and everything under `/etc/kvmd/user`. | Verified by RemoteToHome on a test RM1, with marker files | Same |
| K-6 | KVM firmware runs any script named `S??*` in `/etc/kvmd/user/scripts` at boot, and that directory is inside the list in K-5. | Verified by RemoteToHome by reading the firmware. Whether a script there survives an upgrade has not been tested. | Same |
| K-7 | RM1 1.10.2 leaves SSH switched off after the upgrade. `/etc/init.d/S50dropbear enable` in the web terminal turns it back on. | Verified by RemoteToHome on a test RM1 | Same |
| K-8 | An RM10 on 1.11.3 beta whose owner says the cloud service was not in use "appears infected". No details given yet. | Reported | [Router check thread, post 45](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/45) |

## Open questions

1. Which models and firmware versions were sent the router command in R-3?
2. What is the full time window, and is `170.39.226.219` the only address involved?
3. What does the process in G-3 do, and how does it relate to the "gl-helper" files in K-1?
4. Were devices with the cloud service enabled but not bound to an account reachable?
5. What was run through the remote shells?
6. Which firmware removes the unchecked code in R-3?
