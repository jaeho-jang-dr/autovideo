# -*- coding: utf-8 -*-
"""W19 지은 포즈(표정 32 + 걷기 16)를 anim_char_poses(char_key='jieun_w19')에 등록.
   ★렌더러는 이 테이블로 포즈를 찾는다. assets/graphics/poses/jieun_w19_*.png 전부."""
import sqlite3, os, glob

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"; os.chdir(ROOT)
DB = "channel/content.db"
CHAR = "jieun_w19"

con = sqlite3.connect(DB); cur = con.cursor()
cur.execute("DELETE FROM anim_char_poses WHERE char_key=?", (CHAR,))
n = 0
for p in sorted(glob.glob("assets/graphics/poses/jieun_w19_*.png")):
    name = os.path.basename(p).replace("jieun_w19_", "").replace(".png", "")
    cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,?,?)",
                (CHAR, name, p.replace("\\", "/"), 0, 0))
    n += 1
con.commit()
have = sorted(r[0] for r in con.execute("SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,)))
con.close()
print(f"등록: {CHAR} {n}종")
print("  표정:", [h for h in have if not h.startswith("walk")])
print("  걷기:", [h for h in have if h.startswith("walk")])
