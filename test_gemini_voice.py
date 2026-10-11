import wave
import os
import time
import google.generativeai as genai

API_KEY = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=API_KEY)

models_to_try = [
    "models/gemini-2.5-flash-preview-tts",
    "models/gemini-3.1-flash-tts-preview",
    "models/gemini-3.8-flash-tts",
    "models/gemini-2.5-pro-preview-tts"
]

text = "يا هلا ومية هلا بيك عيوني، اني ريام ومساعدتك العراقية الذكية، شلونك شخبارك؟"

for mname in models_to_try:
    print(f"[*] Trying model: {mname}")
    try:
        model = genai.GenerativeModel(mname)
        resp = model.generate_content(
            text,
            generation_config={
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": "Kore"
                        }
                    }
                }
            }
        )
        audio_saved = False
        for part in resp.candidates[0].content.parts:
            if hasattr(part, "inline_data") and part.inline_data:
                clean_name = mname.replace("models/", "").replace("/", "_")
                fname = f"{clean_name}.wav"
                with wave.open(fname, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(part.inline_data.data)
                print(f"[+] SUCCESS with {mname}! Saved to {fname}, size: {os.path.getsize(fname)} bytes")
                audio_saved = True
                break
        if audio_saved:
            break
    except Exception as e:
        print(f"[-] Error with {mname}: {e}")
        time.sleep(2)
