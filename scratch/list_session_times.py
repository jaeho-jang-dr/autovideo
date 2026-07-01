import os
import sys
import datetime

BRAIN_DIR = r"C:\Users\antigravity\.gemini\antigravity\brain"
sys.stdout.reconfigure(encoding='utf-8')

def main():
    if not os.path.exists(BRAIN_DIR):
        print(f"[ERR] Brain dir not found: {BRAIN_DIR}")
        return
        
    print(f"Listing all sessions and modification times:")
    sessions = []
    
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
        sessions.append((folder, mtime))
        
    # Sort by modification time
    for folder, mtime in sorted(sessions, key=lambda x: x[1]):
        print(f"  Session ID: {folder} | Last Active: {mtime}")

if __name__ == "__main__":
    main()
