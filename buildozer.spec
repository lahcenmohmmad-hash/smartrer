[app]

# اسم التطبيق كما سيظهر في الهاتف
title = SmartSRS

# اسم الحزمة (يجب أن يكون فريداً)
package.name = smartsrs
package.domain = org.mysrs

# المجلد المصدري للتطبيق
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,mp3,wav,ogg,m4a,json

# رقم الإصدار
version = 5.0

# المكتبات المطلوبة (مهم جداً)
requirements = python3,kivy==2.3.0,android,pyjnius,plyer

# الخدمة الخلفية
services = SRSService:service.py:foreground

# اتجاه الشاشة
orientation = portrait
fullscreen = 0

# الأذونات (شاملة لحل جميع المشاكل)
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,WAKE_LOCK,FOREGROUND_SERVICE,FOREGROUND_SERVICE_MEDIA_PLAYBACK,POST_NOTIFICATIONS,REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,MODIFY_AUDIO_SETTINGS,ACCESS_NOTIFICATION_POLICY,SCHEDULE_EXACT_ALARM,USE_EXACT_ALARM,VIBRATE,RECEIVE_BOOT_COMPLETED

# إعدادات Android API
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# معمارية المعالج
android.archs = arm64-v8a,armeabi-v7a

# إعدادات إضافية
android.allow_backup = True
android.backup_rules = True

# نوع الخدمة
android.service_class_name = org.kivy.android.PythonService

# Manifest Placeholders لحل مشاكل الأذونات
android.manifest_placeholders = [("USE_EXACT_ALARM", "true"), ("SCHEDULE_EXACT_ALARM", "true")]

# نقطة البداية
android.entrypoint = org.kivy.android.PythonActivity

# استخدام master branch لحل مشكلة AAB
p4a.branch = master
p4a.bootstrap = sdl2

# إعدادات Gradle (لحل مشاكل البناء)
android.gradle_dependencies = com.android.support:support-v4:28.0.0

# تفعيل AndroidX
android.enable_androidx = True

[buildozer]

# مستوى السجلات (2 = مفصل)
log_level = 2

# تحذير عند التشغيل كـ root
warn_on_root = 1

# مسار SDK و NDK (اختياري - سيتم تحميلهم تلقائياً)
# android.sdk_path = 
# android.ndk_path =
