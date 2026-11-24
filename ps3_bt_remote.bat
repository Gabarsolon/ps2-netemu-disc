@echo off
rem PS3 keyboard remote over the Bluetooth dongle. PS3 must be on.
cd /d "%~dp0"
python tools\ps3_bt_keyboard_remote.py
if errorlevel 1 pause
