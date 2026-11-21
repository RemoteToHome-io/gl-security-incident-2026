#!/bin/bash
# watch.sh — poll one GL device and keep a record of what its cloud client receives and what runs.
# Usage: watch.sh <host> <state-dir> [interval-seconds]
# Read-only on the device, with one exception: if the cloud client restarted and fell back to its
# default log level, the watcher sets debug level again (ubus call gl-cloud set_log_level 7), which
# is a runtime setting. Stop it by creating <state-dir>/STOP.
# Test mode: WATCH_TEST_FILE=<canned collector output> makes one pass without ssh.
set -u
H=$1; W=$2; I=${3:-60}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$W"
touch "$W/log-all.txt" "$W/seen-proc.txt" "$W/seen-net.txt" "$W/files-last.txt" "$W/events.log" "$W/alerts.log"
SSH="ssh -o ControlPath=none -o BatchMode=yes -o ConnectTimeout=8"
MASK='s/[A-Za-z0-9+\/=_-]{40,}/<masked>/g'
# Known attack shapes: GL's published process, the AXT1800 reverse shell, the KVM implant name,
# and shell metacharacters inside a cloud payload.
BAD_PROC='crond -i|/tmp/\.log|mkfifo|(^| |\|)nc [0-9]|(^|/)(sh|ash|bash) -i( |$)|170\.39\.226\.|gl-helper'
BAD_MSG='payload: .*(;[ ]*\(|;[ ]*(sh|bash|ash|nc|wget|curl|rm|mkfifo|cat|echo|while|iptables|chmod|cd) |\$\(|`|&&|\|\||\|[ ]*(/bin/|sh|nc|bash)|mkfifo|/bin/sh|nc [0-9]|>[ ]*/dev/null|>[ ]*/tmp/)'

ev() { echo "$(date -u +%FT%TZ) $*" >> "$W/events.log"; }
alert() {
	echo "$(date -u +%FT%TZ) $*" >> "$W/alerts.log"; ev "ALERT $*"
	command -v notify-send >/dev/null 2>&1 && notify-send -u critical "GL watch $H" "$(echo "$*" | cut -c1-200)" 2>/dev/null
	return 0
}
section() { awk -v s="===$1===" '$0==s{f=1;next} /^===[A-Z]+===$/{f=0} f' "$W/last-raw.txt"; }

LASTUP=0
pass() {
	if [ -n "${WATCH_TEST_FILE:-}" ]; then cat "$WATCH_TEST_FILE" > "$W/last-raw.tmp"; rc=0
	else timeout 50 $SSH "root@$H" sh -s < "$HERE/collect.sh" > "$W/last-raw.tmp" 2>&1; rc=$?
	fi
	if [ "$rc" != 0 ] || ! grep -q '^===END===$' "$W/last-raw.tmp"; then
		ev "POLL-FAIL rc=$rc $(tail -1 "$W/last-raw.tmp" | cut -c1-120)"; return 1
	fi
	sed -E "$MASK" "$W/last-raw.tmp" > "$W/last-raw.txt"; rm -f "$W/last-raw.tmp"

	up=$(section META | sed -n 2p | cut -d. -f1)
	if [ -n "$up" ] && [ "$LASTUP" != 0 ] && [ "$up" -lt "$LASTUP" ]; then alert "REBOOT detected (uptime $LASTUP s -> $up s); RAM log before it is lost beyond what was saved"; fi
	LASTUP=${up:-0}

	section LOG | grep -vxFf "$W/log-all.txt" > "$W/new-log.txt"
	if [ -s "$W/new-log.txt" ]; then
		cat "$W/new-log.txt" >> "$W/log-all.txt"
		grep 'gl-cloud' "$W/new-log.txt" | while IFS= read -r l; do ev "CLOUD $l"; done
		grep -E "$BAD_MSG" "$W/new-log.txt" | while IFS= read -r l; do alert "cloud message with shell characters: $(echo "$l" | cut -c1-400)"; done
		grep -E "$BAD_PROC" "$W/new-log.txt" | grep -v 'gl-cloud' | while IFS= read -r l; do alert "log line matches an attack pattern: $(echo "$l" | cut -c1-300)"; done
	fi

	section PROC | sort -u | grep -vxFf "$W/seen-proc.txt" > "$W/new-proc.txt"
	if [ -s "$W/new-proc.txt" ]; then
		cat "$W/new-proc.txt" >> "$W/seen-proc.txt"
		while IFS= read -r l; do ev "NEWPROC $(echo "$l" | cut -c1-300)"; done < "$W/new-proc.txt"
		grep -E "$BAD_PROC" "$W/new-proc.txt" | while IFS= read -r l; do alert "process matches an attack pattern: $(echo "$l" | cut -c1-400)"; done
	fi

	section NET | awk '{sub(/:[0-9]+$/,"",$1); print $2, $3, $4}' | sort -u | grep -vxFf "$W/seen-net.txt" > "$W/new-net.txt"
	if [ -s "$W/new-net.txt" ]; then
		cat "$W/new-net.txt" >> "$W/seen-net.txt"
		while IFS= read -r l; do ev "NEWCONN $l"; done < "$W/new-net.txt"
		grep -E '170\.39\.226\.' "$W/new-net.txt" | while IFS= read -r l; do alert "connection to the known attacker network: $l"; done
	fi

	section FILES > "$W/files-now.txt"
	if [ -s "$W/files-last.txt" ] && ! cmp -s "$W/files-now.txt" "$W/files-last.txt"; then
		diff "$W/files-last.txt" "$W/files-now.txt" | grep '^[<>]' | while IFS= read -r l; do alert "watched file or directory changed: $(echo "$l" | cut -c1-250)"; done
	fi
	cp "$W/files-now.txt" "$W/files-last.txt"

	# Cloud client restarted since debug was last set? Then set it again (runtime setting only).
	if [ -z "${WATCH_TEST_FILE:-}" ]; then
		a=$(grep -n 'gl-cloud.*lua-eco version' "$W/log-all.txt" | tail -1 | cut -d: -f1)
		b=$(grep -n 'gl-cloud.*set logevel = 7' "$W/log-all.txt" | tail -1 | cut -d: -f1)
		if [ -n "$a" ] && [ "${b:-0}" -lt "$a" ]; then
			timeout 20 $SSH "root@$H" 'ubus call gl-cloud set_log_level "{\"level\":7}"' >/dev/null 2>&1 && ev "DEBUG-LEVEL re-set after a cloud client restart" || ev "DEBUG-LEVEL re-set FAILED"
		fi
	fi
	date -u +%FT%TZ > "$W/heartbeat"
	return 0
}

if [ -n "${WATCH_TEST_FILE:-}" ]; then pass; exit $?; fi
ev "START watching $H every ${I}s (pid $$)"
echo $$ > "$W/watch.pid"
while [ ! -e "$W/STOP" ]; do
	pass
	for _ in $(seq "$I"); do [ -e "$W/STOP" ] && break; read -r -t 1 _x < /dev/null 2>/dev/null || sleep 1; done
done
ev "STOP file found, watcher exiting"
rm -f "$W/watch.pid"
