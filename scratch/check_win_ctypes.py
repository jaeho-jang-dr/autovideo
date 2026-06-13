import ctypes

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
GetWindowText = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
GetClassName = ctypes.windll.user32.GetClassNameW

def foreach_window(hwnd, lParam):
    if IsWindowVisible(hwnd):
        length = GetWindowTextLength(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowText(hwnd, buff, length + 1)
        
        class_buff = ctypes.create_unicode_buffer(256)
        GetClassName(hwnd, class_buff, 256)
        
        title = buff.value
        cls = class_buff.value
        if title or cls:
            print(f"HWND: {hwnd}, Class: '{cls}', Title: '{title}'")
    return True

if __name__ == "__main__":
    print("Listing windows via ctypes:")
    EnumWindows(EnumWindowsProc(foreach_window), 0)
