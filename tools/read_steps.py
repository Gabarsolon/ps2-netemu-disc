import json
from pathlib import Path

p = Path(r"C:\Users\remus\AgyProfiles\gabar\.gemini\antigravity-cli\brain\fc13349c-d476-43f8-8fde-aa7625f2321d\.system_generated\logs\transcript_full.jsonl")
with open(p, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            idx = d.get("step_index")
            if idx and 9470 <= idx <= 9520:
                print(f"=== STEP {idx} ({d.get('source')}) ===")
                if d.get('tool_calls'):
                    for tc in d.get('tool_calls'):
                        print("  TOOL:", tc.get('name'), tc.get('args', {}).get('CommandLine') or tc.get('args', {}).get('Path') or tc.get('args'))
                if d.get('content'):
                    print(d.get('content')[:200])
        except Exception:
            pass
