# The attack in GoodCloud's own log, and how to check yours

*Added 24 November 2026. Part of [the incident pages](../README.md). Times are UTC.*

## In short

- **GoodCloud keeps a log of every message each device sent to the cloud, and an owner can read
  it.** It is under Logs, Device Logs, in the GoodCloud account the device is bound to.
- **The attack is in it.** A device that ran the attacker's command answered the cloud, and the
  answer is logged. It carries `"id": 1`, which no ordinary GoodCloud message does.
- **You can check a device this way without SSH,** and after the device has been reset or
  reinstalled, as long as the log still reaches back to the dates.
- **In the 260-device cross-section we studied, 210 answered the attacker,** and the log shows the first
  call on 19 November 2026, a day and a half before the main wave.

## Check your own device

1. Sign in at <https://www.goodcloud.xyz/> with the account the device is bound to.
2. Open **Logs**, then **Device Logs**. If you do not see it, your role in that organisation does
   not include it; ask the organisation's owner.
3. Set the date range to cover **19 November 2026 08:00 to 21 November 2026 09:00 UTC**. The page
   shows times in your own time zone, so convert first.
4. Put the device's MAC address in the MAC box if you have more than one device.
5. Each row has a **Details** link. Open the rows around the times in the table below and look at
   the message.

What to look for in a message:

| Message | Meaning |
|---|---|
| `{"id":1,"astrowarp":[],"code":0,"time":...}` | The device ran a command sent in the attacker's form. This is the reply from the older firmware lines |
| `{"astrowarp":{"virtual_ip_info":[]},"code":0,"id":1,"time":...}` | The same, from the newer firmware lines |
| `"id"` followed by a long quoted string, such as `"id":"3f2a…"` | An ordinary GoodCloud message. Not a sign of the attack |

The mark is the `id`: the number `1`, with no quotes. The order of the fields varies.

**If you find it,** the attacker's command ran on that device as root. Treat the device as
compromised and follow [If you find something](../README.md#if-you-find-something). The log does
not say which command it was.

**If you do not find it,** that is not proof. The device may have been off or disconnected when it
was sent, the log may not reach back far enough, and three calls on 19 November did not use that
mark (below).

## What the log holds

*Verified by us in our own GoodCloud account on 24 November 2026, version shown v3.19.14.*

Each row is one message, with the time, the device's MAC, who it is bound to, and the message
itself. The Details view names the message type:

| Type | What it is |
|---|---|
| `publish` | A message GoodCloud itself sent to the device, with its content |
| `tsl_command_response` | The device's reply to a command |
| `tsl_event_report` | The device's routine reports |
| `connected`, `disconnected`, `register` | The device's connections to the message broker, with the address it connected from |

The log can be filtered by MAC and by time. Its Export button exports the rows you tick.

**How far back it goes.** Our account holds rows for 18 November 2026, the earliest date we asked
for, and returned nothing for 20 December 2025. We did not look for the earliest date it holds. So it covers the attack of 19 to 21
November and not the install dates of the [older backdoor](older-backdoor-loader.md).

## What ours shows

As with our checks on the routers themselves, we took a relevant cross-section of what we manage.
We read the Device Logs in our own GoodCloud account for 18 to 21 November 2026, for a cross-section of
260 devices: 42,085 rows. A device appears only if it sent something to GoodCloud in those
four days, so devices that were switched off or not connected are not among them.

| | |
|---|---|
| Devices that sent a reply carrying `"id": 1` | **210 of the 260 in the cross-section** |
| Such replies in all | 455 |
| The first | **19 November 2026 09:33:36** |
| The main wave | 20 November 20:06:29 to 21 November 08:04:42 |
| Replies per device | one on 110 devices, two on 44, three on 11, four on 1, five on 44 |

By hour: 19 November 09h, 1. 20 November 20h, 52; 21h, 112; 22h, 69; 23h, 16. 21 November 00h, 61;
01h, 34; 02h, 1; 03h, 2; 04h, 12; 05h, 26; 06h, 54; 07h, 13; 08h, 2.

**It agrees with what we recovered from the routers.** The window we published from the routers'
own memory runs from 20 November 20:06:35 to 21 November 08:04:42
([attacker messages](attacker-messages.md#totals)). The log's main wave ends in the same second
and starts six seconds earlier.

**The attacker's requests are not in the log; only the replies are.** For ordinary commands the log
holds both halves: GoodCloud's `publish` row and then the device's reply, with the same `id`. Of
the 1,035 `astrowarp` replies with an ordinary `id`, 1,032 have their request in the log; the three
that do not are the three of 19 November below. Of the 455 replies carrying `"id": 1`, none has. The request reached the device without
passing through the part of GoodCloud that logs what it sends. That fits GL.iNet's own account of
the cause, a message broker that let an outside client publish to other people's devices
([GL.iNet's statements](gl-statements.md#glinets-published-vulnerability-reports)).

**GoodCloud itself does send `virtual_ip_info`,** to devices that take part in AstroWarp, right
after they reconnect. We saw it twice in the four days. Those have a `publish` row and a long
quoted `id`. So the command name alone is not the mark; the `id` and the missing `publish` row are.

## Model by model

*Added 24 November 2026.* When a device connects, the log records its model and firmware. That
gives both for 195 of the 260 in the cross-section; the other 65 did not reconnect in those four days, so
the log does not say what they are. The table is in the order the attacker reached each group. It
uses each device's first answer in the attacker's form; the single early answer of 19 November
is from a device without a registration row and is not in it.

| Model | Firmware | Devices | Answered | First answers (UTC) |
|---|---|---|---|---|
| GL-MT6000 | 4.9.1 | 6 | 6 | 20 Nov 20:06:29 to 20:07:19 |
| GL-AXT1800 | 4.8.4 | 2 | 2 | 20 Nov 20:46:14 to 20:47:14 |
| GL-AXT1800 | 4.8.2 | 16 | 13 | 20 Nov 20:46:15 to 20:48:40 |
| GL-AXT1800 | 4.8.3 | 22 | 19 | 20 Nov 20:46:22 to 20:48:41 |
| GL-MT6000 | 4.8.3 | 13 | 12 | 20 Nov 23:46:58 to 21 Nov 00:49:05 |
| GL-AX1800 | 4.8.3 | 1 | 1 | 20 Nov 23:50:12 |
| GL-BE3600 | 4.8.3 | 1 | 1 | 20 Nov 23:51:19 |
| GL-BE9300 | 4.9.0 | 1 | 1 | 20 Nov 23:54:16 |
| GL-BE9300 | 4.8.4 | 1 | 1 | 20 Nov 23:54:52 |
| GL-MT3000 | 4.8.1 | 16 | 13 | 21 Nov 00:21:10 to 00:23:05 |
| GL-MT3000 | 4.9.0 | 7 | 7 | 21 Nov 00:21:12 to 00:22:59 |
| GL-MT3000 | 4.8.0 | 3 | 3 | 21 Nov 00:21:47 to 00:22:40 |
| GL-MT3000 | 4.8.2 | 1 | 1 | 21 Nov 00:21:48 |
| GL-MT6000 | 4.8.2 | 5 | 5 | 21 Nov 00:48:04 to 00:48:31 |
| GL-MT6000 | 4.9.0 | 4 | 4 | 21 Nov 00:48:16 to 00:49:10 |
| GL-MT6000 | 4.8.4 | 2 | 2 | 21 Nov 00:48:35 to 00:48:49 |
| GL-MT6000 | 4.8.1 | 1 | 1 | 21 Nov 00:48:41 |
| GL-BE3600 | 4.9.2 | 1 | 1 | 21 Nov 01:16:36 |
| GL-BE3600 | 4.8.1 | 4 | 4 | 21 Nov 01:20:04 to 01:26:24 |
| GL-MT5000 | 4.9.0 | 19 | 18 | 21 Nov 01:40:55 to 01:41:51 |
| GL-MT5000 | 4.8.6 | 7 | 7 | 21 Nov 01:41:08 to 01:41:49 |
| GL-BE6500 | 4.8.7 | 1 | 1 | 21 Nov 02:11:44 |
| GL-MT2500 | 4.9.0 | 1 | 1 | 21 Nov 03:01:47 |
| GL-BE10000 | 4.8.6 | 1 | 1 | 21 Nov 03:17:49 |
| GL-MT3600BE | 4.9.0 | 10 | 8 | 21 Nov 04:39:39 to 04:40:14 |
| GL-MT3600BE | 4.9.1 | 2 | 2 | 21 Nov 04:39:51 to 04:40:09 |
| GL-MT3600BE | 4.8.5 | 2 | 2 | 21 Nov 04:40:01 to 04:40:07 |
| GL-MT6000 | 4.7.0 | 2 | 2 | 21 Nov 05:50:01 to 05:50:53 |
| GL-MT6000 | 4.7.7 | 8 | 7 | 21 Nov 05:50:29 to 05:51:15 |
| GL-MT6000 | 4.7.4 | 2 | 2 | 21 Nov 05:50:55 to 05:51:35 |
| GL-MT2500 | 4.7.4 | 3 | 3 | 21 Nov 06:13:08 to 06:14:17 |
| GL-MT2500 | 4.7.13 | 5 | 5 | 21 Nov 06:13:09 to 06:13:52 |
| GL-MT3000 | 4.7.4 | 9 | 9 | 21 Nov 07:44:15 to 07:49:52 |
| GL-MT3000 | 4.7.0 | 2 | 2 | 21 Nov 07:49:52 to 07:49:52 |
| GL-AXT1800 | 4.7.0 | 2 | 2 | 21 Nov 08:04:42 to 08:04:42 |
| GL-AX1800 | 4.7.0 | 1 | 0 | none |
| GL-E5800 | 4.10.0 | 1 | 0 | none |
| GL-MT3000 | 4.11.0 | 6 | 0 | none |
| GL-MT3600BE | 4.8.7 | 1 | 0 | none |
| GL-MT6000 | 4.11.0 | 3 | 0 | none |

- **The attacker worked through the devices one model and firmware line at a time.** Each group was
  reached within a minute or two, across unrelated owners. That is the same pattern, and the same
  minutes, that we read from the routers themselves
  ([attacker messages](attacker-messages.md#totals)).
- **No device on 4.11.0 answered.** Nine devices on 4.11.0 (GL-MT3000 and GL-MT6000) were connected
  in those days and none was called. The flaw is in 4.11.0
  ([technical breakdown](technical-breakdown.md)); the attacker did not use it there. We do not
  know why.
- **Of the 195 devices whose firmware the log gives, 169 answered.** Leaving out the groups that
  were not called at all, nearly every device in a group that was called answered.

## 19 November: the first calls

Four replies on the morning of 19 November answer requests GoodCloud did not log:

| Time | Reply | `id` |
|---|---|---|
| 08:48:57 | empty `astrowarp` list | a long quoted string |
| 08:49:05 | `virtual_ip_info` | a long quoted string |
| 08:49:12 | empty `astrowarp` list | a long quoted string |
| 09:33:36 | empty `astrowarp` list | the number `1` |

- They are four different devices. In the three minutes either side of each reply, the log holds
  nothing for that device but its routine reports: no reconnection, and nothing published to it.
- In four days and 42,085 rows these are the only replies of this kind before the main wave.
- On three of the four routers the handler's state file, `/etc/mp_ip_mapping_info`, was first
  written within a second of the reply: at 08:48:57 and 09:33:36, the same second as the logged
  reply, and at 08:49:11, one second before the reply logged at 08:49:12. The fourth is a device
  we have not examined. *Corrected 25 November 2026: this said "the same second" for all three.*

**What this makes likely:** that the attacker tried the handler on a few devices about 36 hours
before the main wave, at first with an `id` made to look ordinary and then with the `1` it used
from then on. That is an inference from the pattern; the log does not name the sender. It also
means a search for `"id": 1` alone misses the earliest calls.

GL.iNet's notice dates the incident to 20 November. Its own records would show whether anything
was sent before 19 November; ours do not reach further back than the 18th in what we read.

## Limits

- This is one account, ours, and a cross-section we chose. It is not a sample of all GoodCloud
  devices.
- A reply shows that a command in that form ran and returned. It does not show what the command
  was. For that see [attacker messages](attacker-messages.md), from the routers' memory.
- 50 of the 260 in the cross-section show no such reply. We have not worked out, device by device, whether they
  were offline, on firmware without the flaw, or missed.
- We read the rows from the Device Logs page as it displays them and saved them privately. They
  are not published: they hold account names and device addresses.
- In a second organisation where our account is not the owner, the Device Logs page is not
  offered to us, so those devices are not counted here.
