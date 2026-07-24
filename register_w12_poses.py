# -*- coding: utf-8 -*-
"""W12 인준 포즈 23종을 anim_char_poses(char_key='injun_w12')에 등록.
★렌더러(compile_stickman)는 이 테이블로 포즈를 찾는다 — 등록 안 하면 정면 하나만 나온다."""
import sqlite3, os, glob

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
os.chdir(ROOT)
DB = "channel/content.db"
CHAR = "injun_w12"

con = sqlite3.connect(DB); cur = con.cursor()
cur.execute("DELETE FROM anim_char_poses WHERE char_key=?", (CHAR,))

files = sorted(glob.glob("assets/graphics/poses/injun_w12_*.png"))
n = 0
for p in files:
    name = os.path.basename(p).replace("injun_w12_", "").replace(".png", "")
    rel = p.replace("\\", "/")
    cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,?,?)",
                (CHAR, name, rel, 0, 0))   # flip=0: normalize_w12에서 이미 리버스 처리 완료
    n += 1

# 빌더 beats가 쓰는 이름 중 파일이 없는 것 → 대체 별칭 등록(렌더 누락 방지)
ALIAS = {
    "walk_right": "walk_right", "walk_left": "walk_left",
    "greeting": "presenting", "clapping": "cheering", "wave": "presenting",
    "point_left": "point_left",
}
have = {r[0] for r in cur.execute("SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,))}
for want, src in ALIAS.items():
    if want not in have and src in have:
        fp = cur.execute("SELECT file_path FROM anim_char_poses WHERE char_key=? AND pose_name=?", (CHAR, src)).fetchone()[0]
        cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,?,?)",
                    (CHAR, want, fp, 0, 0)); n += 1

con.commit()

# 검증: 씬 beats에서 쓰는 포즈가 전부 등록됐나
import json
used = set()
for (ip,) in cur.execute("SELECT image_prompt FROM scenes WHERE episode='KO-W12'"):
    aseq = json.loads(ip).get("anim_seq")
    r = cur.execute("SELECT beats_json FROM anim_sequences WHERE seq_name=?", (aseq,)).fetchone()
    if r:
        for b in json.loads(r[0]):
            used.add(b["name"])
reg = {r[0] for r in cur.execute("SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,))}
missing = sorted(used - reg)
print(f"등록 완료: {CHAR} {n}개")
print(f"씬에서 쓰는 포즈 {len(used)}종: {', '.join(sorted(used))}")
print(f"★미등록(정면으로 대체될 것): {missing if missing else '없음 ✅'}")
con.close()
