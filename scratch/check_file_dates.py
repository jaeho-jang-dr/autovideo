import os
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

def print_file_times(path):
    if not os.path.exists(path):
        print(f"[ERR] File not found: {path}")
        return
    stat = os.stat(path)
    # Windows creation time is st_ctime
    ctime = datetime.datetime.fromtimestamp(stat.st_ctime)
    mtime = datetime.datetime.fromtimestamp(stat.st_mtime)
    print(f"File: {path}")
    print(f"  Created: {ctime}")
    print(f"  Modified: {mtime}")
    print(f"  Size: {stat.st_size} bytes")

def main():
    p1 = os.path.join(ROOT, "jay_whiteboard_consonants_prompt", "scene_1.mp4")
    p2 = os.path.join(ROOT, "assets", "videos", "jay_whiteboard_consonants.mp4")
    p3 = os.path.join(ROOT, "scratch", "register_jay_consonants_video.py")
    p4 = os.path.join(ROOT, "scratch", "jay_whiteboard_consonants_prompt.txt")
    
    print_file_times(p1)
    print("-" * 50)
    print_file_times(p2)
    print("-" * 50)
    print_file_times(p3)
    print("-" * 50)
    print_file_times(p4)

if __name__ == "__main__":
    main()
