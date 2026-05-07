[app]
title = 数据管理
package.name = betsapp
package.domain = com.zhushou
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,ttc
version = 1.0
requirements = python3,kivy,openpyxl
orientation = portrait
fullscreen = 1
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.permissions = INTERNET,ACCESS_WIFI_STATE,BLUETOOTH,BLUETOOTH_ADMIN,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.meta_data = android.max_aspect = 2.2

[buildozer]
log_level = 2
warn_on_root = 1
