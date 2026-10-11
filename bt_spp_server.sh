#!/bin/sh
# Iraqi AI Smart Speaker - Bluetooth SPP Server
# Listens for Bluetooth Serial Port Profile connections and processes commands

DEV="/dev/rfcomm0"

while true; do
    # Register SDP SPP profile
    sdptool add SP >/dev/null 2>&1
    hciconfig hci0 piscan >/dev/null 2>&1

    # Listen on RFCOMM channel 1
    rfcomm release 0 >/dev/null 2>&1
    rfcomm listen 0 1 >/dev/null 2>&1 &
    RF_PID=$!

    # Wait for rfcomm0 device node to appear upon phone connection
    COUNT=0
    while [ ! -e "$DEV" ] && kill -0 $RF_PID 2>/dev/null; do
        sleep 1
    done

    if [ -e "$DEV" ]; then
        # Handle incoming commands from phone over Bluetooth SPP
        stty -F "$DEV" 115200 cs8 -cstopb -parenb raw -echo 2>/dev/null
        while read -r line < "$DEV"; do
            [ -z "$line" ] && break
            resp=$(echo "$line" | /usr/data/iraqi_os/iraqi_cmd_handler.sh)
            echo "$resp" > "$DEV" 2>/dev/null
        done
        rfcomm release 0 >/dev/null 2>&1
    fi

    wait $RF_PID 2>/dev/null
    sleep 1
done
