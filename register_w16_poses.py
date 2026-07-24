# -*- coding: utf-8 -*-
"""W16 인준 포즈를 anim_char_poses(char_key='injun_w16')에 등록.
★렌더러는 이 테이블로 포즈를 찾는다 — 등록 안 하면 기본 정면으로 떨어진다(W12 사고).
   normalize_injun.py 실행 후(assets/graphics/poses/injun_w16_*.png 생성 완료 후) 돌린다."""
import sqlite3, os, glob
from collections import Counter

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
os.chdir(ROOT)
DB = "channel/content.db"
CHAR = "injun_w16"

con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("DELETE FROM anim_char_poses WHERE char_key=?", (CHAR,))

n = 0
for p in sorted(glob.glob("assets/graphics/poses/injun_w16_*.png")):
    name = os.path.basename(p).replace("injun_w16_", "").replace(".png", "")
    cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,?,?)",
                (CHAR, name, p.replace("\\", "/"), 0, 0))
    n += 1
con.commit()

# asset_catalog 갱신
cur.execute("DELETE FROM asset_catalog WHERE project='W16' AND category='캐릭터포즈'")
cur.execute("INSERT INTO asset_catalog (project,category,name,location,kind,storage,count,db_table,note) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            ("W16", "캐릭터포즈", "injun_w16 투명 컷아웃", "assets/graphics/poses/", "png", "local",
             n, "anim_char_poses", "1376x880 정규화·발끝y800·서기640·앉기486, 걷기4프레임+모션2프레임"))
con.commit()

print(f"등록: {CHAR} {n}종")
# 걷기·모션 프레임 점검
have = {r[0] for r in con.execute("SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,))}
walks = [w for w in ("walk_r1", "walk_r2", "walk_l1", "walk_l2") if w in have]
motion_b = [m for m in ("cycling_b", "jogging_b", "jump_rope_b", "badminton_b", "frisbee_b", "skateboard_b") if m in have]
print("  걷기 프레임:", walks)
print("  모션 2프레임:", motion_b)
con.close()
