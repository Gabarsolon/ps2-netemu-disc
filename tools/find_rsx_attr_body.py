import subprocess
import base64

res = subprocess.run(['gh', 'api', 'repos/RPCS3/rpcs3/contents/rpcs3/Emu/Cell/lv2/sys_rsx.cpp', '--jq', '.content'], capture_output=True, text=True)
if res.returncode == 0:
    content = base64.b64decode(res.stdout.strip()).decode('utf-8', errors='ignore')
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if 'error_code sys_rsx_context_attribute(' in line:
            for j in range(i, min(len(lines), i+80)):
                print(f"{j+1}: {lines[j]}")
            break
