"""
Android截屏服务管理器
使用MediaProjection API实现实时截屏
"""

import threading
import time
from typing import Callable, Optional
from kivy.utils import platform

# Android平台导入
if platform == 'android':
    try:
        from jnius import autoclass, cast, JavaMethod, JavaCallback
        from android.runnable import run_on_ui_thread
    except ImportError:
        pass


class ScreenCaptureManager:
    """
    截屏服务管理器
    
    功能：
    1. 申请截屏权限（MediaProjection）
    2. 启动/停止截屏服务
    3. 定时截取屏幕
    4. 回调处理截屏结果
    """

    def __init__(self):
        self.is_capturing = False
        self.capture_thread: Optional[threading.Thread] = None
        self.callback: Optional[Callable] = None
        self.capture_interval = 1.0  # 截屏间隔（秒）
        
        # Android组件
        self._projection_manager = None
        self._image_reader = None
        self._handler = None
        
        # 状态
        self._permission_granted = False
        self._projection = None
        
        if platform == 'android':
            self._init_android_components()

    def _init_android_components(self):
        """初始化Android组件"""
        try:
            from jnius import autoclass
            
            # 获取必要的类
            self._Activity = autoclass('org.kivy.android.PythonActivity')
            self._MediaProjectionManager = autoclass('android.media.projection.MediaProjectionManager')
            self._ImageReader = autoclass('android.media.ImageReader')
            self._Handler = autoclass('android.os.Handler')
            self._Looper = autoclass('android.os.Looper')
            self._Context = autoclass('android.content.Context')
            self._PixelFormat = autoclass('android.graphics.PixelFormat')
            
            print("[ScreenCapture] Android组件初始化成功")
            
        except ImportError as e:
            print(f"[ScreenCapture] Android组件初始化失败: {e}")

    def request_permission(self, activity, request_code: int = 1001):
        """
        请求截屏权限
        
        Args:
            activity: Activity实例
            request_code: 请求码
        """
        if platform != 'android':
            return
            
        try:
            # 获取MediaProjectionManager
            service = activity.getSystemService(self._Context.MEDIA_PROJECTION_SERVICE)
            self._projection_manager = cast(
                self._MediaProjectionManager,
                service
            )
            
            # 启动权限请求
            if self._projection_manager:
                intent = self._projection_manager.createScreenCaptureIntent()
                activity.startActivityForResult(intent, request_code)
                print("[ScreenCapture] 已请求截屏权限")
            else:
                print("[ScreenCapture] 无法获取MediaProjectionManager")
                
        except Exception as e:
            print(f"[ScreenCapture] 请求权限失败: {e}")

    def on_permission_result(self, resultCode, data):
        """
        权限请求结果回调
        
        Args:
            resultCode: 结果码
            data: Intent数据
        """
        if platform != 'android':
            return
            
        try:
            from jnius import autoclass
            
            if resultCode == -1:  # RESULT_OK
                # 获取MediaProjection
                self._projection = self._projection_manager.getMediaProjection(
                    resultCode, data
                )
                self._permission_granted = True
                print("[ScreenCapture] 截屏权限已授予")
                
                # 初始化ImageReader
                self._init_image_reader()
            else:
                print("[ScreenCapture] 截屏权限被拒绝")
                self._permission_granted = False
                
        except Exception as e:
            print(f"[ScreenCapture] 处理权限结果失败: {e}")

    def _init_image_reader(self):
        """初始化ImageReader"""
        if platform != 'android':
            return
            
        try:
            activity = self._Activity.mActivity
            display_metrics = activity.getResources().getDisplayMetrics()
            width = display_metrics.widthPixels
            height = display_metrics.heightPixels
            
            # 创建ImageReader
            self._image_reader = self._ImageReader.newInstance(
                width, height,
                self._PixelFormat.RGBA_8888,
                2
            )
            
            # 获取Handler
            self._handler = self._Handler(self._Looper.getMainLooper())
            
            print(f"[ScreenCapture] ImageReader初始化成功 ({width}x{height})")
            
        except Exception as e:
            print(f"[ScreenCapture] ImageReader初始化失败: {e}")

    def start_capture(self, callback: Callable):
        """
        开始截屏
        
        Args:
            callback: 截屏回调函数，接收图像数据
        """
        if not self._permission_granted:
            print("[ScreenCapture] 未获得截屏权限")
            return
            
        if self.is_capturing:
            print("[ScreenCapture] 已经在截屏中")
            return
            
        self.callback = callback
        self.is_capturing = True
        
        # 启动截屏线程
        self.capture_thread = threading.Thread(
            target=self._capture_loop,
            daemon=True
        )
        self.capture_thread.start()
        
        print("[ScreenCapture] 开始截屏")

    def stop_capture(self):
        """停止截屏"""
        self.is_capturing = False
        
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
            self.capture_thread = None
            
        print("[ScreenCapture] 停止截屏")

    def _capture_loop(self):
        """截屏循环"""
        while self.is_capturing:
            try:
                # 执行截屏
                image_data = self._do_capture()
                
                if image_data and self.callback:
                    # 调用回调
                    self.callback(image_data)
                    
            except Exception as e:
                print(f"[ScreenCapture] 截屏失败: {e}")
            
            # 等待下一次截屏
            time.sleep(self.capture_interval)

    def _do_capture(self):
        """
        执行实际截屏操作
        
        Returns:
            图像数据
        """
        if platform != 'android':
            # 桌面模式返回None
            return None
            
        try:
            # 使用VirtualDisplay截屏
            activity = self._Activity.mActivity
            display_metrics = activity.getResources().getDisplayMetrics()
            width = display_metrics.widthPixels
            height = display_metrics.heightPixels
            
            # 获取Display
            display = activity.getWindowManager().getDefaultDisplay()
            
            # 创建VirtualDisplay
            # 注意：这里简化了实现，实际需要更完整的代码
            
            # 暂时返回模拟数据用于调试
            return None
            
        except Exception as e:
            print(f"[ScreenCapture] 截屏异常: {e}")
            return None

    def pause(self):
        """暂停截屏"""
        self.is_capturing = False
        print("[ScreenCapture] 截屏已暂停")

    def resume(self):
        """恢复截屏"""
        if self.callback and not self.is_capturing:
            self.start_capture(self.callback)
        print("[ScreenCapture] 截屏已恢复")

    def set_interval(self, interval: float):
        """
        设置截屏间隔
        
        Args:
            interval: 间隔时间（秒）
        """
        self.capture_interval = max(0.5, min(5.0, interval))
        print(f"[ScreenCapture] 截屏间隔设置为 {self.capture_interval}s")

    def release(self):
        """释放资源"""
        self.stop_capture()
        
        if platform == 'android' and self._image_reader:
            try:
                self._image_reader.close()
            except:
                pass
            self._image_reader = None
            
        print("[ScreenCapture] 资源已释放")


class DesktopScreenCapture:
    """
    桌面调试用的截屏模拟
    
    用于在PC上测试时模拟截屏功能
    """

    def __init__(self):
        self.is_capturing = False
        self.callback = None
        self.capture_interval = 1.0

    def request_permission(self, activity=None, request_code: int = 1001):
        """桌面模式：模拟权限请求"""
        print("[ScreenCapture] 桌面调试模式：模拟权限请求")
        # 模拟授权成功
        self._permission_granted = True

    def on_permission_result(self, resultCode, data):
        """桌面模式：模拟权限结果"""
        print("[ScreenCapture] 桌面调试模式：模拟权限结果")
        self._permission_granted = True

    def start_capture(self, callback: Callable):
        """桌面模式：模拟开始截屏"""
        self.callback = callback
        self.is_capturing = True
        print("[ScreenCapture] 桌面调试模式：开始模拟截屏")

    def stop_capture(self):
        """桌面模式：模拟停止截屏"""
        self.is_capturing = False
        print("[ScreenCapture] 桌面调试模式：停止模拟截屏")

    def pause(self):
        """桌面模式：模拟暂停"""
        print("[ScreenCapture] 桌面调试模式：暂停")

    def resume(self):
        """桌面模式：模拟恢复"""
        print("[ScreenCapture] 桌面调试模式：恢复")

    def release(self):
        """桌面模式：模拟释放"""
        self.is_capturing = False
        print("[ScreenCapture] 桌面调试模式：释放资源")


# 工厂函数：根据平台创建合适的截屏管理器
def create_capture_manager() -> ScreenCaptureManager:
    """创建适合当前平台的截屏管理器"""
    if platform == 'android':
        return ScreenCaptureManager()
    else:
        return DesktopScreenCapture()
