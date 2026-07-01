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
    
    # Check tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]
    print("Available tables:", tables)
    
    # Query video_clips for jay_whiteboard_consonants
    print("\n--- video_clips matching 'jay_whiteboard_consonants' ---")
    cur.execute("SELECT * FROM video_clips WHERE project LIKE '%jay_whiteboard_consonants%' OR notes LIKE '%jay_whiteboard_consonants%'")
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    for row in rows:
        for c, val in zip(cols, row):
            print(f"  {c}: {val}")
        print("-" * 40)
        
    # Query other tables
    for t in tables:
        if t == "video_clips":
            continue
        try:
            cur.execute(f"SELECT * FROM {t}")
            cols = [d[0] for d in cur.description]
            # Search for keyword
            where_clause = " OR ".join([f"CAST({c} AS TEXT) LIKE '%consonant%'" for c in cols])
            cur.execute(f"SELECT * FROM {t} WHERE {where_clause}")
            rows = cur.fetchall()
            if rows:
                print(f"\n--- {t} matches ---")
                for row in rows:
                    for c, val in zip(cols, row):
                        print(f"  {c}: {val}")
                    print("-" * 40)
        except Exception as e:
            # print(f"Error reading {t}: {e}")
            pass
            
    conn.close()

if __name__ == "__main__":
    main()
