import psutil
import os

target = os.path.abspath(r"assets/chrome_profile/lockfile").lower()
print(f"Searching for processes locking: {target}")

found = False
for proc in psutil.process_iter(['pid', 'name']):
    try:
        # Check open files
        for f in proc.open_files():
            if f.path.lower() == target:
                print(f"FOUND LOCKER: PID={proc.info['pid']} | Name={proc.info['name']}")
                # Print cmdline too
                try:
                    print(f"Cmdline: {' '.join(proc.cmdline())}")
                except Exception:
                    pass
                found = True
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        pass
    except Exception as e:
        pass

if not found:
    print("No process found holding a handle to the lockfile via open_files().")
    print("Checking if any process has 'chrome_profile' in its open files or cmdline...")
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for f in proc.open_files():
                if 'chrome_profile' in f.path.lower():
                    print(f"Match in open files: PID={proc.info['pid']} | Name={proc.info['name']} | File={f.path}")
                    found = True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
        except Exception:
            pass

if not found:
    print("No lockers found.")
