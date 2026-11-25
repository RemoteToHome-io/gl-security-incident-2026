# What the data suggests: inferences, not findings

*Started 24 November 2026. Part of [the incident pages](../README.md).*

Everything on [the findings page](findings.md) is something a person saw, with a note of who saw it
and how. This page is different. It holds reasoning: what the verified facts make more likely or
less likely, where no fact settles the question.

The rules for this page:

- Every inference names the facts it rests on, and those facts are on the findings page.
- Every inference lists what fits it, what would fit the opposite, and what would settle it.
- Nothing here is proof. Do not quote an inference as a finding.
- We make no claim about who the attacker is.

---

## Inference 1. The attack of 20 November and the older backdoor look like two operations that did not share information

**In one sentence:** whoever ran the 20 November attack acted as if the older backdoor was not
there, including on routers it already controlled.

### The facts it rests on

All from the routers we manage. 49 of them carry the older backdoor
([loader](older-backdoor-loader.md), [second stage](older-backdoor-second-stage.md)); 47 of those
are among the 143 routers whose cloud-client memory we saved after the attack
([attacker messages](attacker-messages.md)).

**1. Nothing in the attack mentions the older backdoor.** We searched every attacker message, every
router reply and all the text recovered from the reverse shells (147 cloud-client images, 106
shell images) for the older backdoor's files, processes and servers: `ulogd`, `urandom_seed`,
`ujaild`, `monitord`, `keep.d` and its six domain names. There is no match in any of them. The same
search finds the strings we know are there (the implant's folder path over two thousand times), so
the search works. The commands that end the reverse shells stop the attacker's own programs and
nothing of the older backdoor's.

**2. The attack was sent to routers the older backdoor already controlled.** On those 47 routers
the older backdoor's second stage was running and checking in with its server, and it can run any
command. Its operator had no need of GoodCloud to reach them. Yet the cloud handler was called on
45 of the 47, as it was on all 96 routers without the backdoor.

| | Older backdoor present (47) | Absent (96) |
|---|---|---|
| Cloud handler called on 20 or 21 November | 45 | 96 |
| Reverse shell | 0 | 23 |

**3. The attacker chose by model and firmware, not by whether the backdoor was there.** The second
row above looks like a difference, and is not one. Every reverse shell was on a GL-AXT1800 on 4.8.2
or 4.8.3, or a GL-MT6000 on 4.9.1. None of the 49 backdoored routers runs one of those builds. The
calls came in batches by model and firmware ([attacker messages](attacker-messages.md#totals)).

**4. The two use different files, different servers and different tools.** The older backdoor is a
Lua loader and a Go program, with five server names for the first and three for the second. The attack of 20 November
used a shell one-liner to `170.39.226.219`, and on one router called the KVM implant's server
([attacker infrastructure](attacker-infrastructure.md)).

### What this makes more likely

That the two are separate operations: either two unrelated parties, or one party whose two efforts
had no shared list of devices. An operator who knew it already held a router would not have needed
to exploit that router again, and would more plausibly have used or at least checked what it had.

### What fits the opposite

- **A linked operator would not need to check.** Its own server already knows which routers report
  in. Silence about the backdoor fits "unrelated" and also fits "already knows".
- **One group, two teams or two toolchains,** would look the same from the router.
- **We see only what was still in memory** when each image was saved. A command that was sent and
  later overwritten would not appear.

### What we cannot explain

On 20 of the 47 backdoored routers no attacker message was left in the cloud client's memory,
against 3 of the 96 others, although the handler's state file shows it ran. We do not know why. It
may come from when or how those images were saved. Until that is understood, the number of routers
where the folder check was still in memory (27 of 47 against 85 of 96) should not be compared
between the two groups, and we do not use it above.

### What would settle it

GL.iNet's message logs. They would show who published to these routers in the minutes the older
backdoor's files were written, between September 2025 and May 2026, and whether that publisher is
the one that published on 20 November. We have asked GL.iNet for exactly that.

---

## Inference 2. The most common command was the attacker checking for its own implant

**In one sentence:** on most routers the only thing we recovered was a check for the "gl-helper"
implant on the router itself, and the answer was no.

### The facts it rests on

The command, found in memory on 98 routers, lists `/etc/config/.gl` and `/etc/glinet/.cache` and
sends the listing to the attacker ([attacker messages, C1](attacker-messages.md)). Those are the
implant's folders ([the implant](gl-helper-implant.md)). Wherever the output was still in memory
the folders were absent. The command writes nothing to the router. It does not look at the network
behind the router or for any other device.

The implant existed before 20 November: the installer forum users took apart is version 63 and
removes files left by older versions of itself, and one compromised KVM downloaded it on
19 November (both Reported, on the implant page).

### What this makes more likely

That the attacker was taking stock of its implant across every device it could reach, not looking
for KVMs and not, on most routers, doing anything else that we could recover.

### What it does not tell us

Why. Three readings fit the same listing, and we cannot choose between them:

- a look before a first install on routers;
- a check of an install that had been tried and had not worked on these models;
- a sorting step, to decide which devices to open a shell on.

An empty answer on every router we could read fits a first look better than a check-up, but it is
also what a failed install would leave.

### What this does not mean for an owner

It does not mean nothing was taken. The command ran as root, and the same channel could have
carried any command. A router that was sent this check should be treated as compromised
([If you find something](../README.md#if-you-find-something)).

### What would settle it

The same logs: any message in the attacker's form to these routers before 20 November.

---

## Inference 3. The attacker tried the flaw on a few devices on 19 November, before the main wave

*Added 24 November 2026.*

**In one sentence:** four calls on the morning of 19 November look like a trial run, about 36 hours
before the attack began in earnest.

### The facts it rests on

From GoodCloud's own Device Logs in our account
([the attack in GoodCloud's own log](goodcloud-device-log.md), findings R-37 and R-38), and from the
routers.

**1. Four devices answered `astrowarp` requests that GoodCloud did not send.**

| Time (UTC, 19 November) | Reply | `id` in the reply |
|---|---|---|
| 08:48:57 | empty `astrowarp` list | a long quoted string, the ordinary form |
| 08:49:05 | `virtual_ip_info` | a long quoted string |
| 08:49:12 | empty `astrowarp` list | a long quoted string |
| 09:33:36 | empty `astrowarp` list | the number `1`, the attacker's form |

**2. Nothing else like them exists in four days of log.** Of 1,035 `astrowarp` replies with an
ordinary `id` between 18 and 21 November, 1,032 have the request that caused them in the log.
These are the other three. In the three minutes either side of each of the four, the log holds
nothing for that device but its routine reports.

**3. Then nothing for 34 hours.** The next reply in the attacker's form, or without a logged
request, is at 20:06:29 on 20 November, the start of the main wave, after which 210 devices
answered in the attacker's form. In between, the log holds four replies of the same two shapes
(an empty `astrowarp` list, or `virtual_ip_info`), all on 20 November between 04:00 and 06:00.
Each has an ordinary `id` and its request beside it in the log, so they are GoodCloud's own
traffic: two answer the two `virtual_ip_info` messages GoodCloud itself sent in these four days
([the log page](goodcloud-device-log.md#what-ours-shows)), and two answer its
`connection_info` command. *Reworded 25 November 2026; the counts are unchanged.*

**4. The routers agree.** On three of the four devices the handler's state file was first written
within a second of the reply (the same second on two, one second earlier on the third). The fourth
is a device we have not examined. *Corrected 25 November 2026: this said "the same second" for
all three.*

**5. What we know of the three we examined.** They are three different models. Two run 4.7.0, the
oldest firmware line that has the flaw, and carry the older backdoor. The third is the one router
that was later sent a call to the KVM implant's server
([attacker messages, C8](attacker-messages.md)).

**6. The KVM side moved the same day** (Reported). The compromised KVM whose logs were published
made its first connection to the attacker at 02:35:56 UTC on 19 November and downloaded the
implant's installer a minute later ([the KVM implant](gl-helper-implant.md), finding K-15). That is
about six hours before the first router call above.

### What this makes more likely

That someone with the same access the attacker used on 20 November tried the handler on a handful
of devices a day and a half earlier: three calls within fifteen seconds whose `id` was made to
look like GoodCloud's own, then one call 44 minutes later with the plain `1` that every message of
the main wave carries. A trial, and a change of method between the first try and the second.

It also suggests the published start date is the date the attack was noticed, not the date it
began.

### What fits the opposite

- **The first three could be GoodCloud's own.** GoodCloud does send `virtual_ip_info` itself, and
  those three replies carry an ordinary `id`. Against that: every other such reply in the log has
  its request beside it, and these three have none.
- **A different party.** Nothing in the log names the sender. The three early calls and the fourth
  could come from different hands.
- **Not the first.** Our reading starts on 18 November. An earlier trial would not be in it.

### What it does not tell us

What was sent. The log holds the reply, not the request, and nothing from 19 November was left in
the routers' memory. And why those four devices: we see no common owner or network.

### What would settle it

GL.iNet's broker logs: who published to these four devices in those four minutes, from what
address, and whether the same publisher appears before 19 November.

---

## Inference 4. The older backdoor was a planned operation, and its operator had a way onto GoodCloud-bound routers more than a year before the attack

*Added 25 November 2026.*

**In one sentence:** the records show someone building and maintaining this over sixteen months,
which means someone had a working way in long before anyone else knew there was one.

### The facts it rests on

Registration and certificate records looked up by us (findings A-10, A-11), our own samples and
routers (R-18, R-28 to R-30), and the firmware history (R-5). Forum user rdizzie set out the
registration pattern, in [post 18](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/18)
and more fully in [post 50](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/50),
after acs posted the first dates in [post 2](https://forum.gl-inet.com/t/found-other-malware-while-looking-for-11-20-evidence/73097/2);
the dates below are from our own lookups and match theirs.

| Date | What happened | How we know |
|---|---|---|
| 5 December 2024 | The flaw first ships, in GL-MT3000 4.7.0 | Verified, R-5 |
| 4 July 2025 | Three names registered in just over eight minutes at two registrars; certificates the next day | Verified, A-10, A-11 |
| 18 and 19 August 2025 | A fourth name registered; fresh certificates for all four within fifteen minutes the next morning | Verified, A-10, A-11 |
| 15 September 2025 | The first install we hold, with the loader that uses those names | Verified, R-18 |
| 15 September to 7 December 2025 | Seven installs with that loader | Verified, from the routers |
| 8 December 2025 | Two more names registered 25 minutes apart. The second stage that uses them carries the build stamp `25120821`, which reads as 8 December 2025 | Verified for the registration and the stamp; the reading of the stamp as a date is ours |
| 9 December 2025 | The first install with the loader that uses the new names, a day later | Verified, from the routers |
| 9 December 2025 to 24 May 2026 | Forty-two installs with that loader, twenty-nine of them in December | Verified, from the routers |
| 27 June and 12 August 2026 | The names' registration records are changed again: two names one second apart on 27 June, three more within eight hours on 12 August. The records do not say what changed | Verified, A-10 |
| Up to 22 November 2026 | The second stage is still checking in on every router we examined | Verified, R-30 |

Two more facts about where it landed: 48 of the 49 routers were bound to GoodCloud before their
install date, and most have no public address on the WAN side (R-18).

*Corrected 25 November 2026.* The table said thirty of the forty-two installs with the second
loader were in December. Thirty is the December count for all 49 (R-18): twenty-nine with the
second loader and one, on 7 December, with the first. The last row cited lookups that were not
yet on the findings page; they are now in A-10. The first point below said "three pairs of name
servers" as a sign of planning and "renewed a year later"; a name-server pair does not identify
an account ([attacker infrastructure](attacker-infrastructure.md#servers-of-the-older-backdoor)),
and the records show that five of the six were changed in June and August 2026, not what the
change was. The first table row said "within eight minutes"; the three registrations run a
second over that. The credit line above named post 50 as the first account of the pattern; it is
the fuller, later one.

### What this makes more likely

- **It was planned and kept up.** Names bought in sets at three registrars, their records
  changed again in sets in June and August 2026, a second build prepared the day the new names
  were registered, and installs starting the day after. This is an operation with a schedule,
  not something opportunistic.
- **Its operator had a way in by September 2025 at the latest.** Routers with no public address,
  on unrelated networks, were reached in batches of minutes. Whatever the way in was, it worked
  from outside, at scale, fourteen months before the attack of November 2026.
- **The names were ready ten weeks before the first install.** That is preparation ahead of use.
- **So the weakness that made this possible was known to someone from mid-2025.** If the way in
  was GoodCloud, as the binding dates suggest, then the flaw GL.iNet fixed on 22 November 2026 had
  been in use, quietly, for over a year.

### What fits the opposite

- **We have not shown the way in.** The binding dates and the missing public addresses point at
  GoodCloud. They do not prove it. Another route common to these routers would give the same
  picture, and GL.iNet's notice says the entry path is not established.
- **"Planned" does not mean "planned around this flaw".** The names and the builds show
  preparation of the backdoor's own servers. They say nothing directly about which weakness was
  to be used.
- **Our 49 are what we found, not the campaign.** Other owners report installs with other dates.
  The first install anywhere may be earlier than ours.

### How it sits with inference 1

Inference 1 says the attack of 20 November and this backdoor look like two operations that did
not share information. This inference does not change that. It says the older one was patient
and well prepared; the November attack was loud, used two fixed addresses and a look-alike name
registered four days earlier, and was noticed within a day. If both used the same flaw, then two
different parties found it, a year apart.

### What would settle it

GL.iNet's logs for the install windows. We have sent the 49 devices and times. If GoodCloud's
logs no longer reach back that far, the cloud's own account and credential records for
mid-2025 may: when the access that made outside publishing possible first existed.

---

## How this page is kept

An inference is removed or rewritten when a fact settles it, with a dated note saying which fact.
If you can add a fact for or against one of these, see [CONTRIBUTING.md](../CONTRIBUTING.md).
