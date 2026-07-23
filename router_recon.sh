cat > /tmp/router_recon.sh << 'EOF'
#!/bin/sh

cd /tmp || exit 1

OUT="/tmp/router_recon_$(date +%Y%m%d_%H%M%S)"

mkdir -p "$OUT"

collect()
{
    FILE="$1"
    TITLE="$2"
    CMD="$3"

    echo "============================" >> "$OUT/$FILE"
    echo "$TITLE" >> "$OUT/$FILE"
    echo "============================" >> "$OUT/$FILE"

    sh -c "$CMD" >> "$OUT/$FILE" 2>&1

    echo "" >> "$OUT/$FILE"
}


echo "[+] Router Recon"
echo "[+] Output: $OUT"


# ==========================
# SYSTEM INFORMATION
# ==========================

collect system.txt "IDENTITY" "
id
cat /proc/sys/kernel/hostname
uname -a
cat /proc/version
cat /proc/cpuinfo
cat /proc/cmdline
env
"

# ==========================
# DEVICES / STORAGE / MOUNTS
# ==========================

collect storage_devices_mounts.txt "MOUNTS" "
mount
df -h
cat /proc/mtd
cat /proc/devices
ls -la /dev
"

# ==========================
# PROCESSES / SERVICES
# ==========================

collect processes_services.txt "PROCESSES" "
ps
echo
echo '--- Interesting Services ---'
ps | grep -E 'http|web|ftp|bftpd|upnp|dns|dhcp'
"

# ==========================
# NETWORK
# ==========================

collect network.txt "NETWORK" "
ifconfig -a
echo
route -n
echo
cat /proc/net/route
echo
cat /proc/net/tcp
echo
netstat -ln
"

# ==========================
# WEB / WWW
# ==========================

collect web_www.txt "WEB FILESYSTEM" "
find /www -type f
echo
ls -la /www
echo
ls -la /www/cgi-bin
"

# ==========================
# MEMORY / SECURITY
# ==========================

collect memory_security.txt "MEMORY SECURITY" "
cat /proc/sys/kernel/randomize_va_space
cat /proc/self/maps
"


echo "[+] Complete"
echo "[+] Report:"
echo "$OUT"

EOF


