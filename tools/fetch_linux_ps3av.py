import subprocess
import base64
import sys

res = subprocess.run(['gh', 'api', 'repos/torvalds/linux/contents/drivers/ps3/ps3av_cmd.c', '--jq', '.content'], capture_output=True, text=True)
if res.returncode == 0:
    content = base64.b64decode(res.stdout.strip())
    lines = content.decode('utf-8', errors='ignore').splitlines()
    for i, line in enumerate(lines):
        if any(k in line for k in ['video_mode', 'ps3av_cmd_video', 'ps3av_pkt_video', 'CID_VIDEO', 'PS3AV_CMD', 'table', 'struct ps3av_pkt']):
            print(f"{i+1}: {line}")
else:
    print("gh api failed:", res.stderr)
