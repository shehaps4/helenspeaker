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
echo "AI" > $MODE_FILE

# 1. Hardware Volume Setup (85% / Level 26)
amixer sset Master 26 >/dev/null 2>&1

# 2. RGB Initialization (Cyan breathing)
echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null
echo "r 0 g 220 b 255" > ${LED_DEV}/color_blink 2>/dev/null

# 3. Kill legacy Chinese daemons if running
killall -9 AudioMain 2>/dev/null
killall -9 storybook_daemon 2>/dev/null

# 3.1 Setup Bluetooth Name & Discoverability (سماعتي)
hciconfig hci0 name 'Smaati_سماعتي' >/dev/null 2>&1
hciconfig hci0 piscan >/dev/null 2>&1

# 4. Play Native Boot Greeting in background
if [ -f "${OS_DIR}/boot_greeting.mp3" ]; then
    mplayer -volume 100 ${OS_DIR}/boot_greeting.mp3 >/dev/null 2>&1 &
fi

# 5. Launch Hardware Button Watcher with setsid (detached daemon)
killall -9 key_test 2>/dev/null
killall -9 iraqi_button_watcher.sh 2>/dev/null
if [ -x "${OS_DIR}/iraqi_button_watcher.sh" ]; then
    setsid ${OS_DIR}/iraqi_button_watcher.sh </dev/null >/tmp/watcher.log 2>&1 &
fi

# 6. Launch Native Socket Super-Server via BusyBox inetd
killall -9 inetd 2>/dev/null
busybox inetd ${CONF_FILE}

echo "[+] Iraqi OS Ready. Super-Server listening on port 8443."
