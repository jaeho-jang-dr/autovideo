#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_scene_objects_w6.py — KO-W06(연음과 음운 변동) 11씬 배치 → content.db scene_objects.
캐릭터 졸라맨(stickman_zm_*) 왼쪽, 콘텐츠(표기형 → 발음형) 오른쪽. 왼손 가리키기 zm_point_l.
진동 없는 fade_in. 재실행: python hangeul_birth_vowels/build_scene_objects_w6.py
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
EP = "KO-W06"
SEARCH = ["assets/graphics", "assets/graphics/poses", "assets/graphics/letters", "assets/graphics/objects"]


def CH(pose, cx=300, cy=385, sc=0.72):
    return ("stickman_" + pose, cx, cy, sc, 5, 0, "gesture")


def pair(spell, sound, y, x0=620, sc=0.6):
    """표기형 → 발음형 한 줄."""
    return [(f"word_{spell}", x0, y, sc, 3, 0, "fade_in"),
            ("sym_arrow", x0 + 230, y, 0.34, 4, 0, "fade_in"),
            (f"word_{sound}", x0 + 400, y, sc, 3, 0, "fade_in")]


L = {
    1: [CH("zm_waving"),
        ("word_연음", 880, 300, 0.6, 3, 0, "fade_in"),
        ("word_음운변동", 880, 475, 0.5, 3, 0, "fade_in")],
    2: [CH("zm_sitting"),
        ("word_옷이", 760, 370, 0.6, 3, 0, "fade_in"),
        ("sym_arrow", 960, 375, 0.3, 4, 0, "fade_in"),
        ("word_오시", 1110, 370, 0.6, 3, 0, "fade_in")],
    3: [CH("zm_point_l")] + pair("음악", "으막", 385, x0=640, sc=0.7),
    4: [CH("zm_thinking")] + pair("옷이", "오시", 385, x0=640, sc=0.7),
    5: [CH("zm_point_l")] + pair("꽃이", "꼬치", 385, x0=640, sc=0.7),
    6: [CH("zm_studying")] + pair("책을", "채글", 300, x0=640, sc=0.56)
       + pair("한국어", "한구거", 470, x0=640, sc=0.56),
    7: [CH("zm_thinking")] + pair("좋아요", "조아요", 385, x0=625, sc=0.56),
    8: [CH("zm_point_l")] + pair("웃어요", "우서요", 300, x0=640, sc=0.56)
       + pair("있어요", "이써요", 470, x0=640, sc=0.56),
    9: [CH("zm_thinking"),
        ("word_표기형", 720, 300, 0.56, 3, 0, "fade_in"),
        ("word_발음형", 720, 480, 0.56, 3, 0, "fade_in"),
        ("word_옷이", 1010, 300, 0.46, 3, 0, "fade_in"),
        ("word_오시", 1010, 480, 0.46, 3, 0, "fade_in")],
    10: [CH("zm_studying")] + pair("음악", "으막", 300, x0=640, sc=0.56)
        + pair("옷이", "오시", 470, x0=640, sc=0.56),
    11: [CH("zm_jumping"),
         ("word_연음", 880, 300, 0.5, 3, 0, "fade_in"),
         ("word_음운변동", 880, 470, 0.44, 3, 0, "fade_in"),
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
                (name, name, typ, fp, "auto build_scene_objects_w6"))
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
