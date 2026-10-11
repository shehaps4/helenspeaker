#!/bin/sh
# ==============================================================================
# Smaati OS - Unified Mode Switcher (AI Assistant <-> Bluetooth Speaker)
# ==============================================================================

OS_DIR="/usr/data/iraqi_os"
MODE_FILE="/tmp/speaker_current_mode"
LED_DEV="/sys/class/leds/aw2015"

target="$1"
if [ -z "$target" ] || [ "$target" = "TOGGLE" ]; then
    cur=$(cat "$MODE_FILE" 2>/dev/null || echo "AI")
    if [ "$cur" = "AI" ]; then
        target="BT"
    else
        target="AI"
    fi
fi

silent_flag="$2"
play_sound() {
    [ "$silent_flag" = "--silent" ] && return
    snd="$1"
    if [ -f "$OS_DIR/${snd}.wav" ]; then
        mplayer -volume 100 "$OS_DIR/${snd}.wav" >/dev/null 2>&1 &
    elif [ -f "$OS_DIR/${snd}.mp3" ]; then
        mplayer -volume 100 "$OS_DIR/${snd}.mp3" >/dev/null 2>&1 &
    fi
}

case "$target" in
    BT|bt|Bluetooth|bluetooth)
        # ------------------------------------------------------------------
        # SWITCH TO BLUETOOTH MODE:
        # Bluetooth turns ON, piscan, starts bluealsa-aplay, auto reconnects
        # ------------------------------------------------------------------
        killall -9 mplayer 2>/dev/null
        hciconfig hci0 up >/dev/null 2>&1
        hciconfig hci0 name 'Smaati_سماعتي' >/dev/null 2>&1
        hciconfig hci0 piscan >/dev/null 2>&1
        
        killall -9 bluealsa-aplay 2>/dev/null
        bluealsa-aplay 00:00:00:00:00:00 >/dev/null 2>&1 &
        
        echo "BT" > "$MODE_FILE"
        echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null
        echo "0 50 255" > ${LED_DEV}/color_blink 2>/dev/null
        
        play_sound "mode_bt"
        
        # Auto-reconnect to paired phone(s)
        for dev in /var/lib/bluetooth/70:4F:08:00:84:C8/*:*; do
            if [ -d "$dev" ]; then
                mac=$(basename "$dev")
                [ "$mac" = "cache" ] && continue
                printf "power on\nconnect %s\nquit\n" "$mac" | bluetoothctl >/dev/null 2>&1 &
                hcitool cc "$mac" >/dev/null 2>&1 &
            fi
        done
        echo "BT"
        ;;

    *)
        # ------------------------------------------------------------------
        # SWITCH TO IRAQI ASSISTANT MODE:
        # Bluetooth turns OFF completely (hciconfig hci0 down), Cyan RGB
        # ------------------------------------------------------------------
        killall -9 bluealsa-aplay 2>/dev/null
        hciconfig hci0 down >/dev/null 2>&1
        
        echo "AI" > "$MODE_FILE"
        echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null
        echo "0 220 255" > ${LED_DEV}/color_blink 2>/dev/null
        
        killall -9 mplayer 2>/dev/null
        play_sound "mode_ai"
        echo "AI"
        ;;
esac
