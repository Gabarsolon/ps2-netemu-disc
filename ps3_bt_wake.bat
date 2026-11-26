@echo off
rem Turn on the PS3 from standby over the Bluetooth dongle.
cd /d "%~dp0"
python tools\ps3_bt_power.py wake
if errorlevel 1 pause
