import sqlite3
import os

sqlite_path = "channel/content.db"
conn = sqlite3.connect(sqlite_path)
c = conn.cursor()
c.execute("select id, project, file_path, notes from video_clips where file_path like '%consonants.mp4'")
for row in c.fetchall():
    print("MATCH:", row)
conn.close()
