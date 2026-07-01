import sqlite3
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(ROOT, 'channel', 'content.db'))
cur = conn.cursor()

print("=== Assets table ===")
cur.execute("SELECT id, name_kr, name_en, type, file_path FROM assets WHERE name_en LIKE '%board%' OR name_en LIKE '%bg%' OR type='background'")
for row in cur.fetchall():
    print(row)

print("\n=== Character Assets (Supabase mock or local) ===")
# SQLite character_assets
try:
    cur.execute("SELECT id, name, file_path, category FROM character_assets WHERE name LIKE '%board%' OR name LIKE '%bg%'")
    for row in cur.fetchall():
        print(row)
except Exception as e:
    print("Error querying character_assets:", e)

conn.close()
