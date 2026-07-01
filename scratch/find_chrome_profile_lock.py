import psutil
print("Scanning for Chrome processes using assets/chrome_profile...")
found = False
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        name = proc.info['name'] or ''
        if 'chrome' in name.lower():
            cmdline = proc.info['cmdline'] or []
            cmd_str = ' '.join(cmdline)
            if 'chrome_profile' in cmd_str:
                print(f"MATCH: PID={proc.info['pid']} | Cmd={cmd_str}")
                found = True
    except Exception:
        pass

if not found:
    print("No chrome process found with 'chrome_profile' in command line.")
    print("Checking all chrome processes:")
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name'] or ''
            if 'chrome' in name.lower():
                cmdline = proc.info['cmdline'] or []
                print(f"PID={proc.info['pid']} | Cmd={' '.join(cmdline)[:150]}")
        except Exception:
            pass
