#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""build_scene_objects_w7.py — KO-W07(인사말·자기소개) 11씬 배치 → content.db scene_objects.
졸라걸(stickman_zw_*) 왼쪽, 인사말/자기소개 문구 오른쪽(fade_in). 진동 없음.
재실행: python hangeul_birth_vowels/build_scene_objects_w7.py
"""
import os
import sys
import sqlite3

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "channel", "content.db")
EP = "KO-W07"
SEARCH = ["assets/graphics", "assets/graphics/poses", "assets/graphics/letters", "assets/graphics/objects"]


def CH(pose, cx=300, cy=385, sc=0.72):
    return ("stickman_" + pose, cx, cy, sc, 5, 0, "gesture")


def W(name, cx, cy, sc):
    return (f"word_{name}", cx, cy, sc, 3, 0, "fade_in")


# 자기소개 한 줄: 저는 [핵심] 입니다/사람입니다  (콘텐츠 우측, 가운데 정렬)
def intro(core, tail, y, cx=890):
    return [W("저는", cx - 250, y, 0.34), W(core, cx, y, 0.5), W(tail, cx + 250, y, 0.34)]


L = {
    1: [CH("zw_waving"), W("인사말", 880, 300, 0.6), W("자기소개", 880, 480, 0.52)],
    2: [CH("zw_sitting"), W("인사말", 900, 385, 0.7)],
    3: [CH("zw_point_l"), W("안녕하세요", 900, 385, 0.5)],
    4: [CH("zw_base"), W("감사합니다", 900, 385, 0.5)],
    5: [CH("zw_point_l"), W("반갑습니다", 900, 385, 0.5)],
    6: [CH("zw_thinking"), W("안녕히 가세요", 905, 300, 0.42), W("안녕히 계세요", 905, 480, 0.42)],
    7: [CH("zw_raising_hand"), W("저는", 720, 385, 0.6), W("입니다", 1040, 385, 0.6)],
    8: [CH("zw_point_l")] + intro("민수", "입니다", 385),
    9: [CH("zw_base"), W("저는", 645, 385, 0.32), W("미국", 830, 385, 0.46), W("사람입니다", 1075, 385, 0.3)],
    10: [CH("zw_point_l")] + intro("학생", "입니다", 385),
    11: [CH("zw_jumping"), W("인사말", 880, 300, 0.5), W("자기소개", 880, 480, 0.46),
         ("obj_sparkle", 1090, 250, 0.5, 4, 0, "fade_in")],
}


def find_file(name):
    for d in SEARCH:
        p = os.path.join(ROOT, d, f"{name}.png")
        if os.path.exists(p):
            return os.path.relpath(p, ROOT).replace("\\", "/")
    return None


def resolve(cur, name):
    r = cur.execute("SELECT id FROM assets WHERE name_en=?", (name,)).fetchone()
    if r:
        return r[0]
    r = cur.execute("SELECT id FROM assets WHERE file_path LIKE ?", (f"%{name}.png",)).fetchone()
    if r:
        return r[0]
    fp = find_file(name)
    if not fp:
        raise FileNotFoundError(f"asset not found: {name}")
    typ = "character" if name.startswith("stickman_") else ("word" if name.startswith("word_") else (
        "letter" if name.startswith("letter_") else "object"))
    cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?,?,?,?,?)",
                (name, name, typ, fp, "auto build_scene_objects_w7"))
    print(f"  + auto-registered {name} ({fp})")
    return cur.lastrowid


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
    for seq, items in sorted(L.items()):
        for (name, cx, cy, scale, z, isp, mo) in items:
            aid = resolve(cur, name)
            cur.execute(
                "INSERT INTO scene_objects (episode, scene_seq, asset_id, cx, cy, scale, z_order, is_point, motion_type) "
                "VALUES (?,?,?,?,?,?,?,?,?)", (EP, seq, aid, cx, cy, scale, z, isp, mo))
    con.commit()
    n = cur.execute("SELECT count(*) FROM scene_objects WHERE episode=?", (EP,)).fetchone()[0]
    print(f"scene_objects for {EP}: {n} placements across {len(L)} scenes")
    con.close()


if __name__ == "__main__":
    main()
