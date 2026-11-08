import urllib.request
import re

url = 'http://192.168.0.169/dev_flash/vsh/resource/explore/xmb/category_game.xml'
req = urllib.request.Request(url, headers={'User-Agent': 'test'})
try:
    with urllib.request.urlopen(req, timeout=5) as r:
        xml = r.read().decode('utf-8', errors='ignore')
    print('Length:', len(xml))
    for m in re.finditer(r'id=["\']([^"\']+)["\']', xml):
        val = m.group(1)
        if any(k in val.lower() for k in ['disc', 'device', 'game', 'bdvd', 'boot', 'seg_']):
            print('id:', val)
    for m in re.finditer(r'key=["\']([^"\']+)["\']', xml):
        val = m.group(1)
        if any(k in val.lower() for k in ['disc', 'device', 'game', 'bdvd', 'boot', 'seg_']):
            print('key:', val)
except Exception as e:
    print('Error:', e)
