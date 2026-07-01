import os

TARGET_DIR = r"D:\Entertainments\DevEnvironment\autovideo\binge_watching"
DL_DIR = r"D:\Entertainments\DevEnvironment\autovideo\debug\downloads"

def is_real_mp4(path):
    try:
        with open(path, "rb") as f:
            head = f.read(16)
        return b"ftyp" in head
    except Exception:
        return False

# Clean binge_watching directory
if os.path.exists(TARGET_DIR):
    for f in os.listdir(TARGET_DIR):
        p = os.path.join(TARGET_DIR, f)
        if os.path.isfile(p):
            # If it's not a real mp4 or has non-mp4 extension, delete it
            if not f.endswith(".mp4") or not is_real_mp4(p):
                print(f"Deleting garbage file in target: {f}")
                try:
                    os.remove(p)
                except Exception as e:
                    print(f"Failed to delete {f}: {e}")

# Clean temporary downloads directory
if os.path.exists(DL_DIR):
    for f in os.listdir(DL_DIR):
        p = os.path.join(DL_DIR, f)
        if os.path.isfile(p):
            print(f"Deleting temp download: {f}")
            try:
                os.remove(p)
            except Exception as e:
                print(f"Failed to delete {f}: {e}")

print("Clean-up finished.")
