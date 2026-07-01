# -*- coding: utf-8 -*-
import os
import psycopg2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_env():
    p = os.path.join(ROOT, ".env")
    d = {}
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d

def main():
    env = load_env()
    conn = psycopg2.connect(
        host=env["SUPABASE_DB_HOST"], port=env.get("SUPABASE_DB_PORT", "5432"),
        user=env["SUPABASE_DB_USER"], password=env["SUPABASE_DB_PASSWORD"],
        dbname=env.get("SUPABASE_DB_NAME", "postgres"), sslmode="require")
    cur = conn.cursor()
    
    cur.execute("""
        SELECT key, character_id, view, pose, file_path, storage_url, method, created_at 
        FROM character_assets 
        WHERE key IN ('zollaman_pointing', 'zollaman_thinking')
    """)
    rows = cur.fetchall()
    print("=== Zollaman Pointing & Thinking DB Status ===")
    for row in rows:
        print(f"Key: {row[0]}")
        print(f"  CharID: {row[1]}, View: {row[2]}, Pose: {row[3]}")
        print(f"  File: {row[4]}")
        print(f"  URL: {row[5]}")
        print(f"  Method: {row[6]}")
        print(f"  Created At: {row[7]}")
        print("-" * 50)
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
