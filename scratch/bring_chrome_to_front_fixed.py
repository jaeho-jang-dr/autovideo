import uiautomation as auto
import sys

print("Listing all root window controls via UI Automation:")
root = auto.GetRootControl()
chrome_wins = []

for w in root.GetChildren():
    try:
        name = w.Name or ""
        cls = w.ClassName or ""
        if name or cls:
            print(f"Name: {name} | ClassName: {cls}")
            # Identify any window that looks like Chrome or Google Flow
            if "Chrome_WidgetWin_1" in cls or "chrome" in cls.lower() or "chrome" in name.lower() or "flow" in name.lower():
                chrome_wins.append(w)
    except Exception as e:
        pass

if chrome_wins:
    print(f"\nFound {len(chrome_wins)} matching windows. Attempting to bring them to front...")
    for i, win in enumerate(chrome_wins):
        try:
            print(f"Targeting window [{i}]: Name='{win.Name}', ClassName='{win.ClassName}'")
            # 9 is SW_RESTORE (restores window size and position), 5 is SW_SHOW, 3 is SW_MAXIMIZE
            win.ShowWindow(9)
            win.SetActive()
            win.SetFocus()
            print(f"  Brought window [{i}] to the foreground.")
        except Exception as e:
            print(f"  Failed to bring window [{i}] to front: {e}")
else:
    print("\nNo matching Chrome/Flow windows found.")
