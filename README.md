# GL.iNet cloud incident, November 2026: what is known, how to check, how to recover

> **New, 22 November 2026: the exploit in detail, and where it came from.** GL.iNet has released
> fixed firmware, so the details we had held back are now published:
>
> - [Technical breakdown](docs/technical-breakdown.md): the flaw line by line, how we read code
>   that ships only in compiled form, and its history back to firmware released in December 2024.
> - [Fixed firmware](#fixed-firmware): what the fix does, what its clean-up leaves behind, and
>   which models have it.
>
> One further weakness is not addressed by the fixed firmware we read. We reported it to GL.iNet
> on 22 November and are withholding it until it is fixed.

A place to coordinate findings on the GL.iNet cloud remote-management incident of 20 November 2026,
kept by [RemoteToHome Consulting](https://remotetohome.io). GL.iNet's information is spread over
forum threads that change and get buried; this page collects what is known in one place and is
updated as findings come in.

We manage a large and varied set of GL.iNet routers and are checking them model by model. The
results go into [docs/field-survey.md](docs/field-survey.md) as counts by model and firmware, with
nothing that identifies an owner, a network or a device. Every statement here says where it comes
from and how it was checked. Corrections and findings from anyone are welcome: see
[CONTRIBUTING.md](CONTRIBUTING.md).

**Last reviewed: 2026-11-23 08:39 UTC.** GL.iNet's notice changes; read
[the current version](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056)
as well.

This is not an official GL.iNet page and GL.iNet has not reviewed it.

## The short version

1. **The weakness on the router has shipped in GL.iNet firmware since December 2024.** The cloud
   client runs, as root, a value from a cloud message without checking it. Every version we have
   read from GL-MT3000 4.7.0 (released 5 December 2024) to 4.11.0 has it. For 715 days before the
   attack of 20 November 2026, any such router with GoodCloud switched on would run whatever
   command arrived over that channel, whether or not AstroWarp was in use. GL.iNet has not said
   when the cloud side became usable by an outsider. The client is shipped as compiled code and
   we have not found its source in GL.iNet's published repositories, so nobody outside the
   company was in a position to review it.
2. **This is not limited to one model, and it is not rare on the routers we manage.** Of 199
   routers we have reached so far, 166 show the attack of 20 November, an older backdoor, or both:
   a root remote shell on 24 (GL-AXT1800 and GL-MT6000), an older backdoor installed and running
   on 49 (GL-MT2500, GL-MT3000, GL-MT6000, GL-AX1800 and GL-AXT1800), and on 93 more a command
   from the attacker that ran as root. That is not a random sample; see
   [docs/field-survey.md](docs/field-survey.md).
3. **If your router or KVM had GL.iNet's cloud service switched on, check it now**, before you
   reboot or upgrade it. Some traces only exist until the next restart.
4. **GL.iNet's published check looks for one process (`crond -i /tmp/.log`). We have not found
   that process on a single router.** The remote shell, the attacker's command and the older
   backdoor all read as healthy in that check. Use the wider checks in
   [Check a device](#check-a-device).
5. **Killing a process or reinstalling firmware does not undo a compromise.** If a device was hit,
   every key and password stored on it should be treated as read by someone else. That includes
   its VPN client profiles and SSH keys: access has to be removed on the server side as well. See
   [If you find something](#if-you-find-something).
6. **GL.iNet has released fixed firmware for most router models. Install it, but do not treat it
   as a clean-up.** Stable builds dated 22 and 23 November are in its listing for eleven router
   models; see [Fixed firmware](#fixed-firmware). In the build we read, the handler that the
   attack came through has gained input validation. The firmware's own clean-up is partial, and one
   further weakness in the cloud client is not addressed in that build: we reported it to
   GL.iNet on 22 November and are not publishing it. A router that shows any sign still needs the steps in
   [If you find something](#if-you-find-something).

## What GL.iNet has said

From the [security notice](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056)
as it read at 02:38 UTC on 23 November 2026 (marked "Last updated November 23, 2026 (UTC)"; the
same text is on [GL.iNet's site](https://www.gl-inet.com/en-us/blogs/blog/glinet-security-notice-2026-11-20)).
These are GL.iNet's statements, not our findings:

- **The incident.** On 20 November 2026 GL.iNet identified a vulnerability in its cloud remote
  management services. An unauthorized party used it to access some routers and KVM devices and
  install malicious software on them.
- **The attack path has been blocked.** The cloud vulnerability is fixed and devices can no
  longer be newly infected through it. That does not remove malware from devices already
  infected.
- **Install the security firmware,** for your exact model, even if the checks find nothing.
  The notice lists minimum versions:
  - Routers: GL-MG1300, GL-MT3000, GL-MT6000: 4.11.1. GL-E5800: 4.10.3. GL-BE3600, GL-BE9300:
    4.10.2. GL-BE14000: 4.9.3. GL-BE6500, GL-MT3600BE, GL-MT5000: 4.9.1. GL-BE10000: 4.8.7.
    GL-AX1800, GL-AXT1800, GL-SFT1200, GL-X3000, GL-XE3000: 4.8.4. GL-MT2500 / GL-MT2500A,
    GL-X2000: 4.7.14.
  - KVMs: RM1, RM1V2, RM10, RM10RC, RM1PE, RM4PE: 1.10.3. RMQ1: 1.8.7.
  - "An unlisted model is not necessarily unaffected."
- **"The security firmware update removes the malware identified in this incident without
  requiring a factory reset. You can keep your existing settings during the update."**
- **The check.** On a router: `ps | grep tmp` over SSH, or search for `tmp/.log` in LuCI under
  Status → Processes. On a KVM, in its own terminal: `ps -aux | grep tmp` (`ps -a | grep tmp`
  on the RMQ1). In each case the indicator is the exact text `crond -i /tmp/.log` in the
  details of a running process. The full steps are under
  [GL.iNet's own checks](#glinets-own-checks).
- **If you find the indicator:** treat the device as infected and install the security
  firmware; settings can be kept. If the indicator is still there afterwards, or the model is
  not listed, contact support@gl-inet.com.
- **If you do not find it** and have no other reason to suspect infection: "no factory reset or
  other cleanup is needed".
- **If a KVM is infected,** also check the computer connected to it.
- **The official checks "may not detect every affected device".** The notice now says further
  indicators have been identified and points to the community script as an optional,
  unofficial, more comprehensive check.
- **Notifications.** GL.iNet says it will email the owners it identifies as affected, at the
  address of their GL.iNet cloud account.
- **The investigation continues,** including whether computers connected to affected KVMs were
  impacted.

GL.iNet has not published which firmware versions were affected, the time window, how many
devices, or what the malicious software does.

**How the notice has changed.** Earlier wording is kept, with dates, in
[docs/gl-statements.md](docs/gl-statements.md). The times are the forum's edit times of the
versions we saved; three earlier edits on 21 November were made before our first copy.

| Version edited (UTC) | What it told owners |
|---|---|
| 21 November, 10:35 | Factory reset every router and KVM and set it up again. Corrective measures had been implemented "on affected devices". No indicator and no check |
| 21 November, 14:10 | The factory reset recommendation was removed. In its place: links to two forum topics on how to check a router and a KVM |
| 21 November, 16:00 | Rewritten. One indicator, `crond -i /tmp/.log`. If found: KVM beta firmware, or a factory reset. If not found: no reset or cleanup needed. The sentence about corrective measures on affected devices was removed |
| 23 November, 01:53 | The current text above. The security firmware is said to remove the malware with settings kept; the factory reset option is gone, also when the indicator is found; the official checks "may not detect every affected device" |

**Where this differs from what we found.** The notice says the update removes the malware and
that settings can be kept. We unpacked the fixed build of seventeen router models: the clean-up
is one short script, the same in each. It puts back the start-up file the older backdoor
changes, leaves that backdoor's other file on the router, and does not examine the settings an
upgrade keeps. In our test on a GL-MT3000, start-up entries it does not name survived an
upgrade with settings kept and ran on the fixed firmware; see
[Fixed firmware](#fixed-firmware). Our advice in
[If you find something](#if-you-find-something) is unchanged: reinstall with "Keep Settings"
switched off.

## What has been found beyond that

Full list with sources and evidence in [docs/findings.md](docs/findings.md). The main points:

| Finding | Status |
|---|---|
| The GoodCloud client on the router passes a value from a cloud message to the shell, as root, without checking it. That is how the attack got in | Verified by us by reading the client's code; not confirmed by GL.iNet |
| The earliest firmware in which we find that code is GL-MT3000 4.7.0, released 5 December 2024. The 4.6 images we read do not have it. It is still in GL-AXT1800 4.8.4 (beta of 11 November) and GL-MT3000 4.11.0 | Verified by us from the official images and from routers |
| It runs whether or not AstroWarp / SD-WAN is enabled | Verified by us |
| GL.iNet's fixed firmware adds input validation in that same handler, and a start-up clean-up that restores the file the older backdoor changes. It leaves one further weakness in the cloud client unaddressed in the build we read | Verified by us in the GL-MT3000 4.11.1 build; see [Fixed firmware](#fixed-firmware) |
| The attacker used it on at least seven models: GL-AXT1800, GL-AX1800, GL-MT2500, GL-MT3000, GL-MT5000, GL-MT6000 and GL-MT3600BE, on firmware from 4.7.4 to 4.9.0 | Verified by us on routers we manage |
| On GL-AXT1800 (firmware 4.8.2 and 4.8.3) and GL-MT6000 (firmware 4.9.1) it opened a root remote shell to `170.39.226.219`, starting between 20:06 and 21:40 UTC on 20 November. On routers that were not restarted the shell was still running, or still trying to reconnect, on 22 November | Verified by us on 24 routers we manage or own; two more reported by other owners |
| On most routers it ran a single command as root and left only a firewall rule. We recovered the command from memory on seven routers: it looks for the folders of the KVM implant ("gl-helper") and sends the result to `170.39.226.219` | Verified by us; another owner recovered the same message independently |
| A separate, older backdoor is installed and running on 49 routers we manage (GL-MT2500, GL-MT3000, GL-MT6000, GL-AX1800 and GL-AXT1800; firmware 4.7.0 to 4.11.0), with file dates from September 2025 to May 2026. It was installed in batches on routers in unrelated networks, almost none of which has a public address. It starts at every boot and adds itself to the list of files kept across upgrades | Verified by us; first reported by forum users |
| GL.iNet's published indicator, a `crond -i /tmp/.log` process, was not running on any router we checked, including all of the above | Verified by us |
| The shells connected to `170.39.226.219`, a rented server at a US hosting provider with no named customer in the registry. We reported it to the provider on 21 November 2026; the provider replied the same day that it has suspended the server, notified its customer and preserved the data. On 22 November the address did not answer from any of 20 outside test points | Verified by us from public registries; see [docs/attacker-infrastructure.md](docs/attacker-infrastructure.md) |
| The shell leaves one file behind, an empty `/etc/mp_ip_mapping_info`; the shell, its named pipe `/tmp/f` and the firewall rule are gone after a reboot | Verified by us |
| KVM firmware 1.10.3 removes an implant called "gl-helper" at boot on all six models we read. In 1.10.2 the RM1PE did and the RM1 did not. It keeps no copy, so upgrading an infected KVM removes the evidence | Verified by us from the official images; see [docs/kvm-firmware.md](docs/kvm-firmware.md) |
| A KVM upgrade to 1.10.3 that keeps the configuration also keeps a boot script and an added SSH key, and the script runs on the new firmware. SSH is on at every boot in 1.10.3 | Verified by us on a test RM1 with harmless stand-ins; see [docs/kvm-firmware.md](docs/kvm-firmware.md) |
| On the RM1, an upgrade that keeps settings carries the password, SSH keys and `/etc/kvmd/user` across | Verified by us on a test unit |

## The signs, and what each one means

Seven different things get called "an indicator" in this incident. They are not equal: some show
that an attacker's command ran, some show a backdoor that is still running, and some vanish at
the next restart.

The attack of 20 November came in through one cloud command, `virtual_ip_info`, in the AstroWarp
part of the router's cloud client. The firewall rule, the state file and the cloud log entry
below are all traces of that command; the remote shell is what the attacker chose to run through
it on some routers. You may see the command's name on the forum, and the community triage
script reports the state file as "cloud-command". The checks further down and the [field survey](docs/field-survey.md) use these
names.

| Sign | What you see | Survives a restart | What it tells you |
|---|---|---|---|
| **Remote shell** | Processes `nc 170.39.226.219 <port>`, `/bin/sh -i`, `cat /tmp/f`, and a parent whose command line starts `sh -c iptables -t nat -A SDWAN_IP_MAPPING` | No | Someone outside has, or had, an interactive root shell on the router. The parent keeps retrying, so it reconnects by itself if that server answers again |
| **Shell pipe** | `/tmp/f`, a named pipe (the listing line starts with `p`) | No | The remote shell has run since the last boot, even if it has been stopped |
| **Firewall rule** | `-A SDWAN_IP_MAPPING -d 127.0.0.1/32 -j DNAT --to-destination 127.0.0.1` in the NAT table | No. It is also gone once GoodCloud is switched off on the router, without a restart | The cloud client was sent the attacker's message and ran it as root. The rule itself is harmless; it is the wrapper the attacker's command arrived in |
| **State file** | `/etc/mp_ip_mapping_info`, empty, dated 20 November 2026 or later, on a router that does not use AstroWarp | Yes | The same handler ran. It is the only trace left after a restart. It does not show what the message carried |
| **Cloud log entry** | In the device log exported from your GoodCloud account: command responses containing `"astrowarp"` with the id `1`, where ordinary commands carry a 32-character id | Yes, it is kept on GL.iNet's side | The `virtual_ip_info` command was sent to that device, with the time. Reported by one owner; we have not checked it ourselves |
| **Older backdoor** | Extra lines at the top of `/etc/init.d/urandom_seed`, a file `/bin/ulogd`, and an added line in `/lib/upgrade/keep.d/netifd`; when running, processes named `monitord` and `ujaild` | Yes; its keep-list line is there to carry it through upgrades that keep settings | A separate, earlier compromise, with file dates from October 2025 on. It starts at every boot and contacts its own servers |
| **GL.iNet's indicator** | GL.iNet's check for a router is `ps \| grep tmp` over SSH (or search for `tmp/.log` in LuCI under Status → Processes); a hit is a line containing `crond -i /tmp/.log`. On a KVM it is `ps -aux \| grep tmp` (`ps -a \| grep tmp` on the RMQ1). All four are in [GL.iNet's own checks](#glinets-own-checks) | Not known to us | The one sign GL.iNet's notice tells owners to look for. It is reported to be the name the KVM installer gives its own process (findings K-9). We have not found it on any router |

How to read a combination:

- **Rule or state file, nothing else:** the attacker's command ran on the router. On the routers
  where we recovered it, that command only looked for another implant and reported back. Treat
  the router as reached by the attacker; we cannot show that nothing more was sent.
- **Remote shell or shell pipe:** treat every key and password on the router as read.
- **Older backdoor:** the same, and for much longer.
- **None of them on a router that has been restarted since 20 November:** only the state file
  and the older backdoor could still be there. A clean result says less than it seems to.

On a GL-AXT1800 the firewall rule did not appear in the listing on our own unit although the
handler had run, so on that model do not rely on the rule being absent.

## Check a device

Three ways: the community script, by hand, or GL.iNet's own checks. The first two follow the
table in [The signs, and what each one means](#the-signs-and-what-each-one-means). GL.iNet's
checks look for one sign only and are listed last.

### With the script

The most complete check is the community triage script by Admon. It looks for every sign in that
table that can be seen on the device itself, which is all of them except the cloud log entry. It
saves evidence before it changes anything, and is being updated as findings come in:

- Step-by-step guide: <https://gl-i.net/security/csa-2026-01/fix/>
- Script and documentation: <https://github.com/admonstrator/glinet-csa-2026-01>

Read a script before you run it as root. To keep it off the device's storage, pipe it over SSH from
a copy you have read, as that repository's README shows.

It also looks for things that are not in our table because we have not found them on a router:
the files of the "gl-helper" implant reported on KVMs, a replaced `netstat`, and an SSH key or
remote-terminal setting added by an attacker. Its `--fix` does not remove the older backdoor.

### By hand, over SSH on a router

One check per sign, in the order of the table. Run them before you restart the router. The first
command is ours and covers three signs at once; GL.iNet's own command for its indicator is
`ps | grep tmp`, listed under [GL.iNet's own checks](#glinets-own-checks).

| Sign | Command | A hit looks like |
|---|---|---|
| Remote shell, older backdoor processes, GL.iNet's indicator | `ps w \| grep -E 'crond -i\|mkfifo\|nc [0-9]\|sh -i\|monitord\|ujaild' \| grep -v grep` | `nc` with an address, `/bin/sh -i` or `mkfifo`: the remote shell. `monitord` or `ujaild`: the older backdoor. `crond -i /tmp/.log`: GL.iNet's indicator |
| Shell pipe | `ls -la /tmp/f /tmp/.log` | `/tmp/f` listed with a line that starts with `p` |
| Firewall rule | `iptables -t nat -S SDWAN_IP_MAPPING` and, on firmware that answers "use 'nft' tool", `nft list ruleset \| grep -i sdwan` | A rule with `127.0.0.1` on both sides |
| State file | `ls -la /etc/mp_ip_mapping_info` and `uci -q get mptun.global.enable` | The file exists, has size 0 and a date of 20 November 2026 or later (shown in the router's own time zone), and the second command prints `0` or nothing (AstroWarp is not in use) |
| Older backdoor, start-up script | `/rom/bin/busybox cmp /etc/init.d/urandom_seed /rom/etc/init.d/urandom_seed` | Any output. Nothing printed means the file is the firmware's own |
| Older backdoor, added file | `ls -l /bin/ulogd` | The file exists |
| Older backdoor, keep list | `/rom/bin/busybox cmp /lib/upgrade/keep.d/netifd /rom/lib/upgrade/keep.d/netifd` | Any output. No output does not clear the router: we found the backdoor without this change on some |
| Cloud log entry | Not on the router: export the device log from your GoodCloud account | See below |

Before you use `netstat` on a suspect router, look at it first: GL.iNet staff warn that it may
have been replaced on an infected device and that running the replacement starts the malware.
On a router it should be a link to `busybox`:

```
ls -l /bin/netstat
```

No hit only tells you nothing is running now and nothing of this kind has run since the last
boot; the state file and the older backdoor are the two signs that outlast a restart. It cannot
tell you a device was never compromised.

**The older backdoor** was first reported by several owners in
[this forum topic](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097),
on GL-AX1800, GL-X2000 and GL-MT3000 routers. Verified by us on 22 November:
we found it running on 49 routers we manage
  (GL-MT2500, GL-MT3000, GL-MT6000, GL-AX1800 and GL-AXT1800;
  firmware 4.7.0 to 4.11.0), with file dates from September 2025 to May 2026. An earlier
version of this page said we had not seen an affected device. GL.iNet's check does not find it:
the process it looks for was not running on any of the 49. The remedy is the reinstall in
[If you find something](#if-you-find-something).

**The cloud log entry** (Reported by one owner; we have not checked it). In their GoodCloud
account, the exported device log for a GL-AXT1800 on 4.8.3 that never used AstroWarp held three
command responses on 20 November, between 20:46 and 21:31 UTC, of the form
`{"id":1,"astrowarp":[],"code":0}`. Ordinary commands in that log carry a 32-character id and a
matching `publish` entry; these had the number `1` and no matching entry. It is the one place
that still shows the command after the router has been restarted or reinstalled. If you look,
export the log before you change anything on the account: the same owner lost it after
resetting the account password.

### GL.iNet's own checks

These are the checks in GL.iNet's
[security notice](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056)
as it stood on 23 November 2026. All four look for the same thing: the exact text
`crond -i /tmp/.log` in the details of a running process. A line that shows only the `grep`
command is not a match.

| Device | Where | Check |
|---|---|---|
| Router, web interface | Admin Panel: **System → Advanced Settings**, sign in to LuCI, then **Status → Processes** | Search the page (Ctrl+F) for `tmp/.log` |
| Router, SSH | SSH session | `ps \| grep tmp` |
| KVM, RMQ1 | KVM web interface: **Toolbox → Terminal → Access** | `ps -a \| grep tmp` |
| KVM, all other models | The same terminal | `ps -aux \| grep tmp` |

Run the KVM commands in the KVM's own terminal, not on the computer connected to it. If a KVM
is infected, the notice also says to check that computer: unfamiliar programs, browser
extensions or user accounts, unexpected start-up items or scheduled tasks, unusual settings
changes or network activity, and a full scan with up-to-date security software.

What we can say about these checks:

- **On routers, not known to us.** That process was not running on any router we checked,
  including every router where we found one of the other signs.
- **On KVMs, not known to us either.** We have not examined an infected KVM. It is reported to
  be the name the KVM installer gives its own process (findings K-9).
- A result without a match says nothing about the other signs in the table above. The notice
  itself now says its quick checks "may not detect every affected device".

For KVM firmware see [docs/kvm-firmware.md](docs/kvm-firmware.md).

## If you find something

**A compromised router is not the only thing that is compromised. Everything it held a key for is
too.** The attacker had a root shell, so every key, password and profile stored on the device
could be copied. Cleaning or reinstalling the router does not take those back. You have to remove
that access at the other end.

1. Save the output and note the time. In a business network, talk to whoever handles incidents or
   insurance for you before changing anything.
   - **Take the evidence archive while the device is still running, before any restart.** The
     triage script's `--archive` records what exists only in memory and is gone after a reboot:
     the process list, the details and the program file of each suspect process (even one
     whose file was deleted), open connections, the firewall rules in force and the system log.
     It does not copy all of `/tmp` or the memory of running programs. By default it writes
     the archive to `/tmp`, which is memory too, so copy it off the device before you restart,
     or stream it to your computer with `--archive --stdout`.
   - **If it is a KVM that was attached to a work computer, think carefully before you wipe it
     and install new firmware.** If someone used it to reach that computer and went on into
     your employer's systems, the compromised KVM may be the only evidence you have that it was
     not you personally. Save the evidence archive first (the triage script's `--archive`), keep
     a copy off the device, and consider setting the unit aside untouched.
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
7. **Reinstall the firmware with "Keep Settings" switched off, from an image you downloaded
   yourself** (see [Firmware downloads](#firmware-downloads)), then set the device up again from
   known-good information and the new keys.
   - **Do not upgrade a suspect router with settings kept.** The firmware's own keep list carries
     `/etc/rc.local`, the root crontab, everything under `/etc/config`, `/etc/openvpn` and
     `/etc/udhcpc.user.d` into the new installation, and the router runs every script in that
     last directory on each DHCP event (read in the GL-AXT1800 4.6.11 and GL-MT3600BE 4.9.0
     images). Forum users report a backdoor that survived upgrades with settings kept. We have
     since found that backdoor on routers we manage, with its own line added to the keep list
     (*corrected 22 November: this page said we had not seen such a device*). We also
     tested it: on a GL-MT3000, start-up entries placed in kept settings survived an upgrade to
     the fixed firmware and ran on it (see [Fixed firmware](#fixed-firmware)).
   - **Do it in one step, not two.** A reinstall with settings off replaces the firmware image
     and the writable layer at the same moment. Any sequence that renews them one after the
     other (a factory reset and then an upgrade with settings kept, or the other way round)
     leaves one of the two as it was while the other is renewed, so whatever is in the old half
     gets a first boot in which it can write into the new half. We have not seen a changed
     firmware image on a router. That is not much comfort: our checks find what we already know
     to look for, and someone careful would not have left that.
   - **A factory reset alone is not a recovery.** Use it only as a stop-gap when you cannot
     reinstall yet. It erases the writable layer, where everything we and the forum reports have
     found lives, but leaves the installed firmware image as it is. On a
     GL-AXT1800 (4.8.4) the flash partition that holds that image is writable from a root shell
     and the tools a firmware update uses are on the router, so an attacker with root was not
     prevented from changing the image (read from the device; we did not attempt a write, and we
     know of no report that it was done). A reinstall writes the image again and, with settings
     off, starts with an empty writable layer (read in the upgrade scripts of the GL-MT3600BE
     4.9.0 image; other models not checked, and on a model with two firmware slots the other
     slot is not rewritten).
   - **What a reinstall does not replace.** It is the most complete step an owner has; it is
     not a guarantee. On a GL-MT3000 (4.11.1) the upgrade rewrites only the firmware image and
     the writable layer. The boot loader and the partition that holds the device's own data
     (serial number, hardware address, DDNS id, country code) are left as they were, by a reset
     and by a reinstall alike (read in that firmware's upgrade scripts and partition table; we
     have not compared them before and after an upgrade).
   - **The boot loader.** We found no step in a reset or a reinstall that rewrites it (read in
     the GL-AXT1800 and GL-MT3600BE firmware). On the GL-AXT1800 that had the remote shell
     (firmware 4.8.3) the kernel marks the boot loader partition writable and let us open it
     for writing; we wrote nothing. We compared that router's boot loader with the binaries
     GL.iNet publishes for the model in its
     [uboot-ipq60xx](https://github.com/gl-inet/uboot-ipq60xx) repository: it is byte for byte
     the one published on 1 December 2021. That is one router; we know of no report of a
     changed boot loader. *Corrected 22 November: this page said the kernel marked the boot
     loader not writable on both routers we read. That was true of one of them.*
   - **KVMs.** The same applies. An upgrade with "Save current configuration" ticked carried a
     boot script and an added SSH key into 1.10.3 on our test RM1. Untick it. By our reading of
     the 1.10.2 upgrade code nothing is then copied across; we have not run that case. See
     [docs/kvm-firmware.md](docs/kvm-firmware.md).
8. Check the computers behind the device. For a KVM, check the computer it was attached to.

## Fixed firmware

GL.iNet's listing holds stable firmware dated 22 and 23 November 2026 for eighteen router
models: GL-MG1300, GL-MT3000 and GL-MT6000 (4.11.1), GL-E5800 (4.10.3), GL-BE3600 and GL-BE9300
(4.10.2), GL-BE14000 (4.9.3), GL-BE6500, GL-MT3600BE and GL-MT5000 (4.9.1), GL-BE10000 (4.8.7),
GL-AX1800, GL-AXT1800, GL-SFT1200, GL-X3000 and GL-XE3000 (4.8.4), GL-MT2500 and GL-X2000
(4.7.14); and for all seven KVM models (1.10.3, or 1.8.7 for the RMQ1). That is the list as our
mirror held it at 01:18 UTC on 23 November.

All of these builds are on our firmware mirror, <https://gl-fw.remotetohome.io/>, next to the
builds they replace. Each file's checksum is verified against the one GL.iNet publishes. Use it
to get a fixed build, or to compare a fixed build with the one before, as we did.

What we have read ourselves is the GL-MT3000 build, compared with the one before it:

- **The fix is in the handler we identified.** The cloud client's AstroWarp module is the file
  that changed in substance. For the command the attack used, `virtual_ip_info`, the handler
  now checks its two address fields as IPv4 addresses and its third field as a hardware address
  before it builds any command, and returns without acting when the check fails or the checker
  is missing. At least two other commands got the same treatment. GL.iNet has not said in words
  that this was the entry point; its fix says so. We have not sent the attack message to a
  fixed router to watch it being refused.
- **The firmware cleans up only part of what we have found.** A new script runs once at the
  first start after the update. It restores `/etc/init.d/urandom_seed` from the firmware's own
  copy, which is the start-up file the older backdoor changes. It does not remove that
  backdoor's added files or its keep-list line. It removes the entries of the KVM-style implant
  only if one particular folder exists. We have not tested what still runs afterwards.
- **That script is the whole clean-up, and it is the same in every build we could open.** On
  23 November we unpacked the fixed build of seventeen of the eighteen models (not the
  GL-E5800, whose file format we could not open). Each carries that one script, byte for byte
  the same, and no other file in any of them mentions the names of the older backdoor's files
  or of its servers. Nothing in the firmware looks for `/bin/ulogd`, for added SSH keys, or
  for anything else in the settings an upgrade keeps.
- **What an upgrade keeps has not been narrowed.** Read in the GL-MT3000 4.11.1 image, the
  keep list still carries all of `/etc/config`, the cron tables, `/etc/rc.local`, the SSH
  server's authorised keys, the account and password files and the scripts in
  `/etc/udhcpc.user.d`. A root-level intruder could have written to any of those.
- **So "removes the malware, keep your settings" holds only for the known start-up routes.
  We tested it.** On 23 November we put harmless stand-ins for each known way of starting at
  boot on a test GL-MT3000 (files of our own that only write a log line when they run),
  confirmed that every one ran after a restart on 4.11.0, then upgraded to 4.11.1 with settings
  kept:

  | Planted before the upgrade | After the upgrade | Ran on 4.11.1 |
  |---|---|---|
  | The changed start-up file of the older backdoor | Put back to the firmware's own | No |
  | `/bin/ulogd`, with the backdoor's own line in the upgrade keep list | Still there. The keep-list line is what carries it: a file put in `/bin` without that line is dropped by any upgrade | No |
  | The KVM-style implant's folder in `/etc/config`, its `rc.local` line and its three cron lines | Removed | No |
  | An added SSH key, and an added account | Still there | (these do not run) |
  | A different line in `rc.local` | Still there | Yes |
  | A different cron line | Still there | Yes |
  | A script in `/etc/udhcpc.user.d` | Still there | Yes |

  The clean-up does what its script says: the start-up routes it names are removed before they
  run. Everything it does not name is carried over with the settings, and what can run does
  run on the fixed firmware. An intruder with root access was not limited to the routes that
  have been found so far. One router, one model, upgraded with the router's command-line tool;
  the stand-ins copy the file names and start-up routes, not the real programs.
- **One weakness is not addressed in that build.** It concerns the cloud client and is separate
  from the handler. The component involved is byte for byte the same as before. We reported
  it to GL.iNet on 22 November 2026 and will not describe it here until it is fixed.
- **The VPN server settings were changed on most routers with the older backdoor, and an
  upgrade keeps them.** On 27 of the 30 such routers with a dated install,
  `/etc/config/wireguard_server` was changed 9 to 12 seconds after the backdoor's files were
  written. We had saved only the time of the change, so we do not know what was changed. That
  file is in `/etc/config`, which an upgrade with settings kept carries over whole, and the
  clean-up does not look at it. A clean-up that removed every file of the backdoor would still
  leave it as the intruder left it.
- **An update does not take back what was read.** A router with the remote shell or the older
  backdoor has had everything on it readable by someone else: its SSH keys, the Wi-Fi and admin
  passwords, VPN keys and profiles, its Tailscale and ZeroTier identities, DDNS and cloud
  credentials. Keeping settings keeps exactly those. They have to be replaced whatever the
  firmware does.
- **So once any of [the signs](#the-signs-and-what-each-one-means) is found, do not keep
  settings.** What was read has to
  be replaced, what was changed cannot be told apart from your own settings, and where only the
  attacker's command ran we cannot show that nothing more was sent. We know of no case in which
  an upgrade with settings kept is the right way to recover such a router. Reinstall with
  "Keep Settings" switched off and set it up again, as in
  [If you find something](#if-you-find-something).

We compared the two GL-MT3000 builds file by file, and read the changed handler and the new
checker instruction by instruction, for that one model only. In the other sixteen builds we
read the clean-up script and searched the files; we have not read their handler.

**KVMs.** The same holds for the KVM firmware. On a test RM1, a boot script and an added SSH
key that we placed before the upgrade were both still there on 1.10.3 after an upgrade with
"Save current configuration" ticked, and the script ran at the first boot. Details and what to
do are in [docs/kvm-firmware.md](docs/kvm-firmware.md).

Because of the unaddressed weakness we are leaving GoodCloud switched off on the routers we
look after, also after updating. With GoodCloud off on the router, the cloud client does not run.

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

## Recovery tools

Two RemoteToHome projects for the cases GL.iNet's "factory reset and set up again" advice does
not cover, mainly devices that are far away:

- **[gl-portable-backup](https://github.com/RemoteToHome-io/gl-portable-backup)**, a backup and
  restore plugin. [Version 1.1.1](https://github.com/RemoteToHome-io/gl-portable-backup/releases/tag/v1.1.1)
  (21 November) adds a read-only `gl-portable-backup check` for the indicators on this page, and
  every backup runs it. Its result is `indicators`, `inconclusive` or `none`. A backup taken from
  a router with indicators is kept as a record only: its file name carries `-COMPROMISED-` and
  it cannot be restored. A result of `none` does not show that the router was never compromised.
  Its README says which modes and firmware versions have been tested; read that before relying
  on it.
- **gl-remote-rebuild** (not yet released, in design): wipe and reinstall a remote router and
  bring remote access back on first boot, carrying across only a short, inspected list of
  settings.

## More detail

- [docs/technical-breakdown.md](docs/technical-breakdown.md): the long version: the flaw line by
  line, how it was read, its history back to December 2024, what was sent through it, the older
  backdoor in detail, and the fix
- [docs/findings.md](docs/findings.md): every finding, its source, and how it was checked
- [docs/field-survey.md](docs/field-survey.md): devices checked so far, by model and firmware
- [docs/router-reverse-shell.md](docs/router-reverse-shell.md): the remote shell, the cloud command behind it and which routers have that code
- [docs/attacker-infrastructure.md](docs/attacker-infrastructure.md): what is known about the address the shells
  connected to, and the abuse report
- [docs/gl-statements.md](docs/gl-statements.md): what GL.iNet has said in public, version by
  version, with what was added and removed
- [docs/kvm-firmware.md](docs/kvm-firmware.md): what the KVM 1.10.2 and 1.10.3 firmware does and
  does not do
- [docs/monitoring.md](docs/monitoring.md): how to record what the cloud sends a device
- [tools/cloud-watch](tools/cloud-watch): a small watcher for a test device

## What is deliberately not published here

Until 22 November we did not name the cloud command or describe the handler. GL.iNet has now
released fixed firmware, and anyone can compare it with the build before, so those are described
on this page and in [docs/router-reverse-shell.md](docs/router-reverse-shell.md).

Still not published: the message itself as sent, and one further weakness in the cloud client
that the fixed firmware we read does not address. That one is with GL.iNet's security team
(security@gl-inet.com) and stays out of this repository until it is fixed. Reports that include
either will be edited before they are merged.

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
