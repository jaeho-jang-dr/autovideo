import psutil

print("Listing all active python processes and their cmdlines:")
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if 'python' in proc.info['name'].lower():
            print(f"PID: {proc.info['pid']} - Cmd: {proc.info['cmdline']}")
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
