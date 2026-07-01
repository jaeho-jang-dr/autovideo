#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_scene_objects.py — KO-W01 각 씬의 에셋 배치(레이아웃)를 content.db `scene_objects` 에 기록.

placement = (logical_name, cx, cy, scale, z_order, is_point, motion_type)  좌표=1280x720 픽셀.
logical_name 해석: assets.name_en 또는 file_path 매칭, 없으면 디스크에서 찾아 자동 등록.
멱등: KO-W01 의 기존 scene_objects 삭제 후 재삽입. 재실행: python hangeul_birth_vowels/build_scene_objects.py
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
EP = "KO-W01"
SEARCH = ["assets/graphics", "assets/graphics/poses", "assets/graphics/letters"]

# seq -> [(name, cx, cy, scale, z, is_point, motion), ...]
L = {
    # ★ 세종대왕상(우측)에 글자가 안 닿도록 중앙 band(cx≤900)에 배치
    1: [("stickman_greeting_wave", 300, 455, 0.62, 5, 0, "fade_in"),
        ("letter_ㅏ", 560, 175, 0.55, 2, 0, "float"), ("letter_ㅓ", 720, 165, 0.50, 2, 0, "float"),
        ("letter_ㅗ", 640, 320, 0.55, 2, 0, "float"), ("letter_ㅜ", 870, 185, 0.45, 2, 0, "float"),
        ("letter_ㅡ", 500, 305, 0.45, 2, 0, "float"), ("letter_ㅣ", 880, 330, 0.45, 2, 0, "float"),
        ("letter_ㅐ", 780, 445, 0.45, 2, 0, "float"), ("letter_ㅔ", 600, 450, 0.40, 2, 0, "float")],
    2: [("stickman_thinking", 360, 455, 0.62, 5, 0, "fade_in"),
        ("obj_book", 800, 470, 0.95, 3, 0, "elastic_pop"),
        ("obj_qmark", 950, 230, 0.5, 4, 1, "elastic_pop")],
    3: [("stickman_sejong", 640, 492, 0.66, 5, 0, "fade_in"),
        ("obj_crown", 640, 156, 0.60, 6, 0, "elastic_pop"),
        ("obj_badge_28", 970, 260, 0.6, 4, 1, "elastic_pop")],
    4: [("stickman_presenting", 320, 455, 0.60, 5, 0, "fade_in"),
        ("obj_haerye_scroll", 820, 380, 0.95, 3, 1, "unfurl"),
        ("obj_sparkle", 880, 210, 0.5, 4, 0, "fade_in")],
    5: [("stickman_pointing_up", 300, 455, 0.60, 5, 0, "fade_in"),
        ("sym_heaven_dot", 700, 235, 0.5, 3, 1, "elastic_pop"),
        ("sym_earth_line", 905, 300, 0.5, 3, 0, "elastic_pop"),
        ("sym_human_line", 1085, 290, 0.5, 3, 0, "elastic_pop")],
    6: [("stickman_pointing_right", 300, 460, 0.60, 5, 0, "fade_in"),
        ("letter_ㅣ", 720, 360, 0.90, 3, 0, "fade_in"),
        ("obj_sun", 965, 215, 0.45, 4, 1, "arc"),
        ("letter_ㅏ", 905, 380, 0.85, 3, 0, "write"), ("letter_ㅓ", 1095, 380, 0.85, 3, 0, "write")],
    7: [("stickman_pointing_down", 300, 455, 0.60, 5, 0, "fade_in"),
        ("letter_ㅡ", 720, 360, 0.90, 3, 0, "fade_in"),
        ("sym_heaven_dot", 720, 278, 0.32, 4, 1, "elastic_pop"),
        ("letter_ㅗ", 935, 360, 0.85, 3, 0, "write"), ("letter_ㅜ", 1105, 360, 0.85, 3, 0, "write")],
    8: [("stickman_arms_open", 320, 460, 0.60, 5, 0, "fade_in"),
        ("letter_ㅏ", 790, 255, 0.62, 3, 0, "elastic_pop"), ("letter_ㅗ", 935, 255, 0.62, 3, 0, "elastic_pop"),
        ("letter_ㅓ", 790, 450, 0.62, 3, 0, "elastic_pop"), ("letter_ㅜ", 935, 450, 0.62, 3, 0, "elastic_pop")],
    9: [("stickman_mouth_demo", 215, 460, 0.58, 5, 0, "fade_in")]
       + [(f"letter_{v}", 440 + i * 78, 330, 0.48, 3, 0, "elastic_pop")
          for i, v in enumerate("ㅏㅓㅗㅜㅡㅣㅐㅔ")],   # ★ 세종대왕상 회피(cx≤986, cy 아래쪽)
    10: [("stickman_presenting", 300, 460, 0.60, 5, 0, "fade_in"),
         ("mouth_open_vertical", 780, 300, 0.85, 4, 1, "elastic_pop"),
         ("letter_ㅏ", 1010, 250, 0.70, 3, 0, "write"), ("letter_ㅓ", 1010, 405, 0.70, 3, 0, "write")],
    11: [("stickman_mouth_demo", 300, 460, 0.58, 5, 0, "fade_in"),
         ("mouth_rounded", 780, 300, 0.95, 4, 1, "elastic_pop"),
         ("letter_ㅗ", 1010, 250, 0.70, 3, 0, "write"), ("letter_ㅜ", 1010, 405, 0.70, 3, 0, "write")],
    12: [("stickman_presenting", 300, 460, 0.60, 5, 0, "fade_in"),
         ("mouth_flat_wide", 790, 310, 0.95, 4, 1, "elastic_pop"),
         ("letter_ㅡ", 1015, 250, 0.70, 3, 0, "write"), ("letter_ㅣ", 1015, 405, 0.70, 3, 0, "write")],
    13: [("stickman_mouth_demo", 300, 460, 0.58, 5, 0, "fade_in"),
         ("mouth_mid_open", 780, 300, 0.90, 4, 1, "elastic_pop"),
         ("letter_ㅐ", 1010, 250, 0.65, 3, 0, "write"), ("letter_ㅔ", 1010, 405, 0.65, 3, 0, "write")],
    14: [("stickman_holding_mirror", 380, 455, 0.62, 5, 0, "fade_in"),
         ("obj_mirror", 470, 270, 0.55, 6, 1, "elastic_pop"),
         ("letter_ㅗ", 850, 285, 0.5, 3, 0, "elastic_pop"), ("letter_ㅜ", 980, 285, 0.5, 3, 0, "elastic_pop"),
         ("letter_ㅓ", 850, 455, 0.5, 3, 0, "elastic_pop"), ("letter_ㅡ", 980, 455, 0.5, 3, 0, "elastic_pop")],
    15: [("stickman_cheer", 600, 455, 0.62, 5, 0, "fade_in"),
         ("obj_bell", 930, 470, 0.50, 4, 1, "swing"),       # ★ 세종대왕 얼굴 아래로 내림(가림 방지)
         ("obj_sparkle", 330, 260, 0.50, 4, 0, "fade_in")],
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
    typ = "character" if name.startswith("stickman_") else ("letter" if name.startswith(("letter_", "word_")) else "object")
    cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?,?,?,?,?)",
                (name, name, typ, fp, "auto-registered by build_scene_objects"))
    print(f"  + auto-registered asset {name} ({fp})")
    return cur.lastrowid


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("DELETE FROM scene_objects WHERE episode=?", (EP,))
    total = 0
    POSE_SCALE = 1.10   # 스틱맨 ~10% 확대 (사용자 요청)
    for seq, items in sorted(L.items()):
        for (name, cx, cy, scale, z, isp, mo) in items:
            aid = resolve(cur, name)
            if name.startswith("stickman_"):
                scale = round(scale * POSE_SCALE, 3)
                cy = cy - 18            # 커진 만큼 살짝 올려 발이 자막 위에 머물게
            cur.execute(
                "INSERT INTO scene_objects (episode, scene_seq, asset_id, cx, cy, scale, z_order, is_point, motion_type) "
                "VALUES (?,?,?,?,?,?,?,?,?)", (EP, seq, aid, cx, cy, scale, z, isp, mo))
            total += 1
    con.commit()
    n = cur.execute("SELECT count(*) FROM scene_objects WHERE episode=?", (EP,)).fetchone()[0]
    print(f"\nscene_objects for {EP}: {n} placements across {len(L)} scenes")
    con.close()


if __name__ == "__main__":
    main()
