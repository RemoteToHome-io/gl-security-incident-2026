# cloud-watch

Watches one GL.iNet router or KVM from a Linux computer and keeps a record of what its cloud client
receives and what runs on it. See [docs/monitoring.md](../../docs/monitoring.md) for when to use it.

```
./watch.sh <device-address> <state-directory> [interval-seconds]
```

- Needs key-based root SSH to the device, `bash`, `ssh`, `timeout`, `awk`, `diff`.
- `collect.sh` is what runs on the device each pass. It only reads.
- Output in the state directory: `events.log` (everything new), `alerts.log` (things to look at),
  `log-all.txt` (the device's system log as collected).
- Stop it by creating a file named `STOP` in the state directory.

The saved log can contain private details from the device. Keep the state directory private.
