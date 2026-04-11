"""
Android服务Java代码模板
用于实现原生截屏和悬浮窗服务

使用方法：
1. 将对应代码放入 android/src/main/java/com/guandan/guandan_assistant/ 目录
2. 修改 buildozer.spec 中的 android.whitelist 配置
"""

# ====== ScreenCaptureService.java ======
SCREEN_CAPTURE_SERVICE = '''
// ScreenCaptureService.java
package com.guandan.guandan_assistant;

import android.app.*;
import android.content.Intent;
import android.hardware.display.*;
import android.media.ImageReader;
import android.media.projection.*;
import android.os.*;

public class ScreenCaptureService extends Service {
    private static final int NOTIFICATION_ID = 1001;
    private MediaProjectionManager projectionManager;
    private MediaProjection mediaProjection;
    private VirtualDisplay virtualDisplay;
    private ImageReader imageReader;
    
    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        startForeground(NOTIFICATION_ID, createNotification());
    }
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null) {
            int resultCode = intent.getIntExtra("resultCode", -1);
            Intent data = intent.getParcelableExtra("data");
            if (resultCode != -1 && data != null) {
                startProjection(resultCode, data);
            }
        }
        return START_STICKY;
    }
    
    private void startProjection(int resultCode, Intent data) {
        projectionManager = (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);
        mediaProjection = projectionManager.getMediaProjection(resultCode, data);
        
        WindowManager windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
        int width = windowManager.getDefaultDisplay().getWidth();
        int height = windowManager.getDefaultDisplay().getHeight();
        int density = windowManager.getDefaultDisplay().getMetrics(new android.util.DisplayMetrics()).densityDpi;
        
        imageReader = ImageReader.newInstance(width, height, android.graphics.PixelFormat.RGBA_8888, 2);
        
        virtualDisplay = mediaProjection.createVirtualDisplay(
            "GuandanCapture",
            width, height, density,
            Display.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
            imageReader.getSurface(),
            null, null
        );
    }
    
    private void createNotificationChannel() {
        NotificationChannel channel = new NotificationChannel(
            "capture_channel", "截屏服务", NotificationManager.IMPORTANCE_LOW);
        NotificationManager manager = getSystemService(NotificationManager.class);
        manager.createNotificationChannel(channel);
    }
    
    private Notification createNotification() {
        Intent notificationIntent = new Intent(this, org.kivy.android.PythonActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(this, 0, notificationIntent, PendingIntent.FLAG_IMMUTABLE);
        
        return new Notification.Builder(this, "capture_channel")
            .setContentTitle("掼蛋记牌器")
            .setContentText("正在监控游戏")
            .setSmallIcon(android.R.drawable.ic_menu_view)
            .setContentIntent(pendingIntent)
            .build();
    }
    
    @Override
    public void onDestroy() {
        if (virtualDisplay != null) virtualDisplay.release();
        if (mediaProjection != null) mediaProjection.stop();
        super.onDestroy();
    }
    
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
'''

# ====== FloatWindowService.java ======
FLOAT_WINDOW_SERVICE = '''
// FloatWindowService.java
package com.guandan.guandan_assistant;

import android.app.*;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.os.*;
import android.view.*;
import android.widget.*;

public class FloatWindowService extends Service {
    private WindowManager windowManager;
    private View floatingView;
    
    @Override
    public void onCreate() {
        super.onCreate();
        windowManager = (WindowManager) getSystemService(WINDOW_SERVICE);
        createFloatingWindow();
    }
    
    private void createFloatingWindow() {
        // 创建悬浮窗布局
        WindowManager.LayoutParams params = new WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        );
        
        params.gravity = Gravity.TOP | Gravity.START;
        params.x = 0;
        params.y = 200;
        
        LayoutInflater inflater = LayoutInflater.from(this);
        floatingView = inflater.inflate(R.layout.floating_window, null);
        
        windowManager.addView(floatingView, params);
    }
    
    public void updateText(String text) {
        if (floatingView != null) {
            TextView tv = floatingView.findViewById(R.id.float_content);
            if (tv != null) {
                tv.setText(text);
            }
        }
    }
    
    @Override
    public void onDestroy() {
        if (floatingView != null) {
            windowManager.removeView(floatingView);
        }
        super.onDestroy();
    }
    
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}
'''

# ====== floating_window.xml ======
FLOATING_WINDOW_LAYOUT = '''
// res/layout/floating_window.xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="180dp"
    android:layout_height="300dp"
    android:orientation="vertical"
    android:background="#CC333333"
    android:padding="10dp">

    <TextView
        android:id="@+id/float_title"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="掼蛋记牌器"
        android:textColor="#FFE082"
        android:textSize="16sp"
        android:textStyle="bold"
        android:gravity="center" />

    <View
        android:layout_width="match_parent"
        android:layout_height="1dp"
        android:layout_marginTop="5dp"
        android:layout_marginBottom="5dp"
        android:background="#666666" />

    <TextView
        android:id="@+id/float_content"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:textColor="#FFFFFF"
        android:textSize="12sp"
        android:scrollbars="vertical" />

    <TextView
        android:id="@+id/float_alert"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:textColor="#FF6B6B"
        android:textSize="10sp"
        android:visibility="gone" />

</LinearLayout>
'''

if __name__ == '__main__':
    # 生成Java文件
    import os
    os.makedirs('android_template', exist_ok=True)
    
    with open('android_template/ScreenCaptureService.java', 'w') as f:
        f.write(SCREEN_CAPTURE_SERVICE)
    
    with open('android_template/FloatWindowService.java', 'w') as f:
        f.write(FLOAT_WINDOW_SERVICE)
    
    print("Android Java模板已生成到 android_template/ 目录")
