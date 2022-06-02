@echo off
set APK_PATH=%~dpnx1
set CURR_DIR=%~dp0
set PURE_PATH=%CURR_DIR%install_apk_to_devices.py

@echo off & color 0f & title Install Apk To Devices
py %PURE_PATH% -p %APK_PATH%
pause