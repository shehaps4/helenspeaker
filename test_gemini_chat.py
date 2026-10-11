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
المستخدم كتب: "شلونج هيلين مشتاقلك"

أرجعي JSON حصراً بهذا المخطط:
{
  "voice_tone": "نبرة ودية 💖",
  "intent_type": "chat",
  "song_query": "",
  "reply_text": "رد هيلين العراقي الصوتي البشري",
  "new_fact_to_remember": ""
}
"""

res = model.generate_content(prompt)
print("Raw response:\n", res.text)
data = json.loads(res.text)
print("Parsed reply_text:", data.get("reply_text"))
