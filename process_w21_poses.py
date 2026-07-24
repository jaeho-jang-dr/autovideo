# -*- coding: utf-8 -*-
"""agy 생성 순백배경 포즈(home_vocab/w21/poses_raw/mj_w21_*.png) → 투명 컷아웃 + 정규화
   (발끝 y1209·몸높이 770·캔버스 1024x1280, 걷기/인사 컷과 동일 규격) → assets/graphics/poses/,
   그리고 DB anim_char_poses(mj_w21)에 등록."""
import os, glob, sqlite3
from PIL import Image
from cutout_madam_w21 import cutout, normalize  # 동일 컷아웃/정규화 재사용

ROOT = "D:/Entertainments/DevEnvironment/autovideo"
SRC = os.path.join(ROOT, "home_vocab/w21/poses_raw")
DST = os.path.join(ROOT, "assets/graphics/poses")

def main():
    files = sorted(glob.glob(os.path.join(SRC, "mj_w21_*.png")))
    db = sqlite3.connect(os.path.join(ROOT, "channel/content.db")); c = db.cursor()
    cols = [r[1] for r in c.execute("PRAGMA table_info(anim_char_poses)")]
    n = 0
    for p in files:
        key = os.path.splitext(os.path.basename(p))[0]          # mj_w21_<pose>
        pose = key[len("mj_w21_"):]
        crop = cutout(p)
        if crop is None:
            print("  빈:", key); continue
        canvas = normalize(crop)
        out = os.path.join(DST, key + ".png")
        canvas.save(out)
        fp = f"assets/graphics/poses/{key}.png"
        if set(["char_key","pose_name","file_path","flip","pen"]).issubset(cols):
            c.execute("INSERT OR REPLACE INTO anim_char_poses(char_key,pose_name,file_path,flip,pen) VALUES(?,?,?,0,1)",
                      ("mj_w21", pose, fp))
        else:
            c.execute("INSERT OR REPLACE INTO anim_char_poses(char_key,pose_name,file_path) VALUES(?,?,?)",
                      ("mj_w21", pose, fp))
        n += 1
        print(f"  {pose}")
    db.commit()
    tot = c.execute("SELECT COUNT(*) FROM anim_char_poses WHERE char_key='mj_w21'").fetchone()[0]
    db.close()
    print(f"정규화·등록 {n}개 → {DST}/mj_w21_*.png  (DB mj_w21 총 {tot}개)")

if __name__ == "__main__":
    main()
