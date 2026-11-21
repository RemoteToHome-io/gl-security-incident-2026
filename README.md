# GL.iNet cloud incident, November 2026: what is known, how to check, how to recover

A place to coordinate findings on the GL.iNet cloud remote-management incident of 20 November 2026,
kept by [RemoteToHome Consulting](https://remotetohome.io). GL.iNet's information is spread over
forum threads that change and get buried; this page collects what is known in one place and is
updated as findings come in.

We manage a large and varied set of GL.iNet routers and are checking them model by model. The
results go into [docs/field-survey.md](docs/field-survey.md) as counts by model and firmware, with
nothing that identifies a client, a network or a device. Every statement here says where it comes
from and how it was checked. Corrections and findings from anyone are welcome: see
[CONTRIBUTING.md](CONTRIBUTING.md).

**Last reviewed: 2026-11-21 18:20 UTC.** GL.iNet's notice changes; read
[the current version](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056)
as well.

This is not an official GL.iNet page and GL.iNet has not reviewed it.

## The short version

1. **If your router or KVM had GL.iNet's cloud service switched on, check it now**, before you
   reboot or upgrade it. Some traces only exist until the next restart.
2. **GL.iNet's published check looks for one process (`crond -i /tmp/.log`). It does not catch
   everything.** A root remote shell has been found on GL-AXT1800 routers that this check reads as
   healthy. Use the wider checks in [Check a device](#check-a-device).
3. **Killing a process or reinstalling firmware does not undo a compromise.** If a device was hit,
   every key and password stored on it should be treated as read by someone else. That includes
   its VPN client profiles and SSH keys: access has to be removed on the server side as well. See
   [If you find something](#if-you-find-something).
4. **GL.iNet says the attack path is closed on its side** and that fixed stable firmware for routers
   and KVMs is scheduled for 22 November 2026. The weakness on the router side is still present in
   the firmware we have read.

## What GL.iNet has said

From the [security notice](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056)
as it read at 16:00 UTC on 21 November 2026:

- A vulnerability in its cloud remote management services was exploited to install malicious
  software on some routers and KVM devices.
- The attack path has been blocked. This does not remove malware from devices already infected.
- The indicator to look for is a running process containing `crond -i /tmp/.log`.
- If the check finds nothing and there is no other reason for suspicion, no cleanup is needed.
- KVM beta firmware with fixes is available; stable firmware for routers and KVMs is scheduled for
  22 November 2026.

GL.iNet has not published which models and firmware versions were affected, the time window, how
many devices, or what the malicious software does.

## What has been found beyond that

Full list with sources and evidence in [docs/findings.md](docs/findings.md). The main points:

| Finding | Status |
|---|---|
| A root remote shell to `170.39.226.219` on GL-AXT1800 routers on firmware 4.8.3, started about 21:40 UTC on 20 November | Three independent reports; one verified by us on our own router |
| The shell came in through the GoodCloud client on the router, which passes a value from a cloud message to the shell without checking it | Verified by us by reading the client's code; not confirmed by GL.iNet |
| The same unchecked code is in AXT1800 4.8.4 (beta of 11 November) and GL-MT3000 4.11.0 | Verified by us |
| It runs whether or not AstroWarp / SD-WAN is enabled | Verified by us |
| The shells connected to `170.39.226.219`, a rented server at a US hosting provider with no named customer in the registry. An abuse report went to the provider on 21 November 2026 | Verified by us from public registries; see [docs/attacker-infrastructure.md](docs/attacker-infrastructure.md) |
| That shell leaves no file behind and is gone after a reboot; its named pipe `/tmp/f` remains until then | Verified by us |
| KVM firmware RM1PE 1.10.2 removes an implant called "gl-helper" at boot; RM1 1.10.2 has no such cleanup | Verified by us from the official images |
| On the RM1, an upgrade that keeps settings carries the password, SSH keys and `/etc/kvmd/user` across | Verified by us on a test unit |

## Check a device

The most complete check is the community triage script by Admon. It covers the indicators listed
here, saves evidence before it changes anything, and is being updated as findings come in:

- Script and documentation: <https://github.com/admonstrator/glinet-csa-2026-01>
- Step-by-step guide: <https://gl-i.net/security/csa-2026-01/fix/>

Read a script before you run it as root. To keep it off the device's storage, pipe it over SSH from
a copy you have read, as that repository's README shows.

If you only want to look by hand, over SSH on a router:

```
ps w | grep -E 'crond -i|mkfifo|nc [0-9]|sh -i' | grep -v grep
```

```
ls -la /tmp/f /tmp/.log
```

```
ls -l /bin/netstat
```

- A `crond -i /tmp/.log` process is GL.iNet's indicator.
- `nc` with an IP address, `/bin/sh -i`, or `mkfifo` is the remote shell described in
  [docs/router-reverse-shell.md](docs/router-reverse-shell.md).
- `/tmp/f` as a named pipe (the line starts with `p`) means that shell has run since the last boot,
  even if it has since been stopped.
- GL.iNet staff warn that `netstat` itself may have been replaced on an infected device and that
  running the replacement starts the malware. On a router it should be a link to `busybox`. Check
  that before you use `netstat`.

No output only tells you nothing is running now and nothing of this kind has run since the last
boot. It cannot tell you a device was never compromised.

For KVMs see [docs/kvm-firmware.md](docs/kvm-firmware.md).

## If you find something

**A compromised router is not the only thing that is compromised. Everything it held a key for is
too.** The attacker had a root shell, so every key, password and profile stored on the device
could be copied. Cleaning or reinstalling the router does not take those back. You have to remove
that access at the other end.

1. Save the output and note the time. In a business network, talk to whoever handles incidents or
   insurance for you before changing anything.
2. Stop the processes or disconnect the device from the internet.
3. **Revoke every VPN client profile the router held, on the server side.** Deleting the profile
   from the router is not enough: a copy of it still works from anywhere.
   - WireGuard and AmneziaWG: remove that peer on the server, or give the server new keys. Then
     create a new profile with a new key pair for the router.
   - OpenVPN: revoke the client certificate on the server, or change the username and password
     if the profile used them.
   - Commercial VPN services: sign in to the provider and regenerate the keys or change the
     password. A copied profile is a login to your account.
   - ZeroTier, Tailscale and similar: remove the router's node from the network in the controller
     or admin console, then join again as a new node after the router is reinstalled.
4. **If the router was itself a VPN server,** its private key was readable too. Give it a new key
   and issue new profiles to every client.
5. **Revoke SSH keys the router used to log in elsewhere.** If the router held an SSH private key
   (by default `/root/.ssh/id_dropbear`; also any `id_rsa`, `id_ed25519` or similar under
   `/root/.ssh`), every machine that trusts it must have the matching public key removed from its
   `authorized_keys`. Check the router's own `authorized_keys` as well for keys you did not add.
6. Replace the rest of what it stored: Wi-Fi passwords, the admin password, DDNS and cloud
   credentials.
7. Reinstall firmware without keeping settings, or factory-reset, then set the device up again
   from known-good information and the new keys.
8. Check the computers behind the device. For a KVM, check the computer it was attached to.

## Reducing exposure until fixed firmware is installed

This is temporary hardening. It does not clean a device that was already hit; for that, see
[If you find something](#if-you-find-something).

- Switch GoodCloud off on the device itself. On the router firmware we read, the cloud client only
  starts when GoodCloud is enabled on the device. In the admin panel that is the GoodCloud
  switch. Over SSH, this is what we ran on a GL-AXT1800 on 4.8.3, after which the
  client was no longer running and no longer set to start:

  ```
  /etc/init.d/gl-cloud stop
  uci set gl-cloud.@cloud[0].enable='0'
  uci commit gl-cloud
  /etc/init.d/gl-cloud disable
  ```

  The device disappears from GoodCloud until you turn it back on. Make sure you have another way
  to reach a remote device first.
- To also drop traffic to the address range seen in the remote-shell cases, on firmware that uses
  nftables (run on the same router; it lasts until the next reboot):

  ```
  nft insert rule inet fw4 output ip daddr 170.39.226.0/24 counter drop
  ```
- On a KVM, switch the cloud service off in its settings if you do not need it. A forum user
  reports the switch is under "More Settings"; we have not checked where it is on each model.
- Do not rely on "I never used AstroWarp" or "remote access was off": the affected code runs
  regardless.

## Firmware downloads

- GL.iNet's own download pages are linked from its
  [security notice](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056).
- Our community mirror at <https://gl-fw.remotetohome.io/> keeps stable, beta and older builds for
  GL.iNet routers and KVMs in one place, including the KVM security builds. File checksums are
  verified automatically against the files GL.iNet publishes. It is useful when you need a specific
  build, an older one to compare against, or a copy that stays available.

Check which build you are installing: GL.iNet has more than one build under the same version
number, and for KVMs what the 1.10.2 build does differs by model. See
[docs/kvm-firmware.md](docs/kvm-firmware.md).

## Recovery tools (planned)

Two RemoteToHome projects are being prepared for the cases GL.iNet's "factory reset and set up
again" advice does not cover, mainly devices that are far away:

- **[gl-portable-backup](https://github.com/RemoteToHome-io/gl-portable-backup)**: an existing
  backup and restore plugin, being extended to carry only the settings a person chose, so that a
  restore does not bring an attacker's changes back.
- **gl-remote-rescue** (not yet released): wipe and reinstall a remote router and bring remote
  access back on first boot, carrying across only a short, inspected list of settings.

Neither is ready for incident use yet. This page will say so when they are.

## More detail

- [docs/findings.md](docs/findings.md): every finding, its source, and how it was checked
- [docs/field-survey.md](docs/field-survey.md): devices checked so far, by model and firmware
- [docs/router-reverse-shell.md](docs/router-reverse-shell.md): the AXT1800 remote shell
- [docs/attacker-infrastructure.md](docs/attacker-infrastructure.md): what is known about the address the shells
  connected to, and the abuse report
- [docs/kvm-firmware.md](docs/kvm-firmware.md): what the KVM 1.10.2 firmware does and does not do
- [docs/monitoring.md](docs/monitoring.md): how to record what the cloud sends a device
- [tools/cloud-watch](tools/cloud-watch): a small watcher for a test device

## What is deliberately not published here

The exact cloud message that triggers the router-side weakness, and anything else that would work
as instructions for attacking a device. Those details belong with GL.iNet's security team
(security@gl-inet.com), not here. Reports that include them will be edited before they are merged.

## Credits

- [Admon](https://forum.gl-inet.com/u/admon/) for the triage script, the first firmware
  comparison, and the guide at gl-i.net.
- Forum users kosrkosr and TakashiSasaki for the first two remote-shell reports, and AdamK for the
  connection checks.
- Everyone who posted output in the GL.iNet forum threads.

## Disclaimer and licence

Provided as is, without warranty. Nothing here can prove a device is clean.

Copyright (c) 2026 RemoteToHome Consulting. Text and tools are released under the
[GNU General Public License, version 3](LICENSE).
