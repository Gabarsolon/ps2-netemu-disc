import json

path = r"C:\Users\remus\AgyProfiles\gabar\.gemini\antigravity-cli\brain\fc13349c-d476-43f8-8fde-aa7625f2321d\.system_generated\logs\transcript.jsonl"
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            idx = d.get("step_index")
            if idx == 9761:
                print("CONTENT 9761:", d.get("content"))
        except Exception:
            pass
