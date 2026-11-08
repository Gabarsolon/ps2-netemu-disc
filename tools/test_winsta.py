import ctypes
from ctypes import wintypes
from PIL import Image

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# Open interactive window station
hwinsta = user32.OpenWindowStationW("WinSta0", False, 0x10000000 | 0x37F)
print("OpenWindowStation:", hwinsta)
if hwinsta:
    ret = user32.SetProcessWindowStation(hwinsta)
    print("SetProcessWindowStation:", ret)

# Open desktop
hdesk = user32.OpenDesktopW("Default", 0, False, 0x10000000 | 0x1FF)
print("OpenDesktop:", hdesk)
if hdesk:
    ret = user32.SetThreadDesktop(hdesk)
    print("SetThreadDesktop:", ret)

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
    print(f"  {hex(h)} -> {t}")
