#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_scene_objects_w2.py — KO-W02(기초 자음과 모아쓰기) 26씬 에셋 배치 → content.db scene_objects.
컬러 연필 포즈 + 발음기관 머리(상형) + 자음/모음/단어 글자 + 음절블록. 1280x720 픽셀.
재실행: python hangeul_birth_vowels/build_scene_objects_w2.py
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
EP = "KO-W02"
SEARCH = ["assets/graphics", "assets/graphics/poses", "assets/graphics/letters"]

PP = "stickman_pencil_"   # pencil pose prefix


def C(name): return name  # passthrough


def row(letters, y, x0, step, scale, z=3, mo="elastic_pop"):
    return [(f"letter_{v}", x0 + i * step, y, scale, z, 0, mo) for i, v in enumerate(letters)]


# seq -> [(name, cx, cy, scale, z, is_point, motion)]
HEAD = ("organ_head_profile", 870, 350, 0.92, 3, 0, "fade_in")
L = {
    1: [(PP + "wave", 320, 450, 0.60, 5, 0, "fade_in")]
       + row("ㄱㄴㄷㄹㅁ", 200, 720, 95, 0.5, 2, "float")
       + row("ㅂㅅㅇㅈㅎ", 330, 760, 95, 0.5, 2, "float"),
    2: [(PP + "point", 300, 455, 0.58, 5, 0, "fade_in"), HEAD],
    3: [(PP + "point", 290, 455, 0.56, 5, 0, "fade_in"), HEAD,
        ("obj_reddot", 805, 372, 0.5, 4, 1, "elastic_pop"), ("letter_ㄱ", 1130, 360, 1.2, 3, 0, "write")],
    4: [(PP + "point", 290, 455, 0.56, 5, 0, "fade_in"), HEAD,
        ("obj_reddot", 930, 372, 0.45, 4, 1, "elastic_pop"), ("letter_ㄴ", 1130, 360, 1.2, 3, 0, "write")],
    5: [(PP + "point", 290, 455, 0.56, 5, 0, "fade_in"), HEAD,
        ("obj_reddot", 950, 360, 0.45, 4, 1, "elastic_pop"), ("letter_ㅁ", 1130, 360, 1.1, 3, 0, "write")],
    6: [(PP + "point", 290, 455, 0.56, 5, 0, "fade_in"), HEAD,
        ("obj_reddot", 935, 365, 0.4, 4, 1, "elastic_pop"), ("letter_ㅅ", 1130, 360, 1.2, 3, 0, "write")],
    7: [(PP + "point", 290, 455, 0.56, 5, 0, "fade_in"), HEAD,
        ("obj_reddot", 800, 360, 0.5, 4, 1, "elastic_pop"), ("letter_ㅇ", 1130, 360, 1.2, 3, 0, "write")],
    8: [(PP + "present", 300, 460, 0.58, 5, 0, "fade_in")] + row("ㄱㄴㅁㅅㅇ", 320, 600, 130, 0.62, 3),
    9: [(PP + "point", 300, 455, 0.58, 5, 0, "fade_in"),
        ("letter_ㄴ", 700, 360, 1.0, 3, 0, "fade_in"), ("obj_plus", 880, 360, 0.5, 4, 1, "elastic_pop"),
        ("letter_ㄷ", 1050, 360, 1.0, 3, 0, "write")],
    10: [(PP + "write", 300, 460, 0.58, 5, 0, "fade_in"),
         ("letter_ㄴ", 640, 280, 0.8, 3, 0, "fade_in"), ("obj_plus", 770, 280, 0.34, 4, 0, "elastic_pop"),
         ("letter_ㄷ", 900, 280, 0.8, 3, 0, "write"),
         ("letter_ㅁ", 640, 470, 0.8, 3, 0, "fade_in"), ("obj_plus", 770, 470, 0.34, 4, 0, "elastic_pop"),
         ("letter_ㅂ", 900, 470, 0.8, 3, 0, "write")],
    11: [(PP + "write", 300, 460, 0.58, 5, 0, "fade_in"),
         ("letter_ㅅ", 600, 270, 0.7, 3, 0, "fade_in"), ("obj_plus", 710, 270, 0.3, 4, 0, "elastic_pop"),
         ("letter_ㅈ", 820, 270, 0.7, 3, 0, "write"),
         ("letter_ㅇ", 600, 450, 0.7, 3, 0, "fade_in"), ("obj_plus", 710, 450, 0.3, 4, 0, "elastic_pop"),
         ("letter_ㅎ", 820, 450, 0.7, 3, 0, "write"),
         ("letter_ㄹ", 1050, 360, 0.95, 3, 0, "write")],
    12: [(PP + "present", 300, 460, 0.56, 5, 0, "fade_in")]
        + row("ㄱㄴㄷㄹㅁ", 300, 560, 100, 0.5, 3)
        + row("ㅂㅅㅇㅈㅎ", 440, 560, 100, 0.5, 3),
    13: [(PP + "point", 300, 455, 0.58, 5, 0, "fade_in"), ("obj_block", 850, 360, 1.0, 3, 1, "elastic_pop")],
    14: [(PP + "write", 290, 460, 0.56, 5, 0, "fade_in"),
         ("letter_ㄱ", 640, 360, 0.85, 3, 0, "write"), ("obj_plus", 760, 360, 0.34, 4, 0, "elastic_pop"),
         ("letter_ㅏ", 870, 360, 0.85, 3, 0, "write"), ("word_가", 1080, 360, 0.85, 3, 1, "elastic_pop")],
    15: [(PP + "point", 300, 455, 0.58, 5, 0, "fade_in"),
         ("word_나", 700, 340, 0.85, 3, 0, "elastic_pop"), ("word_머", 920, 340, 0.85, 3, 0, "elastic_pop"),
         ("word_디", 1120, 340, 0.85, 3, 0, "elastic_pop")],
    16: [(PP + "point", 300, 455, 0.58, 5, 0, "fade_in"),
         ("word_고", 720, 340, 0.85, 3, 0, "elastic_pop"), ("word_누", 950, 340, 0.85, 3, 0, "elastic_pop"),
         ("word_드", 1140, 340, 0.85, 3, 0, "elastic_pop")],
    17: [(PP + "present", 300, 460, 0.58, 5, 0, "fade_in"), ("obj_block", 850, 360, 1.0, 3, 1, "elastic_pop")],
    18: [(PP + "write", 280, 460, 0.56, 5, 0, "fade_in"),
         ("word_고", 560, 360, 0.58, 3, 0, "write"), ("obj_plus", 672, 360, 0.30, 4, 0, "elastic_pop"),
         ("word_기", 772, 360, 0.58, 3, 0, "write"), ("word_고기", 1030, 360, 0.68, 3, 1, "elastic_pop")],
    19: [(PP + "present", 300, 460, 0.58, 5, 0, "fade_in"),
         ("word_나", 720, 350, 0.9, 3, 0, "elastic_pop"), ("word_누나", 1010, 350, 0.85, 3, 0, "elastic_pop")],
    20: [(PP + "present", 280, 460, 0.56, 5, 0, "fade_in"),
         ("word_머리", 620, 355, 0.60, 3, 0, "elastic_pop"), ("word_바나나", 980, 355, 0.56, 3, 0, "elastic_pop")],
    21: [(PP + "present", 280, 460, 0.56, 5, 0, "fade_in"),
         ("word_아버지", 660, 355, 0.56, 3, 0, "elastic_pop"), ("word_어머니", 1030, 355, 0.56, 3, 0, "elastic_pop")],
    22: [(PP + "present", 280, 460, 0.56, 5, 0, "fade_in"),
         ("word_오이", 580, 358, 0.52, 3, 0, "elastic_pop"), ("word_호수", 820, 358, 0.52, 3, 0, "elastic_pop"),
         ("word_지도", 1060, 358, 0.52, 3, 0, "elastic_pop")],
    23: [(PP + "point", 280, 455, 0.56, 5, 0, "fade_in"),
         ("obj_card", 870, 368, 1.15, 3, 1, "elastic_pop"), ("word_고기", 870, 352, 0.46, 4, 0, "fade_in")],
    24: [(PP + "write", 300, 460, 0.58, 5, 0, "fade_in"),
         ("obj_block", 820, 350, 0.85, 3, 1, "elastic_pop"), ("letter_ㄱ", 820, 350, 0.7, 4, 0, "write")],
    25: [(PP + "present", 300, 460, 0.56, 5, 0, "fade_in")]
        + row("ㄱㄴㄷㄹㅁ", 280, 580, 95, 0.46, 3)
        + row("ㅂㅅㅇㅈㅎ", 400, 580, 95, 0.46, 3)
        + [("obj_block", 950, 480, 0.55, 3, 0, "elastic_pop")],
    26: [("stickman_cheer", 640, 455, 0.62, 5, 0, "fade_in"),
         ("obj_bell", 935, 250, 0.55, 4, 1, "swing"), ("obj_sparkle", 360, 260, 0.55, 4, 0, "fade_in")],
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
                (name, name, typ, fp, "auto build_scene_objects_w2"))
    print(f"  + auto-registered {name} ({fp})")
    return cur.lastrowid


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
    total = 0
    for seq, items in sorted(L.items()):
        for (name, cx, cy, scale, z, isp, mo) in items:
            aid = resolve(cur, name)
            cur.execute(
                "INSERT INTO scene_objects (episode, scene_seq, asset_id, cx, cy, scale, z_order, is_point, motion_type) "
                "VALUES (?,?,?,?,?,?,?,?,?)", (EP, seq, aid, cx, cy, scale, z, isp, mo))
            total += 1
    con.commit()
    n = cur.execute("SELECT count(*) FROM scene_objects WHERE episode=?", (EP,)).fetchone()[0]
    print(f"scene_objects for {EP}: {n} placements across {len(L)} scenes")
    con.close()


if __name__ == "__main__":
    main()
