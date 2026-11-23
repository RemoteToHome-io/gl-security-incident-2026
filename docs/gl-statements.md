# GL.iNet's statements over time

A running record of what GL.iNet has said in public about this incident, and how it changed.
When GL.iNet changes its wording, the earlier statement stays here with its date.

The main source is GL.iNet's
[security notice](https://forum.gl-inet.com/t/2026-11-20-gl-inet-security-notice-goodcloud-kvm-routers/73056),
the first post of that forum topic. The forum shows when a post was last edited but does not
show earlier versions to the public, so this record rests on the copies we saved. Each entry
gives the forum's edit time of the version and when we saved it. The entries are our summaries;
short passages in quotation marks are GL.iNet's words. We hold the full text of each version.

The post was created on 21 November 2026 at 07:57 UTC and had been edited three times before
our first copy. We do not have those first three versions.

## At a glance

| Subject | 21 Nov, 10:35 UTC | 21 Nov, 14:10 UTC | 21 Nov, 16:00 UTC | 23 Nov, 01:53 UTC |
|---|---|---|---|---|
| What owners should do | Factory reset every router and KVM, set it up again, install the firmware when released | Advice removed; two links to "quickly check" topics | Check for one process; if found, KVM beta firmware or factory reset; if not found, nothing | Install the security firmware; settings can be kept; no factory reset needed |
| Factory reset | Recommended for all router and KVM users | Not mentioned | An option if the indicator is found; not needed otherwise | Not required, also when the indicator is found |
| How to tell if a device was hit | Contact support | Two forum topics | One indicator: a process containing `crond -i /tmp/.log` | The same indicator, and an admission that the official checks may miss affected devices |
| What GL.iNet did on devices | "Implemented corrective measures … on affected devices" | The same sentence | Sentence gone | Not mentioned |
| Does blocking the attack clean a device | Not addressed | Not addressed | No: blocking does not remove malware already installed | No; the firmware is said to remove it |
| Fixed firmware | Being prepared | Being prepared | KVM beta now; stable for routers and KVMs on 22 November | Stable for 18 router models and 7 KVM models, with minimum versions |
| Community script | Not mentioned | Not mentioned | Not mentioned | Linked as an optional, unofficial check, with a disclaimer |

## Version edited 21 November 2026, 10:35 UTC

Saved by us at 12:53 UTC that day. Its own header reads "Last updated November 21, 2026, 04:25 UTC".

- A vulnerability in the cloud remote management services was exploited to install malicious
  software on "a subset" of routers and KVM devices.
- Under "What we have done": the vulnerability in the cloud services was closed; corrective
  measures were implemented "on affected devices"; an investigation was under way.
- Under "What we will do next": a firmware update "as soon as possible"; an individual email to
  everyone affected; investigation of the scope, including computers connected to affected
  KVMs.
- Not sure if your device was affected: contact support.
- **Recommended for all KVM users:** factory reset, set the device up again, check the
  connected computer, install the updated firmware when released.
- **Recommended for all router users:** factory reset, set the router up again, install the
  updated firmware when released.
- No indicator, no check, no list of models.

## Version edited 21 November 2026, 14:10 UTC

Saved by us at 15:24 UTC that day. The header still reads "04:25 UTC".

- **The factory reset recommendation for routers and KVMs is gone.** The whole "What we
  recommend" section was removed.
- In its place, under a heading about whether a device was affected: links to two forum topics,
  "Quickly check if your router is under attack" and "Quickly check if your KVM is under
  attack".
- The rest is unchanged, including the sentence about corrective measures on affected devices.

## Version edited 21 November 2026, 16:00 UTC

Saved by us at 16:41 UTC that day, and again unchanged at 07:12 UTC on 22 November. The header
reads "Last updated November 21, 2026 (UTC)". This version was rewritten throughout.

- New: "The attack path has been blocked." Devices can no longer be newly infected through it.
  These measures do not remove malware from devices already infected.
- **The sentence about corrective measures implemented on affected devices is gone.**
- New: one indicator for routers and KVMs, the exact text `crond -i /tmp/.log` in a running
  process, with the four ways to look for it that are still in the notice.
- If the indicator is found: treat the device as infected. For a KVM, install the security beta
  firmware; or restore the device to factory settings. Install the stable firmware when
  available.
- **If the indicator is not found** and there is no other reason to suspect infection: no
  factory reset or other cleanup is needed.
- If a KVM is infected, check the connected computer.
- KVM beta firmware with fixes listed for seven models (1.10.2 beta, or 1.8.6 beta for the
  RMQ1). Stable firmware for routers and KVMs scheduled for 22 November 2026.
- Notification by email to the owners GL.iNet identifies as affected.

## Version edited 23 November 2026, 01:53 UTC

Saved by us at 02:38 UTC that day. The header reads "Last updated November 23, 2026 (UTC)".
This is the version summarised in the README under "What GL.iNet has said".

- New section: install the latest stable security firmware for your exact model, even if the
  checks find nothing.
- **New claim:** the security firmware removes the malware identified in this incident without
  a factory reset, and existing settings can be kept during the update.

  ![GL.iNet's security notice on its own site, 23 November 2026, with the sentence about keeping settings marked](images/gl-notice-2026-11-23-keep-settings.png)

  *The same passage on GL.iNet's own site
  ([gl-inet.com](https://www.gl-inet.com/en-us/blogs/blog/glinet-security-notice-2026-11-20)),
  screenshot taken on 23 November 2026, not later than 05:31 UTC. The red box is ours.*
- **If the indicator is found, the factory reset option is gone.** The instruction is now to
  install the security firmware, with settings kept; contact support if the indicator is still
  there afterwards or the model is not listed.
- New: minimum fixed versions for 18 router models and 7 KVM models, and the sentence that an
  unlisted model is not necessarily unaffected.
- **New admission:** further indicators have been identified, and the official quick checks
  "may not detect every affected device". The community script is linked as an optional,
  unofficial, more comprehensive check, with a disclaimer.
- Unchanged: the indicator and the four checks; "no factory reset or other cleanup is needed"
  when the indicator is not found; the email notifications; the continuing investigation.

## What the notice has not said in any version we hold

- Which firmware versions were affected, or since when.
- The time window of the attack, or how many devices were reached.
- What the malicious software does, or what it could read.
- That keys and passwords on an affected router or KVM should be replaced. (The 10:35 UTC
  version said to change the passwords of accounts used on a computer connected to a KVM if
  something suspicious was found on that computer. That sentence went with the rest of the
  recommendations at 14:10 UTC.)
- Anything about the older backdoor that owners reported in the forum from 21 November.

## How this record is kept

When the notice changes, we add the new version here with the forum's edit time and the time we
saved it, and mark what was added, changed and removed against the version before. Nothing is
taken out of this page. The README carries the current version and a short dated list of the
changes.
