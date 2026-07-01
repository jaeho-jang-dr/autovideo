# -*- coding: utf-8 -*-
import os
import psycopg2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_env(p=None):
    p = p or os.path.join(ROOT, ".env")
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
        dbname=env.get("SUPABASE_DB_NAME", "postgres"), sslmode="require", connect_timeout=20)
    cur = conn.cursor()
    
    cur.execute("SELECT key, character_id, view, pose, file_path FROM character_assets WHERE key LIKE '%zolla%'")
    rows = cur.fetchall()
    print("=== Newly Added Injun & Injun-Jieun Assets ===")
    for row in rows:
        print(f"Key: {row[0]}, CharID: {row[1]}, View: {row[2]}, Pose: {row[3]}, File: {row[4]}")
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
