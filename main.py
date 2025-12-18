"""
SmartSRS - Spaced Repetition System
برنامج تكرار صوتي متباعد
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.utils import platform
from kivy.core.window import Window
from kivy.clock import Clock
import os

# طلب الأذونات على Android
if platform == 'android':
    from android.permissions import request_permissions, Permission, check_permission
    from jnius import autoclass
    
    # قائمة الأذونات المطلوبة
    PERMISSIONS = [
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.FOREGROUND_SERVICE,
        Permission.WAKE_LOCK,
        Permission.POST_NOTIFICATIONS,
        Permission.SCHEDULE_EXACT_ALARM,
        Permission.USE_EXACT_ALARM,
        Permission.MODIFY_AUDIO_SETTINGS,
        Permission.VIBRATE,
        Permission.RECEIVE_BOOT_COMPLETED
    ]
    
    # طلب الأذونات
    print("📋 Requesting permissions...")
    request_permissions(PERMISSIONS)
    
    # بدء الخدمة الخلفية
    try:
        print("🚀 Starting background service...")
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity
        
        ServiceClass = autoclass('org.mysrs.smartsrs.ServiceSrsservice')
        ServiceClass.start(activity, '')
        print("✅ Service started successfully")
    except Exception as e:
        print(f"⚠️ Service start warning: {e}")

class SmartSRSApp(App):
    def build(self):
        """بناء واجهة التطبيق"""
        
        # ألوان خلفية داكنة
        Window.clearcolor = (0.05, 0.05, 0.05, 1)
        
        # مسار ملف التكوين
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.app_dir, "srs_config.txt")
        
        # حالة التشغيل
        self.is_running = False
        self.selected_file = None
        
        # التخطيط الرئيسي
        layout = BoxLayout(
            orientation='vertical',
            padding=15,
            spacing=10
        )
        
        # العنوان الرئيسي
        title = Label(
            text='[b]SmartSRS[/b]\n[size=14sp]برنامج التكرار المتباعد[/size]',
            markup=True,
            size_hint=(1, 0.12),
            font_size='28sp',
            color=(0, 0.9, 1, 1)
        )
        layout.add_widget(title)
        
        # زر إصلاح البطارية
        btn_battery = Button(
            text='⚡ إصلاح البطارية (ضروري)',
            size_hint=(1, 0.08),
            background_color=(1, 0.5, 0, 1),
            background_normal='',
            font_size='16sp',
            bold=True
        )
        btn_battery.bind(on_press=self.fix_battery_optimization)
        layout.add_widget(btn_battery)
        
        # زر فتح إعدادات الأذونات
        btn_permissions = Button(
            text='🔓 إعدادات الأذونات',
            size_hint=(1, 0.08),
            background_color=(0.2, 0.6, 0.8, 1),
            background_normal='',
            font_size='16sp'
        )
        btn_permissions.bind(on_press=self.open_app_settings)
        layout.add_widget(btn_permissions)
        
        # معلومات الملف المحدد
        self.lbl_status = Label(
            text='اختر ملف صوتي للبدء',
            size_hint=(1, 0.06),
            color=(1, 1, 1, 0.7),
            font_size='14sp'
        )
        layout.add_widget(self.lbl_status)
        
        # متصفح الملفات
        self.file_chooser = FileChooserIconView(
            path='/storage/emulated/0/',
            filters=['*.mp3', '*.wav', '*.m4a', '*.ogg'],
            size_hint=(1, 0.5)
        )
        self.file_chooser.bind(selection=self.on_file_selected)
        layout.add_widget(self.file_chooser)
        
        # معلومات التكرار
        info = Label(
            text='[size=12sp]التكرار: 10ث • 1د • 5د • 30د • 1س[/size]',
            markup=True,
            size_hint=(1, 0.05),
            color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(info)
        
        # زر البدء/الإيقاف
        self.btn_toggle = Button(
            text='▶️ بدء الجلسة',
            size_hint=(1, 0.11),
            background_color=(0, 0.7, 0.3, 1),
            background_normal='',
            font_size='22sp',
            bold=True
        )
        self.btn_toggle.bind(on_press=self.toggle_session)
        layout.add_widget(self.btn_toggle)
        
        return layout
    
    def on_file_selected(self, instance, selection):
        """عند اختيار ملف"""
        if selection:
            self.selected_file = selection[0]
            filename = os.path.basename(self.selected_file)
            self.lbl_status.text = f'✓ {filename}'
            self.lbl_status.color = (0, 1, 0.5, 1)
    
    def toggle_session(self, instance):
        """تشغيل/إيقاف الجلسة"""
        if not self.is_running:
            # بدء الجلسة
            if not self.selected_file:
                self.show_message("تنبيه", "يرجى اختيار ملف صوتي أولاً")
                return
            
            if not os.path.exists(self.selected_file):
                self.show_message("خطأ", "الملف غير موجود")
                return
            
            # كتابة المسار إلى ملف التكوين
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    f.write(self.selected_file)
                
                self.is_running = True
                self.btn_toggle.text = '⏹️ إيقاف الجلسة'
                self.btn_toggle.background_color = (0.8, 0, 0, 1)
                self.lbl_status.text = '▶️ الجلسة نشطة...'
                self.lbl_status.color = (0, 1, 0, 1)
                
                print(f"✅ Session started: {os.path.basename(self.selected_file)}")
                
            except Exception as e:
                self.show_message("خطأ", f"فشل بدء الجلسة: {str(e)}")
        
        else:
            # إيقاف الجلسة
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    f.write("STOP")
                
                self.is_running = False
                self.btn_toggle.text = '▶️ بدء الجلسة'
                self.btn_toggle.background_color = (0, 0.7, 0.3, 1)
                self.lbl_status.text = 'تم إيقاف الجلسة'
                self.lbl_status.color = (1, 1, 0, 1)
                
                print("🛑 Session stopped")
                
            except Exception as e:
                self.show_message("خطأ", f"فشل إيقاف الجلسة: {str(e)}")
    
    def fix_battery_optimization(self, instance):
        """فتح إعدادات استثناءات البطارية"""
        if platform == 'android':
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                Uri = autoclass('android.net.Uri')
                
                activity = PythonActivity.mActivity
                package = activity.getPackageName()
                
                intent = Intent()
                intent.setAction(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
                intent.setData(Uri.parse(f"package:{package}"))
                
                activity.startActivity(intent)
                
                self.show_message(
                    "إعدادات البطارية",
                    "قم بالسماح للتطبيق بالعمل في الخلفية"
                )
                
            except Exception as e:
                self.show_message("خطأ", f"فشل فتح الإعدادات: {str(e)}")
    
    def open_app_settings(self, instance):
        """فتح إعدادات التطبيق"""
        if platform == 'android':
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                Intent = autoclass('android.content.Intent')
                Settings = autoclass('android.provider.Settings')
                Uri = autoclass('android.net.Uri')
                
                activity = PythonActivity.mActivity
                package = activity.getPackageName()
                
                intent = Intent()
                intent.setAction(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                intent.setData(Uri.parse(f"package:{package}"))
                
                activity.startActivity(intent)
                
            except Exception as e:
                self.show_message("خطأ", f"فشل فتح الإعدادات: {str(e)}")
    
    def show_message(self, title, message):
        """عرض رسالة منبثقة"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        lbl = Label(
            text=message,
            font_size='16sp',
            halign='center',
            valign='middle'
        )
        lbl.bind(size=lbl.setter('text_size'))
        content.add_widget(lbl)
        
        btn = Button(
            text='حسناً',
            size_hint=(1, 0.3),
            background_color=(0, 0.7, 1, 1),
            background_normal=''
        )
        content.add_widget(btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        btn.bind(on_press=popup.dismiss)
        popup.open()

# نقطة بداية التطبيق
if __name__ == '__main__':
    SmartSRSApp().run()
