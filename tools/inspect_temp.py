import glob

for fpath in glob.glob(r'C:\Users\remus\ps2-netemu-disc\tools\*.*'):
    try:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        if '0x5004' in text or '0x5002' in text or '0x5001' in text or '5004' in text:
            print("Found in", fpath)
    except:
        pass
