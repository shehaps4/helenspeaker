# دليل البناء والتثبيت والتشغيل الشامل (Build & Installation Guide)
## مشروع المساعد الصوتي العراقي الذكي (Iraqi AI Smart Speaker)

---

## 1. متطلبات النظام الأساسية (Prerequisites)

* **نظام التشغيل:** Windows 10/11 أو Linux
* **حزمة Java Development Kit:** JDK 17 أو OpenJDK 21 LTS (المتوفرة مع Android Studio)
* **بيئة Android SDK:** Android SDK Platforms 34/35 و Build-tools 34.0.0
* **مترجم Python:** Python 3.10+ مع مكتبات `soundfile`, `requests`, `gtts`, `speech_recognition`, `fastapi`, `uvicorn`
* **أداة ADB:** Android Debug Bridge (متصلة بالسماعة عبر منفذ USB OTG)

---

## 2. بناء تطبيق Android (APK Build)

1. انتقل إلى مجلد تطبيق الأندرويد:
   ```bash
   cd android-app
   ```
2. تأكد من ضبط مسارات `JAVA_HOME` و `ANDROID_HOME`:
   ```powershell
   $env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
   $env:ANDROID_HOME = "C:\Users\Th3painter\AppData\Local\Android\Sdk"
   ```
3. نفّذ أمر البناء لإنشاء حزمة الـ Debug APK:
   ```powershell
   .\gradlew.bat assembleDebug
   ```
4. ستجد ملف الـ APK الناتج في المسار:
   ```text
   android-app/app/build/outputs/apk/debug/app-debug.apk
   ```
5. لتثبيت التطبيق مباشرة على هاتفك المتصل:
   ```powershell
   adb install -r android-app/app/build/outputs/apk/debug/app-debug.apk
   ```

---

## 3. تشغيل خادم البوابة والذكاء الاصطناعي (Backend Gateway)

1. قم بتثبيت المتطلبات إن لم تكن مثبتة:
   ```bash
   pip install fastapi uvicorn soundfile requests gtts speechrecognition
   ```
2. شغّل خادم البوابة التفاعلي:
   ```bash
   python backend/server.py
   ```
   * سيعمل الخادم على المنفذ `8000` (`http://localhost:8000`).
   * يوفر مسار التحقق الصحي `/api/v1/health` ومسارات مزامنة الإعدادات والتحكم.

---

## 4. تشغيل المساعد الصوتي على السماعة (Speaker Deployment)

### الخيار أ: وضع الـ Daemon المباشر (Native Daemon Mode)
1. إنشاء مجلد العمل الدائم داخل قسم المستخدم في السماعة:
   ```bash
   adb shell "mkdir -p /usr/data/iraqi_speaker"
   ```
2. تشغيل عفريت التحكم `speaker-runtime`:
   ```bash
   python speaker-runtime/daemon.py
   ```
   * يتصل بالسماعة ويتحكم بإضاءة الـ RGB (شريحة AW2015) ومستوى الصوت والميكروفونات.

### الخيار ب: وضع الرفيق عبر الهاتف (Companion Mode)
* في حال استخدام السماعة عبر البلوتوث العادي (A2DP)، يقوم تطبيق Android بالتقاط الصوت عبر الهاتف أو ميكروفون البلوتوث، ومعالجة المحادثة بـ Gemini Live، ثم بث الرد الصوتي العراقي عبر السماعة مباشرة بدون الحاجة لتثبيت برمجيات داخلية.

---

## 5. اختبار المنظومة وتشغيل الاختبارات الآلية (Testing)

لتشغيل حزمة الاختبارات الآلية الشاملة:
```bash
python -m unittest discover tests
```
تتحقق الاختبارات من:
* حساب وتدقيق مجاميع التحقق التشفيرية (SHA-256 Checksums).
* دقة بناء نصوص الشخصيات واللهجة العراقية (Iraqi Persona Prompts).
* محددات الأمان في استدعاء الدوال العتادية (Tool Boundaries).
* دقة تحويل الألوان والسطوع لمتحكم AW2015 RGB.
