# -*- coding: utf-8 -*-
"""W18 마담제이 포즈를 anim_char_poses(char_key='mj_w18')에 등록.
★렌더러는 이 테이블로 포즈를 찾는다 — 등록 안 하면 기본 정면으로 떨어진다.
   assets/graphics/poses/mj_w18_*.png (컷아웃·정규화본) 25종 등록."""
import sqlite3, os, glob

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
os.chdir(ROOT)
DB = "channel/content.db"
CHAR = "mj_w18"

con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("DELETE FROM anim_char_poses WHERE char_key=?", (CHAR,))

n = 0
for p in sorted(glob.glob("assets/graphics/poses/mj_w18_*.png")):
    name = os.path.basename(p).replace("mj_w18_", "").replace(".png", "")
    cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,?,?)",
                (CHAR, name, p.replace("\\", "/"), 0, 0))
    n += 1
con.commit()

cur.execute("DELETE FROM asset_catalog WHERE project='W18' AND category='캐릭터포즈'")
cur.execute("INSERT INTO asset_catalog (project,category,name,location,kind,storage,count,db_table,note) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            ("W18", "캐릭터포즈", "mj_w18 마담제이 투명 컷아웃", "assets/graphics/poses/", "png", "local",
             n, "anim_char_poses", "1024x1024·서기 몸높이≈895px·발끝y965 통일·감정표정 다양·오른쪽 향함, 걷기2프레임"))
con.commit()

print(f"등록: {CHAR} {n}종")
have = {r[0] for r in con.execute("SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,))}
print("  포즈:", sorted(have))
con.close()
