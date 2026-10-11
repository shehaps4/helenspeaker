#!/bin/sh
# ==============================================================================
# Iraqi AI Smart Speaker - Embedded Lightweight Autonomous Client (Helen Standalone)
# ==============================================================================
# Runs natively on Ingenic XBurst MIPS Linux board.
# No Python or heavy dependencies required.
# ==============================================================================

OS_DIR="/usr/data/iraqi_os"
LED_DEV="/sys/class/leds/aw2015"
IN_WAV="/tmp/mic_in.wav"
OUT_WAV="/tmp/helen_reply.wav"
GATEWAY_URL="http://127.0.0.1:8000/api/v1/voice/interact"

set_led() {
    state="$1"
    case "$state" in
        "listening")
            echo '0 0 0' > ${LED_DEV}/color_brightness 2>/dev/null
            echo 2 0 2 1 > ${LED_DEV}/led_time 2>/dev/null
            echo '0 255 0' > ${LED_DEV}/color_blink 2>/dev/null
            ;;
        "thinking")
            echo '0 0 0' > ${LED_DEV}/color_blink 2>/dev/null
            echo '0 50 255' > ${LED_DEV}/color_brightness 2>/dev/null
            ;;
        "speaking")
            echo '0 0 0' > ${LED_DEV}/color_brightness 2>/dev/null
            echo 2 0 2 1 > ${LED_DEV}/led_time 2>/dev/null
            echo '255 0 0' > ${LED_DEV}/color_blink 2>/dev/null
            ;;
        "music")
            echo '0 0 0' > ${LED_DEV}/color_brightness 2>/dev/null
            echo 1 0 1 1 > ${LED_DEV}/led_time 2>/dev/null
            echo '255 160 0' > ${LED_DEV}/color_blink 2>/dev/null
            ;;
        "idle")
            echo '0 0 0' > ${LED_DEV}/color_brightness 2>/dev/null
            echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null
            echo '0 220 255' > ${LED_DEV}/color_blink 2>/dev/null
            ;;
    esac
}

echo "[+] Starting Standalone Helen Embedded Client..."
set_led "idle"

# Play greeting on boot
if [ -f "$OS_DIR/preview_Aoede.wav" ]; then
    mplayer -volume 90 "$OS_DIR/preview_Aoede.wav" >/dev/null 2>&1
elif [ -f "$OS_DIR/boot_greeting.wav" ]; then
    mplayer -volume 90 "$OS_DIR/boot_greeting.wav" >/dev/null 2>&1
fi

while true; do
    # Check if music is playing
    if ps | grep -v grep | grep mplayer | grep -v '\[mplayer\]' >/dev/null 2>&1; then
        sleep 1
        continue
    fi

    # Check for hardware triggers or manual button
    if [ -f /tmp/ai_trigger ]; then
        rm -f /tmp/ai_trigger
        TRIGGER=1
    else
        TRIGGER=0
    fi

    if [ "$TRIGGER" = "1" ]; then
        set_led "listening"
        rm -f "$IN_WAV" "$OUT_WAV"
        
        # Record voice from hardware microphone
        /usr/bin/mic_test -f "$IN_WAV" -d 3 >/dev/null 2>&1
        
        if [ -f "$IN_WAV" ] && [ -s "$IN_WAV" ]; then
            set_led "thinking"
            
            # Send audio directly to gateway
            wget -q --post-file="$IN_WAV" --header="Content-Type: audio/wav" -O "$OUT_WAV" "$GATEWAY_URL" >/dev/null 2>&1
            
            if [ -f "$OUT_WAV" ] && [ -s "$OUT_WAV" ]; then
                set_led "speaking"
                mplayer -volume 100 "$OUT_WAV" >/dev/null 2>&1
            fi
        fi
        set_led "idle"
    fi

    sleep 0.15
done
