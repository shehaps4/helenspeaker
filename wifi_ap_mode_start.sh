#!/bin/sh
# ==============================================================================
# Smaati OS - High-Performance SoftAP Manager with 10.0.0.1 Primary Native IP
# ==============================================================================

# 1. Primary Network Interface Configuration (10.0.0.1)
ifconfig wlan1 10.0.0.1 netmask 255.255.255.0 up 2>/dev/null
# Keep 192.168.1.1 as secondary alias for backward compatibility
ifconfig wlan1:0 192.168.1.1 netmask 255.255.255.0 up 2>/dev/null

# 2. Start HostAP daemon (SSID: Smaati_Setup)
if ! pgrep hostapd >/dev/null; then
    killall -9 hostapd 2>/dev/null
    hostapd -B /usr/data/hostapd.conf
fi

# 3. Start High-Performance DNS & DHCP Server (Subnet 10.0.0.0/24 with Captive Portal)
killall -9 dnsmasq 2>/dev/null
sleep 0.5
dnsmasq -i wlan1 \
    --dhcp-range=10.0.0.10,10.0.0.100,255.255.255.0,12h \
    --dhcp-option=3,10.0.0.1 \
    --dhcp-option=6,10.0.0.1 \
    --address=/#/10.0.0.1 \
    --address=/smaati/10.0.0.1 \
    --address=/helen/10.0.0.1

echo "[+] Smaati SoftAP active on 10.0.0.1 (DHCP Range: 10.0.0.10 - 10.0.0.100)"
