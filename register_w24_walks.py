# -*- coding: utf-8 -*-
"""인준·지은 걷기 컷을 **W24 규격 키에 맞춰** 사본으로 만들고 DB에 등록한다.
   ★사장님 지시: 캐릭터 크기는 전 씬에서 일정해야 한다. 기존 컷은 777~785px 인데
     W24 규격은 인준 770 · 지은 706 이다. 지은은 그대로 쓰면 11% 커져 인준만큼 보인다.
   ★축소만 한다. 키워야 하는 것은 손대지 않고 보고한다(원본 화질을 지킨다).

   출력: assets/graphics/poses/w24_<char>_walk_[rl]_<n>.png · anim_char_poses 등록
   사용: python register_w24_walks.py [--dry]
"""
import argparse
import os
import sqlite3

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

DB = "channel/content.db"
OUT = "assets/graphics/poses"
MAX_UP = 1.02                       # 이보다 키워야 하면 손대지 않는다

# (원본 char_key, W24 캐릭터 이름, 규격 키 px)  — 규격은 build_w24.SPEC 과 같다
# ★마담제이 추가(2026-08-05 사장님 지시) — mj_w21 이 20컷으로 가장 많고 전부 실존한다.
SRC = [("injun_w20", "injun", 770), ("jieun_w19", "jieun", 706),
       ("mj_w21", "madam_jay", 693)]
W24_KEY = "w24_walk"                # W24 걷기 전용 char_key


def log(m):
    print(m, flush=True)


def body_h(im):
    b = im.getbbox()
    return (b[3] - b[1]) if b else 0


def main(dry):
    os.makedirs(OUT, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    if not dry:      # ★이 스크립트가 만드는 이름만 지운다(컷랑이 넣은 다른 캐릭터 걷기 보존)
        for _s, nm, _h in SRC:
            cur.execute("DELETE FROM anim_char_poses WHERE char_key=? AND pose_name LIKE ?",
                        (W24_KEY, nm + "_walk%"))
    made, todo = 0, []
    for src_key, name, spec in SRC:
        rows = list(cur.execute(
            "SELECT pose_name,file_path FROM anim_char_poses WHERE char_key=? "
            "AND pose_name LIKE 'walk%' ORDER BY pose_name", (src_key,)))
        for pose, fp in rows:
            if not os.path.exists(fp):
                continue
            im = Image.open(fp).convert("RGBA")
            h = body_h(im)
            k = spec / h if h else 1.0
            if k > MAX_UP:                      # ★키워야 하는 것은 건드리지 않는다
                todo.append(f"{name}_{pose} {h}px → {spec}px (×{k:.3f} 필요)")
                continue
            out = f"{OUT}/w24_{name}_{pose}.png"
            if not dry:
                im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))),
                          Image.LANCZOS).save(out)
                cur.execute(
                    "INSERT INTO anim_char_poses (char_key,pose_name,file_path,flip,pen,updated_at) "
                    "VALUES (?,?,?,0,0,datetime('now'))",
                    (W24_KEY, f"{name}_{pose}", out.replace("\\", "/")))
            made += 1
        log(f"  {name:<8} {len(rows)}컷 · 규격 {spec}px")
    if not dry:
        con.commit()
    con.close()
    log(f"\n{'(모의) ' if dry else ''}W24 걷기 {made}컷 → {OUT}/w24_*_walk_*.png "
        f"· anim_char_poses('{W24_KEY}')")
    if todo:
        log(f"★키워야 해서 손대지 않음 {len(todo)}컷:")
        for t in todo[:8]:
            log(f"    {t}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    raise SystemExit(main(ap.parse_args().dry))
