"""
掼蛋实时助手 - Android APK版本
主程序入口
"""
import os
import sys
from kivy.config import Config

# Android平台特殊配置
if os.environ.get('ANDROID_ARGUMENT', None):
    Config.set('graphics', 'width', '1080')
    Config.set('graphics', 'height', '1920')
    Config.set('graphics', 'fullscreen', '0')
    Config.set('input', 'mouse', 'mouse')

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.utils import platform

# 导入自定义模块
from src.ui.main_window import MainWindow
from src.ui.overlay import CardCounterOverlay
from src.float_window import FloatWindowManager
from src.card_counter import CardCounter
from src.screen_capture import ScreenCaptureManager
from src.card_recognizer import CardRecognizer


class GuandanAssistantApp(App):
    """掼蛋实时助手主应用"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.card_counter = CardCounter()
        self.recognizer = CardRecognizer()
        self.screen_capture = None
        self.float_manager = None
        self.overlay = None
        self.monitoring = False

    def build(self):
        """构建应用界面"""
        # 创建主窗口
        sm = ScreenManager()
        sm.add_widget(MainWindow(name='main'))
        
        # 初始化悬浮窗（仅Android平台）
        if platform == 'android':
            self._init_android_services()
        
        return sm

    def _init_android_services(self):
        """初始化Android服务"""
        try:
            from jnius import autoclass
            from android.runnable import run_on_ui_thread
            
            # 初始化悬浮窗管理器
            self.float_manager = FloatWindowManager()
            self.float_manager.create_overlay()
            
            # 初始化截屏管理器
            self.screen_capture = ScreenCaptureManager()
            
            print("[GuandanAssistant] Android服务初始化成功")
        except ImportError as e:
            print(f"[GuandanAssistant] Android服务初始化失败: {e}")
            # 在桌面环境中使用模拟模式
            self._init_desktop_mode()

    def _init_desktop_mode(self):
        """桌面开发调试模式"""
        print("[GuandanAssistant] 运行在桌面调试模式")
        # 创建模拟的悬浮窗UI
        from kivy.uix.floatlayout import FloatLayout
        from kivy.uix.label import Label
        
        Window.add_widget(
            CardCounterOverlay(card_counter=self.card_counter)
        )

    def on_start(self):
        """应用启动时"""
        print("[GuandanAssistant] 应用已启动")
        
        # Android平台启动前台服务
        if platform == 'android' and self.float_manager:
            try:
                from android import mActivity
                from jnius import JavaMethod
                
                # 请求必要的权限已在AndroidManifest中声明
                # 悬浮窗权限需要用户手动授权
                self.float_manager.request_overlay_permission()
                
            except Exception as e:
                print(f"[GuandanAssistant] 启动服务失败: {e}")

    def on_pause(self):
        """应用暂停时"""
        print("[GuandanAssistant] 应用暂停")
        if self.screen_capture:
            self.screen_capture.pause()
        return True

    def on_resume(self):
        """应用恢复时"""
        print("[GuandanAssistant] 应用恢复")
        if self.screen_capture and self.monitoring:
            self.screen_capture.resume()

    def on_stop(self):
        """应用停止时"""
        print("[GuandanAssistant] 应用停止")
        self.stop_monitoring()
        
        # 清理Android服务
        if platform == 'android' and self.float_manager:
            self.float_manager.destroy_overlay()

    def start_monitoring(self):
        """开始监控"""
        if not self.monitoring and self.screen_capture:
            self.monitoring = True
            self.screen_capture.start_capture(self._on_capture)
            print("[GuandanAssistant] 开始监控")

    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.screen_capture:
            self.screen_capture.stop_capture()
            print("[GuandanAssistant] 停止监控")

    def _on_capture(self, image_data):
        """截屏回调"""
        if not image_data:
            return
            
        try:
            # 识别牌面
            cards = self.recognizer.recognize(image_data)
            
            if cards:
                # 更新记牌器
                self.card_counter.update(cards)
                
                # 更新悬浮窗显示
                if self.overlay:
                    self.overlay.update_display(self.card_counter.get_state())
                    
        except Exception as e:
            print(f"[GuandanAssistant] 处理截屏失败: {e}")

    def toggle_float_window(self, show):
        """切换悬浮窗显示"""
        if self.float_manager:
            if show:
                self.float_manager.show_overlay()
            else:
                self.float_manager.hide_overlay()

    def get_card_counter(self):
        """获取记牌器实例"""
        return self.card_counter


def main():
    """应用入口"""
    GuandanAssistantApp().run()


if __name__ == '__main__':
    main()
