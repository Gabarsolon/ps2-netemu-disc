#!/usr/bin/env python3
"""Launch a PS2 carrier and monitor console state via webMAN HTTP + Tapo plug wattage.

HTTP up            -> GameOS/XMB.
HTTP down + >30W   -> PS2 mode running (normal; webMAN is gone in PS2 mode).
HTTP down + <15W   -> powered OFF.
Prints a timeline and a final verdict. Does NOT cut power. Read-only on the console.
"""
import asyncio, json, os, time, urllib.request
from tapo import ApiClient

HOST="192.168.0.169"
ISO="/dev_hdd0/PS2ISO/Buzz%21%20The%20Schools%20Quiz%20%28Europe%29.iso"
DUR=160

def http_up():
    try:
        urllib.request.urlopen(f"http://{HOST}/",timeout=3); return True
    except Exception: return False

def load_cfg():
    # Credentials are never hardcoded/committed. Read from a gitignored file or env.
    for p in ("local_only/tapo_config.json", os.path.expanduser("~/tapo_config.json")):
        if os.path.exists(p):
            return json.load(open(p))
    return {"ip": os.environ.get("TAPO_IP","192.168.0.12"),
            "email": os.environ.get("TAPO_EMAIL",""),
            "password": os.environ.get("TAPO_PASSWORD","")}

async def main():
    cfg=load_cfg()
    plug=None
    try:
        c=ApiClient(cfg["email"],cfg["password"]); plug=await asyncio.wait_for(c.p115(cfg["ip"]),timeout=8)
    except Exception as e:
        print("plug unreachable, HTTP-only mode:",str(e)[:40],flush=True)
    async def watt():
        if plug is None: return -1
        try: return (await asyncio.wait_for(plug.get_energy_usage(),timeout=6)).current_power
        except Exception: return -1
    t0=time.time()
    print(f"start W={await watt()} http={http_up()}",flush=True)
    try: urllib.request.urlopen(f"http://{HOST}/play.ps3{ISO}",timeout=12)
    except Exception as e: print("launch notice",str(e)[:40],flush=True)
    last=None; entered_ps2=False; returned=False
    while time.time()-t0<DUR:
        el=time.time()-t0; up=http_up(); w=await watt()
        if up: st="XMB"
        elif w>30: st="PS2"
        elif 0<=w<15: st="OFF"
        else: st="PS2?"   # http down, wattage unknown -> assume PS2 mode
        if st!=last: print(f"  {el:5.0f}s http={'up' if up else 'dn':3} W={w:6} -> {st}",flush=True); last=st
        if st in ("PS2","PS2?") and el>6: entered_ps2=True
        if entered_ps2 and up and el>12: returned=True; print(f"  {el:.0f}s RETURNED to XMB",flush=True); break
        if entered_ps2 and st=="OFF": print(f"  {el:.0f}s POWERED OFF",flush=True); break
        await asyncio.sleep(3)
    wf=await watt()
    print(f"VERDICT entered_ps2={entered_ps2} returned={returned} final_http={http_up()} final_W={wf}",flush=True)
asyncio.run(main())
