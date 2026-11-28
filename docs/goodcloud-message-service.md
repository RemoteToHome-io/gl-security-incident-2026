# How the attack found its targets: GoodCloud's message service

*Added 28 November 2026. Part of [the incident pages](../README.md). Each point is marked **GL statement** (GL.iNet said
it, with a link), **Verified** (we read or counted it; the source is given), **Inference** (our reasoning, with
what would fit the opposite), or **Not known**. The reasoning is also
[inference 5](inferences.md#inference-5-the-attacker-worked-from-a-list-of-real-router-addresses-and-the-list-left-out-410-and-411).*

## What we think happened, in short

To send a command to one router through GoodCloud you must name that router's channel exactly: its model, its
firmware version and its MAC address. A MAC address alone reaches nothing. So the attacker either listened to the
routers' own traffic on GoodCloud and collected their addresses, or tried every combination: at least 1.2
billion messages. A list is far more likely. Every router names its full address in the topic of each report it
sends, and GL.iNet's own report says the attack needed control of at least one real GL device connected to
GoodCloud.

The data from our routers shows the shape of the preparation. Routers on firmware 4.7 to 4.9 were hit almost
everywhere: 169 of 185 such devices in our GoodCloud account answered the attacker. Routers on 4.10 and 4.11 were
missed entirely: none of the 10 such devices in the account, none of the 10 such routers in our sweeps, although
4.11.0 carries the same flaw. Every firmware version that was hit existed by 1 September 2026; 4.11.0 first
appeared in our firmware mirror on 5 September. The firmware version is part of a router's address, and two
readings fit every router in our data:

- **The attacker knew the routers and their models, and worked from a list of firmware versions frozen
  around early September.** Each router was sent the message under every version the attacker knew for its
  model; 4.11 was not on that list.
- **The attacker knew every router's current version, and left 4.10 and later out.** One GL-MT6000 on
  4.11.0 was online and reporting during the attack and was never addressed.

Our first idea, a list of routers with their versions harvested in August or September and gone stale for
those that upgraded, does not fit one router: it moved to a new 4.8.4 build two days before the attack and
was hit at the new version ([section 8](#8-putting-it-together-inference)). GoodCloud's broker records would
show which reading is right.

The attack itself ran over two days. On 19 November four devices received a few carefully made messages: final
testing. From 20:06 UTC on 20 November the automated wave followed, router group by router group, every message
carrying the same id, `1`, as if the tests had shown that nothing on the router checks it.

That is our reading of the data; each step is labelled below. GoodCloud's broker records can confirm or refute
every step; [what only GL.iNet can answer](#what-only-glinet-can-answer) lists what to pull.

## 1. The parts

- **MQTT** is a publish-and-subscribe protocol. A client publishes a message to a named channel, a *topic*;
  every client subscribed to that topic receives it. A publisher names one exact topic. A subscriber may use
  wildcards: `+` for one level, `#` for everything below.
- **EMQX** is the message broker GoodCloud runs on (**GL statement**). The broker decides who may connect, and
  who may publish or subscribe to which topic. Those rules are configuration that GL.iNet writes. **Verified, as
  product documentation only:** EMQX checks publishing and subscribing separately, so a configuration can close
  one and leave the other open
  ([EMQX: file-based authorization](https://docs.emqx.com/en/emqx/latest/access-control/authz/file.html), read
  28 November 2026). We have not seen GoodCloud's configuration or its EMQX version.

### What EMQX allows as it ships (Verified, in EMQX's own source code)

*Added 28 November 2026.* EMQX's source is public ([github.com/emqx/emqx](https://github.com/emqx/emqx)).
We read its authorization defaults at three releases: 5.8.9 (the last under the Apache licence), 5.10.5
(the latest 5.x) and 6.3.3 (the latest). This is what the product does as shipped, not GoodCloud's
configuration: we do not know which version GoodCloud runs or what it changed. Read in the code, not
tested on a broker.

- **In 5.8.9 and 5.10.5,** the broker checks each request against a rule file,
  [`etc/acl.conf`](https://github.com/emqx/emqx/blob/v5.8.9/apps/emqx_auth/etc/acl.conf), and allows
  whatever the rules leave undecided: the setting `authorization.no_match` defaults to `allow`
  ([`emqx_schema.erl`](https://github.com/emqx/emqx/blob/v5.8.9/apps/emqx/src/emqx_schema.erl)).
- **The shipped rule file has four rules, tried in order:** the dashboard user may subscribe to
  `$SYS/#`; a client on the broker's own machine (127.0.0.1) may do anything; every client is refused
  subscriptions to `$SYS/#` and to exactly `#` and `+/#`; and last, `{allow, all}`. The file itself says
  that for production the last rule should become `{deny, all}` and `no_match` should be set to `deny`.
  The 5.10.5 file has the same four rules
  ([5.10.5](https://github.com/emqx/emqx/blob/e5.10.5/apps/emqx_auth/etc/acl.conf)).
- **So, left as shipped,** any client that can connect may publish to any topic, and may subscribe to
  any filter but those three. Every GL.iNet topic begins with `/` (section 3). A subscription to `/#`,
  `/sys/#` or `/device/registration/#` is none of the three: by EMQX's matching code
  ([`emqx_authz_rule.erl`](https://github.com/emqx/emqx/blob/v5.8.9/apps/emqx_auth/src/emqx_authz/emqx_authz_rule.erl)),
  an exact-match entry matches only that exact filter, and `/#` begins with an empty level where
  `$SYS/#` begins with `$SYS`. The refusal rule does not apply, and the last rule allows it.
- **From 6.3 the shipped default is stricter:** the last rule applies only under a "legacy" profile,
  "hardened" is the default, and requests no rule decides are refused
  ([6.3.3](https://github.com/emqx/emqx/blob/6.3.3/apps/emqx_auth/etc/acl.conf)).

**Inference.** GL.iNet's report says a misconfiguration let a client send messages to other devices'
topics. A 5.8 or 5.10 broker left at these defaults would allow exactly that, and would also let a client
subscribe to every router's topics (section 4). It is one way, not the only one: a rule written for
devices that did not cover topics beginning with `/` would have the same effect. GoodCloud's own
configuration would show which.

## 2. What GL.iNet has said, beside what we found

| GL.iNet's report | What it says | What our data adds |
|---|---|---|
| [EMQX authorization bypass](https://github.com/gl-inet/CVE-issues/blob/main/GoodCloud/EMQX%20Authorization%20Bypass%20Leading%20to%20Remote%20Code%20Execution.md) (`vdb-submit-1112985`) | A misconfiguration let "an attacker who knows another device's MAC address" send forged messages to that device's topics. The attacker must control at least one GL device connected to GoodCloud, and can "enumerate device MAC addresses in bulk to construct forged MQTT subscription topics". GoodCloud 3.19.13 affected, 3.19.14 fixed | A topic built from a MAC alone reaches no router: it also needs the model and the firmware version (section 3). The report does not say where those came from, nor whether a client could also *subscribe* to other devices' topics |
| [AstroWarp command injection](https://github.com/gl-inet/CVE-issues/blob/main/4.0.0/AstroWarp(SDWAN)%20API%20Command%20Injection%20via%20thevirtual_ip_info%20Field%20Allows%20Arbitrary%20Command%20Execution%20as%20Root.md) (`vdb-submit-1112997`) | The `virtual_ip_info` handler runs a crafted value as root, also with AstroWarp off. One affected version per model, among them GL-MT3000 4.11.0 | The same code from 4.7.0 (December 2024) to 4.11.0 ([technical breakdown](technical-breakdown.md)). 4.11 was vulnerable and was not hit (section 6) |
| [Remote terminal configuration](https://github.com/gl-inet/CVE-issues/blob/main/common/Root%20Access%20via%20Rtty%20Configuration%20Modification%20and%20TLS%20Certificate%20Verification%20Bypass.md) (`vdb-submit-1112986`) | A changed start-up argument can point the remote terminal at a hostile server; seven KVM models and 31 router models listed | Concerns the remote terminal, a separate channel; it does not bear on how the routers' messages were addressed |

## 3. How a router is addressed (Verified)

A router listens on topics built from three things it knows about itself:

```
/sys/<model>/<firmware version>/<MAC>/command/<module>/<method>/request
/sys/<model>/<firmware version>/<MAC>/attribute/set_request
/sys/<model>/<firmware version>/<MAC>/attribute/get_request
```

- `<model>` is the model in lower case without "GL-" (`mt6000`); `<firmware version>` is the text of the router's
  `/etc/glversion` (`4.8.3`); `<MAC>` is its hardware address as twelve hexadecimal characters.
- **Read in the router's cloud client** (`/usr/bin/gl-cloud`), GL-AXT1800 4.8.3 and GL-MT3000 4.11.2, from
  instruction listings: the client reads the version from `/etc/glversion` when it starts, builds the three parts
  into one prefix, and subscribes to exact topics. There is no wildcard in any of its subscriptions.
- **Seen in the attack:** the attacker's messages, 187 of them recovered from 123 memory images of the cloud client
  on routers we manage, arrived on
  `…/command/astrowarp/virtual_ip_info/request` under each router's own model, version and MAC
  ([attacker messages](attacker-messages.md)).
- **So** a message reaches a router only if all three parts are right. A message built for a router's previous
  firmware version goes to a topic that router no longer listens on. *Not tested on a device:* we read this in
  the code; we have not watched a router's subscriptions change across an upgrade.

## 4. What a router tells the broker about itself (Verified)

Read in the same two builds of the cloud client.

- **Every report a router publishes under `/sys/` carries its full address in the topic:** its events, its
  attribute reports and its answers to commands all go to `/sys/<model>/<version>/<MAC>/…`.
- **On every connection it also publishes to `/device/registration/<MAC>`.** In GL-MT3000 4.11.2 the message
  holds the board model, the WAN, LAN and public IP addresses, the Wi-Fi network names and their BSSIDs, modem
  identifiers (IMEI, ICCID) where there is a modem, and the state of its remote-access switches. The topic is in
  every client we have read, GL-AXT1800 4.8.3 and 4.8.4 included; we read the message's content only in 4.11.2.
- **So:** a client that could subscribe to these topics would have learned, without sending anything, the full
  address of every router that reported in, and from the registration messages where each router sits on the
  internet. **Not known:** whether the misconfiguration allowed that. GL.iNet's report speaks of sending only.

## 5. Could the attacker have guessed? (Verified counts, then Inference)

- **MACs are easy.** All of the devices in the 260-device cross-section of our GoodCloud account that we studied share one
  manufacturer prefix,
  `94:83:C4` (GL Technologies (Hong Kong) Limited in the public registry). One prefix leaves 16,777,216
  addresses, and 148 of the 260 sit within 4,096 addresses of another: factory numbering runs in sequences. A MAC
  is also on the label and on the air.
- **The full topic is not.** Our firmware mirror holds 72 stable releases from 4.7.0 on, across 19 router models,
  dated on or before 19 November 2026 (115 counting beta and test builds). These are lower bounds: three versions
  we found on routers are not in it. Trying each of 16,777,216 addresses under each pair comes to 1,207,959,552
  messages (1,929,379,840 with the test builds).
- **Inference.** The wave lasted 12 hours (section 7): 1.2 billion messages in that time is about 28,000 a second,
  every second. A broker can carry that, so the number alone does not rule guessing out. What points to a list
  is the shape: the groups were started one after another, the versions of one model within about a minute of
  each other (section 7), and
  every hit router was on a version the attacker expected for its model (section 6). A list of real topics,
  collected by listening (section 4) or obtained some other way, fits all of it. **What fits the opposite:** a
  guesser that tried only the model and version pairs it expected would also leave this shape. GoodCloud's records
  of publishes to topics no router listens on would show it.

## 6. Who was hit, by firmware line (Verified counts)

**Devices in our GoodCloud account that answered the attacker** (214 of the 260 report a firmware version; read
from the Device Logs, 18 to 22 November):

| Firmware line | Answered | Did not |
|---|---|---|
| 4.3 to 4.6 (no vulnerable handler) | 0 | 19 |
| 4.7 | 32 | 2 |
| 4.8 | 89 | 10 |
| 4.9 | 48 | 4 |
| 4.10 | 0 | 1 |
| 4.11 | 0 | 9 |

**Routers we manage that had not been restarted since before 20 November** (first sweep, 21 to 23 November). A
router not restarted keeps the firewall rule the attacker's command leaves, so this is the cleanest test of
whether it was reached:

| Firmware line | Showed the attack | Showed nothing |
|---|---|---|
| 4.7 | 25 | 1 |
| 4.8 | 66 | 1 |
| 4.9 | 36 | 0 |
| 4.11 | 0 | 5 |

- **4.7 to 4.9:** 169 of 185 devices answered; 127 of 129 routers not restarted showed the attack.
- **4.10 and 4.11:** none hit. 0 of 10 devices in the account, 0 of 10 routers in either sweep, including the 5
  above. One GL-MT6000 on 4.11.0, running since 17 October, sent 1,670 log entries during the wave and was never
  addressed.
- **When each version existed** (first appearance in our firmware mirror, any stage): every version that was hit
  existed by 1 September 2026, the latest being GL-BE10000 4.8.6. Two hit versions are not in the mirror,
  GL-AXT1800 4.7.0 and GL-MT6000 4.8.1; the builds those devices report are dated March and August 2025. GL-MT3000 4.11.0 and GL-MT6000 4.11.0 first
  appear on 5 September (stable release 28 September). GL-E5800 4.10.0, not hit (one device), first appears on
  7 August (stable 1 September).

## 7. When, and in what order (Verified)

- **19 November 2026:** four devices answered requests GoodCloud did not send. Three, at 08:48:57, 08:49:05 and
  08:49:12 UTC, answered messages whose `id` looked like GoodCloud's own (32 hexadecimal characters) but had no
  matching send by GoodCloud. One, at 09:33:36 UTC, answered a message with the `id` `1`
  ([GoodCloud log](goodcloud-device-log.md)).
- **20 to 21 November:** the wave. 455 replies with `id` `1` from 210 devices, from 20:06:29 UTC on 20 November to
  08:04:42 UTC on 21 November. Replies per hour (UTC): 20 Nov 20h 52, 21h 112, 22h 69, 23h 16; 21 Nov 00h 61, 01h
  34, 02h 1, 03h 2, 04h 12, 05h 26, 06h 54, 07h 13, 08h 2. None in any other hour from 19 to 21 November apart from
  the one at 09:33 on 19 November.
- **Group by group.** The first reply of each model and version group, in order:

  | First reply (UTC) | Model, firmware | Devices in the log | Answered |
  |---|---|---|---|
  | 20 Nov 20:06:29 | GL-MT6000 4.9.1 | 6 | 6 |
  | 20 Nov 20:46:14 to 20:46:22 | GL-AXT1800 4.8.4, 4.8.2, 4.8.3 | 3, 16, 21 | 3, 13, 18 |
  | 20 Nov 23:46:58 to 23:54:52 | GL-MT6000 4.8.3; GL-AX1800 4.8.3; GL-BE3600 4.8.3; GL-BE9300 4.9.0, 4.8.4 | 13, 1, 1, 1, 1 | 12, 1, 1, 1, 1 |
  | 21 Nov 00:21:10 to 00:21:48 | GL-MT3000 4.8.1, 4.9.0, 4.8.0, 4.8.2 | 16, 7, 3, 1 | 13, 7, 3, 1 |
  | 21 Nov 00:48:04 to 00:48:41 | GL-MT6000 4.8.2, 4.9.0, 4.8.4, 4.8.1 | 5, 4, 2, 1 | 5, 4, 2, 1 |
  | 21 Nov 01:16:36 to 01:20:04 | GL-BE3600 4.9.2, 4.8.1 | 1, 4 | 1, 4 |
  | 21 Nov 01:40:55 to 01:41:08 | GL-MT5000 4.9.0, 4.8.6 | 19, 7 | 18, 7 |
  | 21 Nov 02:11:44 | GL-BE6500 4.8.7 | 1 | 1 |
  | 21 Nov 03:01:47 | GL-MT2500 4.9.0 | 1 | 1 |
  | 21 Nov 03:17:49 | GL-BE10000 4.8.6 | 1 | 1 |
  | 21 Nov 04:39:39 to 04:40:01 | GL-MT3600BE 4.9.0, 4.9.1, 4.8.5 | 11, 2, 2 | 8, 2, 2 |
  | 21 Nov 05:50:01 to 05:50:55 | GL-MT6000 4.7.0, 4.7.7, 4.7.4 | 2, 8, 2 | 2, 7, 2 |
  | 21 Nov 06:13:08 to 06:13:09 | GL-MT2500 4.7.4, 4.7.13 | 3, 5 | 3, 5 |
  | 21 Nov 07:44:15 to 07:49:52 | GL-MT3000 4.7.4, 4.7.0 | 9, 2 | 9, 2 |
  | 21 Nov 08:04:42 | GL-AXT1800 4.7.0 | 2 | 2 |

  46 devices in the log report no version; 41 of them answered.
- **Every message of the wave has the same form:** `id` `1`, a space after each colon and comma, no `ts` field.
  GoodCloud's own commands carry a 32-character id and a `ts` ([attacker messages](attacker-messages.md)).

## 8. Putting it together (Inference)

| Step | What we think | Rests on | Label |
|---|---|---|---|
| 1 | The attacker had a GL device, or its way onto GoodCloud, connected | GL.iNet's report | GL statement |
| 2 | It worked from a list of real router topics, not blind guesses | sections 3, 5, 7 | Inference |
| 3 | It got the addresses by listening on GoodCloud | section 4, and what EMQX allows as it ships (section 1) | Inference |
| 4 | The firmware versions it addressed were those that existed by about September 2026 | section 6 | Inference |
| 5 | On 19 November it tested by hand on a few devices | section 7 | Inference (also [inference 3](inferences.md#inference-3-the-attacker-tried-the-flaw-on-a-few-devices-on-19-november-before-the-main-wave)) |
| 6 | From 20 November it sent the list through automation, group by group | section 7 | Inference |

**How 4.11 was missed: two readings, and one router that decides between our first idea and them.**

Our first reading was that the attacker built a list of routers, each with its version, around August to
September, and that routers which upgraded to 4.11 afterwards were addressed under their old version and missed.
One router in our data does not fit it. A GL-AXT1800 in our account's cross-section (not one of our own lab
units) reported firmware 4.8.3 at 16:37 UTC on 18 November and the 4.8.4 beta2 build of 11 November from 18:04
that day, and it answered the attacker five times from 20:47 UTC on 20 November. The topic carries only `4.8.4`
whichever 4.8.4 build a router runs (the build type is kept in a separate file), and on 20 November every
GL-AXT1800 4.8.4 build was a beta: the security build is dated 23 November. Since a
router listens only at its current version (section 3), the attacker addressed it at 4.8.4, a version it had been
on for two days. A list made in August or September would have held it at 4.8.3 (unless it was on 4.8.4 then and
went back, which our log, starting 18 November, cannot show).

Two readings fit every router in our data, that one included:

- **A list of routers by model, and a list of versions frozen around early September.** Each router was sent the
  message under every version the attacker knew for its model; a router on any of those versions answered. 4.11
  was not among them. This fits the three GL-AXT1800 versions answering within 8 seconds of each other (section
  7), and dates the version list, not the router list.
- **Up-to-date knowledge of every router, with 4.10 and later left out.** This fits the GL-MT6000 on 4.11.0 that
  was online and reporting throughout the wave and was never addressed. Why versions would be left out we cannot
  say.

**What fits the opposite of both.** A handful of routers on 4.7 to 4.9 were online and not hit: two GL-AXT1800 on
4.8.2 that were connected when their group was addressed (13 of 16 on that version answered), and one GL-AXT1800
on 4.8.3, not restarted, that showed nothing (it is not in our account's log, so whether it was online is not
known). Small numbers: 10 devices on 4.10 and 4.11 in our account, 10 routers in our sweeps.

**What would settle it** is in GoodCloud's broker records. The first reading means many publishes to topics no
router listens on, each router's MAC under several versions; the second means publishes only to live topics.

## What only GL.iNet can answer

1. Every publish to a `…/virtual_ip_info/request` topic from 19 to 21 November: the publishing client, its
   credentials and source address, and the topic it named.
2. Publishes to topics no router was subscribed to, and the firmware versions those topics carried. Publishes
   naming several versions for one MAC point to the first reading above; only live topics, to the second.
3. Whether that client subscribed to anything beyond its own topics, when, and with which patterns. That is step 3.
4. Whether the clients of 19 November and of 20 November are the same.
5. How far back the broker's records go.
6. The EMQX version that GoodCloud 3.19.13 ran on, its authorization rules and its `no_match`
   setting, and what GoodCloud 3.19.14 changed in them.

## Limits

- The code is read in two builds of the cloud client, not tested on a router.
- Counts come from the routers we manage and the 260-device cross-section of our own GoodCloud account that we studied: not a
  random sample. Our account's log starts on 18 November, so it shows each device's version from then only.
- One router answered the attacker (21 November, 00:48 UTC) and, after a restart, showed no state file in either
  sweep. So a missing state file does not prove a router was never called.
- We have not seen GoodCloud's broker, its configuration or its logs. EMQX's defaults are read in its
  source code, not tested on a running broker.
