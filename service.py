"""
SmartSRS Background Service - Ultimate Version
يعمل في الخلفية حتى مع قفل الشاشة وتفعيل توفير البطارية
"""

from time import sleep, time
from jnius import autoclass, cast
from android import AndroidService
import os

# فترات التكرار بالثواني: 10ث، 1د، 5د، 30د، 1س
INTERVALS = [10, 60, 300, 1800, 3600]

class SmartSRSService:
    def __init__(self):
        self.service = None
        self.context = None
        self.wakelock = None
        self.audio_manager = None
        self.current_player = None
        self.alarm_manager = None
        
    def setup_android_service(self):
        """إعداد الخدمة والحصول على Context"""
        try:
            PythonService = autoclass('org.kivy.android.PythonService')
            self.service = PythonService.mService
            self.context = cast(autoclass('android.content.Context'), self.service)
            return True
        except Exception as e:
            print(f"❌ Service setup failed: {e}")
            return False
    
    def acquire_wakelock(self):
        """الحصول على WakeLock لمنع النوم"""
        try:
            PowerManager = autoclass('android.os.PowerManager')
            Context = autoclass('android.content.Context')
            
            pm = self.context.getSystemService(Context.POWER_SERVICE)
            pm = cast(PowerManager, pm)
            
            # PARTIAL_WAKE_LOCK = 1
            self.wakelock = pm.newWakeLock(1, "SmartSRS:WakeLock")
            self.wakelock.acquire()
            print("✅ WakeLock acquired")
            return True
        except Exception as e:
            print(f"❌ WakeLock failed: {e}")
            return False
    
    def setup_audio_manager(self):
        """إعداد Audio Manager للتحكم بالصوت"""
        try:
            Context = autoclass('android.content.Context')
            AudioManager = autoclass('android.media.AudioManager')
            
            self.audio_manager = self.context.getSystemService(Context.AUDIO_SERVICE)
            self.audio_manager = cast(AudioManager, self.audio_manager)
            print("✅ Audio Manager ready")
            return True
        except Exception as e:
            print(f"❌ Audio Manager failed: {e}")
            return False
    
    def create_notification_channel(self):
        """إنشاء قناة الإشعارات (Android 8+)"""
        try:
            NotificationChannel = autoclass('android.app.NotificationChannel')
            NotificationManager = autoclass('android.app.NotificationManager')
            Context = autoclass('android.content.Context')
            
            nm = self.context.getSystemService(Context.NOTIFICATION_SERVICE)
            nm = cast(NotificationManager, nm)
            
            # IMPORTANCE_HIGH = 4
            channel = NotificationChannel(
                "smartsrs_channel",
                "SmartSRS Reviews",
                4
            )
            channel.setDescription("Spaced Repetition System Active")
            channel.enableVibration(False)
            channel.setSound(None, None)
            
            nm.createNotificationChannel(channel)
            print("✅ Notification channel created")
            return True
        except Exception as e:
            print(f"❌ Notification channel failed: {e}")
            return False
    
    def start_foreground_service(self):
        """تشغيل الخدمة في المقدمة (Foreground Service)"""
        try:
            NotificationBuilder = autoclass('android.app.Notification$Builder')
            
            notification = NotificationBuilder(self.context, "smartsrs_channel") \
                .setContentTitle("SmartSRS Active 🎯") \
                .setContentText("Spaced repetition running in background") \
                .setSmallIcon(17301543) \
                .setOngoing(True) \
                .setPriority(2) \
                .build()
            
            self.service.startForeground(1001, notification)
            print("✅ Foreground service started")
            return True
        except Exception as e:
            print(f"❌ Foreground service failed: {e}")
            return False
    
    def play_audio(self, file_path):
        """تشغيل الملف الصوتي مع Audio Focus"""
        try:
            # طلب Audio Focus
            # AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK = 3
            # AUDIOFOCUS_REQUEST_GRANTED = 1
            AudioManager = autoclass('android.media.AudioManager')
            focus_result = self.audio_manager.requestAudioFocus(
                None,
                AudioManager.STREAM_MUSIC,
                3
            )
            
            if focus_result != 1:
                print("⚠️ Audio focus not granted, playing anyway...")
            
            # إنشاء MediaPlayer
            MediaPlayer = autoclass('android.media.MediaPlayer')
            
            # إيقاف المشغل السابق إن وجد
            if self.current_player:
                try:
                    self.current_player.stop()
                    self.current_player.release()
                except:
                    pass
            
            self.current_player = MediaPlayer()
            self.current_player.setDataSource(file_path)
            
            # استخدام مكبر الصوت (Speaker)
            self.current_player.setAudioStreamType(3)  # STREAM_MUSIC
            
            # رفع مستوى الصوت
            max_vol = self.audio_manager.getStreamMaxVolume(3)
            self.audio_manager.setStreamVolume(3, int(max_vol * 0.7), 0)
            
            self.current_player.prepare()
            self.current_player.start()
            
            print(f"▶️ Playing: {os.path.basename(file_path)}")
            
            # الانتظار حتى انتهاء التشغيل
            while self.current_player.isPlaying():
                sleep(0.5)
            
            # التنظيف
            self.current_player.release()
            self.current_player = None
            self.audio_manager.abandonAudioFocus(None)
            
            print("✅ Audio playback completed")
            return True
            
        except Exception as e:
            print(f"❌ Audio playback failed: {e}")
            return False
    
    def schedule_alarm(self, delay_seconds, request_code):
        """جدولة منبه دقيق (Exact Alarm) للتشغيل التالي"""
        try:
            if not self.alarm_manager:
                AlarmManager = autoclass('android.app.AlarmManager')
                Context = autoclass('android.content.Context')
                self.alarm_manager = self.context.getSystemService(Context.ALARM_SERVICE)
                self.alarm_manager = cast(AlarmManager, self.alarm_manager)
            
            Intent = autoclass('android.content.Intent')
            PendingIntent = autoclass('android.app.PendingIntent')
            SystemClock = autoclass('android.os.SystemClock')
            
            # إنشاء Intent للخدمة
            intent = Intent(self.context, autoclass('org.mysrs.smartsrs.ServiceSrsservice'))
            intent.setAction(f"ALARM_TRIGGER_{request_code}")
            
            # FLAG_IMMUTABLE = 0x04000000
            pending_intent = PendingIntent.getService(
                self.context,
                request_code,
                intent,
                0x04000000
            )
            
            # حساب وقت التشغيل
            trigger_time = SystemClock.elapsedRealtime() + (delay_seconds * 1000)
            
            # جدولة المنبه
            # ELAPSED_REALTIME_WAKEUP = 2
            try:
                self.alarm_manager.setExactAndAllowWhileIdle(2, trigger_time, pending_intent)
                print(f"⏰ Alarm scheduled in {delay_seconds}s (code: {request_code})")
            except:
                # Fallback
                self.alarm_manager.setExact(2, trigger_time, pending_intent)
                print(f"⏰ Alarm scheduled (fallback) in {delay_seconds}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Alarm scheduling failed: {e}")
            return False

def run_service():
    """Main service loop"""
    print("=" * 50)
    print("🚀 SmartSRS Service Starting...")
    print("=" * 50)
    
    # إنشاء كائن الخدمة
    srs = SmartSRSService()
    
    # إعداد الخدمة
    if not srs.setup_android_service():
        print("❌ Failed to initialize service")
        return
    
    # الحصول على WakeLock
    srs.acquire_wakelock()
    
    # إعداد Audio
    srs.setup_audio_manager()
    
    # إنشاء قناة الإشعارات
    srs.create_notification_channel()
    
    # بدء Foreground Service
    srs.start_foreground_service()
    
    # مسار ملف التكوين
    app_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(app_dir, "srs_config.txt")
    
    # متغيرات الحالة
    current_audio_file = None
    next_play_time = 0
    current_interval_index = 0
    
    print("✅ Service ready - Waiting for commands...")
    print("=" * 50)
    
    # الحلقة الرئيسية
    while True:
        try:
            # قراءة ملف التكوين
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    command = f.read().strip()
                
                # أمر الإيقاف
                if command == "STOP":
                    print("🛑 Stop command received")
                    current_audio_file = None
                    next_play_time = 0
                    current_interval_index = 0
                    os.remove(config_file)
                    continue
                
                # ملف صوتي جديد
                if command and command != current_audio_file:
                    if os.path.exists(command):
                        print(f"📁 New audio file: {os.path.basename(command)}")
                        current_audio_file = command
                        current_interval_index = 0
                        
                        # تشغيل فوري
                        srs.play_audio(current_audio_file)
                        
                        # جدولة التكرارات القادمة
                        for i, interval in enumerate(INTERVALS):
                            srs.schedule_alarm(interval, 100 + i)
                        
                        # تحديد وقت التشغيل التالي
                        next_play_time = time() + INTERVALS[0]
                        
                        # حذف ملف التكوين
                        os.remove(config_file)
                    else:
                        print(f"❌ File not found: {command}")
                        os.remove(config_file)
            
            # تشغيل تلقائي حسب الجدول
            if current_audio_file and next_play_time > 0:
                if time() >= next_play_time:
                    print(f"🔄 Auto-play (interval #{current_interval_index + 1})")
                    srs.play_audio(current_audio_file)
                    
                    current_interval_index += 1
                    
                    # تحديد الوقت التالي أو الإنهاء
                    if current_interval_index < len(INTERVALS):
                        next_play_time = time() + INTERVALS[current_interval_index]
                    else:
                        print("✅ Review session completed")
                        current_audio_file = None
                        next_play_time = 0
                        current_interval_index = 0
            
            # نوم قصير لتوفير البطارية
            sleep(2)
            
        except Exception as e:
            print(f"❌ Service error: {e}")
            sleep(5)

# نقطة البداية
if __name__ == '__main__':
    run_service()
