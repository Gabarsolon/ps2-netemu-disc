import json

with open(r'C:\Users\remus\AgyProfiles\gabar\.gemini\antigravity-cli\brain\fc13349c-d476-43f8-8fde-aa7625f2321d\.system_generated\logs\transcript.jsonl', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get('step_index') in [15655, 15656, 15657]:
            print(f"=== STEP {d.get('step_index')} ===")
            print(d.get('content') or d.get('tool_calls'))
