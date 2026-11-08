import subprocess
import base64

res = subprocess.run(['gh', 'api', 'repos/torvalds/linux/contents/arch/powerpc/include/asm/ps3av.h', '--jq', '.content'], capture_output=True, text=True)
if res.returncode == 0:
    content = base64.b64decode(res.stdout.strip()).decode('utf-8', errors='ignore')
    for line in content.splitlines():
        if 'PS3AV_CMD_AV_VID_' in line or 'PS3AV_CMD_VIDEO_VID_' in line or 'PS3AV_MODE_' in line or 'PS3AV_CID_' in line:
            print(line)
else:
    print("Failed:", res.stderr)
