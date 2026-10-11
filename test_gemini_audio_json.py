import google.generativeai as genai
import json
import time

genai.configure(api_key="YOUR_GEMINI_API_KEY_HERE")
model = genai.GenerativeModel(
    "models/gemini-2.5-flash",
    generation_config={"response_mime_type": "application/json"}
)

prompt = """
أنتِ المساعد العراقي الذكي واسمكِ "هيلين".
المستخدم يتحدث معكِ باللهجة العراقية.
استمعي للتسجيل الصوتي بدقة.
حللي نبرة صوت المتحدث بدقة (مثال: نبرة هادئة ورومانسية، نبرة متضايقة أو حزينة، نبرة معصبة ومستعجلة، نبرة مرحة ومشاكسة، نبرة تعبانة...).
أعيدي النتيجة بصيغة JSON حصراً بهذا المخطط:
{
  "user_text": "النص المنطوق بدقة باللهجة العراقية",
  "voice_tone": "وصف دقيق لنبرة صوت المتحدث ومشاعره",
  "is_story_request": false,
  "is_music_request": "none",
  "reply_text": "رد هيلين العراقي العفوي السريع والمناسب لنبرة صوته"
}
"""

with open("test_mono.wav", "rb") as f:
    audio_bytes = f.read()

t0 = time.time()
res = model.generate_content([prompt, {"mime_type": "audio/wav", "data": audio_bytes}])
t1 = time.time()

with open("out_res.json", "w", encoding="utf-8") as out:
    out.write(res.text)

print(f"Elapsed: {t1 - t0:.2f}s")
