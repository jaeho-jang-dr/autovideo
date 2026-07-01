#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""build_scene_objects_w8.py — KO-W08(숫자·날짜·시간) 11씬 배치 → content.db scene_objects.
졸라맨(stickman_zm_*) 왼쪽, 숫자/요일/시간 콘텐츠 오른쪽(fade_in). 진동 없음.
재실행: python hangeul_birth_vowels/build_scene_objects_w8.py
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
EP = "KO-W08"
SEARCH = ["assets/graphics", "assets/graphics/poses", "assets/graphics/letters", "assets/graphics/objects"]


def CH(pose, cx=300, cy=385, sc=0.72):
    return ("stickman_" + pose, cx, cy, sc, 5, 0, "gesture")


def W(name, cx, cy, sc):
    return (f"word_{name}", cx, cy, sc, 3, 0, "fade_in")


def num_row(words, y, x0=600, step=160, sc=0.5):
    """숫자/요일 한 줄(콘텐츠 우측, 균등 배치)."""
    return [W(w, x0 + i * step, y, sc) for i, w in enumerate(words)]


L = {
    1: [CH("zm_waving"), W("숫자", 760, 280, 0.5), W("날짜", 980, 280, 0.5), W("시간", 880, 470, 0.5)],
    2: [CH("zm_sitting"), W("고유어", 800, 320, 0.52), W("한자어", 800, 480, 0.52)],
    3: [CH("zm_point_l")] + num_row(["하나", "둘", "셋", "넷", "다섯"], 385, x0=575, step=160, sc=0.32),
    4: [CH("zm_clapping")] + num_row(["여섯", "일곱", "여덟", "아홉", "열"], 385, x0=575, step=160, sc=0.32),
    5: [CH("zm_point_l")] + num_row(["일", "이", "삼", "사", "오"], 385, x0=640, step=128, sc=0.6),
    6: [CH("zm_base")] + num_row(["육", "칠", "팔", "구", "십"], 385, x0=640, step=128, sc=0.6),
    7: [CH("zm_thinking"),
        W("고유어", 700, 300, 0.46), W("개수", 980, 300, 0.46),
        W("한자어", 700, 480, 0.46), W("날짜", 980, 480, 0.46)],
    8: [CH("zm_point_l"),
        W("세", 655, 385, 0.5), W("시", 790, 385, 0.5),
        W("삼십", 955, 385, 0.38), W("분", 1140, 385, 0.46)],
    9: [CH("zm_studying")] + num_row(["월", "화", "수", "목", "금", "토", "일"], 385, x0=580, step=102, sc=0.46),
    10: [CH("zm_thinking"), W("고유어", 800, 320, 0.5), W("한자어", 800, 480, 0.5)],
    11: [CH("zm_jumping"), W("숫자", 820, 290, 0.46), W("날짜", 980, 290, 0.46), W("시간", 900, 470, 0.46),
         ("obj_sparkle", 1100, 250, 0.5, 4, 0, "fade_in")],
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
                (name, name, typ, fp, "auto build_scene_objects_w8"))
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
