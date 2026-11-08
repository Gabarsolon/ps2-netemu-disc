import urllib.request
import struct

def peek_lv1(addr):
    url = f"http://192.168.0.169/peek.lv1?{addr:x}"
    req = urllib.request.urlopen(url, timeout=5)
    resp = req.read().decode('utf-8')
    # webman returns hex string e.g. "0000000000165b50: 3bc00000 38600002 ..."
    return resp

print("Peeking 0x00165b40:")
print(peek_lv1(0x00165b40))

print("Peeking 0x00165cc0:")
print(peek_lv1(0x00165cc0))
