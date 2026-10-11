#!/bin/sh
# ==============================================================================
# Iraqi AI Smart Speaker OS - Exact Hardware Button Manager
# Verified and calibrated via Live Hardware Identification:
#
# Hardware Keys:
#  - 105: Volume Up (زر رفع الصوت +)
#         * Single tap: Volume +2 (plays beep.wav at 100%)
#         * Long press: Continuously ramp volume up to 100% and play beep.wav
#         * 3 clicks within 2s: Trigger Pairing / Discovery Mode
#
#  - 108: Volume Down (زر خفض الصوت -)
#         * Single tap: Volume -2 (plays beep.wav at 0%)
#         * Long press: Continuously ramp volume down to 0% and play beep.wav
#
#  - 103: Mic Button (زر المايك 🎙️)
#         * Long press (> 2s): Switch Mode:
#           - AI -> BT: "تم التحويل لوضع البلوتوث" (mode_bt.mp3) + Blue LED
#           - BT -> AI: "تم التحويل لوضع المساعد العراقي" (mode_ai.mp3) + Cyan LED
#
#  - 102: Play/Pause Button (زر التشغيل ▶️)
#         * Single tap: Toggle Play / Pause for music and stories
# ==============================================================================

OS_DIR="/usr/data/iraqi_os"
MODE_FILE="/tmp/speaker_current_mode"
PAIRING_FILE="/tmp/speaker_pairing_mode"
LED_DEV="/sys/class/leds/aw2015"

test -f $MODE_FILE || echo "AI" > $MODE_FILE

press_mic_time=0
up_c1=0
up_c2=0
up_c3=0

trigger_pairing_mode() {
    touch $PAIRING_FILE
    # Flash Amber / Gold rapid blink to indicate pairing mode
    echo 1 0 1 1 > ${LED_DEV}/led_time 2>/dev/null
    echo "255 180 0" > ${LED_DEV}/color_blink 2>/dev/null
    
    # Ensure Wi-Fi Setup SoftAP is active (Smaati_Setup)
    if [ -x "$OS_DIR/wifi_ap_mode_start.sh" ]; then
        $OS_DIR/wifi_ap_mode_start.sh >/dev/null 2>&1 &
    fi

    # Make sure Bluetooth is discoverable as Smaati
    hciconfig hci0 name 'Smaati_سماعتي' 2>/dev/null
    hciconfig hci0 piscan 2>/dev/null

    # Play pairing audio: "تم تفعيل وضع الاقتران"
    if [ -f "$OS_DIR/pairing_ready.mp3" ]; then
        killall -9 mplayer 2>/dev/null
        mplayer -volume 100 "$OS_DIR/pairing_ready.mp3" >/dev/null 2>&1 &
    fi
}

echo "[+] Calibrated Iraqi Button Watcher active on /usr/bin/key_test" > /tmp/watcher.log

# Stream key events from native key_test
/usr/bin/key_test 2>/dev/null | while read -r _k code action; do
    [ "$_k" != "Key" ] && continue
    [ -z "$code" ] && continue
    [ -z "$action" ] && continue

    now=$(date +%s)
    echo "EVENT: code=$code action=$action time=$now" >> /tmp/watcher.log

    case "$code" in
        # ----------------------------------------------------------------------
        # 105: VOLUME UP (زر رفع الصوت +)
        # ----------------------------------------------------------------------
        105)
            if [ "$action" = "press" ]; then
                touch /tmp/vol_up_held
                # Continuous ramp for long press hold
                (
                    usleep 350000 2>/dev/null || sleep 1
                    while [ -f /tmp/vol_up_held ]; do
                        amixer sset Master 4+ >/dev/null 2>&1
                        usleep 200000 2>/dev/null || sleep 1
                    done
                ) &
            elif [ "$action" = "release" ]; then
                rm -f /tmp/vol_up_held
                
                # Check for 3 clicks within 2 seconds (Triple-Click)
                up_c1=$up_c2
                up_c2=$up_c3
                up_c3=$now

                if [ "$up_c1" -gt 0 ] && [ $(( now - up_c1 )) -le 2 ]; then
                    up_c1=0; up_c2=0; up_c3=0
                    trigger_pairing_mode
                else
                    # Calibrated single click volume increment (+4 / ~13%)
                    amixer sset Master 4+ >/dev/null 2>&1
                    cur_m=$(cat $MODE_FILE 2>/dev/null || echo "AI")
                    if [ "$cur_m" = "AI" ]; then
                        pct=$(amixer sget Master 2>/dev/null | grep Mono: | cut -d '[' -f 2 | cut -d '%' -f 1)
                        if [ "${pct:-0}" -ge 100 ]; then
                            mplayer -volume 100 "$OS_DIR/beep.wav" >/dev/null 2>&1 &
                        fi
                    else
                        # In BT mode: Quick white flash for feedback without touching ALSA audio stream
                        echo "255 255 255" > ${LED_DEV}/color_brightness 2>/dev/null
                        (usleep 80000 2>/dev/null; echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null; echo "0 50 255" > ${LED_DEV}/color_blink 2>/dev/null) &
                    fi
                fi
            fi
            ;;

        # ----------------------------------------------------------------------
        # 108: VOLUME DOWN (زر خفض الصوت -)
        # ----------------------------------------------------------------------
        108)
            if [ "$action" = "press" ]; then
                touch /tmp/vol_down_held
                # Continuous ramp for long press hold
                (
                    usleep 350000 2>/dev/null || sleep 1
                    while [ -f /tmp/vol_down_held ]; do
                        amixer sset Master 4- >/dev/null 2>&1
                        usleep 200000 2>/dev/null || sleep 1
                    done
                ) &
            elif [ "$action" = "release" ]; then
                rm -f /tmp/vol_down_held
                # Calibrated single click volume decrement (-4 / ~13%)
                amixer sset Master 4- >/dev/null 2>&1
                cur_m=$(cat $MODE_FILE 2>/dev/null || echo "AI")
                if [ "$cur_m" = "AI" ]; then
                    pct=$(amixer sget Master 2>/dev/null | grep Mono: | cut -d '[' -f 2 | cut -d '%' -f 1)
                    if [ "${pct:-0}" -le 0 ]; then
                        mplayer -volume 100 "$OS_DIR/beep.wav" >/dev/null 2>&1 &
                    fi
                else
                    echo "255 255 255" > ${LED_DEV}/color_brightness 2>/dev/null
                    (usleep 80000 2>/dev/null; echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null; echo "0 50 255" > ${LED_DEV}/color_blink 2>/dev/null) &
                fi
            fi
            ;;

        # ----------------------------------------------------------------------
        # 103: MIC BUTTON (زر المايك 🎙️ - ضغطة مطولة للتبديل بين البلوتوث والمساعد)
        # ----------------------------------------------------------------------
        103)
            if [ "$action" = "press" ]; then
                press_mic_time=$now
            elif [ "$action" = "release" ]; then
                dur=$(( now - press_mic_time ))
                press_mic_time=0

                # Long press >= 2 seconds: Toggle AI <-> BT
                if [ "$dur" -ge 2 ]; then
                    if [ -x "$OS_DIR/switch_mode.sh" ]; then
                        $OS_DIR/switch_mode.sh TOGGLE >/dev/null 2>&1 &
                    fi
                else
                    # Short press (< 2s): Trigger Assistant to Listen!
                    echo "LISTEN" > /tmp/ai_trigger
                    echo 2 0 2 1 > ${LED_DEV}/led_time 2>/dev/null
                    echo "0 220 255" > ${LED_DEV}/color_blink 2>/dev/null
                    if [ -f "$OS_DIR/beep.wav" ]; then
                        mplayer -volume 70 "$OS_DIR/beep.wav" >/dev/null 2>&1 &
                    fi
                fi
            fi
            ;;

        # ----------------------------------------------------------------------
        # 102: PLAY / PAUSE BUTTON (زر Play ▶️ لتشغيل وإيقاف الأغاني)
        # ----------------------------------------------------------------------
        102)
            if [ "$action" = "release" ]; then
                # Toggle Play / Pause
                if pidof mplayer >/dev/null 2>&1; then
                    killall -9 mplayer 2>/dev/null
                else
                    # Resume or start default song
                    if [ -f "$OS_DIR/helo_hobak.m4a" ]; then
                        mplayer -volume 100 "$OS_DIR/helo_hobak.m4a" >/dev/null 2>&1 &
                    fi
                fi
            fi
            ;;
    esac
done
