#!/bin/sh
# ==============================================================================
# Iraqi AI Smart Speaker - Native Embedded OS Daemon
# Runs permanently on Ingenic X1800 MIPS Linux (/usr/data/iraqi_os/)
# ==============================================================================

OS_DIR="/usr/data/iraqi_os"
LED_DEV="/sys/class/leds/aw2015"
CONF_FILE="${OS_DIR}/inetd.conf"
MODE_FILE="/tmp/speaker_current_mode"

echo "[+] Starting Iraqi AI Smart Speaker OS..."

# 1. Hardware Volume Setup (85% / Level 26)
amixer sset Master 26 >/dev/null 2>&1

# 2. RGB Initialization (Cyan breathing)
echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null
echo "r 0 g 220 b 255" > ${LED_DEV}/color_blink 2>/dev/null

# 3. Kill legacy Chinese daemons if running
killall -9 AudioMain 2>/dev/null
killall -9 storybook_daemon 2>/dev/null

# 4. Remove all old legacy MP3 files to prevent double boot sound
rm -f ${OS_DIR}/boot_greeting.mp3 ${OS_DIR}/greeting_iq.mp3 ${OS_DIR}/iraqi_boot_greeting.mp3 2>/dev/null

# 5. Set AI Mode silently (No duplicate sound on boot!)
killall -9 bluealsa-aplay 2>/dev/null
hciconfig hci0 down >/dev/null 2>&1
echo "AI" > $MODE_FILE

# 6. Set Fast Router IP Alias (10.0.0.1) on active interfaces
ifconfig wlan0:0 10.0.0.1 netmask 255.0.0.0 up 2>/dev/null
ifconfig wlan1:0 10.0.0.1 netmask 255.0.0.0 up 2>/dev/null

# 7. Wi-Fi SoftAP Setup (SSID: Smaati_Setup, IP: 192.168.1.1 & 10.0.0.1)
if [ -x "${OS_DIR}/wifi_ap_mode_start.sh" ]; then
    ${OS_DIR}/wifi_ap_mode_start.sh >/dev/null 2>&1 &
fi

# 8. Play Single, Crisp, Short Gemini Live Boot Greeting ("يا هلا بيك عيوني، اني هيلين ومساعدتك الذكية جاهزة، أمرني وتدلل!")
if [ -f "${OS_DIR}/boot_greeting.wav" ]; then
    killall -9 mplayer 2>/dev/null
    mplayer -volume 100 ${OS_DIR}/boot_greeting.wav >/dev/null 2>&1 &
fi

# 9. Launch Hardware Button Watcher
killall -9 key_test 2>/dev/null
killall -9 iraqi_button_watcher.sh 2>/dev/null
if [ -x "${OS_DIR}/iraqi_button_watcher.sh" ]; then
    ${OS_DIR}/iraqi_button_watcher.sh >/tmp/watcher.log 2>&1 &
fi

# 10. Launch Native Socket Super-Server via BusyBox inetd
killall -9 inetd 2>/dev/null
busybox inetd ${CONF_FILE}

echo "[+] Iraqi OS Ready. Access router dashboard at http://10.0.0.1/ or http://192.168.1.1/"
