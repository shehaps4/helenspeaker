#!/bin/sh
# ==============================================================================
# Iraqi AI Smart Speaker OS - Embedded Router Web Control Center
# High-performance lightweight HTTP Server for BusyBox inetd (Ports 80 & 8080)
# ==============================================================================

OS_DIR="/usr/data/iraqi_os"
WWW_DIR="${OS_DIR}/www"
CONFIG_FILE="${OS_DIR}/config.json"
WPA_CONF="/usr/data/wpa_supplicant.conf"
MODE_FILE="/tmp/speaker_current_mode"
LED_DEV="/sys/class/leds/aw2015"

read -r request_line
method=$(echo "$request_line" | awk '{print $1}')
full_path=$(echo "$request_line" | awk '{print $2}')
path=$(echo "$full_path" | cut -d'?' -f1)
query=$(echo "$full_path" | cut -s -d'?' -f2-)

# Read HTTP headers
content_length=0
while read -r header; do
    header=$(echo "$header" | tr -d '\r')
    [ -z "$header" ] && break
    case "$header" in
        [Cc][Oo][Nn][Tt][Ee][Nn][Tt]-[Ll][Ee][Nn][Gg][Tt][Hh]:*)
            content_length=$(echo "$header" | cut -d: -f2 | tr -d ' ')
            ;;
    esac
done

# Immediate CORS OPTIONS preflight response (after draining headers)
if [ "$method" = "OPTIONS" ]; then
    printf "HTTP/1.1 200 OK\r\n"
    printf "Access-Control-Allow-Origin: *\r\n"
    printf "Access-Control-Allow-Methods: GET, POST, OPTIONS, PUT, DELETE\r\n"
    printf "Access-Control-Allow-Headers: *\r\n"
    printf "Access-Control-Max-Age: 86400\r\n"
    printf "Content-Length: 0\r\n"
    printf "Connection: close\r\n\r\n"
    exit 0
fi

# Read POST request body if present using exact byte count
body=""
if [ "$method" = "POST" ] && [ "${content_length:-0}" -gt 0 ]; then
    body=$(head -c "$content_length")
fi

params="${query}&${body}"

get_param() {
    _key="$1"
    _val=$(echo "$query" | grep -o "${_key}=[^&]*" 2>/dev/null | head -n1 | cut -d= -f2-)
    if [ -z "$_val" ]; then
        _val=$(echo "$body" | grep -o "${_key}=[^&]*" 2>/dev/null | head -n1 | cut -d= -f2-)
    fi
    if [ -z "$_val" ]; then
        _val=$(echo "$body" | sed -n "s/.*\"${_key}\"[ ]*:[ ]*\"\([^\"]*\)\".*/\1/p" 2>/dev/null | head -n1)
    fi
    if [ -z "$_val" ]; then
        _val=$(echo "$body" | sed -n "s/.*\"${_key}\"[ ]*:[ ]*\([0-9a-zA-Z_]*\).*/\1/p" 2>/dev/null | head -n1)
    fi
    echo "$_val" | tr -d '\r\n'
}

send_header() {
    status_code="${1:-200 OK}"
    content_type="${2:-text/html; charset=utf-8}"
    printf "HTTP/1.1 %s\r\n" "$status_code"
    printf "Content-Type: %s\r\n" "$content_type"
    printf "Access-Control-Allow-Origin: *\r\n"
    printf "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
    printf "Access-Control-Allow-Headers: *\r\n"
    printf "Cache-Control: no-cache, no-store, must-revalidate\r\n"
    printf "Connection: close\r\n"
    printf "\r\n"
}

case "$path" in
    ""|"/"|"/index.html"|"/index.htm")
        send_header "200 OK" "text/html; charset=utf-8"
        if [ -f "${WWW_DIR}/index.html" ]; then
            cat "${WWW_DIR}/index.html"
        else
            echo "<h1>Smaati OS Web Center Ready</h1>"
        fi
        ;;

    "/api/status")
        send_header "200 OK" "application/json; charset=utf-8"
        cur_mode=$(cat "$MODE_FILE" 2>/dev/null || echo "AI")
        wlan0_ip=$(ifconfig wlan0 2>/dev/null | grep 'inet addr:' | cut -d: -f2 | awk '{print $1}')
        wlan1_ip=$(ifconfig wlan1 2>/dev/null | grep 'inet addr:' | cut -d: -f2 | awk '{print $1}')
        vol_pct=$(amixer sget Master 2>/dev/null | grep Mono: | cut -d '[' -f 2 | cut -d '%' -f 1)
        uptime_str=$(uptime | cut -d, -f1 | sed 's/.*up //')
        mem_free=$(free -m 2>/dev/null | grep Mem: | awk '{print $4}')
        flash_free=$(df -h /usr/data 2>/dev/null | tail -n1 | awk '{print $4}')
        bt_status=$(hciconfig hci0 2>/dev/null | grep -q "UP RUNNING" && echo "ON" || echo "OFF")
        
        # Check paired phone
        paired_phone=""
        for pdir in /var/lib/bluetooth/70:4F:08:00:84:C8/*:*; do
            if [ -d "$pdir" ]; then
                pmac=$(basename "$pdir")
                [ "$pmac" = "cache" ] && continue
                pname=$(grep '^Name=' "$pdir/info" 2>/dev/null | cut -d= -f2)
                paired_phone="${pname:-Device} (${pmac})"
                break
            fi
        done

        last_user=$(cat /tmp/speaker_last_user 2>/dev/null | tr -d '\r\n"' || echo '')
        last_reply=$(cat /tmp/speaker_last_reply 2>/dev/null | tr -d '\r\n"' || echo '')

        cat << JSON_STATUS
{
  "mode": "${cur_mode}",
  "bluetooth": "${bt_status}",
  "wlan0_ip": "${wlan0_ip:-غير متصل}",
  "wlan1_ip": "${wlan1_ip:-192.168.1.1}",
  "volume": ${vol_pct:-85},
  "uptime": "${uptime_str:-1 min}",
  "mem_free": "${mem_free:-38} MB",
  "flash_free": "${flash_free:-21.7M}",
  "paired_phone": "${paired_phone:-لا يوجد جهاز مقترن}",
  "tone_status": "$(cat /tmp/speaker_tone_status 2>/dev/null || echo 'نبرة هادئة ورومانسية 💖')",
  "last_user": "${last_user}",
  "last_reply": "${last_reply}"
}
JSON_STATUS
        ;;

    "/api/config")
        send_header "200 OK" "application/json; charset=utf-8"
        if [ -f "$CONFIG_FILE" ]; then
            cat "$CONFIG_FILE"
        else
            echo '{"character_name":"هيلين","voice_gender":"female","voice_name":"Kore","dialect":"baghdadi","relationship_style":"Romantic","romance_level":95,"boldness_level":90,"humor_level":90,"user_nickname":"عيوني","live_model":"gemini-2.0-flash-exp","rgb_enabled":true,"rgb_mode":"LISTENING","rgb_color":"#00DCFF","rgb_brightness":200}'
        fi
        ;;

    "/api/reset")
        send_header "200 OK" "application/json; charset=utf-8"
        cat << RESET_EOF > "$CONFIG_FILE"
{
  "character_name": "هيلين",
  "user_nickname": "عيوني",
  "voice_gender": "female",
  "voice_name": "Kore",
  "dialect": "baghdadi",
  "relationship_style": "Romantic",
  "romance_level": 95,
  "boldness_level": 90,
  "humor_level": 90,
  "live_model": "gemini-2.0-flash-exp",
  "api_key": "YOUR_GEMINI_API_KEY_HERE",
  "rgb_enabled": true,
  "rgb_mode": "LISTENING",
  "rgb_color": "#00DCFF",
  "rgb_brightness": 200,
  "wifi_ssid": "",
  "wifi_password": ""
}
RESET_EOF
        killall -9 mplayer 2>/dev/null
        if [ -f "$OS_DIR/config_saved.wav" ]; then
            mplayer -volume 100 "$OS_DIR/config_saved.wav" >/dev/null 2>&1 &
        fi
        echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null
        echo "0 220 255" > ${LED_DEV}/color_blink 2>/dev/null
        echo '{"status":"OK","message":"تمت استعادة إعدادات المصنع وتصفير إعدادات هيلين بنجاح"}'
        ;;


    "/api/save")
        send_header "200 OK" "application/json; charset=utf-8"
        if [ -n "$body" ]; then
            echo "$body" > "$CONFIG_FILE"
            
            # Update Wi-Fi supplicant if wifi_ssid provided
            save_ssid=$(echo "$body" | sed -n 's/.*"wifi_ssid"[ ]*:[ ]*"\([^"]*\)".*/\1/p')
            save_psk=$(echo "$body" | sed -n 's/.*"wifi_password"[ ]*:[ ]*"\([^"]*\)".*/\1/p')
            if [ -n "$save_ssid" ]; then
                if [ -n "$save_psk" ]; then
                    cat << WPA_SAVE_EOF > "$WPA_CONF"
ctrl_interface=/var/run/wpa_supplicant
update_config=1
country=GB

network={
    ssid="$save_ssid"
    psk="$save_psk"
}
WPA_SAVE_EOF
                else
                    cat << WPA_SAVE_EOF > "$WPA_CONF"
ctrl_interface=/var/run/wpa_supplicant
update_config=1
country=GB

network={
    ssid="$save_ssid"
    key_mgmt=NONE
}
WPA_SAVE_EOF
                fi
                wpa_cli -i wlan0 reconfigure >/dev/null 2>&1
                udhcpc -i wlan0 -b >/dev/null 2>&1 &
            fi

            killall -9 mplayer 2>/dev/null
            if [ -f "$OS_DIR/config_saved.wav" ]; then
                mplayer -volume 100 "$OS_DIR/config_saved.wav" >/dev/null 2>&1 &
            elif [ -f "$OS_DIR/config_saved.mp3" ]; then
                mplayer -volume 100 "$OS_DIR/config_saved.mp3" >/dev/null 2>&1 &
            fi
            echo '{"status":"OK","message":"تم حفظ جميع الإعدادات في ذاكرة السماعة بنجاح"}'
        else
            echo '{"status":"ERROR","message":"البيانات فارغة"}'
        fi
        ;;

    "/api/mode")
        send_header "200 OK" "application/json; charset=utf-8"
        case "$params" in
            *BT*|*bt*|*Bluetooth*|*bluetooth*)
                target_mode="BT"
                ;;
            *)
                target_mode="AI"
                ;;
        esac

        if [ -x "$OS_DIR/switch_mode.sh" ]; then
            $OS_DIR/switch_mode.sh "$target_mode" >/dev/null 2>&1 &
        fi

        if [ "$target_mode" = "BT" ]; then
            echo '{"status":"OK","mode":"BT","message":"تم تفعيل وضع البلوتوث والاقتران التلقائي فوراً"}'
        else
            echo '{"status":"OK","mode":"AI","message":"تم إيقاف البلوتوث تماماً وتفعيل المساعد العراقي"}'
        fi
        ;;

    "/api/scan_wifi")
        send_header "200 OK" "application/json; charset=utf-8"
        wpa_cli -i wlan0 scan >/dev/null 2>&1
        sleep 1
        raw_results=$(wpa_cli -i wlan0 scan_results 2>/dev/null | tail -n +2)
        
        printf "["
        first=1
        echo "$raw_results" | while IFS="$(printf '\t')" read -r bssid freq signal flags ssid; do
            [ -z "$ssid" ] && continue
            if [ $first -eq 0 ]; then printf ","; fi
            first=0
            printf '{"ssid":"%s","signal":"%s","bssid":"%s"}' "$ssid" "$signal" "$bssid"
        done
        printf "]"
        ;;

    "/api/wifi")
        send_header "200 OK" "application/json; charset=utf-8"
        ssid=$(echo "$params" | grep -o 'ssid=[^&]*' | cut -d= -f2)
        [ -z "$ssid" ] && ssid=$(echo "$body" | sed -n 's/.*"ssid"[ ]*:[ ]*"\([^"]*\)".*/\1/p')

        psk=$(echo "$params" | grep -o 'psk=[^&]*' | cut -d= -f2)
        [ -z "$psk" ] && psk=$(echo "$body" | sed -n 's/.*"psk"[ ]*:[ ]*"\([^"]*\)".*/\1/p')

        if [ -n "$ssid" ]; then
            if [ -n "$psk" ]; then
                cat << WPA_EOF > "$WPA_CONF"
ctrl_interface=/var/run/wpa_supplicant
update_config=1
country=GB

network={
    ssid="$ssid"
    psk="$psk"
}
WPA_EOF
            else
                cat << WPA_EOF > "$WPA_CONF"
ctrl_interface=/var/run/wpa_supplicant
update_config=1
country=GB

network={
    ssid="$ssid"
    key_mgmt=NONE
}
WPA_EOF
            fi
            wpa_cli -i wlan0 reconfigure >/dev/null 2>&1
            udhcpc -i wlan0 -b >/dev/null 2>&1 &
            
            # Update config.json with current wifi info
            if [ -f "$CONFIG_FILE" ]; then
                sed -i 's/"wifi_ssid"[ ]*:[ ]*"[^"]*"/"wifi_ssid":"'"$ssid"'"/' "$CONFIG_FILE" 2>/dev/null
                sed -i 's/"wifi_password"[ ]*:[ ]*"[^"]*"/"wifi_password":"'"$psk"'"/' "$CONFIG_FILE" 2>/dev/null
            fi

            killall -9 mplayer 2>/dev/null
            if [ -f "$OS_DIR/wifi_ok.wav" ]; then
                mplayer -volume 100 "$OS_DIR/wifi_ok.wav" >/dev/null 2>&1 &
            elif [ -f "$OS_DIR/wifi_ok.mp3" ]; then
                mplayer -volume 100 "$OS_DIR/wifi_ok.mp3" >/dev/null 2>&1 &
            fi
            echo '{"status":"OK","message":"تم الاتصال بشبكة الواي فاي بنجاح"}'
        else
            echo '{"status":"ERROR","message":"اسم شبكة الواي فاي مطلوب"}'
        fi
        ;;

    "/api/rgb")
        send_header "200 OK" "application/json; charset=utf-8"
        enabled=$(get_param "enabled")
        mode=$(get_param "mode")
        r=$(get_param "r")
        g=$(get_param "g")
        b=$(get_param "b")
        bright=$(get_param "brightness")

        [ -z "$enabled" ] && enabled="true"
        [ -z "$mode" ] && mode="LISTENING"

        # Extract only digits to prevent arithmetic errors
        r=$(echo "$r" | tr -cd '0-9')
        g=$(echo "$g" | tr -cd '0-9')
        b=$(echo "$b" | tr -cd '0-9')
        bright=$(echo "$bright" | tr -cd '0-9')

        r=${r:-0}
        g=${g:-220}
        b=${b:-255}
        bright=${bright:-200}

        # Apply brightness factor (0-255)
        if [ "$bright" -ge 0 ] 2>/dev/null && [ "$bright" -le 255 ] 2>/dev/null; then
            r=$(( r * bright / 255 ))
            g=$(( g * bright / 255 ))
            b=$(( b * bright / 255 ))
        fi

        # Clamp 0-255
        [ "$r" -gt 255 ] && r=255
        [ "$g" -gt 255 ] && g=255
        [ "$b" -gt 255 ] && b=255

        if [ "$enabled" = "false" ]; then
            echo "0 0 0" > ${LED_DEV}/color_brightness 2>/dev/null
            echo "0 0 0" > ${LED_DEV}/color_blink 2>/dev/null
        else
            case "$mode" in
                "PULSE"|"ROMANCE")
                    echo "0 0 0" > ${LED_DEV}/color_brightness 2>/dev/null
                    echo 2 0 2 1 > ${LED_DEV}/led_time 2>/dev/null
                    echo "${r} ${g} ${b}" > ${LED_DEV}/color_blink 2>/dev/null
                    ;;
                "BREATH")
                    echo "0 0 0" > ${LED_DEV}/color_brightness 2>/dev/null
                    echo 3 1 3 1 > ${LED_DEV}/led_time 2>/dev/null
                    echo "${r} ${g} ${b}" > ${LED_DEV}/color_blink 2>/dev/null
                    ;;
                "STROBE")
                    echo "0 0 0" > ${LED_DEV}/color_brightness 2>/dev/null
                    echo 0 0 1 0 > ${LED_DEV}/led_time 2>/dev/null
                    echo "${r} ${g} ${b}" > ${LED_DEV}/color_blink 2>/dev/null
                    ;;
                "SOLID")
                    echo "0 0 0" > ${LED_DEV}/color_blink 2>/dev/null
                    echo "${r} ${g} ${b}" > ${LED_DEV}/color_brightness 2>/dev/null
                    ;;
                *)
                    echo "0 0 0" > ${LED_DEV}/color_brightness 2>/dev/null
                    echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null
                    echo "${r} ${g} ${b}" > ${LED_DEV}/color_blink 2>/dev/null
                    ;;
            esac
        fi

        # Update config.json with current rgb state
        if [ -f "$CONFIG_FILE" ]; then
            sed -i 's/"rgb_enabled"[ ]*:[ ]*[a-zA-Z]*/"rgb_enabled":'"$enabled"'/' "$CONFIG_FILE" 2>/dev/null
            sed -i 's/"rgb_mode"[ ]*:[ ]*"[^"]*"/"rgb_mode":"'"$mode"'"/' "$CONFIG_FILE" 2>/dev/null
            sed -i 's/"rgb_brightness"[ ]*:[ ]*[0-9]*/"rgb_brightness":'"$bright"'/' "$CONFIG_FILE" 2>/dev/null
        fi

        echo '{"status":"OK","message":"تم تطبيق إعدادات الإضاءة بنجاح"}'
        ;;

    "/api/vol")
        send_header "200 OK" "application/json; charset=utf-8"
        vol=$(get_param "vol")
        vol=$(echo "$vol" | tr -cd '0-9')
        if [ -n "$vol" ]; then
            alsa_lvl=$(( vol * 31 / 100 ))
            amixer sset Master ${alsa_lvl} >/dev/null 2>&1
        fi
        echo '{"status":"OK"}'
        ;;

    "/api/voice_preview")
        send_header "200 OK" "application/json; charset=utf-8"
        vname=$(get_param "voice")
        killall -9 mplayer 2>/dev/null
        if [ -n "$vname" ] && [ -f "$OS_DIR/preview_${vname}.wav" ]; then
            mplayer -volume 100 "$OS_DIR/preview_${vname}.wav" >/dev/null 2>&1 &
        elif [ -f "$OS_DIR/boot_greeting.wav" ]; then
            mplayer -volume 100 "$OS_DIR/boot_greeting.wav" >/dev/null 2>&1 &
        fi
        echo '{"status":"OK","message":"تشغيل عينة الصوت الحي"}'
        ;;

    "/api/trigger_listen")
        send_header "200 OK" "application/json; charset=utf-8"
        echo "LISTEN" > /tmp/ai_trigger
        echo 2 0 2 1 > ${LED_DEV}/led_time 2>/dev/null
        echo "0 255 0" > ${LED_DEV}/color_blink 2>/dev/null
        if [ -f "$OS_DIR/beep.wav" ]; then
            killall -9 mplayer 2>/dev/null
            mplayer -volume 70 "$OS_DIR/beep.wav" >/dev/null 2>&1 &
        fi
        echo '{"status":"OK","message":"تم تفعيل الاستماع، تحدث الآن!"}'
        ;;

    "/api/ask")
        send_header "200 OK" "application/json; charset=utf-8"
        ask_text=$(get_param "text")
        if [ -n "$ask_text" ]; then
            echo "$ask_text" > /tmp/ai_text_input
            echo "TEXT" > /tmp/ai_trigger
            echo '{"status":"OK","message":"جاري التفكير والرد صوتياً بالسماعة..."}'
        else
            echo '{"status":"ERROR","message":"النص فارغ"}'
        fi
        ;;

    "/api/stop")
        send_header "200 OK" "application/json; charset=utf-8"
        killall -9 mplayer 2>/dev/null
        rm -f /tmp/current_online_song.*
        echo 3 0 3 1 > ${LED_DEV}/led_time 2>/dev/null
        echo "0 220 255" > ${LED_DEV}/color_blink 2>/dev/null
        echo '{"status":"OK","message":"تم إيقاف تشغيل الأغنية والصوت فوراً"}'
        ;;

    *)
        send_header "404 Not Found" "text/plain; charset=utf-8"
        echo "404 Not Found"
        ;;
esac

exit 0
