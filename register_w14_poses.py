# -*- coding: utf-8 -*-
"""W14 마담제이 포즈를 anim_char_poses(char_key='madam_j_w14')에 등록.
★렌더러는 이 테이블로 포즈를 찾는다 — 등록 안 하면 전부 기본 정면으로 떨어진다(W12 사고)."""
import sqlite3, os, glob, json

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
os.chdir(ROOT)
DB = "channel/content.db"
CHAR = "madam_j_w14"

con = sqlite3.connect(DB); cur = con.cursor()
cur.execute("DELETE FROM anim_char_poses WHERE char_key=?", (CHAR,))

n = 0
for p in sorted(glob.glob("assets/graphics/poses/mj_w14_*.png")):
    name = os.path.basename(p).replace("mj_w14_", "").replace(".png", "")
    cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,?,?)",
                (CHAR, name, p.replace("\\", "/"), 0, 0))
    n += 1
con.commit()

# 검증: 씬 beats가 쓰는 포즈가 전부 등록됐나 (씬이 아직 없으면 스킵)
used = set()
c2 = con.cursor()
for (ip,) in cur.execute("SELECT image_prompt FROM scenes WHERE episode='KO-W14'"):
    aseq = json.loads(ip).get("anim_seq")
    r = c2.execute("SELECT beats_json FROM anim_sequences WHERE seq_name=?", (aseq,)).fetchone()
    if r:
        for b in json.loads(r[0]):
            used.add(b["name"])
reg = {r[0] for r in con.execute("SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,))}
missing = sorted(used - reg)
print(f"등록: {CHAR} {n}개")
if used:
    print(f"씬이 쓰는 포즈 {len(used)}종 / 미등록: {missing if missing else '없음 ✅'}")
    unused = sorted(reg - used - {"base"})
    print(f"★만들고 안 쓰는 포즈: {unused if unused else '없음 ✅'}")
else:
    print("(씬 아직 미등록 — build_w14.py 실행 후 재검증)")
con.close()
