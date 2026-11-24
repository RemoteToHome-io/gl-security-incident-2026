# The attack in GoodCloud's own log, and how to check yours

*Added 24 November 2026. Part of [the incident pages](../README.md). Times are UTC.*

## In short

- **GoodCloud keeps a log of every message each device sent to the cloud, and an owner can read
  it.** It is under Logs, Device Logs, in the GoodCloud account the device is bound to.
- **The attack is in it.** A device that ran the attacker's command answered the cloud, and the
  answer is logged. It carries `"id": 1`, which no ordinary GoodCloud message does.
- **You can check a device this way without SSH,** and after the device has been reset or
  reinstalled, as long as the log still reaches back to the dates.
- **In a cross-section of 260 devices read so far, 210 answered the attacker,** and the log shows the first
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
We read the Device Logs in our own GoodCloud account for 18 to 21 November 2026: 42,085 rows from
260 devices so far. A device appears only if it sent something to GoodCloud in those
four days, so devices that were switched off or not connected are not among them.

| | |
|---|---|
| Devices that sent a reply carrying `"id": 1` | **210 of the 260 read so far** |
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
  written at the same second as the reply (08:48:57, 08:49:11 and 09:33:36). The fourth is a device
  we have not examined.

**What this makes likely:** that the attacker tried the handler on a few devices about 36 hours
before the main wave, at first with an `id` made to look ordinary and then with the `1` it used
from then on. That is an inference from the pattern; the log does not name the sender. It also
means a search for `"id": 1` alone misses the earliest calls.

GL.iNet's notice dates the incident to 20 November. Its own records would show whether anything
was sent before 19 November; ours do not reach further back than the 18th in what we read.

## Limits

- This is one account: ours, and a cross-section read so far. It is not a sample of all GoodCloud
  devices.
- A reply shows that a command in that form ran and returned. It does not show what the command
  was. For that see [attacker messages](attacker-messages.md), from the routers' memory.
- 50 of the 260 devices show no such reply. We have not worked out, device by device, whether they
  were offline, on firmware without the flaw, or missed.
- We read the rows from the Device Logs page as it displays them and saved them privately. They
  are not published: they hold account names and device addresses.
- In a second organisation where our account is not the owner, the Device Logs page is not
  offered to us, so those devices are not counted here.
