# -*- coding: utf-8 -*-
import sqlite3
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

def main():
    db_path = os.path.join('channel', 'content.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Query for objects containing 강, 꽃, 콩
    cur.execute("SELECT id, name_kr, name_en, file_path, type FROM assets WHERE name_kr LIKE '%강%' OR name_kr LIKE '%꽃%' OR name_kr LIKE '%콩%' OR name_kr LIKE '%강%'")
    rows = cur.fetchall()
    
    print(f"Matched assets: {len(rows)}")
    for row in rows:
        print(f"ID: {row[0]} | KR: {row[1]} | EN: {row[2]} | Path: {row[3]} | Type: {row[4]}")
        
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
