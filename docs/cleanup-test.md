# What survives each clean-up: the test, marker by marker

*Added 27 November 2026.* This page shows the test behind one sentence on the front page: that
installing the firmware again with "Keep Settings" switched off is the only clean-up that starts
clean. It lists what we planted, where, and what was still there after each method.

## In one table

| Clean-up method | Markers at the names GL.iNet's clean-up lists | Other start-up hooks, keys, accounts, settings | Hidden folders |
|---|---|---|---|
| **Upgrade to the fixed firmware (4.11.2), settings kept** | Removed | **Survived. The hooks ran on the new firmware** | **Survived** if the clean-up does not name them |
| **Factory reset** on fixed firmware (4.11.2) | Removed | Removed | **Survived** if the clean-up does not name them |
| **Factory reset** on firmware without the clean-up (4.11.0) | Visible ones removed | Removed | **All survived, including folders at the implant's own paths** |
| **Install the firmware again, "Keep Settings" off** | Removed | Removed | Removed |

## How the test was done

- **The router:** a GL-MT3000 of our own, with GoodCloud switched off for the whole test.
- **The markers:** harmless files and lines that we wrote ourselves. Each one that can run does
  one thing: it appends a line with its name and the time to a log file. None is malware, and no
  sample from the incident was used. We call them markers below.
- **Where they went:** at the file names and start routes seen in this incident and in the older
  backdoor, at near misses of those, and at other places a router starts things from or keeps
  access in.
- **Each run:** read the router's state, place the markers, restart once to see them work, run
  one clean-up method, read the state again. The reads compare every marker by name, and the
  firmware's files and the boot partitions by checksum.
- **The runs,** all on 26 November 2026: an upgrade from 4.11.0 to 4.11.2 with settings kept; a
  factory reset on 4.11.2; a factory reset on 4.11.0; an upgrade from 4.11.0 to 4.11.2 without
  settings. 4.11.0 is the last firmware before the fix and has no clean-up script; 4.11.2 is
  the second fixed build.

In the tables, **kept** means the marker was still there after the method, **ran** means its log
line appeared afterwards, and **gone** means it was removed.

## 1. Markers at the names the incident used

GL.iNet's clean-up script, which runs once on the first start after a firmware install, lists
these names. They are the ones it is written to remove.

| Marker | Upgrade, settings kept | Factory reset, 4.11.2 | Factory reset, 4.11.0 | Reinstall, no settings |
|---|---|---|---|---|
| Files named like the older backdoor's: `/bin/ulogd`, `/usr/bin/monitord`, `/usr/sbin/ujaild` | gone | gone | gone | gone |
| Lines added to the start-up script `/etc/init.d/urandom_seed` | gone | gone | gone | gone |
| The older backdoor's two lines in the upgrade keep list | gone | gone | gone | gone |
| Hidden folder `/etc/config/.gl` with `boot.sh` and `gl-helper` | gone | gone | **kept, with both files** | gone |
| Hidden folder `/etc/glinet/.cache` with four files | gone | gone | **kept, with all four** | gone |
| Hidden folder `/etc/gl_nas/.cache` with one file | gone | gone | **kept** | gone |
| Scheduled lines and the start-up line that would run those folders' scripts | gone (one schedule file was left in place, emptied) | gone | gone | gone |
| Three near misses: the same lines, written so the clean-up's patterns do not match | **kept**; they ran nothing, because the folders they point at were removed | gone | gone | gone |

Read the 4.11.2 and 4.11.0 reset columns together. The reset is the same in both. The only
difference is the clean-up script on the next start. So the factory reset itself does not remove
these hidden folders; on fixed firmware the clean-up does, afterwards.

## 2. Start-up hooks the clean-up does not list

Every one of these is a place a router runs things from. None is in the clean-up's list.

| Marker | Upgrade, settings kept | Factory reset (both) | Reinstall, no settings |
|---|---|---|---|
| A line in `/etc/rc.local` (runs at every start) | **kept, ran** | gone | gone |
| A line in root's schedule (`/etc/crontabs/root`) | **kept, ran** | gone | gone |
| A file in GL.iNet's own schedule folder (`/etc/gl_crontabs/crontabs.d`) | **kept, ran** | gone | gone |
| A script in `/etc/udhcpc.user.d` (runs when the WAN gets an address) | **kept, ran** | gone | gone |
| A line in `/etc/udhcpc.user` | **kept, ran** | gone | gone |
| A script in `/etc/profile.d`, and lines in `/etc/profile` and `/etc/shinit` (run at a login) | **kept, ran** | gone | gone |
| A line in `/etc/firewall.user` (runs when the firewall loads) | **kept, ran** | gone | gone |
| A firewall "include" setting pointing at a script in a hidden folder | **kept, ran** | setting gone; **the script file was kept** | gone |
| A dnsmasq script setting pointing at a script in a hidden folder | **kept, ran**, with root's rights | setting gone; **the script file was kept** | gone |
| A new service: a file in `/etc/init.d` with its start link | **kept, ran** | gone | gone |
| A line in the OpenVPN hook file `openvpn.user` | **kept**; nothing happened during the test that would run it | gone | gone |
| A program in `/usr/bin`, carried by an added keep-list line | **kept** | gone | gone |
| A first-boot script in `/etc/uci-defaults` with a name that sorts before the clean-up's | **ran once, 16 seconds after the start, before the clean-up had finished**; it then deletes itself, as such scripts do | gone | gone |
| A line added to the firmware's own OpenVPN start script | gone: the firmware copies its own scripts back over that folder on the first start | gone | gone |

## 3. Access and settings

| Marker | Upgrade, settings kept | Factory reset (both) | Reinstall, no settings |
|---|---|---|---|
| An extra SSH key in `authorized_keys` | **kept** | gone | gone |
| An extra account (lines in `passwd`, `shadow`, `group`) and a `sudoers` file | **kept** | gone | gone |
| An extra peer in the WireGuard server's settings | **kept, and the server loaded it** | gone | gone |
| A switched-off port forward | **kept** | gone | gone |
| Marker lines in `hosts`, `dnsmasq.conf`, `sysctl.conf`, the package feed list, and a file in `/etc/dnsmasq.d` | **kept** | gone | gone |
| Marker sections in nine settings files (`wireguard`, `rtty`, `zerotier`, `tailscale`, `gl-cloud`, `openvpn`, `ovpnclient`, `ovpnserver`, `upnpd`) | **kept** | gone | gone |
| Marker sections in six more (`network`, `dropbear`, `uhttpd`, `oui-httpd`, `system`, `glconfig`) | not placed in that run | gone | gone |

## 4. Hidden files and folders of our own

These are not names from the incident. They are there to tell "the method skips hidden folders"
apart from "the clean-up happens to list this one".

| Marker | Upgrade, settings kept | Factory reset, 4.11.2 | Factory reset, 4.11.0 | Reinstall, no settings |
|---|---|---|---|---|
| Hidden folder `/etc/config/.rth-standin` with eight files | **kept** | **kept, with all eight** | **kept, with all eight** | gone |
| Hidden folder `/etc/.rth-standin-hidden-dir` with one file | not placed | not placed | **kept** | gone |
| Hidden file `/etc/.rth-standin-hidden-file`, directly in `/etc` | not placed | not placed | gone | not placed |

So the reset removes a hidden file that sits directly in a normal folder, and leaves a hidden
folder and everything inside it. The reset tool's upstream source explains it: it deletes the
files of each folder it visits and never goes into a folder whose name starts with a dot
(openwrt/fstools, `libfstools/overlay.c`, the functions `foreachdir` and `handle_rmdir`). An
upgrade without settings does not walk the files at all: it removes the whole settings volume
and makes a new one (`lib/upgrade/nand.sh` in the 4.11.2 image).

## 5. Outside the settings area

Read before and after every run, by checksum:

| Part | Result in every run |
|---|---|
| Boot loader (the `BL2` and `FIP` partitions) | unchanged |
| Boot loader's settings partition | unchanged |
| `Factory` partition (the device's own data) | unchanged |
| The firmware's files and the kernel | equal to GL.iNet's official image for that version |

No method changed these. We planted nothing there and did not try to.

## What the router printed

The state reads are plain text. These are lines that were still marked present, copied
from the read taken after each run, with the spacing tidied.

After the upgrade with settings kept (4.11.2, 343 seconds after the start), a selection:

```
B1   1        rc.local line
B2   1        cron line
B3   PRESENT  /etc/udhcpc.user.d/rth-standin
B4   PRESENT  /etc/profile.d/rth-standin.sh
B7   1        firewall.user line
B8   PRESENT  firewall include section (/etc/config/.rth-standin/fw-include.sh)
B10  PRESENT  dnsmasq dhcpscript option (ours)
B11  PRESENT  /etc/init.d/rthstandin
B11  PRESENT  /etc/rc.d/S99rthstandin
B14  PRESENT  /etc/gl_crontabs/crontabs.d/rth-standin-b14
C1   1        stand-in key in authorized_keys
C2   1        account line in passwd
C7   PRESENT  extra peers section in the WireGuard server settings (peers)
     (C7 key loaded in the running WireGuard server: yes; peers sections in the settings: 4; peers in the running server: 4)
```

and from the markers' own log on the new firmware:

```
B1-rc.local: 1 runs
B2-cron: 2 runs
B3-udhcpc.user.d (arg=bound): 1 runs
B7-firewall.user: 1 runs
B8-fw-include: 13 runs
B10-dnsmasq-dhcpscript (arg=arp-add): 16 runs
B11-init.d: 1 runs
B14-gl_crontabs: 2 runs
B15-uci-defaults ran 2026-11-26T04:49:59Z up=16.31 cleanup-still-waiting=yes
```

After the factory reset on 4.11.0, every line still marked present:

```
A2a  PRESENT  /etc/glinet/.cache/watch.sh
A2a  PRESENT  /etc/glinet/.cache
A2b  PRESENT  /etc/gl_nas/.cache
A2f  PRESENT  /etc/config/.gl
B8   PRESENT  /etc/config/.rth-standin/fw-include.sh
B10  PRESENT  /etc/config/.rth-standin/dhcp-script.sh
C9   PRESENT  /etc/.rth-standin-hidden-dir/marker
C8   absent   /etc/.rth-standin-hidden-file
```

After the upgrade without settings: no line marked present, and the only hidden entry left in
the settings area was a placeholder file of the firmware's own.

## What this does and does not show

- **It shows** that on this router an upgrade to the fixed firmware with settings kept leaves
  working start-up hooks, keys and accounts in place; that a factory reset leaves hidden folders;
  and that a reinstall without settings left none of our markers.
- **Nothing left by a factory reset ran.** The reset removed every setting and line that would
  start the files in the kept folders. Whether something else on a router could start them was
  not tested.
- **The clean-up runs once.** Markers placed at its own listed names after the upgrade ran at the
  next restart. It removes what is there on the first start; it does not guard those places
  afterwards.
- **Limits.** One router of one model. Each method was run once, the factory reset twice.
  Upgrades were run with the firmware's command-line tool; the web interface's "Keep Settings"
  switch ends in the same command by our reading of the image, but we did not click it. The
  factory resets were done through the web interface; the reset button was not tested. Markers,
  not real samples. Installing from the boot loader's own page has not been tested yet.

The findings table has these as R-43, R-45 and R-46 ([findings](findings.md)); the advice that
follows from them is in the README under
[If you find something](../README.md#if-you-find-something).
