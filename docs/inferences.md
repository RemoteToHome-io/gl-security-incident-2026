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

## How this page is kept

An inference is removed or rewritten when a fact settles it, with a dated note saying which fact.
If you can add a fact for or against one of these, see [CONTRIBUTING.md](../CONTRIBUTING.md).
