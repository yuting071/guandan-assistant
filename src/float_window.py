"""
Android悬浮窗管理器
使用pyjnius调用Android API实现悬浮窗功能
"""

import threading
from typing import Optional, Callable
from kivy.utils import platform

# Android平台导入
if platform == 'android':
    from jnius import autoclass, cast, JavaMethod
    from android.runnable import run_on_ui_thread
    PythonActivity = None
    WindowManager = None
    LayoutParams = None


class FloatWindowManager:
    """
    悬浮窗管理器
    
    功能：
    1. 创建和销毁悬浮窗
    2. 显示和隐藏悬浮窗
    3. 移动悬浮窗位置
    4. 更新悬浮窗内容
    """

    def __init__(self):
        self.overlay_view = None
        self.window_manager = None
        self.is_visible = False
        self.current_x = 0
        self.current_y = 0
        
        # Android组件
        self._android_context = None
        self._activity = None
        
        # 初始化
        if platform == 'android':
            self._init_android_components()

    def _init_android_components(self):
        """初始化Android组件"""
        try:
            from jnius import autoclass
            
            # 获取必要的类
            self._PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self._WindowManager = autoclass('android.view.WindowManager')
            self._LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
            self._TextView = autoclass('android.widget.TextView')
            self._LinearLayout = autoclass('android.widget.LinearLayout')
            self._Context = autoclass('android.content.Context')
            self._Color = autoclass('android.graphics.Color')
            self._Gravity = autoclass('android.view.Gravity')
            self._MotionEvent = autoclass('android.view.MotionEvent')
            
            print("[FloatWindow] Android组件初始化成功")
            
        except ImportError as e:
            print(f"[FloatWindow] Android组件初始化失败: {e}")

    def create_overlay(self):
        """创建悬浮窗"""
        if platform != 'android':
            print("[FloatWindow] 非Android平台，跳过悬浮窗创建")
            return False
            
        try:
            self._create_overlay_impl()
            print("[FloatWindow] 悬浮窗创建成功")
            return True
        except Exception as e:
            print(f"[FloatWindow] 悬浮窗创建失败: {e}")
            return False

    def _create_overlay_impl(self):
        """实际创建悬浮窗的实现"""
        # 获取Activity和Context
        activity = self._PythonActivity.mActivity
        self._android_context = activity.getApplicationContext()
        
        # 获取WindowManager
        self.window_manager = activity.getWindowManager()
        
        # 创建LayoutParams
        params = self._LayoutParams()
        params.type = self._LayoutParams.TYPE_APPLICATION_OVERLAY
        params.format = -3  # PixelFormat.TRANSLUCENT
        params.flags = (
            self._LayoutParams.FLAG_NOT_FOCUSABLE | 
            self._LayoutParams.FLAG_LAYOUT_IN_SCREEN |
            self._LayoutParams.FLAG_LAYOUT_NO_LIMITS
        )
        
        # 设置大小 (180dp x 300dp 转换为像素)
        density = self._android_context.getResources().getDisplayMetrics().density
        params.width = int(180 * density)
        params.height = int(300 * density)
        
        # 设置初始位置 (屏幕右侧)
        display_metrics = self._android_context.getResources().getDisplayMetrics()
        screen_width = display_metrics.widthPixels
        screen_height = display_metrics.heightPixels
        
        self.current_x = int(screen_width * 0.85) - params.width
        self.current_y = int(screen_height * 0.4) - params.height // 2
        
        params.x = self.current_x
        params.y = self.current_y
        params.gravity = self._Gravity.TOP | self._Gravity.LEFT
        
        # 创建布局
        layout = self._LinearLayout(self._android_context)
        layout.setOrientation(1)  # 垂直布局
        
        # 创建标题TextView
        title = self._TextView(self._android_context)
        title.setText("掼蛋记牌器")
        title.setTextSize(16)
        title.setTextColor(self._Color.WHITE)
        title.setGravity(self._Gravity.CENTER)
        title.setPadding(10, 10, 10, 10)
        layout.addView(title)
        
        # 创建内容TextView
        self.content_view = self._TextView(self._android_context)
        self.content_view.setText("初始化中...")
        self.content_view.setTextSize(12)
        self.content_view.setTextColor(self._Color.WHITE)
        self.content_view.setGravity(self._Gravity.LEFT)
        self.content_view.setPadding(20, 5, 20, 5)
        layout.addView(self.content_view)
        
        # 设置背景
        layout.setBackgroundColor(self._Color.argb(200, 50, 50, 50))
        
        # 添加到WindowManager
        self.overlay_view = layout
        self.overlay_params = params
        
        print("[FloatWindow] 悬浮窗视图创建成功")
        
    def show_overlay(self):
        """显示悬浮窗"""
        if platform != 'android':
            return
            
        try:
            if self.overlay_view and not self.is_visible:
                self.window_manager.addView(self.overlay_view, self.overlay_params)
                self.is_visible = True
                print("[FloatWindow] 悬浮窗已显示")
        except Exception as e:
            print(f"[FloatWindow] 显示悬浮窗失败: {e}")

    def hide_overlay(self):
        """隐藏悬浮窗"""
        if platform != 'android':
            return
            
        try:
            if self.overlay_view and self.is_visible:
                self.window_manager.removeView(self.overlay_view)
                self.is_visible = False
                print("[FloatWindow] 悬浮窗已隐藏")
        except Exception as e:
            print(f"[FloatWindow] 隐藏悬浮窗失败: {e}")

    def update_content(self, text: str):
        """更新悬浮窗内容"""
        if platform != 'android':
            return
            
        try:
            if hasattr(self, 'content_view') and self.content_view:
                # 在UI线程更新
                self._update_text(text)
        except Exception as e:
            print(f"[FloatWindow] 更新内容失败: {e}")

    def _update_text(self, text: str):
        """实际更新文本（需要在UI线程调用）"""
        if platform == 'android' and hasattr(self, 'content_view'):
            self.content_view.setText(text)

    def set_position(self, x: int, y: int):
        """设置悬浮窗位置"""
        if platform != 'android':
            return
            
        try:
            if self.overlay_view and self.overlay_params:
                self.overlay_params.x = x
                self.overlay_params.y = y
                self.current_x = x
                self.current_y = y
                
                if self.is_visible:
                    self.window_manager.updateViewLayout(
                        self.overlay_view, 
                        self.overlay_params
                    )
        except Exception as e:
            print(f"[FloatWindow] 设置位置失败: {e}")

    def destroy_overlay(self):
        """销毁悬浮窗"""
        if platform != 'android':
            return
            
        try:
            if self.overlay_view:
                if self.is_visible:
                    self.window_manager.removeView(self.overlay_view)
                self.overlay_view = None
                self.is_visible = False
                print("[FloatWindow] 悬浮窗已销毁")
        except Exception as e:
            print(f"[FloatWindow] 销毁悬浮窗失败: {e}")

    def request_overlay_permission(self):
        """请求悬浮窗权限"""
        if platform != 'android':
            return
            
        try:
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            
            # 检查是否有悬浮窗权限
            activity = self._PythonActivity.mActivity
            context = activity.getApplicationContext()
            
            if not Settings.canDrawOverlays(context):
                # 请求权限
                intent = Intent(
                    Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    activity.getPackageName()
                )
                activity.startActivity(intent)
                print("[FloatWindow] 已请求悬浮窗权限")
            else:
                print("[FloatWindow] 已有悬浮窗权限")
                
        except Exception as e:
            print(f"[FloatWindow] 请求权限失败: {e}")


class DesktopFloatManager:
    """
    桌面调试用的悬浮窗模拟
    
    用于在PC上测试时模拟悬浮窗行为
    """

    def __init__(self):
        self.is_visible = False
        self.content = "桌面调试模式"

    def create_overlay(self):
        """创建模拟悬浮窗"""
        self.is_visible = True
        print("[FloatWindow] 桌面调试模式：悬浮窗已创建")

    def show_overlay(self):
        """显示模拟悬浮窗"""
        self.is_visible = True
        print("[FloatWindow] 桌面调试模式：悬浮窗已显示")

    def hide_overlay(self):
        """隐藏模拟悬浮窗"""
        self.is_visible = False
        print("[FloatWindow] 桌面调试模式：悬浮窗已隐藏")

    def update_content(self, text: str):
        """更新模拟内容"""
        self.content = text
        print(f"[FloatWindow] 桌面调试模式：内容更新\n{text}")

    def set_position(self, x: int, y: int):
        """设置模拟位置"""
        print(f"[FloatWindow] 桌面调试模式：位置设置为 ({x}, {y})")

    def destroy_overlay(self):
        """销毁模拟悬浮窗"""
        self.is_visible = False
        print("[FloatWindow] 桌面调试模式：悬浮窗已销毁")


# 工厂函数：根据平台创建合适的悬浮窗管理器
def create_float_manager() -> FloatWindowManager:
    """创建适合当前平台的悬浮窗管理器"""
    if platform == 'android':
        return FloatWindowManager()
    else:
        return DesktopFloatManager()
