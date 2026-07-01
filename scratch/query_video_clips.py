import sqlite3
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding='utf-8')

def main():
    db_path = os.path.join(ROOT, "channel", "content.db")
    if not os.path.exists(db_path):
        print(f"[ERR] Database not found: {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Query video_clips for jay_whiteboard_consonants
    cur.execute("SELECT * FROM video_clips WHERE project LIKE '%jay_whiteboard_consonants%'")
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    
    print(f"Matched {len(rows)} rows:")
    for row in rows:
        for c, val in zip(cols, row):
            print(f"  {c}: {val}")
        print("-" * 50)
        
    conn.close()

if __name__ == "__main__":
    main()
