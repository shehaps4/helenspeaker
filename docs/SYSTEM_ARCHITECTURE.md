# بنية المنظومة والتصميم الهندسي (System Architecture & Security Specification)
## مشروع المساعد الصوتي العراقي الذكي (Iraqi AI Smart Speaker)

---

## 1. الهيكل العام للـ Monorepo

```text
/iraqi-ai-smart-speaker
├── /android-app             # تطبيق التحكم الأصلي (Kotlin + Jetpack Compose Material 3)
│   ├── /app/src/main/java   # Presentation, Domain, Data, Connectivity, Gemini Client
│   └── /app/src/main/res    # الموارد، الثيمات، وسلاسل النصوص العربية RTL
├── /speaker-runtime         # عفريت التشغيل على نظام لينكس المدمج (Python/C Socket Server)
├── /firmware-adapters       # طبقة التجريد العتادي للوحة Ingenic X1800 ومتحكم AW2015 RGB
├── /backend                 # خادم البوابة وإدارة الجلسات اللحظية ورموز التوثيق المؤقتة
├── /shared-protocol         # مخطط الإعدادات الموحد (JSON Schema) ومجاميع التحقق SHA-256
├── /tools                   # أدوات الفحص العتادي التلقائي (Speaker Scanner) والتهيئة
├── /tests                   # حزمة الاختبارات الآلية للوحدات والبروتوكول والتكامل
└── /docs                    # التوثيق الهندسي، تقارير التوافق، وإرشادات الأمان
```

---

## 2. مخطط تدفق البيانات والتفاعل الصوتي (Sequence Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User as المستخدم العراقي
    participant Mic as مصفوفة الميكروفونات (DMIC)
    participant AW2015 as متحكم الإضاءة (AW2015 RGB)
    participant Daemon as عفريت التشغيل (Speaker Daemon)
    participant Engine as محرك Gemini Live
    participant Speaker as مضخم الصوت (ALSA Codec)

    User->>Mic: تحدث بالسؤال ("شلونك شخبارك؟")
    Daemon->>AW2015: إضاءة باللون السماوي النابض (LISTENING)
    Mic->>Daemon: التقاط 5 قنوات صوتية خام (16kHz PCM)
    Daemon->>Daemon: معالجة DSP (تحويل إلى Mono 16kHz نقي)
    Daemon->>Engine: إرسال مقاطع الصوت اللحظية (Audio Chunks)
    Daemon->>AW2015: تحول للإضاءة العنبرية الثابتة (THINKING)
    Engine->>Engine: معالجة الذكاء الاصطناعي وبناء الرد العراقي
    Engine->>Daemon: بث الرد الصوتي اللحظي
    Daemon->>AW2015: إضاءة خضراء متفاعلة مع الصوت (SPEAKING)
    Daemon->>Speaker: تشغيل الرد عبر مكبر الصوت
    User->>Mic: (مقاطعة / Barge-in) المستخدم يتحدث فجأة
    Daemon->>Speaker: إيقاف الصوت فوراً بدون تأخير
    Daemon->>AW2015: العودة لوضع الاستماع (LISTENING)
```

---

## 3. مخطط آلة الحالات لإضاءة الـ RGB (RGB State Machine)

```mermaid
stateDiagram-v2
    [*] --> OFFLINE: تشغيل الجهاز
    OFFLINE --> IDLE: الاتصال بالشبكة / البوابة
    IDLE --> LISTENING: رصد صوت المستخدم / الضغط على تحدث
    LISTENING --> THINKING: اكتمال التقاط الصوت
    THINKING --> SPEAKING: وصول الرد من Gemini Live
    SPEAKING --> IDLE: اكتمال تشغيل الرد الصوتي
    SPEAKING --> LISTENING: حدوث مقاطعة طبيعية (Barge-in)
    IDLE --> MUSIC: تشغيل الموسيقى العراقية
    MUSIC --> IDLE: إيقاف الموسيقى
    IDLE --> ERROR: فقدان الاتصال / خطأ
    ERROR --> IDLE: استعادة الاتصال
```

---

## 4. نموذج الأمان وإدارة المفاتيح التشفيرية (Security Architecture)

1. **حظر المفاتيح الثابتة:**
   * لا يحتوي ملف الـ APK النهائي أو شفرة المصدر المفتوحة على أي مفاتيح خاصة لـ Gemini API.
2. **بروتوكول الرموز المؤقتة (Ephemeral Token Exchange):**
   * يقوم تطبيق الهاتف بطلب رمز وصول مؤقت مدته 60 دقيقة من مسار `/api/v1/auth/token` في خادم البوابة الخلفي، مما يحمي الحسابات من التسريب.
3. **أمان الذاكرة وتشفير الإعدادات:**
   * كلمات مرور الـ Wi-Fi والبيانات الحساسة تُحفظ في `Android Keystore` مشفرة بنظام AES-256، ولا تُطبع أبداً في سجلات النظام (`Logs`).
4. **تكامل البيانات وسلامة التكوين (Checksum Verification):**
   * كل إرسال لإعدادات الشخصية أو الصوت يتم تذييله بمجموع تحقق تشفيري `SHA-256`. إذا حدث أي تلاعب بالملف في الطريق، ترفض السماعة اعتماده فوراً وتطلب إعادة المزامنة.
