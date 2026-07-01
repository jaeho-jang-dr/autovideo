# -*- coding: utf-8 -*-
import sqlite3

def main():
    conn = sqlite3.connect("channel/content.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name_en, name_kr, type, file_path FROM assets WHERE type='object'")
    rows = cur.fetchall()
    print("=== SQLite Objects ===")
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Name KR: {row[2]}, Type: {row[3]}, File: {row[4]}")
    conn.close()

if __name__ == "__main__":
    main()
