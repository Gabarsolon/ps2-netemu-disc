import subprocess
import base64

res = subprocess.run(['gh', 'api', 'repos/torvalds/linux/contents/drivers/video/fbdev/ps3fb.c', '--jq', '.content'], capture_output=True, text=True)
if res.returncode == 0:
    content = base64.b64decode(res.stdout.strip()).decode('utf-8', errors='ignore')
    for line in content.splitlines():
        if 'ps3fb_res' in line or 'modeline' in line or 'video_mode' in line or 'var->yres' in line:
            print(line)
else:
    print("Failed:", res.stderr)
