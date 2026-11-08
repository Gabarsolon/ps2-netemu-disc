import subprocess
import base64

res = subprocess.run(['gh', 'api', 'repos/RPCS3/rpcs3/contents/rpcs3/Emu/Cell/Modules/cellVideoOut.cpp', '--jq', '.content'], capture_output=True, text=True)
if res.returncode == 0:
    content = base64.b64decode(res.stdout.strip()).decode('utf-8', errors='ignore')
    for line in content.splitlines():
        if any(k in line for k in ['CELL_VIDEO_OUT_RESOLUTION_', 'cellVideoOutConfigure', 'case CELL_VIDEO_OUT_RESOLUTION']):
            print(line)
