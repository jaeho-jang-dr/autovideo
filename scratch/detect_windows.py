import uiautomation as auto
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

print("Scanning ALL top-level windows...")
root = auto.GetRootControl()
for i, w in enumerate(root.GetChildren()):
    try:
        name = w.Name or ""
        cls = w.ClassName or ""
        print(f"[{i}] Name: '{name}', ClassName: '{cls}'")
    except Exception as e:
        print(f"[{i}] Error: {e}")
