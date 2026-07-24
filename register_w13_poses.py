# -*- coding: utf-8 -*-
"""W13 지은 포즈를 anim_char_poses(char_key='jieun_w13')에 등록.
★렌더러는 이 테이블로 포즈를 찾는다 — 등록 안 하면 전부 기본 정면으로 떨어진다(W12에서 겪은 사고)."""
import sqlite3, os, glob, json

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
os.chdir(ROOT)
DB = "channel/content.db"
CHAR = "jieun_w13"

con = sqlite3.connect(DB); cur = con.cursor()
cur.execute("DELETE FROM anim_char_poses WHERE char_key=?", (CHAR,))

n = 0
for p in sorted(glob.glob("assets/graphics/poses/jieun_w13_*.png")):
    name = os.path.basename(p).replace("jieun_w13_", "").replace(".png", "")
    if name == "base":
        continue
    cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,?,?)",
                (CHAR, name, p.replace("\\", "/"), 0, 0))
    n += 1

# base도 등록(폴백용)
if os.path.exists("assets/graphics/poses/jieun_w13_base.png"):
    cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,?,?)",
                (CHAR, "base", "assets/graphics/poses/jieun_w13_base.png", 0, 0)); n += 1

con.commit()

# 검증: 씬 beats가 쓰는 포즈가 전부 등록됐나
used = set()
for (ip,) in cur.execute("SELECT image_prompt FROM scenes WHERE episode='KO-W13'"):
    aseq = json.loads(ip).get("anim_seq")
    r = cur.execute("SELECT beats_json FROM anim_sequences WHERE seq_name=?", (aseq,)).fetchone()
    if r:
        for b in json.loads(r[0]):
            used.add(b["name"])
reg = {r[0] for r in cur.execute("SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,))}
missing = sorted(used - reg)
print(f"등록: {CHAR} {n}개")
print(f"씬이 쓰는 포즈 {len(used)}종")
print(f"★미등록(정면으로 대체될 것): {missing if missing else '없음 ✅'}")
con.close()
