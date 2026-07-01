import ctypes
from ctypes import wintypes

GetWindowRect = ctypes.windll.user32.GetWindowRect
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetWindowPlacement = ctypes.windll.user32.GetWindowPlacement

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [("length", ctypes.c_uint),
                ("flags", ctypes.c_uint),
                ("showCmd", ctypes.c_uint),
                ("ptMinPosition", ctypes.c_longlong), # simple 8-byte point representation
                ("ptMaxPosition", ctypes.c_longlong),
                ("rcNormalPosition", RECT)]

hwnd = 580917732
rect = RECT()
GetWindowRect(hwnd, ctypes.byref(rect))
visible = IsWindowVisible(hwnd)

wp = WINDOWPLACEMENT()
wp.length = ctypes.sizeof(WINDOWPLACEMENT)
GetWindowPlacement(hwnd, ctypes.byref(wp))

print(f"HWND: {hwnd}")
print(f"Visible: {visible}")
print(f"Rect: left={rect.left}, top={rect.top}, right={rect.right}, bottom={rect.bottom}")
print(f"ShowCmd: {wp.showCmd} (1=normal, 2=minimized, 3=maximized, 0=hide)")
