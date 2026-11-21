# What the KVM 1.10.2 firmware does and does not do

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
script there named `S??*` at every boot, and that directory is inside the kept list. Whether a
script placed there survives an upgrade has not been tested yet.

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
