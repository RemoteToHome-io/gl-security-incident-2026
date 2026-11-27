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

## Exactly what we placed

Everything below was written by one script on the test router. Nothing here is from the
incident's own files: where a name matches the incident's, only the name is copied.

### The marker script

Every `.sh` file in the lists below is this same five-line script, with its own label in place
of `LABEL`. All it does is write one line to a log file and one to the system log:

```
#!/bin/sh
# rth-standin (harmless)
echo "LABEL ran $(date -u +%FT%TZ) up=$(cut -d" " -f1 /proc/uptime) arg=$1" >> /etc/rth-test-ran.log 2>/dev/null
logger -t rth-standin "LABEL ran arg=$1" 2>/dev/null
true
```

So "ran" in the tables means: a line with that marker's label appeared in
`/etc/rth-test-ran.log` after the clean-up.

### Hidden folders at the incident's own paths

| Folder | Files placed in it | What each file is |
|---|---|---|
| `/etc/config/.gl` | `boot.sh`, `gl-helper` | `boot.sh` is the marker script; `gl-helper` is a text file holding the word `rth-standin` |
| `/etc/glinet/.cache` | `gl-helper`, `watch.sh`, `wake.sh`, `rtty_keep.sh` | three marker scripts and the same text file |
| `/etc/gl_nas/.cache` | `watch.sh` | the marker script |

And lines that would start them, written in the form GL.iNet's clean-up looks for:

```
# appended to /etc/crontabs/root
*/3 * * * * /bin/sh /etc/glinet/.cache/watch.sh
*/3 * * * * /bin/sh /etc/glinet/.cache/wake.sh
*/3 * * * * /bin/sh /etc/glinet/.cache/rtty_keep.sh

# written to /etc/gl_crontabs/crontabs.d/rth-standin-a2
*/3 * * * * /bin/sh /etc/glinet/.cache/watch.sh

# inserted in /etc/rc.local before its "exit 0"
[ -f /etc/config/.gl/boot.sh ] && /bin/sh /etc/config/.gl/boot.sh >/dev/null 2>&1 &
```

Three near misses, the same idea spelled so that the clean-up's patterns do not match:

```
# appended to /etc/crontabs/root
*/3 * * * * sh /etc/glinet/.cache/watch.sh A3a # rth-standin A3a no /bin/ prefix
*/3 * * * * /bin/sh /etc/gl_nas/.cache/watch.sh A3b # rth-standin A3b second folder

# inserted in /etc/rc.local
[ -f /etc/glinet/.cache/watch.sh ] && sh /etc/glinet/.cache/watch.sh A3c # rth-standin A3c
```

### Files and lines at the older backdoor's names

| Path | What was placed |
|---|---|
| `/bin/ulogd` | the marker script |
| `/usr/bin/monitord` | a copy of the router's own Lua interpreter, as the real backdoor makes |
| `/usr/sbin/ujaild` | the marker script; nothing starts it |
| `/etc/init.d/urandom_seed` | five lines inserted after its first line (below) |
| `/lib/upgrade/keep.d/netifd` | two lines added: `/bin/ulogd` and `/etc/init.d/urandom_seed` |

```
# inserted in /etc/init.d/urandom_seed
cp /usr/bin/lua /usr/bin/monitord 2>/dev/null
cp /bin/ulogd /var/run/monitord.pid 2>/dev/null
sh /var/run/monitord.pid from-urandom_seed >/dev/null 2>&1
sleep 1
rm -f /var/run/monitord.pid
```

Three more lines of our own went into that keep list (`/usr/sbin/ujaild`, `/etc/glinet/.cache/`,
`/etc/gl_nas/.cache/`), so that an upgrade would carry those paths and the clean-up's lines for
them would be put to the test. We do not know that any real implant wrote those three.

### Hidden folders and a hidden file of our own

| Path | Files placed in it | What each file is |
|---|---|---|
| `/etc/config/.rth-standin` | `fw-include.sh`, `dhcp-script.sh`, and six record files (`pre.sha256`, `pre.uci`, `pre.absent-dirs`, `d-configs`, `with-gl-dir`, `c7-pubkey`) | two marker scripts, started by the firewall and dnsmasq settings below; the record files are the test's own notes of the state before |
| `/etc/.rth-standin-hidden-dir` | `marker` | a text file holding the word `rth-standin` |
| `/etc/.rth-standin-hidden-file` | (a file, not a folder) | a text file holding the word `rth-standin` |

### Start-up hooks the clean-up does not list

Lines added to files that already exist on the router. Each writes its label to the log:

```
# inserted in /etc/rc.local before its "exit 0"
echo "B1-rc.local ran $(date -u +%FT%TZ)" >> /etc/rth-test-ran.log 2>/dev/null; logger -t rth-standin "B1-rc.local ran" 2>/dev/null; true # rth-standin

# appended to /etc/crontabs/root
*/3 * * * * echo "B2-cron ran $(date -u +\%FT\%TZ)" >> /etc/rth-test-ran.log; logger -t rth-standin "B2-cron ran"

# written to /etc/gl_crontabs/crontabs.d/rth-standin-b14
*/3 * * * * echo "B14-gl_crontabs ran $(date -u +\%FT\%TZ)" >> /etc/rth-test-ran.log; logger -t rth-standin "B14-gl_crontabs ran"
```

The same one-line form, with its own label, was appended to `/etc/shinit`, `/etc/profile`,
`/etc/firewall.user`, `/etc/udhcpc.user` and `/etc/openvpn.user`, and inserted before the final
`exit 0` of the firmware's OpenVPN start script `/etc/openvpn/scripts/ovpnserver-up`.

New files:

| Path | What was placed |
|---|---|
| `/etc/udhcpc.user.d/rth-standin` | the marker script |
| `/etc/profile.d/rth-standin.sh` | a comment and the one-line form |
| `/etc/init.d/rthstandin` | a service whose start step writes its label to the log (below) |
| `/etc/rc.d/S99rthstandin` | the link that starts that service at boot |
| `/usr/bin/rth-standin-tool`, `/usr/bin/rth-standin-keepd` | the marker script; nothing starts them |
| `/etc/uci-defaults/00-rth-standin` | a first-boot script: it writes its label, the uptime, and whether GL.iNet's clean-up script was still waiting to run |

```
# /etc/init.d/rthstandin
#!/bin/sh /etc/rc.common
# rth-standin (harmless)
START=99
boot() { start; }
start() {
	echo "B11-init.d ran $(date -u +%FT%TZ)" >> /etc/rth-test-ran.log 2>/dev/null
	logger -t rth-standin "B11-init.d ran" 2>/dev/null
	return 0
}
```

Settings that point at the two scripts in our hidden folder:

```
firewall.rthstandin_inc=include
firewall.rthstandin_inc.path='/etc/config/.rth-standin/fw-include.sh'
firewall.rthstandin_inc.reload='1'

dhcp.@dnsmasq[0].dhcpscript='/etc/config/.rth-standin/dhcp-script.sh'
```

Lines added to the upgrade's keep lists, so that the new files above are carried:

```
# appended to /etc/sysupgrade.conf
/etc/init.d/rthstandin
/etc/rc.d/S99rthstandin
/usr/bin/rth-standin-tool
/etc/uci-defaults/00-rth-standin

# appended to /lib/upgrade/keep.d/dropbear
/usr/bin/rth-standin-keepd
```

### Access and settings

```
# appended to /etc/dropbear/authorized_keys: one public key whose private half was deleted when it was made

# appended to /etc/passwd, /etc/shadow, /etc/group: an account that cannot log in
rthstandin:x:65000:65000:rth-standin:/nonexistent:/bin/false
rthstandin:*:0:0:99999:7:::
rthstandin:x:65000:

# /etc/sudoers.d/rthstandin
# rth-standin (comment only, no rule)

# appended to /etc/hosts
192.0.2.1 rth-standin.invalid

# appended to /etc/dnsmasq.conf, /etc/sysctl.conf, /etc/opkg/customfeeds.conf; and the whole of /etc/dnsmasq.d/rth-standin.conf
# rth-standin

# a switched-off port forward in the firewall settings
firewall.rthstandin_dnat=redirect
firewall.rthstandin_dnat.name='rth-standin-disabled'
firewall.rthstandin_dnat.enabled='0'
firewall.rthstandin_dnat.src='wan'
firewall.rthstandin_dnat.src_dport='65022'
firewall.rthstandin_dnat.dest='lan'
firewall.rthstandin_dnat.dest_ip='192.0.2.1'
firewall.rthstandin_dnat.dest_port='22'
firewall.rthstandin_dnat.proto='tcp'

# an extra peer in the WireGuard server's settings
wireguard_server.rthstandin_peer=peers
wireguard_server.rthstandin_peer.public_key='<32 random bytes; no private key for it exists>'
wireguard_server.rthstandin_peer.client_ip='<an unused address in the server's range>'

# a settings file of our own, /etc/config/rthstandin
config marker 'm'
	option note 'rth-standin'

# one section added to each settings file listed in table 3
<file>.rthstandin=rthstandin
<file>.rthstandin.note='rth-standin inert marker'
```

`192.0.2.1` is an address reserved for documentation; it is not anyone's.

### What we did not place

Nothing in the boot loader, the `Factory` partition or any flash partition; no working second
login; no replaced system program; nothing in the web server's settings; nothing in
`/etc/inittab`.

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
