# -*- coding: utf-8 -*-
"""W15 지은 포즈를 anim_char_poses(char_key='jieun_w15')에 등록.
★렌더러는 이 테이블로 포즈를 찾는다 — 등록 안 하면 기본 정면으로 떨어진다(W12 사고)."""
import sqlite3, os, glob

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
os.chdir(ROOT)
DB = "channel/content.db"
CHAR = "jieun_w15"

con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("DELETE FROM anim_char_poses WHERE char_key=?", (CHAR,))

n = 0
for p in sorted(glob.glob("assets/graphics/poses/jieun_w15_*.png")):
    name = os.path.basename(p).replace("jieun_w15_", "").replace(".png", "")
    cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,?,?)",
                (CHAR, name, p.replace("\\", "/"), 0, 0))
    n += 1
con.commit()
print(f"등록: {CHAR} {n}종")

# 계절별 집계
from collections import Counter
c = Counter(r[0].split("_")[0] for r in
            con.execute("SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,)))
print("  계절별:", dict(c))
con.close()
