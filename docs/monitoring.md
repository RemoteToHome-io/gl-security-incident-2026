# Recording what the cloud sends a device

For people keeping a spare device connected to GL.iNet's cloud on purpose, to see whether anything
else arrives. Do this only on a device that carries no traffic you care about and has no computer
attached.

## Turn on message logging

The cloud client can log every message it receives. Over SSH on the device:

```
ubus call gl-cloud set_log_level '{"level":7}'
```

Incoming messages then appear in the system log as lines containing `payload:`:

```
logread | grep 'gl-cloud' | grep 'payload:'
```

Checked on GL-MT3000 firmware 4.11.0 and on an RM1 KVM on 1.10.2. The setting is lost when the
client restarts or the device reboots, and the log is held in memory, so copy it off the device
regularly. At this level the client also logs replies from the device's own settings interface,
which can include private details. Do not post that log unedited.

## Keep a copy off the device

[tools/cloud-watch](../tools/cloud-watch) is a small watcher that runs on a Linux computer. Once a
minute it reads the device's log, process list and connections over SSH, saves anything new, and
raises an alert for the known attack shapes, for shell characters inside a cloud message, for a
reboot, and for changes to the files an implant would touch. It writes nothing on the device apart
from setting the log level again after a client restart.

It polls, so something that starts and ends within a minute can be missed, though the cloud
message that caused it would still be in the log.
