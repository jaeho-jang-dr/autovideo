import os
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

def main():
    scratch_dir = os.path.join(ROOT, "scratch")
    if not os.path.exists(scratch_dir):
        print(f"[ERR] Scratch directory not found: {scratch_dir}")
        return
        
    print("Checking log files modified on June 25th, 2026...")
    
    t_start = datetime.datetime.now() - datetime.timedelta(days=7)
    t_end = datetime.datetime.now() + datetime.timedelta(days=1)
    
    for file in os.listdir(scratch_dir):
        if not file.endswith('.log'):
            continue
            
        file_path = os.path.join(scratch_dir, file)
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        
        if t_start <= mtime <= t_end:
            print("=" * 60)
            print(f"Log File: {file} | Modified: {mtime}")
            print("=" * 60)
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    print(content[:1500])
                    if len(content) > 1500:
                        print("... [TRUNCATED] ...")
            except Exception as e:
                print(f"Error reading log: {e}")
            print("\n")

if __name__ == "__main__":
    main()
