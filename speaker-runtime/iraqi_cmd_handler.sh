#!/bin/sh
# ==============================================================================
# Iraqi AI Smart Speaker OS - Command Dispatcher
# Invoked by BusyBox inetd on incoming TCP connections (Port 8443)
# ==============================================================================

OS_DIR="/usr/data/iraqi_os"
CONFIG_FILE="${OS_DIR}/config.json"
LED_DEV="/sys/class/leds/aw2015"
WPA_CONF="/usr/data/wpa_supplicant.conf"
MODE_FILE="/tmp/speaker_current_mode"

read -r line
cmd=$(echo "$line" | awk '{print $1}')
payload=$(echo "$line" | cut -d' ' -f2-)

case "$cmd" in
    DISCOVER|PING)
        cur_mode=$(cat $MODE_FILE 2>/dev/null || echo "AI")
        wlan_ip=$(ifconfig wlan0 2>/dev/null | grep 'inet addr:' | cut -d: -f2 | awk '{print $1}')
        pairing=$(test -f /tmp/speaker_pairing_mode && echo "YES" || echo "NO")
        echo "SMAATI_SPEAKER_OK|NAME=سماعتي|IP=${wlan_ip:-NoIP}|MODE=${cur_mode}|PAIRING=${pairing}|PORT=8443"
        ;;

    STATUS)
        cur_mode=$(cat $MODE_FILE 2>/dev/null || echo "AI")
        wlan_ip=$(ifconfig wlan0 2>/dev/null | grep 'inet addr:' | cut -d: -f2 | awk '{print $1}')
        pairing=$(test -f /tmp/speaker_pairing_mode && echo "YES" || echo "NO")
        echo "IRAQI_OS_STATUS: Mode=${cur_mode} IP=${wlan_ip:-NoIP} Pairing=${pairing} Uptime=$(uptime | cut -d, -f1)"
        ;;

    GET_CONFIG)
        if [ -f "$CONFIG_FILE" ]; then
            cat "$CONFIG_FILE"
            echo ""
        else
            echo "ERR_NO_CONFIG"
        fi
        ;;

    SET_CONFIG)
        if [ -n "$payload" ]; then
            echo "$payload" > "$CONFIG_FILE"
            if [ -f "$OS_DIR/config_saved.mp3" ]; then
                mplayer -volume 100 "$OS_DIR/config_saved.mp3" >/dev/null 2>&1 &
            fi
            echo "CONFIG_SAVED_OK"
        else
            echo "ERR_EMPTY_CONFIG"
        fi
        ;;

    SET_WIFI)
        # SET_WIFI <ssid> <password>
        ssid=$(echo "$payload" | awk '{print $1}')
        psk=$(echo "$payload" | awk '{print $2}')

        if [ -n "$ssid" ]; then
            cat << WPA_EOF > "$WPA_CONF"
ctrl_interface=/var/run/wpa_supplicant
update_config=1
country=GB

network={
    ssid="$ssid"
    psk="$psk"
}
WPA_EOF
            wpa_cli -i wlan0 reconfigure >/dev/null 2>&1
            udhcpc -i wlan0 -b >/dev/null 2>&1 &
            if [ -f "$OS_DIR/wifi_ok.mp3" ]; then
                mplayer -volume 100 "$OS_DIR/wifi_ok.mp3" >/dev/null 2>&1 &
            fi
            echo "WIFI_CONFIGURED_OK"
        else
            echo "ERR_INVALID_SSID"
        fi
        ;;

    LED_STATE)
        # LED_STATE <LISTENING|THINKING|SPEAKING|ROMANCE|BT_MODE|IDLE>
        state=$(echo "$payload" | awk '{print $1}')
        case "$state" in
            LISTENING)
                echo 2 0 2 0 > ${LED_DEV}/led_time 2>/dev/null
                echo "r 0 g 220 b 255" > ${LED_DEV}/color_blink 2>/dev/null
                echo "LED_STATE_LISTENING"
                ;;
            THINKING)
                echo 1 0 1 0 > ${LED_DEV}/led_time 2>/dev/null
                echo "r 180 g 0 b 255" > ${LED_DEV}/color_blink 2>/dev/null
                echo "LED_STATE_THINKING"
                ;;
            SPEAKING)
                echo 2 0 2 1 > ${LED_DEV}/led_time 2>/dev/null
                echo "r 0 g 255 b 100" > ${LED_DEV}/color_blink 2>/dev/null
                echo "LED_STATE_SPEAKING"
                ;;
            ROMANCE)
                echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null
                echo "r 255 g 20 b 120" > ${LED_DEV}/color_blink 2>/dev/null
                echo "LED_STATE_ROMANCE"
                ;;
            BT_MODE)
                echo "r 0 g 50 b 255" > ${LED_DEV}/color_brightness 2>/dev/null
                echo "LED_STATE_BT"
                ;;
            IDLE)
                echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null
                echo "r 0 g 120 b 180" > ${LED_DEV}/color_blink 2>/dev/null
                echo "LED_STATE_IDLE"
                ;;
            *)
                echo "ERR_UNKNOWN_LED_STATE"
                ;;
        esac
        ;;

    LED_BLINK)
        r=$(echo "$payload" | awk '{print $1}')
        g=$(echo "$payload" | awk '{print $2}')
        b=$(echo "$payload" | awk '{print $3}')
        echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null
        echo "r ${r:-0} g ${g:-220} b ${b:-255}" > ${LED_DEV}/color_blink 2>/dev/null
        echo "LED_BLINK_SET"
        ;;

    LED)
        r=$(echo "$payload" | awk '{print $1}')
        g=$(echo "$payload" | awk '{print $2}')
        b=$(echo "$payload" | awk '{print $3}')
        echo "r ${r:-0} g ${g:-220} b ${b:-255}" > ${LED_DEV}/color_brightness 2>/dev/null
        echo "LED_SET"
        ;;

    VOL)
        v=$(echo "$payload" | awk '{print $1}')
        amixer sset Master ${v:-26} >/dev/null 2>&1
        echo "VOLUME_SET_${v}"
        ;;

    PLAY)
        if [ -n "$payload" ]; then
            killall -9 mplayer 2>/dev/null
            mplayer -volume 100 "$payload" >/dev/null 2>&1 &
            echo "PLAYING"
        else
            echo "ERR_NO_TARGET"
        fi
        ;;

    STOP)
        killall -9 mplayer 2>/dev/null
        echo "STOPPED"
        ;;

    RECORD)
        dur=$(echo "$payload" | awk '{print $1}')
        rm -f /tmp/rec.wav
        /usr/bin/mic_test -f /tmp/rec.wav -d ${dur:-5} >/dev/null 2>&1
        echo "RECORD_FINISHED"
        ;;

    BT_ENABLE)
        killall -9 mplayer 2>/dev/null
        echo "BT" > $MODE_FILE
        echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null
        echo "r 0 g 50 b 255" > ${LED_DEV}/color_blink 2>/dev/null
        if [ -f "$OS_DIR/mode_bt.mp3" ]; then
            mplayer -volume 100 "$OS_DIR/mode_bt.mp3" >/dev/null 2>&1
        fi
        bluealsa-aplay 00:00:00:00:00:00 >/dev/null 2>&1 &
        echo "BT_SPEAKER_ACTIVE"
        ;;

    BT_DISABLE)
        killall -9 bluealsa-aplay 2>/dev/null
        echo "AI" > $MODE_FILE
        echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null
        echo "r 0 g 220 b 255" > ${LED_DEV}/color_blink 2>/dev/null
        if [ -f "$OS_DIR/mode_ai.mp3" ]; then
            mplayer -volume 100 "$OS_DIR/mode_ai.mp3" >/dev/null 2>&1
        fi
        echo "AI_MODE_ACTIVE"
        ;;

    REBOOT)
        echo "REBOOTING_IRAQI_OS"
        reboot
        ;;

    *)
        echo "IRAQI_OS_UNKNOWN_COMMAND"
        ;;
esac

exit 0
