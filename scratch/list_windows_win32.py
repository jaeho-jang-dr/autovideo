import win32gui

def enum_windows_callback(hwnd, extra):
    try:
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            classname = win32gui.GetClassName(hwnd)
            if title.strip():
                print(f"HWND: {hwnd} | Class: {classname} | Title: {title}")
    except Exception as e:
        print(f"Error for HWND {hwnd}: {e}")

print("=== win32gui Visible Windows ===")
win32gui.EnumWindows(enum_windows_callback, None)
