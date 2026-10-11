# دليل إعداد وتكامل Gemini Live API (Gemini Live Integration Guide)
## مشروع المساعد الصوتي العراقي الذكي (Iraqi AI Smart Speaker)

---

## 1. الحصول على مفتاح API (Google AI Studio)

1. توجه إلى [Google AI Studio](https://aistudio.google.com/).
2. سجّل الدخول بحساب Google الخاص بك.
3. انقر على **"Get API key"** ثم **"Create API key in new project"**.
4. انسخ المفتاح، وقم بتعيينه في بيئة العمل الخاصة بك:
   ```bash
   export GEMINI_API_KEY="AIzaSy..."
   ```
   أو في PowerShell:
   ```powershell
   $env:GEMINI_API_KEY = "AIzaSy..."
   ```

---

## 2. النماذج المدعومة وسجل النماذج (Model Registry)

| معرّف النموذج (Model ID) | القدرات الصوتية | حالة النموذج في المشروع | معدل التردد الصوتي |
|---|---|---|---|
| **`gemini-3.8-live`** | محادثة صوتية ثنائية الاتجاه (Audio-to-Audio) + أدوات | **النموذج الأساسي المعتمد** | 16 kHz In / 24 kHz Out |
| **`gemini-2.0-flash-exp`** | محادثة متعددة الوسائط فورية مع المقاطعة | بديل مباشر للمحادثة اللحظية | 16 kHz In / 24 kHz Out |
| **`gemini-1.5-flash`** | خط أنابيب (Speech-to-Text -> Text -> TTS) | بديل عند بطء الشبكة | مخصص للنصوص |
| **`offline-fallback`** | محرك محلي لمعالجة الأوامر دون إنترنت | وضع الطوارئ عند انقطاع الشبكة | 16 kHz Mono |

---

## 3. إعدادات الجلسة الصوتية الحية (Live Session Configuration)

عند فتح جلسة مع Gemini Live:
1. **تنسيق الصوت الوارد (Input Audio):**
   * الترميز: PCM 16-bit Little Endian.
   * القنوات: Mono (قناة واحدة).
   * معدل العينات: 16,000 هرتز.
2. **تنسيق الصوت الصادر (Output Audio):**
   * الترميز: PCM 16-bit أو 24 kHz PCM.
   * يتم تغذيته مباشرة إلى مضخم الصوت الداخلي عبر المشغّل `mplayer` ومتحكم ALSA.
3. **خاصية المقاطعة الطبيعية (Barge-in):**
   * بمجرد أن يلتقط ميكروفون السماعة صوتاً بشرياً أثناء تحدث المساعد، يتم فوراً قطع البث وتصفير المخزن المؤقت للـ DAC للعودة إلى وضع الاستماع بدون أي تأخير.
