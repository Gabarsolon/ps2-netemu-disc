#!/bin/bash
# usage: run_capture.sh <label> [iso_path]
H=192.168.0.169
LBL="$1"
ISO="${2:-/dev_hdd0/PS2ISO/Buzz%21%20The%20Schools%20Quiz%20%28Europe%29.iso}"
OUT="local_only/cap_${LBL}"
mkdir -p "$OUT"
grab(){ ffmpeg -hide_banner -loglevel error -f dshow -rtbufsize 100M -i video="USB3 Video" -frames:v 1 -update 1 -y "$OUT/t$1.png" 2>/dev/null; echo "t$1 http=$(curl -s -m3 -o /dev/null -w '%{http_code}' http://$H/)"; }
grab 000
curl -s -m 10 "http://$H/play.ps3$ISO" >/dev/null 2>&1; echo "launched $LBL"
L=$(date +%s)
for t in 6 18 32 50 70 90 110; do
  now=$(date +%s); d=$(( L + t - now )); [ $d -gt 0 ] && sleep $d
  grab $(printf '%03d' $t)
done
echo "done $LBL"
