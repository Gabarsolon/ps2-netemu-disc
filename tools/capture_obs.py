"""Capture only an existing OBS window, without focus or desktop fallback."""
import argparse
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path


def capture(path):
    u = c.WinDLL('user32', use_last_error=True)
    try:
        u.SetThreadDpiAwarenessContext.argtypes = [c.c_void_p]
        u.SetThreadDpiAwarenessContext.restype = c.c_void_p
        u.SetThreadDpiAwarenessContext(c.c_void_p(-4))
    except AttributeError:
        u.SetProcessDPIAware()
    callback_type = c.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
    u.EnumWindows.argtypes = [callback_type, w.LPARAM]
    u.GetWindowTextLengthW.argtypes = [w.HWND]
    u.GetWindowTextW.argtypes = [w.HWND, w.LPWSTR, c.c_int]
    u.IsWindowVisible.argtypes = [w.HWND]
    u.IsIconic.argtypes = [w.HWND]
    u.GetWindowRect.argtypes = [w.HWND, c.POINTER(w.RECT)]
    windows = []

    @callback_type
    def visit(hwnd, unused):
        size = u.GetWindowTextLengthW(hwnd)
        title = c.create_unicode_buffer(size + 1)
        u.GetWindowTextW(hwnd, title, size + 1)
        if title.value.startswith('OBS ') and u.IsWindowVisible(hwnd) and not u.IsIconic(hwnd):
            windows.append(hwnd)
        return True

    u.EnumWindows(visit, 0)
    if not windows:
        raise RuntimeError('No visible OBS window.')
    hwnd = windows[0]
    rect = w.RECT()
    if not u.GetWindowRect(hwnd, c.byref(rect)):
        raise c.WinError(c.get_last_error())
    width, height = rect.right - rect.left, rect.bottom - rect.top
    # PrintWindow intermittently returns a black GPU preview in OBS. Capture
    # its visible physical bounds instead; never fall back to the full desktop.
    from PIL import ImageGrab
    ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom), all_screens=True).save(path)
    print(str(Path(path).resolve()), width, height)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('output', nargs='?', default=str(Path(__file__).resolve().parents[1] / 'local_only/obs_capture.png'))
    capture(parser.parse_args().output)
