# Field survey

Devices checked so far, by model and firmware. Counts only: no client, network or device is
identified. A device that has been rebooted or upgraded since the evening of 20 November 2026
cannot be cleared for that night, because the remote shell found so far leaves nothing behind
after a restart. Those are counted separately from "no indicators".

Method: the live process list and connections, the named pipe `/tmp/f`, the "gl-helper" files, and
files changed in the writable layer, as described in the [README](../README.md#check-a-device).

Last updated: 2026-11-21 17:05 UTC.

| Model | Firmware | Checked | Indicators found | No indicators, running since before 20 Nov | No indicators, but restarted since |
|---|---|---|---|---|---|
| GL-AXT1800 | 4.8.3 | 1 | 1 (remote shell, see [details](router-reverse-shell.md)) | 0 | 0 |
| GL-AXT1800 | 4.8.4 beta | 1 | 0 | 0 | 1 |
| GL-MT3000 | 4.11.0 | 1 | 0 | 0 | 1 |
| GL-RM1 (KVM) | 1.10.1 | 1 | 0 | 0 | 1 |

All four had GL.iNet's cloud service switched on. These first rows are our own test devices. Rows
from the wider set will be added as each batch is finished.

Contributions use the same columns: see [CONTRIBUTING.md](../CONTRIBUTING.md).
