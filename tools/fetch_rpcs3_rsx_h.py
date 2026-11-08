import subprocess
import base64

res = subprocess.run(['gh', 'api', 'repos/RPCS3/rpcs3/contents/rpcs3/Emu/Cell/lv2/sys_rsx.h', '--jq', '.content'], capture_output=True, text=True)
if res.returncode == 0:
    content = base64.b64decode(res.stdout.strip()).decode('utf-8', errors='ignore')
    for line in content.splitlines():
        if any(k in line for k in ['attribute', 'ATTRIBUTE', 'sys_rsx_context_attribute', '0x100']):
            print(line)
