"""
Android前台服务
用于后台截屏
"""

# 注意：这是一个Java服务文件模板
# 实际使用时会被打包工具处理

# 以下是Python服务入口
# Android服务需要在buildozer.spec中配置

# 示例：如何定义Android服务
"""
在buildozer.spec中：
android.services = service1:service2.py:service3.py

服务文件格式：
"""

# service1.py
"""
#!/usr/bin/env python
import android
import time
from android.service import ForegroundService

class ScreenCaptureService(ForegroundService):
    '''
    截屏前台服务
    
    需要在AndroidManifest中声明：
    <service
        android:name=".ScreenCaptureService"
        android:enabled="true"
        android:exported="false"
        android:foregroundServiceType="mediaProjection" />
    '''
    
    NOTIFICATION_ID = 1
    CHANNEL_ID = "guandan_capture_channel"
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        
    def onCreate(self):
        super().onCreate()
        self.create_notification_channel()
        self.start_foreground(self.NOTIFICATION_ID, self.create_notification())
        
    def onStartCommand(self, intent, flags, startId):
        self.is_running = True
        return super().onStartCommand(intent, flags, startId)
        
    def onDestroy(self):
        self.is_running = False
        super().onDestroy()
        
    def create_notification_channel(self):
        # 创建通知渠道
        pass
        
    def create_notification(self):
        # 创建前台通知
        pass
        
    def stop(self):
        self.stopSelf()
"""
