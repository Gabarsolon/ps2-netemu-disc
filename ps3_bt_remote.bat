@echo off
rem PS3 keyboard remote over the Bluetooth dongle. Wakes the PS3 first if it is off.
cd /d "%~dp0"
python tools\ps3_bt_power.py wake
if errorlevel 1 goto fail
rem Give the XMB a moment after webMAN comes online.
timeout /t 5 /nobreak >nul
python tools\ps3_bt_keyboard_remote.py
if errorlevel 1 pause
goto :eof
:fail
echo PS3 did not wake; remote not started.
pause
