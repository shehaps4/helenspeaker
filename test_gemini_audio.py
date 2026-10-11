import sys
import json
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import google.generativeai as genai

api_key = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    "models/gemini-2.5-flash",
    generation_config={"response_mime_type": "application/json"}
)

prompt = """
أنتِ المساعد العراقي الذكي واسمكِ: "هيلين".
تتحدثين باللهجة العراقية البغدادية مع المستخدم: عيوني.
المطلوب: استمعي للتسجيل الصوتي بدقة. أرجعي JSON حصراً:
{
  "user_text": "النص المنطوق بالعراقية",
  "voice_tone": "نبرة المتحدث",
  "intent_type": "chat | song_search | read_story | stop",
  "song_query": "",
  "reply_text": "رد هيلين العراقي الصوتي البشري المباشر",
  "new_fact_to_remember": ""
}
"""

with open("test_tts_helen.wav", "rb") as f:
    audio_bytes = f.read()

res = model.generate_content([prompt, {"mime_type": "audio/wav", "data": audio_bytes}])
print("Audio multimodal response:\n", res.text)
