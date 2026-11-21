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

Working instructions for attacking a device: the cloud message that triggers the router-side
weakness, proof-of-concept payloads, or scans of other people's devices. Send those to
security@gl-inet.com. Reports that contain them will be edited.

## How

Open an issue with the "Finding" form, or send a pull request that adds a row to
[docs/findings.md](docs/findings.md). Rows carry one of four labels: GL statement, Verified,
Reported, Unconfirmed. If you did not check it yourself, it is Reported.

The README is reviewed whenever GL.iNet updates its notice and whenever a finding changes the
advice. Each review updates the "Last reviewed" line.
