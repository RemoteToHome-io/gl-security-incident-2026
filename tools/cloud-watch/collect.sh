# Read-only collector, run on the watched device by watch.sh (ssh ... sh -s < collect.sh).
# Writes nothing on the device. Works on GL KVM (buildroot) and GL routers (BusyBox ash).
# GL.iNet staff report that the implant replaces netstat and that running the replacement starts the
# malware. Only call netstat when it resolves to a binary identical to the copy in the read-only image.
netstat_is_stock() {
	w=$(command -v netstat 2>/dev/null) || return 1
	t=$(readlink -f "$w" 2>/dev/null); [ -n "$t" ] || return 1
	[ -f "/rom$t" ] || return 1
	[ "$(md5sum "$t" 2>/dev/null | cut -d' ' -f1)" = "$(md5sum "/rom$t" 2>/dev/null | cut -d' ' -f1)" ]
}
echo "===META==="
date -u +%FT%TZ
cut -d' ' -f1 /proc/uptime
[ -f /etc/version ] && grep '^RK_VERSION=' /etc/version
[ -f /etc/glversion ] && cat /etc/glversion
echo "===LOG==="
logread 2>/dev/null
echo "===PROC==="
for d in /proc/[0-9]*; do
	p=${d#/proc/}
	[ "$p" = "$$" ] && continue
	c=$(tr '\0' ' ' < "$d/cmdline" 2>/dev/null)
	[ -n "$c" ] && echo "$c"
done
echo "===NET==="
if netstat_is_stock; then
	netstat -ntp 2>/dev/null | awk 'NR>2 {print $4, $5, $6, $7}'
fi
echo "===FILES==="
netstat_is_stock || echo "NETSTAT-NOT-STOCK: netstat is missing or differs from the read-only image; not run"
for f in /etc/udhcpc.user.d/* /lib/upgrade/keep.d/netifd /etc/init.d/urandom_seed; do
	[ -e "$f" ] && echo "$(md5sum "$f" 2>/dev/null | cut -d' ' -f1) $f"
done
for f in /tmp/f /tmp/.log /etc/glinet/.cache /etc/config/.gl /etc/rc.local /usr/bin/netstat \
	/etc/kvmd/user/scripts /root/.ssh /etc/dropbear /etc/shadow /etc/crontabs /etc/rtty_conf; do
	ls -la "$f" 2>/dev/null
done
for f in /etc/crontabs/*; do [ -f "$f" ] && grep -v '^[[:space:]]*#' "$f" | grep '[^[:space:]]' | sed "s#^#CRON $f: #"; done
echo "===END==="
