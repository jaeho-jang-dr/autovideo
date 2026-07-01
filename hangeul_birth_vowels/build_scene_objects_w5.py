#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_scene_objects_w5.py — KO-W05(이중모음과 반모음 활주) 13씬 배치 → content.db scene_objects.
캐릭터 졸라걸(stickman_zw_*) 왼쪽, 콘텐츠 오른쪽. 단모음(STROKES) = motion 'write'(획순),
이중모음 결과 = 'fade_in'(letter PNG, STROKES 미지원). 진동 없음.
재실행: python hangeul_birth_vowels/build_scene_objects_w5.py
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
EP = "KO-W05"
SEARCH = ["assets/graphics", "assets/graphics/poses", "assets/graphics/letters", "assets/graphics/objects"]

STROKE_V = set("ㅏㅓㅗㅜㅣㅐㅔㅡ")   # 획순 쓰기 지원 단모음


def CH(pose, cx=300, cy=385, sc=0.72):
    return ("stickman_" + pose, cx, cy, sc, 5, 0, "gesture")


def lv(v, x, y, sc):
    """모음 1개: 단모음이면 write(획순), 이중모음이면 fade_in."""
    return (f"letter_{v}", x, y, sc, 3, 0, "write" if v in STROKE_V else "fade_in")


def combine(a, b, res, y, x0=605, sc=0.7):
    """a + b → res 합성 한 줄."""
    return [lv(a, x0, y, sc),
            ("sym_plus", x0 + 130, y, 0.3, 4, 0, "fade_in"),
            lv(b, x0 + 255, y, sc),
            ("sym_arrow", x0 + 380, y, 0.32, 4, 0, "fade_in"),
            lv(res, x0 + 510, y, sc)]


def evo(a, res, y, x0=650, sc=0.62):
    """a → res 한 줄(ㅣ활음)."""
    return [lv(a, x0, y, sc),
            ("sym_arrow", x0 + 150, y, 0.3, 4, 0, "fade_in"),
            lv(res, x0 + 290, y, sc)]


def words(ws, y, x0, step, sc=0.36):
    return [(f"word_{w}", x0 + i * step, y, sc, 3, 0, "fade_in") for i, w in enumerate(ws)]


L = {
    1: [CH("zw_waving"),
        ("word_이중모음", 880, 300, 0.56, 3, 0, "fade_in"),
        ("word_반모음", 880, 470, 0.56, 3, 0, "fade_in")],
    2: [CH("zw_sitting"),
        ("letter_ㅑ", 720, 380, 0.95, 3, 0, "fade_in"),
        ("letter_ㅛ", 900, 380, 0.95, 3, 0, "fade_in"),
        ("letter_ㅠ", 1080, 380, 0.95, 3, 0, "fade_in")],
    3: [CH("zw_thinking"),
        ("letter_ㅣ", 700, 370, 0.85, 3, 0, "write"),
        ("word_반모음", 940, 380, 0.5, 3, 0, "fade_in")],
    4: [CH("zw_point_l")] + combine("ㅣ", "ㅏ", "ㅑ", 385),
    5: [CH("zw_thinking")] + evo("ㅓ", "ㅕ", 280) + evo("ㅗ", "ㅛ", 410) + evo("ㅜ", "ㅠ", 540),
    6: [CH("zw_point_l")] + words(["야구", "여우", "요리", "우유"], 400, 620, 188, 0.36),
    7: [CH("zw_base")] + evo("ㅐ", "ㅒ", 300, x0=620, sc=0.56) + evo("ㅔ", "ㅖ", 470, x0=620, sc=0.56)
       + [("word_얘기", 1140, 300, 0.36, 3, 0, "fade_in"),
          ("word_예의", 1140, 470, 0.36, 3, 0, "fade_in")],
    8: [CH("zw_point_l")] + combine("ㅗ", "ㅏ", "ㅘ", 385),
    9: [CH("zw_thinking")] + combine("ㅜ", "ㅓ", "ㅝ", 270, x0=620, sc=0.55)
       + combine("ㅗ", "ㅣ", "ㅚ", 400, x0=620, sc=0.55)
       + combine("ㅜ", "ㅣ", "ㅟ", 530, x0=620, sc=0.55),
    10: [CH("zw_point_l")] + words(["사과", "샤워", "외투", "가위"], 400, 620, 188, 0.36),
    11: [CH("zw_point_l")] + combine("ㅡ", "ㅣ", "ㅢ", 360)
        + [("word_의자", 905, 520, 0.5, 3, 0, "fade_in")],
    12: [CH("zw_studying")]
        + [(f"letter_{v}", 600 + (i % 5) * 130, 300 + (i // 5) * 150, 0.5, 3, 0, "fade_in")
           for i, v in enumerate("ㅑㅕㅛㅠㅘㅝㅟㅚㅢ")],
    13: [CH("zw_jumping"),
         ("word_이중모음", 880, 300, 0.5, 3, 0, "fade_in"),
         ("word_반모음", 880, 470, 0.46, 3, 0, "fade_in"),
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
                (name, name, typ, fp, "auto build_scene_objects_w5"))
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
