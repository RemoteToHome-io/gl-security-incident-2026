# Weaknesses that the fixed firmware does not close

The fix GL.iNet released on 22 and 23 November 2026 closes the one hole the attack of 20 November
used: the unchecked values in the `virtual_ip_info` handler. This page lists what we have found
around it that is still there. Some of it is by design, some of it is a flaw, and some of it is a
lead we have read but not tested. Each item says which.

One further weakness is not on this page. We reported it to GL.iNet on 22 November 2026 and told
them we would withhold it until it is fixed. Everything else we know is here.

**How to read the labels.** *Read*: we read it in the firmware's code, by instruction listing or
in a plain script. *Tested*: we ran it on a device of our own. *Lead*: read in part, not tested;
it may turn out not to be reachable. *Reported*: someone else's finding, with a link.

When this page was written nothing here had been confirmed by GL.iNet. Since then GL.iNet has
published its own reports on the command injection and on the remote terminal (item 2).

## Summary for owners

- If GoodCloud is switched off **on the device**, the cloud client does not run and items 1 to 3
  do not apply. Unbinding the device in the GoodCloud account is not the same thing (item 3).
- After any firmware upgrade, check that GoodCloud and its remote SSH and web access are still
  off if you had turned them off (item 4).
- Items 5 and 6 need someone to already have root on the router. They matter for recovery: they
  are places where a change can outlast what an owner normally does.

## 1. The cloud channel can do much more than the one command that was abused

*Read, in the GL-AXT1800 4.8.4 beta cloud client (`/usr/bin/gl-cloud`, functions at source lines
1201 to 1451) and its modules. By design. Not re-read in the fixed builds.*

The router's cloud client subscribes to two kinds of topic on GL.iNet's message broker:

```
/sys/<model>/<version>/<mac>/command/<module>/<method>/request
/sys/<model>/<version>/<mac>/attribute/set_request
```

When a message arrives it calls the matching handler directly. In the code we read there is no
check that the device is bound to an account, no signature on the message, and no check of the
device's own remote-access switches before a command is dispatched. A message marked as plain is
accepted as it is. In the 4.8.3 build an input check was applied to attribute changes only, not to
commands; the 4.8.4 beta and 4.11.0 builds had no such check at all before the fix.

So the router relies on one thing: that nobody but GL.iNet can publish to its topic. On
20 November someone else could.

What the same channel offers besides the abused command, in that build:

| Message | What it does on the router |
|---|---|
| attribute `system`, fields `strong_password` / `weak_password` | Sets the root password (`passwd -a sha256`), clears sessions, restarts the SSH server |
| command `base.rpc`, `base.cmd` | Calls any function of the router's local management interface (`http://localhost/rpc`) with an internal header and no login |
| command `base.reboot` | Restarts the router |
| command `base.reset` | Resets the firmware to factory state |
| `ota` module | Starts a firmware upgrade from an address given in the message (*names only; body not read*) |
| `security` module | Adds or removes firewall rules that accept traffic from the internet side (*names only; body not read*) |
| `rtty_run` (item 2) | Opens a remote terminal session to a host named in the message |

The fix validates the fields of `virtual_ip_info` and two neighbouring commands. It does not
change this design. Whoever can publish to a device's topic can still use every row above.

## 2. The remote terminal dials a host that the cloud names

*Read, in the GL-MT3000 4.11.1 image: the start-up and first-boot scripts in full; the web
interface's remote-terminal module by its text and, for the identifier check, by disassembly. By
design.*

GoodCloud's "remote SSH" and "remote web access" use a small program on the router, `rtty`, that
dials out to a relay so that someone on the cloud side can reach a terminal or the web interface.

- The cloud client has a command `rtty_run`. The request carries the relay's **host, port and
  token**.
- The router takes its own identifier from its device data (`/proc/gl-hw-info/device_ddns`),
  keeps only letters, digits, `_` and `-`, and refuses to start if nothing is left.
- It downloads a certificate authority file to `/tmp/ca.crt` from `ca.gl-inet.cn` or
  `ca.gl-inet.com` with `wget`, writes `/tmp/rtty.ini` with the identifier, host, port and token,
  and starts `/usr/sbin/rtty`.
- Two switches control whether the cloud may do this, `rtty.general.ssh_en` and `web_en`. The
  firmware's first-boot script sets **both to 1**.

We did not read whether `wget` checks the certificate of the site it fetches the authority file
from, or what `rtty` asks for before it hands over a shell.

On KVMs the same program runs permanently on a bound device; see
[kvm-firmware.md](kvm-firmware.md).

*Added 23 November.* GL.iNet has now published its own report on this program: certificate
checking in the remote-terminal client can be bypassed by changing the arguments of its start
command, so a device can be made to connect to a hostile terminal server, which then has root.
It lists all seven KVM models (fixed in 1.10.3 and 1.8.7) and 31 router models with an "expected
fix" version, among them older models on the 4.3 and 4.5 firmware lines. Three earlier reports
of 16 October 2026 describe the same chain on the GL-RM1's 1.10.1 firmware. See
[GL.iNet's published vulnerability reports](gl-statements.md#glinets-published-vulnerability-reports).

## 3. Unbinding does not stop the cloud client

*Reported by forum users and GL.iNet staff; not tested by us.*

- A forum user reports that after unbinding a router from the GoodCloud account, the cloud client
  on the router keeps running and keeps its connection to the broker, and gives the command to
  switch it off on the device
  ([router check thread, post 118](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/118)).
- GL.iNet staff state that devices fetch a licence and signature updates for the traffic
  inspection feature from GoodCloud even when not bound
  ([post 7](https://forum.gl-inet.com/t/router-features-going-forward-after-the-remote-exploit/73090/7)).

What we verified ourselves: none of the routers we checked had AstroWarp enabled, and the handler
ran on them all the same. Whether an unbound device could be sent the command is one of the open
questions in [findings.md](findings.md).

To switch the client off on the device. This is the sequence we used on the routers where we
switched GoodCloud off, each read back afterwards (setting 0, not started at boot, no client
process):

```sh
/etc/init.d/gl-cloud stop
uci set gl-cloud.@cloud[0].enable=0
uci commit gl-cloud
/etc/init.d/gl-cloud disable
```

## 4. An upgrade can switch cloud features back on

*Reported; not tested by us.*

One owner reports that after an online upgrade to 4.11.0 with settings kept, the cloud client,
AstroWarp and GoodCloud's remote SSH and web access were switched back on although they had been
turned off
([post 22](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/22)).
Check those settings after every upgrade.

## 5. The fixed handler may still trust values it reads back from its own state file

*Lead. Read in part in the GL-MT3000 4.11.1 cloud client (package build git-2026.323); not
tested. Reported to GL.iNet on 22 November 2026 as a point to check.*

- The `virtual_ip_info` handler (source lines 841 to 965 of `cloud/astrowarp.lua`) now checks its
  input before it builds any command. That is the fix, and we read it in an instruction listing.
- A second function in the same module (source lines about 1468 to 1510, present in 4.11.0 as
  well) rebuilds the firewall rules from the state file `/etc/mp_ip_mapping_info` and from a local
  scan. It puts `virtualIp` and `ip` into the same `iptables` command lines and runs them.
- We did not see the checker called in that function.
- The state file is written by the handler and survives an upgrade that keeps settings.

If values in that file are not checked when they are read back, a state file written through the
old handler before the upgrade could carry a command into the fixed firmware. On every attacked
router we examined the file was empty, so we have no case of this. We read the function only in
part. It may be that the values cannot reach it in a harmful form.

## 6. A DDNS helper builds a shell command from device data without quoting it safely

*Read by disassembly and in the plain shell script, GL-MT3000 4.11.1 (package `gl-sdk4-ddns`
build git-2026.237). Not reachable in the configuration that firmware ships with. Not tested with
a crafted value. Not yet reported to GL.iNet when this page was written.*

- `/usr/lib/gl_ddns/get_ddns_post_cmd.lua` reads the device's DDNS identifier from its device
  data (`/proc/gl-hw-info/device_ddns`) as it is, puts it into a JSON object, wraps that in
  **single quotes** and prints a `curl … --data '<json>' …` command line.
- `/usr/lib/gl_ddns/dynamic_dns_functions.sh`, lines 930 to 941, takes that output and runs it
  with `eval`, as root:

  ```sh
  if [ -n "$update_script" ]; then
      if [ -f "/usr/lib/gl_ddns/get_ddns_post_cmd.lua" ]; then
          local __cmd=$(lua $update_script)
          ...
          eval $__cmd
  ```

- The JSON encoder does not escape a single quote (checked on the router: a value containing `'`
  comes out unchanged). So a single quote in the DDNS identifier would end the quoted argument
  and whatever followed would run as a command.
- The identifier is read from the device-data partition, which neither a factory reset nor a
  firmware reinstall rewrites, and which the running system marks writable (finding R-25).

Why it is not reachable as shipped: that branch only runs when a DDNS entry has `update_script`
set to this helper. On the GL-MT3000 4.11.1 we read, bound to GoodCloud, neither DDNS entry sets
it, and nothing in the firmware image sets it. So today this needs someone who already has root
to both change the device data and add that setting; the setting itself is wiped by a reinstall
without kept settings. It is a flaw in how the command is built, worth fixing, and it may be
reachable on another model or firmware that we have not read.

The same helper's update goes to `https://ddns-tls.glddns.com/nic/tls/update` with `curl -k`,
which tells `curl` not to check the server's certificate, and there is a second address,
`https://ddns.glddns.com/nic/no-tls/update` (*read in the helper's text; which is used when was
not followed*).

## 7. What a clean-up, a reset and a reinstall leave in place

Covered on the main page, listed here so this page is complete:

- The fixed firmware's clean-up removes the start-up routes it names and nothing else. Other
  start-up entries placed in kept settings survive an upgrade and run (*tested*, finding R-24).
- An upgrade keeps all of `/etc/config`, the scheduled-task tables, `/etc/rc.local`, the SSH
  server's authorised keys, the account and password files and `/etc/udhcpc.user.d` (*read*).
- A reinstall does not rewrite the boot loader partitions or the device-data partition
  (*read*, finding R-25). On a GL-AXT1800 the boot loader partition could be opened for writing
  from a root shell (*tested*; nothing was written).
- On KVMs an upgrade that keeps the configuration keeps a boot script folder and added SSH keys,
  and firmware 1.10.3 starts the SSH server at every boot (*tested*, finding K-12).

See [README: If you find something](../README.md#if-you-find-something) and
[Fixed firmware](../README.md#fixed-firmware).

## What would close these

For GL.iNet, in order of effect:

1. Sign every command on the cloud side with a key that never leaves GL.iNet, and have the
   device verify the signature, that the message names this device, and that it is recent, before
   anything is dispatched.
2. Refuse commands when the device is not bound, and put the commands in item 1 behind a switch
   the owner sets on the device, off by default.
3. Have the remote terminal accept only relays the firmware already knows, and ship the
   certificate authority in the firmware instead of downloading it.
4. Check values read from the state file as strictly as values read from a message.
5. Never build a shell command by joining strings: pass arguments as a list, or quote every
   value. Remove `eval` from the DDNS update path.
6. Make the firmware's clean-up report what it found and compare the whole writable layer with
   the image, instead of removing a fixed list of names.
7. Do not let an upgrade change the owner's cloud and remote-access switches.
