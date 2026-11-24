# Contributing

This page exists so findings do not get buried in forum threads. Add yours, or correct ours.

## What helps most

- Output from a device that was hit: the process lines, the connection, the start time.
- A firmware version checked for a fix or for the unchecked code, with how you checked.
- A correction, with the evidence that shows the current text is wrong.
- A clean result from a model or firmware nobody has reported yet, with the checks you ran.

## What every report needs

1. Device model and firmware version, and whether GL.iNet's cloud service was on.
2. The exact command you ran and what it printed.
3. The time in UTC, and whether the device has been rebooted since 20 November 2026.
4. How sure you are: seen yourself, or passed on from someone else.

## Remove before you post

Public and private IP addresses of your own network, hostnames, Wi-Fi names, MAC addresses,
device ids and serial numbers, DDNS names, account e-mail addresses, and anything from a
configuration file. Never attach an evidence archive or a configuration backup: they contain keys
and passwords. The attacker's address and port are fine to post.

## What will not be merged

*Changed 24 November 2026.* GL.iNet has released fixed firmware and published the cause, so this
page now carries full technical detail: the attacker's messages word for word, the malware taken
apart, and the weaknesses the fix leaves open. Findings of that kind are welcome, including
commands and messages recovered from your own device.

Three things are still not merged:

- **The one weakness we are withholding.** A further weakness in the cloud client is not
  addressed by the fixed firmware. We reported it to GL.iNet and said we would hold it back until
  it is fixed (see [What is deliberately not published here](README.md#what-is-deliberately-not-published-here)).
  If your report touches it, we will tell you and take that part out before merging. Please send
  it to GL.iNet as well.
- **Anything that identifies an owner or a device,** yours or anyone else's: see the list above.
- **Scans of, or access to, devices that are not yours.**

Malware files themselves do not go in the repository. Post the SHA-256 and where you found the
file, and say that you hold a copy; a researcher who needs it can ask you.

## How

Open an issue with the "Finding" form, or send a pull request that adds a row to
[docs/findings.md](docs/findings.md). Rows carry one of four labels: GL statement, Verified,
Reported, Unconfirmed. If you did not check it yourself, it is Reported.

The README is reviewed whenever GL.iNet updates its notice and whenever a finding changes the
advice. Each review updates the "Last reviewed" line.
