# The address the remote shells connected to

What is publicly known about `170.39.226.219`, the address in findings R-1 and R-2. Everything here
comes from public registries and public databases, looked up on 21 November 2026, and one outside
reachability test on 22 November. We did not connect to the address ourselves. Times are UTC.

## What it is

| Item | Value | Source |
|---|---|---|
| Address | `170.39.226.219`, TCP, a different port for each affected router (41221, 41297, 42499, 43104 and 43149 among those seen) | Findings R-1, R-2, R-13 |
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
and to preserve the server and its records for 19 to 22 November 2026.

**The provider replied on 21 November 2026 at about 20:54 UTC** (Provider statement):

- it has suspended the server and notified its customer;
- the data has been preserved under its standard abuse process;
- it has no network flow records for that site;
- it will give further details only on a subpoena or similar legal request.

On 22 November at 07:21 UTC we asked a public test service to try the address from 20 points
around the world: ping, and TCP to three ports including two the attack used. None got an
answer; every attempt timed out or was rejected as unreachable. That agrees with the provider's
statement. It does not show since when.

So the known address should no longer accept these connections, and the evidence on it is held
for an investigation by GL.iNet or law enforcement. A shell that is still running on a router
keeps trying to reconnect until it is stopped or the router restarts, and the attacker may use
another address.

If your device connected to this address, you can report it too. The provider's abuse contact, as
published in the ARIN registry, is `abuse-arin@misaka.email` (email only). Include your connection's
port, the time it started in UTC, and your public IP address at the time so the provider can match
it in its own records.

## Blocking it

Dropping traffic to `170.39.226.0/24` is a reasonable stopgap, shown in the
[README](../README.md#reducing-exposure-until-fixed-firmware-is-installed). It only covers the
address the router shells used.

## Other addresses, reported

Two more addresses are reported for the KVM side of the attack: `66.245.219.252` and
`65.20.71.131`, from the network logs of a compromised GL-RM1 and from the installer script it
downloaded on 19 November ([BleepingComputer, 22 November 2026](https://www.bleepingcomputer.com/news/security/hackers-exploit-glinet-cloud-flaw-to-infect-routers-kvm-devices/)). *Corrected 23 November 2026:* this page said we had not seen either on a router. We have now
found the first of them in the saved memory of one router's cloud client, inside a command sent
through GL.iNet's cloud: `http://66.245.219.252:8899/wake?m=KK_<id>` (finding A-6). Forum users
report the KVM implant calls the same server, port and path. The second address,
`65.20.71.131`, is in none of the 255 memory images we hold.

## Servers of the older backdoor

Separate from the above. Read from our own samples on 23 November 2026 (findings R-28 to R-30):

| Name | Used by | Path |
|---|---|---|
| `cdn.adguardns.com`, `cdn.adguardns.org` | the loader, 33,722-byte build (42 of 49 routers) | `/v1/gl/access`, downloads from `/v1/gl/download` |
| `cdn.lede-openproject.org`, `cdn.adxinsight.com`, `cdn.openwrt-project.org` | the loader, 35,745-byte build (7 of 49) | the same |
| `up.adguardns.com`, `up.adguardns.org` | the second stage, build on 42 routers | `/v1/gl/instance` |
| `up.adsanalypro.com` | the second stage, build on 7 routers | `/v1/gl/instance` |

All are reached over HTTPS. The names imitate AdGuard, OpenWrt and an advertising service; nothing
we have links them to those. If your DNS resolver keeps a query log, look for these names: a device that
asks for one of them should be checked at once. Blocking them stops the loader from fetching the
second stage; it does not remove anything.
