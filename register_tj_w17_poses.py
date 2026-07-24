# -*- coding: utf-8 -*-
"""W17 티쳐제이 포즈를 anim_char_poses(char_key='tj_w17')에 등록.
★렌더러는 이 테이블로 포즈를 찾는다 — 등록 안 하면 기본 정면으로 떨어진다(W12 사고).
   assets/graphics/poses/tj_w17_*.png (승인 컷아웃 복사본) 24종을 그대로 등록한다."""
import sqlite3, os, glob

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
os.chdir(ROOT)
DB = "channel/content.db"
CHAR = "tj_w17"

con = sqlite3.connect(DB)
cur = con.cursor()
cur.execute("DELETE FROM anim_char_poses WHERE char_key=?", (CHAR,))

n = 0
for p in sorted(glob.glob("assets/graphics/poses/tj_w17_*.png")):
    name = os.path.basename(p).replace("tj_w17_", "").replace(".png", "")
    cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,?,?)",
                (CHAR, name, p.replace("\\", "/"), 0, 0))
    n += 1
con.commit()

# asset_catalog 갱신
cur.execute("DELETE FROM asset_catalog WHERE project='W17' AND category='캐릭터포즈'")
cur.execute("INSERT INTO asset_catalog (project,category,name,location,kind,storage,count,db_table,note) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            ("W17", "캐릭터포즈", "tj_w17 티쳐제이 투명 컷아웃", "assets/graphics/poses/", "png", "local",
             n, "anim_char_poses", "1024x1024·인물높이~897px 일관(편차15px)·발끝y966·서기 style4 락, 걷기4프레임"))
con.commit()

print(f"등록: {CHAR} {n}종")
have = {r[0] for r in con.execute("SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,))}
walks = [w for w in ("walk_right_1", "walk_right_2", "walk_left_1", "walk_left_2") if w in have]
print("  등록 포즈:", sorted(have))
print("  걷기 프레임:", walks)
con.close()
