# What the KVM 1.10.2 and 1.10.3 firmware does and does not do

**Update, 22 November 2026: firmware 1.10.3.** GL.iNet has released stable 1.10.3 for the RM1,
RM1V2, RM1PE, RM4PE, RM10 and RM10RC, and 1.8.7 for the RMQ1; all are on our
[firmware mirror](https://gl-fw.remotetohome.io/). We read the six 1.10.3 images, each matching
its published checksum (findings K-10 and K-11). We have not read the RMQ1 build, which ships in
a different format. On 23 November we upgraded a test RM1 from 1.10.2 to 1.10.3 through its web
interface with "Save current configuration" ticked (finding K-12).

- **An upgrade that keeps the configuration also keeps a boot script and an SSH key.** Before
  the upgrade we placed two harmless stand-ins on the RM1: a script in
  `/etc/kvmd/user/scripts` that only writes a log line, and an extra public key in
  `/root/.ssh/authorized_keys`. After the upgrade both were still there, and the script had run
  ten seconds into the first boot on 1.10.3. The clean-up routine below names neither place.
  So on a KVM that may have been hit, do not rely on the upgrade: untick "Save current
  configuration" when you upgrade, or look in both places afterwards. By our reading of the
  1.10.2 upgrade code, nothing is copied across when the box is unticked; we have not run that
  case, and we have not read that code in 1.10.3.

- **The cleanup is now in all six.** The routine described below, which in 1.10.2 was in the
  RM1PE image and not in the RM1 image, is in the 1.10.3 image of every one of the six models. It
  is the same routine: the same four trigger files and the same five removals. The RM1PE's is
  unchanged from 1.10.2.
- **It still keeps no copy.** Upgrading an infected unit to 1.10.3 removes the evidence that it
  was infected, on every model now. Check, and save what you find, before you upgrade.
- **It still does not remove everything.** It does not touch `/root/.ssh` or
  `/etc/kvmd/user`. The installer is reported to add an SSH key (finding K-9), so look for keys
  you did not add after upgrading.
- **SSH starts at boot again.** In the RM1's 1.10.2 the SSH server only started when a settings
  file said so (see below). In 1.10.3 the SSH start script of all six models is the ordinary one
  and starts the server at every boot. Read in the images, and confirmed on our RM1: after the
  upgrade to 1.10.3 it answered on SSH fifteen seconds after boot with nothing switched on by
  hand. With a kept SSH key, that key works again straight after the upgrade.
- **The cloud remote terminal's start script is unchanged** from 1.10.2 on the RM1, and is the
  same file in all six models.

**What GL.iNet itself had written up before the attack.** GL.iNet's public vulnerability
repository holds three reports on the GL-RM1's 1.10.1 firmware, added on 16 October 2026: the
cloud agent did not check the name on the cloud's certificate; the certificate authorities for
the message broker and the remote terminal were downloaded at run time and trusted without any
check; and the remote-terminal start-up script built its command from cloud-delivered
configuration without quoting, so a crafted entry could open a root terminal with no login. A
fourth, of 15 October, describes cross-tenant device control in the KVM cloud service. Our test
RM1 was still on 1.10.1 on 21 November. What we read in 1.10.2 (the remote terminal always using
TLS with a fixed authority, finding K-4) fits a fix for these. See
[GL.iNet's published vulnerability reports](gl-statements.md#glinets-published-vulnerability-reports)
(finding G-17).

The rest of this page describes 1.10.2, which is what we tested on a device.

Findings K-1 to K-7 in [findings.md](findings.md). Read from GL.iNet's official images for RM1PE
(1.10.1 and 1.10.2) and RM1 (1.10.2), and tested on an RM1 upgraded from 1.10.1 to 1.10.2 with
settings kept. Other models have not been read by us.

## The cleanup is not in every model's 1.10.2

RM1PE 1.10.2 adds a routine to `/etc/init.d/S08overlayfs`. At boot it looks in the writable layer
(`/userdata/overlay/upper`) for any of:

- `etc/glinet/.cache/gl-helper`
- `etc/glinet/.cache/gb`
- `etc/config/.gl/gl-helper`
- `etc/config/.gl/gb`

If one exists it deletes `etc/glinet/.cache`, `etc/config/.gl`, `etc/rc.local`,
`etc/crontabs/root` and `usr/bin/netstat` from that layer. It keeps no copy, so **upgrading an
infected unit removes the evidence that it was infected**. Check before you upgrade.

RM1 1.10.2 contains no such routine. Admon found the same for RM1V2.

## What an RM1 upgrade keeps

With "keep settings", the RM1 upgrade rebuilds the writable layer from a fixed list and drops
everything else. In our test that removed planted copies of all the files above, although this
firmware has no cleanup routine. It kept:

- the password file (`/etc/shadow`)
- `/root/.ssh` and the SSH host keys
- everything under `/etc/kvmd/user`: the web password file, two-factor secret, TLS key, VPN
  identities
- the cloud settings in `/etc/glinet` (but not hidden entries such as `.cache`)

So after an upgrade on a unit that may have been hit: change the device and web passwords, look in
`/root/.ssh` for keys you did not add, and look in `/etc/kvmd/user/scripts`. The firmware runs any
script there named `S??*` at every boot, and that directory is inside the kept list. A script
placed there survives an upgrade that keeps the configuration and runs afterwards: tested on
23 November on the upgrade to 1.10.3 (see the top of this page).

A factory reset wipes the whole writable partition on these models (read from the firmware's reset
script; not run by us).

## Two things that change after upgrading an RM1

- **SSH is switched off.** 1.10.2 only starts the SSH server when
  `/etc/kvmd/user/ssh.conf` says `enabled=1`. We found no setting for it in the web interface. From
  the web terminal, `/etc/init.d/S50dropbear enable` turns it on and keeps it on.
- **The cloud remote terminal always uses TLS.** In 1.10.1, TLS was added only if a setting that
  arrives from the cloud did not say otherwise. In 1.10.2 the program enforces it with a fixed
  certificate authority.

## The connected computer

A KVM has keyboard, video and mouse on the computer it is attached to. If a KVM was infected,
check that computer as GL.iNet's notice describes, and assume anything typed or shown through the
KVM in that period could have been seen.
