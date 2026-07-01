import winreg

def search(root, key_name):
    try:
        with winreg.OpenKey(root, key_name) as key:
            info = winreg.QueryInfoKey(key)
            # Print values
            for i in range(info[1]):
                try:
                    name, val, val_type = winreg.EnumValue(key, i)
                    # Convert to string and filter if it looks like a path
                    val_str = str(val)
                    if ":" in val_str or "\\" in val_str or "/" in val_str:
                        print(f"[FOUND PATH] {key_name} -> {name}: {val_str}")
                except WindowsError:
                    pass
            # Recurse
            for i in range(info[0]):
                try:
                    sub_key_name = winreg.EnumKey(key, i)
                    search(root, f"{key_name}\\{sub_key_name}")
                except WindowsError:
                    pass
    except WindowsError:
        pass

print("Scanning Registry HKCU Software\\Bytedance...")
search(winreg.HKEY_CURRENT_USER, r"Software\Bytedance")
print("Scanning Registry HKCU Software\\CapCut...")
search(winreg.HKEY_CURRENT_USER, r"Software\CapCut")
print("Scanning Registry HKLM Software\\Bytedance...")
search(winreg.HKEY_LOCAL_MACHINE, r"Software\Bytedance")
print("Scanning Registry HKLM Software\\CapCut...")
search(winreg.HKEY_LOCAL_MACHINE, r"Software\CapCut")
print("Scan Finished.")
