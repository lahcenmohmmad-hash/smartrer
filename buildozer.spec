[app]
title = SmartRSR
package.name = smartrer
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1

requirements = python3,kivy

orientation = portrait

fullscreen = 1

android.permissions = INTERNET

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b

# معماريّة واحدة لتجنّب فشل GitHub Actions
android.archs = armeabi-v7a

android.accept_sdk_license = True

log_level = 2

[buildozer]
warn_on_root = 0
