import subprocess
import base64

res = subprocess.run(['gh', 'api', 'repos/torvalds/linux/contents/arch/powerpc/include/asm/lv1call.h', '--jq', '.content'], capture_output=True, text=True)
if res.returncode == 0:
    content = base64.b64decode(res.stdout.strip()).decode('utf-8', errors='ignore')
    for line in content.splitlines():
        if 'gpu_context_attribute' in line:
            print(line)
