#!/bin/sh
# ==============================================================================
# Bluetooth Speaker Mode Switcher (Iraqi AI Smart Speaker)
# Performs safe audio & mic resource handover on Ingenic X1800 Linux
# ==============================================================================

ACTION=$1

if [ "$ACTION" = "enable" ]; then
    echo "[*] Switching to Bluetooth Speaker Mode (A2DP Sink)..."
    # 1. Stop AI Audio and release playback device
    killall -9 mplayer 2>/dev/null
    killall -9 madplay 2>/dev/null
    
    # 2. Release mic DMA
    killall -9 mic_test 2>/dev/null
    
    # 3. Set LED to Blue pulse
    echo "r 0 g 0 b 255" > /sys/class/leds/aw2015/color_blink
    
    # 4. Start BlueALSA A2DP playback sink listener
    killall -9 bluealsa-aplay 2>/dev/null
    bluealsa-aplay 00:00:00:00:00:00 >/dev/null 2>&1 &
    echo "[+] Bluetooth Speaker Mode Active. Connect your phone via Bluetooth."

elif [ "$ACTION" = "disable" ]; then
    echo "[*] Returning to AI Assistant Mode..."
    # 1. Stop BlueALSA streaming
    killall -9 bluealsa-aplay 2>/dev/null
    
    # 2. Set LED to idle Cyan
    echo "r 0 g 220 b 255" > /sys/class/leds/aw2015/color_brightness
    echo "[+] AI Assistant Mode Active."
else
    echo "Usage: $0 [enable|disable]"
    exit 1
fi
