import sqlite3

conn = sqlite3.connect('channel/content.db')
cur = conn.cursor()
cur.execute("SELECT code, title_kr, title_en FROM episodes")
rows = cur.fetchall()

print("All episodes:")
for row in rows:
    print(row)
