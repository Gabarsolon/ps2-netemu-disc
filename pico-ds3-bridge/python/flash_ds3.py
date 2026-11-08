import os
import time
import shutil
import subprocess
import json

uf2_source = r"C:\Users\remus\pico_ds3_serial.uf2"

def get_pico_bootsel_drive():
    try:
        cmd = "Get-Volume | Where-Object { ($_.FileSystemLabel -match 'RP2350|RPI-RP2' -or $_.DriveType -eq 'Removable') -and $_.FileSystemType -eq 'FAT' } | Select-Object DriveLetter | ConvertTo-Json"
        p = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True)
        if not p.stdout.strip():
            return None
        data = json.loads(p.stdout)
        if isinstance(data, dict):
            dl = data.get("DriveLetter")
            if dl:
                return f"{dl}:\\"
        elif isinstance(data, list) and len(data) > 0:
            dl = data[0].get("DriveLetter")
            if dl:
                return f"{dl}:\\"
    except Exception:
        pass
    return None

print("Listening for Pico in BOOTSEL mode (Drive F:\\ or Removable FAT volume)...")
for _ in range(600):
    drive = get_pico_bootsel_drive()
    if drive and os.path.exists(os.path.join(drive, "INFO_UF2.TXT")):
        print(f"Detected Pico BOOTSEL drive: {drive}! Flashing pico_ds3_serial.uf2...")
        time.sleep(0.5)
        try:
            target = os.path.join(drive, "pico_ds3_serial.uf2")
            shutil.copyfile(uf2_source, target)
            print(f"SUCCESS: Flashed to {drive} successfully!")
            break
        except Exception as e:
            print("Copy error:", e)
    time.sleep(0.5)
