[app]

# 应用名称
title = 掼蛋实时助手

# 应用包名（必须唯一）
package.name = guandan_assistant

# 应用域名（通常反过来写包名）
package.domain = com.guandan

# 应用的版本
version = 1.0.0

# Python依赖
requirements = python3,kivy==2.3.0,pyjnius,pillow

# 源码目录
source.dir = .

# 需要包含的Python文件
source.include_exts = py,png,jpg,kv,atlas,json,xml,ttf,otf

# 排除的文件
source.exclude_patterns = license,images/*/*.jpg

# Android版本支持
android.minapi = 21
android.api = 29

# 支持的Android架构
android.archs = arm64-v8a

# 屏幕方向
orientation = portrait

# 全屏模式
fullscreen = 0

# Android包类型
android.packagetype = release

# Release签名配置
android.release_artifact = apk

# 是否支持多点触控
android.multidex = 1

# ==================== 权限配置 ====================
# 悬浮窗、前台服务、截屏权限
android.permissions = SYSTEM_ALERT_WINDOW,FOREGROUND_SERVICE,CAPTURE_VIDEO_OUTPUT

# ==================== 服务配置 ====================
# 截屏前台服务
android.services = %(source.dir)s/android_service.py:start

# ==================== 应用图标 ====================
android.icon.filename = %(source.dir)s/res/drawable/icon.png

# ==================== 启动画面 ====================
android.presplash.filename = %(source.dir)s/res/drawable/presplash.png

# ==================== 主题配置 ====================
android.theme = android:theme/Theme.DeviceDefault.NoActionBar

# ==================== Kivy配置 ====================
# Kivy版本
p4a.bootstrap = sdl2

# SDL2相关
p4a.SDL2_DEPSITIES = 2

# ==================== 日志配置 ====================
log_level = 2

# ==================== 打包方式 ====================
mode = release

# 禁用外部zlib
android.ndk_mode = system
