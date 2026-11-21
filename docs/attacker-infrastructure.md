# The address the remote shells connected to

What is publicly known about `170.39.226.219`, the address in findings R-1 and R-2. Everything here
comes from public registries and public databases, looked up on 21 November 2026. Nobody connected
to the address to gather it. Times are UTC.

## What it is

| Item | Value | Source |
|---|---|---|
| Address | `170.39.226.219`, TCP, a different port for each affected router (42499, 43104 and 43149 seen so far) | Findings R-1, R-2 |
| Reverse DNS | `aa27e2db.ewr.customer.misaka.io` | DNS lookup |
| Network | `170.39.226.0/24`, registry name US-MISAKA-EWR02-1, inside `170.39.224.0/22` (MISAKA-ARIN-02) | ARIN registration data |
| Registered to | Misaka Network, Inc. | ARIN registration data |
| Customer named in the registry | None. No reassignment to a customer is recorded. | ARIN registration data |
| Routed by | AS917 (AS57695 until late 2024) | RIPEstat routing data |
| Earlier use | One passive-DNS record: `szlsntvpnxxx04.top` pointed here for about 13 hours on 22 January 2022 | AlienVault OTX |
| Reputation databases | No record in GreyNoise or Shodan InternetDB | Those services' public lookups |

## What that does and does not tell us

- The reverse DNS name follows the hosting provider's naming for customer servers, and other
  addresses in the same range have names of the same form. This looks like a server rented from the
  provider. It does not mean the provider is involved.
- The registry does not say who rented it. Only the provider knows that.
- "No record" in a reputation database means nobody had reported the address there. It is not a
  clean bill of health.
- The 2022 domain no longer resolves and may belong to an earlier user of the address.
- Not checked: AbuseIPDB, abuse.ch, Censys and VirusTotal, which need a login or blocked automated
  lookups.

## Abuse report

We sent an abuse report to the provider's published abuse contact on **21 November 2026 at 17:24
UTC**, copied to the provider's network operations contact and to GL.iNet. It gives the three known
connections with their ports and times, and asks the provider to stop the service on that address
and to preserve the server and its records for 19 to 22 November 2026. We will record any reply
here.

If your device connected to this address, you can report it too. The provider's abuse contact, as
published in the ARIN registry, is `abuse-arin@misaka.email` (email only). Include your connection's
port, the time it started in UTC, and your public IP address at the time so the provider can match
it in its own records.

## Blocking it

Dropping traffic to `170.39.226.0/24` is a reasonable stopgap, shown in the
[README](../README.md#reducing-exposure-until-fixed-firmware-is-installed). It only covers the one
address seen so far. Whether other addresses were used is an open question for GL.iNet.
