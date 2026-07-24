# -*- coding: utf-8 -*-
"""W20 인준 포즈(표정 30 + 기존 걷기 14)를 anim_char_poses(char_key='injun_w20')에 등록하고,
   포즈·배경을 asset_catalog에 요약 등록. ★렌더러는 anim_char_poses로 포즈를 찾는다."""
import sqlite3, os, glob, datetime

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"; os.chdir(ROOT)
DB = "channel/content.db"
CHAR = "injun_w20"
NOW = datetime.datetime.now().isoformat(timespec="seconds")

con = sqlite3.connect(DB); cur = con.cursor()

# --- anim_char_poses ---
cur.execute("DELETE FROM anim_char_poses WHERE char_key=?", (CHAR,))
n = 0
for p in sorted(glob.glob("assets/graphics/poses/injun_w20_*.png")):
    name = os.path.basename(p).replace("injun_w20_", "").replace(".png", "")
    cur.execute("INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen) VALUES (?,?,?,?,?)",
                (CHAR, name, p.replace("\\", "/"), 0, 0))
    n += 1

# --- asset_catalog 요약 (poses / backgrounds) ---
def upsert_catalog(project, category, name, location, kind, count, note):
    row = cur.execute("SELECT id FROM asset_catalog WHERE name=? AND project=?", (name, project)).fetchone()
    if row:
        cur.execute("UPDATE asset_catalog SET category=?,location=?,kind=?,count=?,note=?,updated_at=? WHERE id=?",
                    (category, location, kind, count, note, NOW, row[0]))
    else:
        cur.execute("INSERT INTO asset_catalog (project,category,name,location,kind,storage,count,note,updated_at)"
                    " VALUES (?,?,?,?,?,?,?,?,?)",
                    (project, category, name, location, kind, "local", count, note, NOW))

npose = len(glob.glob("assets/graphics/poses/injun_w20_*.png"))
ntalk = npose - len(glob.glob("assets/graphics/poses/injun_w20_walk_*.png"))
nbg = len(glob.glob("home_vocab/w20/bg/w20_*.png"))
upsert_catalog("W20", "character_poses", "injun_w20 poses (talk + walk)",
               "assets/graphics/poses/injun_w20_<key>.png", "png", npose,
               f"인준 이태원 포즈 표정 {ntalk} + 걷기 {npose - ntalk} (agy 생성·컷아웃·정규화, char_key=injun_w20)")
upsert_catalog("W20", "backgrounds", "이태원 배경 23",
               "home_vocab/w20/bg/w20_<key>.png", "png", nbg,
               "이태원 구석구석 배경 23종 (agy 나노바나나, 글자없음·연속풍경·1280x720)")

con.commit()
have = sorted(r[0] for r in con.execute("SELECT pose_name FROM anim_char_poses WHERE char_key=?", (CHAR,)))
con.close()
print(f"anim_char_poses 등록: {CHAR} {n}종")
print("  표정:", [h for h in have if not h.startswith("walk")])
print("  걷기:", [h for h in have if h.startswith("walk")])
print(f"asset_catalog: poses {npose}(표정 {ntalk}+걷기 {npose-ntalk}), backgrounds {nbg}")
