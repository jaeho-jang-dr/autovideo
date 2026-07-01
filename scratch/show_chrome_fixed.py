import ctypes
from ctypes import wintypes
import sys

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId

hwnds = []

def callback(hwnd, lParam):
    try:
        pid = wintypes.DWORD()
        GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        length = GetWindowTextLength(hwnd)
        title = ""
        if length > 0:
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            title = buff.value
            
        hwnds.append((hwnd, pid.value, title))
    except Exception as e:
        print(f"Error in callback: {e}")
    return True

# EnumWindows를 명시적인 타입 프로토타입으로 지정
EnumWindows.argtypes = [EnumWindowsProc, wintypes.LPARAM]
EnumWindows.restype = wintypes.BOOL

cb = EnumWindowsProc(callback)
res = EnumWindows(cb, 0)

print(f"EnumWindows returned: {res}")
print(f"Total windows checked: {len(hwnds)}")
if not res:
    print(f"GetLastError: {ctypes.GetLastError()}")

chrome_hwnds = []
for hwnd, pid, title in hwnds:
    title_lower = title.lower()
    is_chrome = False
    if "chrome" in title_lower or "flow" in title_lower or "google" in title_lower or "veo" in title_lower:
        is_chrome = True
    
    if is_chrome and title.strip():
        print(f"Found Chrome/Flow window: HWND={hwnd}, PID={pid}, Title={title}")
        chrome_hwnds.append(hwnd)

if not chrome_hwnds:
    print("No chrome window found by title. Showing all visible windows with titles:")
    for hwnd, pid, title in hwnds:
        if title.strip() and IsWindowVisible(hwnd):
            print(f"HWND={hwnd}, PID={pid}, Title={title}")
else:
    print(f"Bringing {len(chrome_hwnds)} Chrome windows to foreground...")
    for hwnd in chrome_hwnds:
        try:
            # 9 = SW_RESTORE, 5 = SW_SHOW, 1 = SW_SHOWNORMAL
            ctypes.windll.user32.ShowWindow(hwnd, 9)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            print(f"Activated HWND {hwnd}")
        except Exception as e:
            print(f"Failed to activate HWND {hwnd}: {e}")
