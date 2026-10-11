# -*- coding: utf-8 -*-
"""
==============================================================================
Iraqi AI Smart Speaker OS - Advanced Neural Assistant Engine ("هيلين - Helen")
==============================================================================
Features:
 1. Immediate Text Interaction (<150ms from Web Dashboard /api/ask)
 2. Automatic Continuous Voice Activity Detection (Hands-Free VAD, no button required)
 3. Tri-Color Speech LED Hardware Feedback:
    - Listening (User speaking): GREEN (الأخضر 0 255 0)
    - Thinking (AI Reasoning):   BLUE  (الأزرق 0 50 255)
    - Speaking (AI Replying):    RED   (الأحمر 255 0 0)
    - Idle:                     CYAN  (السماوي 0 220 255)
 4. Multi-Gender Gemini Live TTS Voices (Kore, Aoede, Leda, Puck, Fenrir, Charon)
 5. Online Song Search & High-Fidelity Streaming (yt-dlp)
 6. Complete Uninterrupted Storytelling until "وقفي" / "كافي" / "اسكتي"
 7. Persistent Long-term & Short-term Memory (helen_memory.json)
 8. Acoustic Pitch & Energy Voice Tone DSP Analysis
==============================================================================
"""

import os
import sys
import json
import time
import wave
import shutil
import urllib.parse
import threading
import subprocess
import numpy as np
import soundfile as sf
import google.generativeai as genai

# Reconfigure console streams for UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ----------------------------------------------------------------------
# ADB Path Resolution & Robust Execution
# ----------------------------------------------------------------------
def find_adb_binary():
    sdk_adb = os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe")
    if os.path.exists(sdk_adb):
        return sdk_adb
    candidates = [
        shutil.which("adb"),
        r"C:\Users\Th3painter\AppData\Local\Microsoft\WinGet\Packages\Google.PlatformTools_Microsoft.Winget.Source_8wekyb3d8bbwe\platform-tools\adb.exe"
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return "adb"

ADB_PATH = find_adb_binary()
DEVICE_SERIAL = "audio_84c8"
DEFAULT_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
MEMORY_FILE = os.path.join(os.path.dirname(__file__), "helen_memory.json")

def adb_cmd(cmd, timeout=12):
    try:
        res = subprocess.run(
            [ADB_PATH, "-s", DEVICE_SERIAL, "shell", cmd],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout
        )
        return res.stdout.strip()
    except Exception as e:
        return ""

def adb_push(local_file, remote_file, timeout=15):
    try:
        subprocess.run(
            [ADB_PATH, "-s", DEVICE_SERIAL, "push", local_file, remote_file],
            check=True,
            capture_output=True,
            timeout=timeout
        )
        return True
    except Exception:
        return False

def adb_pull(remote_file, local_file, timeout=15):
    try:
        subprocess.run(
            [ADB_PATH, "-s", DEVICE_SERIAL, "pull", remote_file, local_file],
            check=True,
            capture_output=True,
            timeout=timeout
        )
        return True
    except Exception:
        return False

# ----------------------------------------------------------------------
# Hardware Tri-Color LED Control (AW2015 Driver)
# ----------------------------------------------------------------------
def set_led(state):
    """
    AW2015 RGB Hardware LEDs:
    - listening: GREEN pulse (0 255 0)
    - thinking:  BLUE solid  (0 50 255)
    - speaking:  RED pulse   (255 0 0)
    - music:     GOLD blink  (255 160 0)
    - idle:      CYAN pulse  (0 220 255)
    """
    if state == "listening":
        adb_cmd("echo '0 0 0' > /sys/class/leds/aw2015/color_brightness 2>/dev/null; echo 2 0 2 1 > /sys/class/leds/aw2015/led_time 2>/dev/null; echo '0 255 0' > /sys/class/leds/aw2015/color_blink 2>/dev/null")
    elif state == "thinking":
        adb_cmd("echo '0 0 0' > /sys/class/leds/aw2015/color_blink 2>/dev/null; echo '0 50 255' > /sys/class/leds/aw2015/color_brightness 2>/dev/null")
    elif state == "speaking":
        adb_cmd("echo '0 0 0' > /sys/class/leds/aw2015/color_brightness 2>/dev/null; echo 2 0 2 1 > /sys/class/leds/aw2015/led_time 2>/dev/null; echo '255 0 0' > /sys/class/leds/aw2015/color_blink 2>/dev/null")
    elif state == "music":
        adb_cmd("echo '0 0 0' > /sys/class/leds/aw2015/color_brightness 2>/dev/null; echo 1 0 1 1 > /sys/class/leds/aw2015/led_time 2>/dev/null; echo '255 160 0' > /sys/class/leds/aw2015/color_blink 2>/dev/null")
    elif state == "idle":
        adb_cmd("echo '0 0 0' > /sys/class/leds/aw2015/color_brightness 2>/dev/null; echo 3 0 3 1 > /sys/class/leds/aw2015/led_time 2>/dev/null; echo '0 220 255' > /sys/class/leds/aw2015/color_blink 2>/dev/null")

def update_tone_telemetry(tone_text):
    sanitized = tone_text.replace('"', '').replace("'", "").replace("\n", " ").strip()
    adb_cmd(f"echo '{sanitized}' > /tmp/speaker_tone_status 2>/dev/null")

def update_chat_telemetry(user_text, reply_text):
    u = user_text.replace('"', '').replace("'", "").replace("\n", " ").strip()
    r = reply_text.replace('"', '').replace("'", "").replace("\n", " ").strip()
    adb_cmd(f"echo '{u}' > /tmp/speaker_last_user 2>/dev/null; echo '{r}' > /tmp/speaker_last_reply 2>/dev/null")

# ----------------------------------------------------------------------
# Persistent Long-Term Memory
# ----------------------------------------------------------------------
class HelenMemory:
    def __init__(self, filepath=MEMORY_FILE):
        self.filepath = filepath
        self.data = self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "user_facts": [],
            "conversation_history": [],
            "favorite_topics": []
        }

    def save(self):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[-] Error saving memory: {e}")

    def add_interaction(self, user_text, reply_text, tone=""):
        if not user_text:
            return
        self.data["conversation_history"].append({
            "timestamp": time.time(),
            "user": user_text,
            "assistant": reply_text,
            "tone": tone
        })
        if len(self.data["conversation_history"]) > 25:
            self.data["conversation_history"] = self.data["conversation_history"][-25:]
        self.save()

    def add_fact(self, fact):
        if fact and fact.strip() and fact not in self.data["user_facts"]:
            self.data["user_facts"].append(fact.strip())
            print(f"[🧠] تم حفظ معلومة جديدة في ذاكرة هيلين: {fact.strip()}")
            self.save()

    def get_context_prompt(self):
        facts = "\n".join([f"- {f}" for f in self.data.get("user_facts", [])[-15:]])
        recent = ""
        for item in self.data.get("conversation_history", [])[-4:]:
            recent += f"- المستخدم: {item['user']} -> رد هيلين: {item['assistant']}\n"
        
        ctx = ""
        if facts:
            ctx += f"\n[ذاكرة هيلين - معلومات تتذكرينها عن المستخدم من محادثاتكم السابقة]:\n{facts}\n"
        if recent:
            ctx += f"\n[سياق آخر كلام دار بينكم]:\n{recent}\n"
        return ctx

memory = HelenMemory()

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
def load_speaker_config():
    default_config = {
        "character_name": "هيلين",
        "user_nickname": "عيوني",
        "voice_gender": "female",
        "voice_name": "Kore",
        "dialect": "baghdadi",
        "relationship_style": "Romantic",
        "romance_level": 95,
        "boldness_level": 90,
        "humor_level": 90,
        "api_key": DEFAULT_API_KEY
    }
    try:
        raw = adb_cmd("cat /usr/data/iraqi_os/config.json 2>/dev/null")
        if raw and raw.startswith("{"):
            cfg = json.loads(raw)
            default_config.update(cfg)
    except Exception as e:
        pass
    if not default_config.get("api_key"):
        default_config["api_key"] = DEFAULT_API_KEY
    return default_config

# ----------------------------------------------------------------------
# Microphone Recording, Normalization & Calibrated VAD
# ----------------------------------------------------------------------
def record_probe_audio(duration=1.4, local_wav="probe_chunk.wav"):
    """Quick audio probe to detect voice activity."""
    adb_cmd(f"rm -f /tmp/probe.wav; /usr/bin/mic_test -f /tmp/probe.wav -d {duration} >/dev/null 2>&1")
    if not adb_pull("/tmp/probe.wav", local_wav):
        return None
    if not os.path.exists(local_wav) or os.path.getsize(local_wav) < 1000:
        return None
    return local_wav

def record_continuation_audio(duration=2.2, local_wav="continuation_chunk.wav"):
    """Record continuation when speech is detected."""
    adb_cmd(f"rm -f /tmp/cont.wav; /usr/bin/mic_test -f /tmp/cont.wav -d {duration} >/dev/null 2>&1")
    if not adb_pull("/tmp/cont.wav", local_wav):
        return None
    if not os.path.exists(local_wav) or os.path.getsize(local_wav) < 1000:
        return None
    return local_wav

def combine_and_normalize(probe_file, cont_file, out_file="recorded_input.wav"):
    """Combine probe and continuation into one normalized high-gain 16kHz mono WAV."""
    try:
        d1, sr1 = sf.read(probe_file)
        ch1 = d1[:, 0] if len(d1.shape) > 1 else d1
        ch1 = ch1 - np.mean(ch1) # Remove DC offset

        if cont_file and os.path.exists(cont_file):
            d2, sr2 = sf.read(cont_file)
            ch2 = d2[:, 0] if len(d2.shape) > 1 else d2
            ch2 = ch2 - np.mean(ch2)
            combined = np.concatenate([ch1, ch2])
        else:
            combined = ch1
            
        peak = np.abs(combined).max()
        if peak > 0.003:
            combined = combined / peak * 0.95
            
        sf.write(out_file, combined, sr1, subtype="PCM_16")
        return out_file
    except Exception as e:
        print(f"[-] Combine audio error: {e}")
        return None

def check_voice_activity(wav_file, threshold_rms=0.0072, threshold_peak=0.028):
    """
    Calibrated VAD:
    Speaker hardware ambient silence: RMS ~ 0.0049, Peak ~ 0.0197.
    Human speech threshold: RMS >= 0.0072 or Peak >= 0.028.
    """
    try:
        data, _ = sf.read(wav_file)
        mono = data[:, 0] if len(data.shape) > 1 else data
        mono = mono - np.mean(mono) # Remove DC offset
        rms = float(np.sqrt(np.mean(mono**2)))
        peak = float(np.abs(mono).max())
        return (rms >= threshold_rms or peak >= threshold_peak), rms, peak
    except Exception:
        return False, 0.0, 0.0

# ----------------------------------------------------------------------
# Acoustic Voice Tone DSP Analysis
# ----------------------------------------------------------------------
def analyze_acoustic_pitch_and_energy(wav_file):
    try:
        data, sr_rate = sf.read(wav_file)
        mono = data[:, 0] if len(data.shape) > 1 else data
        mono = mono - np.mean(mono)
        rms = float(np.sqrt(np.mean(mono**2)))
        peak = float(np.abs(mono).max())

        min_lag = int(sr_rate / 400)
        max_lag = int(sr_rate / 80)
        corr = np.correlate(mono, mono, mode='full')[len(mono)-1:]

        f0 = 0.0
        if len(corr) > max_lag:
            peak_lag = min_lag + np.argmax(corr[min_lag:max_lag])
            if corr[peak_lag] > 0.25 * corr[0]:
                f0 = float(sr_rate / peak_lag)

        if f0 > 220:
            pitch_type = "نبرة عاطفية أو حماسية"
        elif f0 > 130:
            pitch_type = "نبرة عفوية وطبيعية"
        elif f0 > 60:
            pitch_type = "نبرة هادئة ورزينة"
        else:
            pitch_type = "نبرة دافئة وهامسة"

        if rms > 0.12:
            energy_type = "صوت قوي وواضح"
        elif rms > 0.03:
            energy_type = "صوت معتدل"
        else:
            energy_type = "صوت ناعم ورومانسي"

        return {
            "f0_hz": round(f0, 1),
            "rms": round(rms, 3),
            "pitch_type": pitch_type,
            "energy_type": energy_type
        }
    except Exception:
        return {"f0_hz": 0, "rms": 0, "pitch_type": "طبيعي", "energy_type": "طبيعي"}

# ----------------------------------------------------------------------
# Gemini Multimodal Audio Processing & Persistent Memory
# ----------------------------------------------------------------------
def process_audio_with_gemini(wav_file, acoustics, config):
    char_name = config.get("character_name", "هيلين")
    user_name = config.get("user_nickname", "عيوني")
    dialect = config.get("dialect", "baghdadi")
    rel_style = config.get("relationship_style", "Romantic")
    romance = config.get("romance_level", 95)
    boldness = config.get("boldness_level", 90)
    humor = config.get("humor_level", 90)
    api_key = config.get("api_key", DEFAULT_API_KEY)

    memory_context = memory.get_context_prompt()

    prompt = f"""
أنتِ المساعد العراقي الذكي واسمكِ: "{char_name}".
تتحدثين باللهجة العراقية الـ ({dialect}) الحقيقية مع المستخدم: {user_name}.
أسلوب العلاقة: {rel_style}.
الرومانسية: {romance}%. الجراءة: {boldness}%. المزاح والمشاكسة: {humor}%.

{memory_context}

الخصائص الصوتية المرصودة من المايك:
- النبرة: {acoustics.get('pitch_type')}
- الطاقة: {acoustics.get('energy_type')}

المطلوب بدقة:
استمعي للتسجيل الصوتي بدقة. أرجعي JSON حصراً بهذا المخطط:
{{
  "user_text": "النص الدقيق المنطوق باللهجة العراقية",
  "voice_tone": "نبرة المتحدث (مثال: نبرة هادئة ورومانسية 💖، نبرة مرحة ومشاكسة 😄، نبرة عفوية ✨)",
  "intent_type": "chat | song_search | read_story | stop",
  "song_query": "اسم الأغنية والفنان إن كان طلب أغنية، وإلا فارغ",
  "reply_text": "رد هيلين العراقي الصوتي البشري المباشر",
  "new_fact_to_remember": "معلومة جديدة ذكرها المستخدم عن نفسه لحفظها في الذاكرة، أو فارغ"
}}

قواعد الأوامر:
1. إذا طلب أغنية أو موسيقى أو ذكر اسم فنان أو أغنية (مثال: "شغلي اغنية كاظم الساهر", "ابحثي عن اغنية وشغليها", "سمعيني اغنية ...", "شغليلي سيف نبيل", "كاظم الساهر", "اريد اغنية ..."):
   - خاصة إذا كان سياق الحديث السابق أنكِ سألته عن الأغنية التي يريدها وذكر لك اسم فنان أو أغنية!
   - intent_type: "song_search"
   - song_query: اسم الأغنية أو الفنان المطلوب بدقة للبحث في الإنترنت (مثال: "كاظم الساهر", "سيف نبيل", "زيد الحبيب")
   - reply_text: كلام ترحيبي عراقي دافئ ومختصر يبشره بتشغيل الأغنية فوراً (مثلاً: "تدلل يا بعد عيوني، هسة لكيت الأغنية وجاي اشغلها الك!").
2. إذا طلب قصة (مثال: "اقريلي قصة", "احجيلي سالفة عن ...", "سولفيلي قصة كاملة"):
   - intent_type: "read_story"
   - reply_text: اسردي له قصة عراقية كاملة ومفصلة بدون توقف ذات بداية وأحداث ونهاية جميلة.
3. إذا طلب التوقف (مثال: "وقفي", "كافي", "اسكتي", "stop"):
   - intent_type: "stop"
   - reply_text: "تدلل عيوني، وقفت كلشي وسكتت."
4. في المحادثة العادية:
   - intent_type: "chat"
   - أجيبي بحرارة وعفوية وأسلوب عراقي جذاب واستفيدي من الذاكرة إذا كان هناك سياق سابق.
"""
    MODELS_TO_TRY = [
        "models/gemini-3.5-flash-lite",
        "models/gemini-3.1-flash-lite",
        "models/gemini-flash-lite-latest",
        "models/gemini-2.5-flash"
    ]

    with open(wav_file, "rb") as f:
        audio_bytes = f.read()

    last_error = None
    for mname in MODELS_TO_TRY:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                mname,
                generation_config={"response_mime_type": "application/json"}
            )
            res = model.generate_content([prompt, {"mime_type": "audio/wav", "data": audio_bytes}])
            return json.loads(res.text.strip())
        except Exception as e:
            last_error = e
            time.sleep(0.3)

    return {
        "user_text": "",
        "voice_tone": "عفوي ✨",
        "intent_type": "chat",
        "song_query": "",
        "reply_text": "سمعتك عيوني، بس الصوت ما جان واضح، كلي مرة ثانية وأني اسمعك.",
        "new_fact_to_remember": ""
    }

# ----------------------------------------------------------------------
# Text Interaction via Web Dashboard
# ----------------------------------------------------------------------
def process_text_with_gemini(user_text, config):
    char_name = config.get("character_name", "هيلين")
    user_name = config.get("user_nickname", "عيوني")
    dialect = config.get("dialect", "baghdadi")
    rel_style = config.get("relationship_style", "Romantic")
    romance = config.get("romance_level", 95)
    boldness = config.get("boldness_level", 90)
    humor = config.get("humor_level", 90)
    api_key = config.get("api_key", DEFAULT_API_KEY)

    memory_context = memory.get_context_prompt()

    prompt = f"""
أنتِ المساعد العراقي الذكي واسمكِ: "{char_name}".
تتحدثين مع: {user_name} باللهجة ({dialect}).
العلاقة: {rel_style}. الرومانسية: {romance}%. الجراءة: {boldness}%. المزاح: {humor}%.

{memory_context}

المستخدم كتب: "{user_text}"

أرجعي JSON حصراً:
{{
  "voice_tone": "نبرة كتابية دافئة 💖",
  "intent_type": "chat | song_search | read_story | stop",
  "song_query": "اسم الأغنية إن وجدت، وإلا فارغ",
  "reply_text": "رد هيلين العراقي الصوتي البشري المباشر",
  "new_fact_to_remember": "معلومة جديدة ذكرها المستخدم، أو فارغ"
}}

قواعد:
- إذا طلب أغنية أو موسيقى أو ذكر اسم فنان أو أغنية (مثل: "شغلي كاظم الساهر", "سيف نبيل", "اغنية زيد الحبيب"): intent_type: "song_search"، وضعي اسم الأغنية أو الفنان في song_query، وردي: "تدلل يا روحي، هسة لكيت الأغنية وجاي اشغلها الك!".
- إذا طلب قصة: intent_type: "read_story"، واكتبي قصة كاملة ومفصلة.
- إذا طلب التوقف ("وقفي", "كافي", "اسكتي"): intent_type: "stop"، وردي "تدلل عيوني، وقفت وسكتت."
- في المحادثة العادية: ردي بأسلوب عراقي بشري جذاب وحميمي.
"""
    MODELS_TO_TRY = [
        "models/gemini-3.5-flash-lite",
        "models/gemini-3.1-flash-lite",
        "models/gemini-flash-lite-latest",
        "models/gemini-2.5-flash"
    ]
    for mname in MODELS_TO_TRY:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                mname,
                generation_config={"response_mime_type": "application/json"}
            )
            res = model.generate_content(prompt)
            return json.loads(res.text.strip())
        except Exception:
            time.sleep(0.3)

    return {
        "voice_tone": "نبرة ودية 💖",
        "intent_type": "chat",
        "song_query": "",
        "reply_text": f"هلا بيك يا {user_name}، فدوة لعينك، أني وياك تدلل بأي وكت.",
        "new_fact_to_remember": ""
    }

# ----------------------------------------------------------------------
# Gemini Live TTS Voice Synthesis
# ----------------------------------------------------------------------
def synthesize_gemini_live_speech(reply_text, config, out_wav="gemini_live_reply.wav"):
    """
    Synthesize human-like speech with Gemini Live TTS model.
    Voices: Female (Kore, Aoede, Leda), Male (Puck, Fenrir, Charon).
    """
    voice = config.get("voice_name", "Kore")
    api_key = config.get("api_key", DEFAULT_API_KEY)
    genai.configure(api_key=api_key)

    tts_models = [
        "models/gemini-2.5-flash-preview-tts",
        "models/gemini-3.8-flash-tts",
        "models/gemini-3.8-flash-lite-tts",
        "models/gemini-2.5-pro-preview-tts"
    ]

    for mname in tts_models:
        try:
            model = genai.GenerativeModel(mname)
            resp = model.generate_content(
                reply_text,
                generation_config={
                    "response_modalities": ["AUDIO"],
                    "speech_config": {
                        "voice_config": {
                            "prebuilt_voice_config": {
                                "voice_name": voice
                            }
                        }
                    }
                }
            )
            raw_parts = []
            if resp.candidates and resp.candidates[0].content:
                for part in resp.candidates[0].content.parts:
                    if hasattr(part, "inline_data") and part.inline_data:
                        raw_parts.append(part.inline_data.data)
            if raw_parts:
                raw = b"".join(raw_parts)
                if len(raw) % 2 != 0:
                    raw = raw[:-1]
                
                # Boost volume for crisp speaker output
                audio_arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32)
                peak = np.max(np.abs(audio_arr))
                if peak > 200 and peak < 28000:
                    gain = min(1.7, 31000.0 / peak)
                    audio_arr = np.clip(audio_arr * gain, -32767, 32767).astype(np.int16)
                    raw = audio_arr.tobytes()

                with wave.open(out_wav, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(raw)
                return out_wav
        except Exception as e:
            time.sleep(0.2)

    return None

def speak_response_on_hardware(wav_file):
    """Play speech on speaker with RED speaking LED."""
    remote_wav = "/tmp/gemini_live_reply.wav"
    if not adb_push(wav_file, remote_wav):
        return
    set_led("speaking")  # RED LED
    adb_cmd(f"killall -9 mplayer 2>/dev/null; mplayer -volume 100 {remote_wav}")
    set_led("idle")

# ----------------------------------------------------------------------
# Online Song Search & Playback Engine (yt-dlp)
# ----------------------------------------------------------------------
def _song_player_thread(remote_dest):
    set_led("music")
    adb_cmd(f"killall -9 mplayer 2>/dev/null; mplayer -volume 100 {remote_dest}")
    set_led("idle")

def search_and_play_online_song(query):
    import yt_dlp
    print(f"[🔍] جاري البحث عن الأغنية عبر الإنترنت: {query}...")
    temp_prefix = "online_stream_song"
    for ext in ['m4a', 'mp3', 'webm', 'opus']:
        p = f"{temp_prefix}.{ext}"
        if os.path.exists(p):
            try: os.remove(p)
            except Exception: pass

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best[ext=mp3]/bestaudio',
        'outtmpl': f'{temp_prefix}.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 10,
    }

    song_path = None
    title = query
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            entries = info.get('entries', [info])
            if entries and entries[0]:
                title = entries[0].get('title', query)
        for ext in ['m4a', 'webm', 'mp3', 'opus']:
            p = f"{temp_prefix}.{ext}"
            if os.path.exists(p):
                song_path = p
                break
    except Exception as e:
        print(f"[-] Song download error: {e}")
        return False, query

    if song_path and os.path.exists(song_path):
        print(f"[🎵] تم تنزيل الأغنية بنجاح: {title}")
        remote_dest = "/tmp/current_online_song.m4a"
        adb_push(song_path, remote_dest)
        
        # Start persistent playback in thread so ADB connection remains open throughout the song
        pt = threading.Thread(target=_song_player_thread, args=(remote_dest,), daemon=True)
        pt.start()
        
        update_chat_telemetry(f"أغنية: {query}", f"جاري تشغيل: {title} 🎵")
        return True, title
    return False, query

# ----------------------------------------------------------------------
# Central Interaction Execution
# ----------------------------------------------------------------------
interaction_lock = threading.Lock()

def execute_interaction(analysis_result, config, is_automatic_vad=False):
    with interaction_lock:
        char_name = config.get("character_name", "هيلين")
        user_text = analysis_result.get("user_text", "")
        tone_str = analysis_result.get("voice_tone", "نبرة عفوية ✨")
        intent = analysis_result.get("intent_type", "chat")
        song_query = analysis_result.get("song_query", "")
        reply_text = analysis_result.get("reply_text", "")
        new_fact = analysis_result.get("new_fact_to_remember", "")

        # Ignore false-positive room noises in automatic VAD
        if is_automatic_vad and (not user_text or len(user_text.strip()) < 2):
            print("[-] لم يتم رصد كلمات واضحة (صوت عابر) -> العودة لحالة الاستعداد.")
            set_led("idle")
            return

        print(f"\n[🗣️] المستخدم: {user_text}")
        print(f"[🎭] نبرة الصوت: {tone_str}")
        print(f"[💬] رد {char_name}: {reply_text}")

        update_tone_telemetry(tone_str)
        update_chat_telemetry(user_text, reply_text)

        # 1. Update persistent memory
        if new_fact and new_fact.strip():
            memory.add_fact(new_fact)
        memory.add_interaction(user_text, reply_text, tone_str)

        # 2. Stop command
        if intent == "stop":
            print("[⏹️] أمر إيقاف فوري!")
            adb_cmd("killall -9 mplayer 2>/dev/null")
            set_led("speaking")
            sp_file = synthesize_gemini_live_speech(reply_text, config)
            if sp_file:
                speak_response_on_hardware(sp_file)
            set_led("idle")
            return

        # 3. Answering & speaking with RED LED
        set_led("speaking")
        sp_file = synthesize_gemini_live_speech(reply_text, config)
        if sp_file:
            speak_response_on_hardware(sp_file)

        # 4. Song search online
        if intent == "song_search" and song_query:
            ok, title = search_and_play_online_song(song_query)
            if not ok:
                err_msg = "ما كدرت الكى الأغنية بالإنترنت عيوني، كلي اسمها مرة ثانية وأني حاضر."
                sp = synthesize_gemini_live_speech(err_msg, config)
                if sp: speak_response_on_hardware(sp)
                set_led("idle")
            else:
                set_led("music")
            return

        set_led("idle")

# ----------------------------------------------------------------------
# Responsive Trigger Monitor (Web Dashboard & Button Handler)
# ----------------------------------------------------------------------
def run_trigger_monitor_thread():
    """Checks for Web Dashboard / Hardware Button triggers with instant ~100ms response."""
    while True:
        try:
            # Check trigger file
            raw_trigger = adb_cmd("cat /tmp/ai_trigger 2>/dev/null; rm -f /tmp/ai_trigger")
            trigger = raw_trigger.strip() if raw_trigger else ""

            if trigger == "TEXT":
                raw_user_text = adb_cmd("cat /tmp/ai_text_input 2>/dev/null; rm -f /tmp/ai_text_input")
                user_text = urllib.parse.unquote_plus(raw_user_text.strip()) if raw_user_text else ""
                if user_text:
                    print(f"\n[💬] رسالة كتابية فورية من المتصفح: {user_text}")
                    set_led("thinking")  # BLUE LED
                    config = load_speaker_config()
                    analysis = process_text_with_gemini(user_text, config)
                    analysis["user_text"] = user_text
                    execute_interaction(analysis, config)
                else:
                    set_led("idle")

            elif trigger == "LISTEN":
                print("\n[🎯] تم طلب الاستماع يدوياً (زر المتصفح/المايك)!")
                set_led("listening")  # GREEN LED
                config = load_speaker_config()
                probe = record_probe_audio(duration=2.0)
                cont = record_continuation_audio(duration=2.5)
                full_wav = combine_and_normalize(probe, cont)
                if full_wav:
                    set_led("thinking")  # BLUE LED
                    acoustics = analyze_acoustic_pitch_and_energy(full_wav)
                    analysis = process_audio_with_gemini(full_wav, acoustics, config)
                    execute_interaction(analysis, config)
                set_led("idle")

            time.sleep(0.12)
        except Exception as e:
            time.sleep(0.25)

# ----------------------------------------------------------------------
# Automatic Continuous Hands-Free VAD Daemon
# ----------------------------------------------------------------------
def run_automatic_speaker_daemon():
    print("=" * 70)
    print("🚀 انطلاق المساعد العراقي التلقائي (\"هيلين - Helen\")")
    print("• الاستماع التلقائي مستمر بدون الحاجة للضغط على زر المايك (Full Hands-Free VAD)")
    print("• الألوان التفاعلية الحية:")
    print("  🟢 الأخضر: عند تحدث المستخدم (استماع)")
    print("  🔵 الأزرق: عند تفكير المساعد")
    print("  🔴 الأحمر: عند إجابة ونطق المساعد")
    print("• ميزة البحث عن الأغاني وتشغيلها عبر الإنترنت (yt-dlp)")
    print("• ميزة قراءة القصص الكاملة وسردها بدون توقف إلا عند أمر التوقف")
    print("• نظام الذاكرة الدائمة (Helen Memory) لحفظ معلومات وتفضيلات المستخدم")
    print("=" * 70)

    # Initialize speaker state
    adb_cmd("rm -f /tmp/ai_trigger /tmp/ai_text_input")
    set_led("idle")
    update_tone_telemetry("نبرة هادئة ورومانسية 💖")

    # Start trigger monitor thread for instant text & button responsiveness
    t = threading.Thread(target=run_trigger_monitor_thread, daemon=True)
    t.start()
    print("[⚡] تم تفعيل مراقب الرسائل الكتابية والأزرار الفوري (Instant Responsive Trigger Monitor)")

    was_playing_music = False

    while True:
        try:
            # Check mode: Only listen in AI mode
            cur_mode = adb_cmd("cat /tmp/speaker_current_mode 2>/dev/null") or "AI"
            if cur_mode != "AI":
                time.sleep(2)
                continue

            # If playing audio or interaction in progress, pause VAD probe to avoid self-hearing
            playing = adb_cmd("ps | grep -v grep | grep mplayer | grep -v '\\[mplayer\\]'")
            if playing:
                was_playing_music = True
                time.sleep(0.5)
                continue
            elif was_playing_music:
                was_playing_music = False
                set_led("idle")

            if interaction_lock.locked():
                time.sleep(0.3)
                continue

            # Automatic Voice Activity Probe
            probe_wav = record_probe_audio(duration=1.4)
            if not probe_wav:
                time.sleep(0.15)
                continue

            has_speech, rms, peak = check_voice_activity(probe_wav, threshold_rms=0.0072, threshold_peak=0.028)

            if has_speech and not interaction_lock.locked():
                print(f"\n[🎙️] رصد صوت بشري تلقائياً! (RMS: {rms:.4f}, Peak: {peak:.4f})")
                set_led("listening")  # GREEN LED!

                cont_wav = record_continuation_audio(duration=2.2)
                full_wav = combine_and_normalize(probe_wav, cont_wav)

                if full_wav:
                    set_led("thinking")  # BLUE LED!
                    config = load_speaker_config()
                    acoustics = analyze_acoustic_pitch_and_energy(full_wav)
                    analysis = process_audio_with_gemini(full_wav, acoustics, config)
                    execute_interaction(analysis, config, is_automatic_vad=True)

                set_led("idle")
            else:
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n[!] تم إيقاف الخدمة يدوياً.")
            break
        except Exception as e:
            print(f"[-] تنبيه في حلقة التشغيل: {e}")
            set_led("idle")
            time.sleep(1)

if __name__ == "__main__":
    run_automatic_speaker_daemon()
