import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

titles = []
def enum_cb(hwnd, lparam):
    if user32.IsWindowVisible(hwnd):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            titles.append((hwnd, buff.value))
    return True

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

print(f"Total visible windows: {len(titles)}")
for h, t in titles:
    if any(k in t.lower() for k in ['obs', 'studio', 'capture', 'video', 'ps3', 'hdmi']):
        print(f"Match: {hex(h)} -> {t}")
