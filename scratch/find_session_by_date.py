import os
import sys
import datetime

BRAIN_DIR = r"C:\Users\antigravity\.gemini\antigravity\brain"
sys.stdout.reconfigure(encoding='utf-8')

def main():
    if not os.path.exists(BRAIN_DIR):
        print(f"[ERR] Brain dir not found: {BRAIN_DIR}")
        return
        
    print(f"Scanning sessions for activity around 2026-06-25 15:00~16:00 KST...")
    
    # Target range: 2026-06-25 15:00 ~ 16:00 KST
    # KST is UTC+9. So local datetime on the machine is KST.
    t_start = datetime.datetime(2026, 6, 25, 14, 30)
    t_end = datetime.datetime(2026, 6, 25, 16, 30)
    
    matches = []
    for folder in os.listdir(BRAIN_DIR):
        folder_path = os.path.join(BRAIN_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
            
        logs_dir = os.path.join(folder_path, ".system_generated", "logs")
        if not os.path.exists(logs_dir):
            continue
            
        transcript_path = os.path.join(logs_dir, "transcript.jsonl")
        if not os.path.exists(transcript_path):
            continue
            
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(transcript_path))
        if t_start <= mtime <= t_end:
            matches.append((folder, mtime))
            
    print(f"\nFound {len(matches)} active sessions in this time range:")
    for folder, mtime in sorted(matches, key=lambda x: x[1]):
        print(f"  Session ID: {folder} | Last Active: {mtime}")
        
if __name__ == "__main__":
    main()
