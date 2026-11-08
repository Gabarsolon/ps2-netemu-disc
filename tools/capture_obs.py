import ctypes
from ctypes import wintypes
import os
from PIL import Image

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

# Attach to interactive desktop
hwinsta = user32.OpenWindowStationW("WinSta0", False, 0x10000000 | 0x37F)
if hwinsta:
    user32.SetProcessWindowStation(hwinsta)

hdesk = user32.OpenDesktopW("Default", 0, False, 0x10000000 | 0x1FF)
if hdesk:
    user32.SetThreadDesktop(hdesk)

# Find OBS window
obs_hwnd = None
def enum_cb(hwnd, lparam):
    global obs_hwnd
    if user32.IsWindowVisible(hwnd):
        length = user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            if "obs" in buff.value.lower():
                obs_hwnd = hwnd
                return False
    return True

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

print("Found OBS HWND:", hex(obs_hwnd) if obs_hwnd else None)

# Capture either OBS window or whole desktop
if obs_hwnd:
    target_hwnd = obs_hwnd
    rect = wintypes.RECT()
    user32.GetWindowRect(target_hwnd, ctypes.byref(rect))
    w = rect.right - rect.left
    h = rect.bottom - rect.top
else:
    target_hwnd = user32.GetDesktopWindow()
    w = user32.GetSystemMetrics(0)
    h = user32.GetSystemMetrics(1)

print(f"Capture dimensions: {w}x{h}")

# DC capture
hwnd_dc = user32.GetWindowDC(target_hwnd)
mfc_dc = gdi32.CreateCompatibleDC(hwnd_dc)
save_bitmap = gdi32.CreateCompatibleBitmap(hwnd_dc, w, h)
gdi32.SelectObject(mfc_dc, save_bitmap)

# Try PrintWindow first (works even if partially occluded)
PW_RENDERFULLCONTENT = 2
printed = user32.PrintWindow(target_hwnd, mfc_dc, PW_RENDERFULLCONTENT)
print("PrintWindow result:", printed)
if not printed:
    # Fallback to BitBlt
    gdi32.BitBlt(mfc_dc, 0, 0, w, h, hwnd_dc, 0, 0, 0x00CC0020)

# Convert HBITMAP to PIL Image
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD)
    ]

bmi = BITMAPINFOHEADER()
bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
bmi.biWidth = w
bmi.biHeight = -h  # top-down
bmi.biPlanes = 1
bmi.biBitCount = 32
bmi.biCompression = 0

buf_size = w * h * 4
buf = ctypes.create_string_buffer(buf_size)
gdi32.GetDIBits(mfc_dc, save_bitmap, 0, h, buf, ctypes.byref(bmi), 0)

# Save
img = Image.frombuffer('RGBA', (w, h), buf, 'raw', 'BGRA', 0, 1)
rgb_img = img.convert('RGB')

out_path = r"C:\Users\remus\AgyProfiles\gabar\.gemini\antigravity-cli\brain\fc13349c-d476-43f8-8fde-aa7625f2321d\obs_capture.png"
rgb_img.save(out_path)
print(f"Saved capture to: {out_path} ({os.path.getsize(out_path)} bytes)")

# Cleanup
gdi32.DeleteObject(save_bitmap)
gdi32.DeleteDC(mfc_dc)
user32.ReleaseDC(target_hwnd, hwnd_dc)
