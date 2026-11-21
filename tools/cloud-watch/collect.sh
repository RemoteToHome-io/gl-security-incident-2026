# Read-only collector, run on the watched device by watch.sh (ssh ... sh -s < collect.sh).
# Writes nothing on the device. Works on GL KVM (buildroot) and GL routers (BusyBox ash).
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
netstat -ntp 2>/dev/null | awk 'NR>2 {print $4, $5, $6, $7}'
echo "===FILES==="
for f in /tmp/f /tmp/.log /etc/glinet/.cache /etc/config/.gl /etc/rc.local /usr/bin/netstat \
	/etc/kvmd/user/scripts /root/.ssh /etc/dropbear /etc/shadow /etc/crontabs /etc/rtty_conf; do
	ls -la "$f" 2>/dev/null
done
for f in /etc/crontabs/*; do [ -f "$f" ] && grep -v '^[[:space:]]*#' "$f" | grep '[^[:space:]]' | sed "s#^#CRON $f: #"; done
echo "===END==="
