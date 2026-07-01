# -*- coding: utf-8 -*-
import os
import sqlite3

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    db = os.path.join(ROOT, "channel", "content.db")
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute("SELECT name_en, name_kr, type, file_path, flow_prompt FROM assets WHERE name_en LIKE 'jieun_%'")
    rows = cur.fetchall()
    print("=== SQLite assets for 'jieun' ===")
    for row in rows:
        print(f"Name_en: {row[0]}, Name_kr: {row[1]}, Type: {row[2]}, File: {row[3]}, Prompt: {row[4][:60]}...")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
