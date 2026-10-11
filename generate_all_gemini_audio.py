import wave
import os
import time
import google.generativeai as genai

API_KEY = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=API_KEY)

MODELS = [
    "models/gemini-3.1-flash-tts-preview",
    "models/gemini-3.8-flash-tts",
    "models/gemini-2.5-flash-preview-tts"
]

tasks = [
    ("boot_greeting.wav", "يا هلا ومية هلا بيك عيوني، اني ريام ومساعدتك العراقية الذكية، نورتني وكل الهلا بيك!", "Kore"),
    ("mode_ai.wav", "تم إيقاف البلوتوث، ورجعت وياك للمساعد العراقي الذكي عيوني.", "Kore"),
    ("mode_bt.wav", "تم تشغيل البلوتوث، واقترنت ويا جهازك حتى تسمع أحلى طرب.", "Kore"),
    ("config_saved.wav", "تدلل عيوني، تم حفظ وتثبيت كل الإعدادات بذاكرة سماعتي.", "Kore"),
    ("wifi_ok.wav", "متصلة بالواي فاي والإنترنت جاهز، أمرني شمحتاج تدلل!", "Kore"),
    ("preview_Kore.wav", "هلا عيوني، اني نبرة كوري، صوتي ناعم ودافي، ومستعدة لكل سوالفك ورومانسيتك.", "Kore"),
    ("preview_Aoede.wav", "هلو يا الغالي، اني أوييدي، صوتي مفعم بالطاقة والحيوية والضحكة الحلوة.", "Aoede"),
    ("preview_Leda.wav", "يا هلا! اني ليدا، صوتي شبابي ومشاكس، ومستعدة لأحلى غزل ومقالب.", "Leda"),
    ("preview_Puck.wav", "يا هلا بالحبيب! اني باك، صوتي مرح وشبابي، وجاهز للضحك والطرب.", "Puck"),
    ("preview_Fenrir.wav", "أهلاً وسهلاً بيك يا الطيب، اني فينرير، صوتي رجولي فخم وعميق، بخدمتك بأي وقت.", "Fenrir"),
    ("preview_Charon.wav", "مرحباً بيك، اني كارون، نبرتي هادية ورزينة، ومستعد لكل استفساراتك وسوالفك.", "Charon"),
]

out_dir = "gemini_audio_assets"
os.makedirs(out_dir, exist_ok=True)

for fname, text, voice in tasks:
    out_path = os.path.join(out_dir, fname)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        print(f"[SKIP] Already exists: {fname}")
        continue

    print(f"\n[*] Generating: {fname} (Voice: {voice})...")
    success = False

    for mname in MODELS:
        try:
            print(f"    Trying with model {mname}...")
            model = genai.GenerativeModel(mname)
            resp = model.generate_content(
                text,
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
            for part in resp.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    with wave.open(out_path, "wb") as wf:
                        wf.setnchannels(1)
                        wf.setsampwidth(2)
                        wf.setframerate(24000)
                        wf.writeframes(part.inline_data.data)
                    print(f"    [+] SUCCESS! Saved {fname} ({os.path.getsize(out_path)} bytes)")
                    success = True
                    break
            if success:
                break
        except Exception as e:
            print(f"    [-] Failed on {mname}: {e}")
            time.sleep(2)

    time.sleep(3)

print("\n[+] All audio generation completed!")
