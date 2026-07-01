#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_scene_objects_w4.py — KO-W04(받침과 대표 7음) 13씬 에셋 배치 → content.db scene_objects.
캐릭터 = **졸라걸**(stickman_zw_*), 왼쪽 배치. 콘텐츠(받침 낱자/예시 단어)는 오른쪽.
졸라걸은 왼손 가리키기(zw_point_l)로 오른쪽 콘텐츠를 지시. 진동 없는 fade_in/elastic_pop만.
재실행: python hangeul_birth_vowels/build_scene_objects_w4.py
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
EP = "KO-W04"
SEARCH = ["assets/graphics", "assets/graphics/poses", "assets/graphics/letters", "assets/graphics/objects"]


def CH(pose, cx=300, cy=385, sc=0.72):
    """메인 졸라걸(zollanyeo 컷아웃) — motion='gesture'. gesture[0] 과 일치."""
    return ("stickman_" + pose, cx, cy, sc, 5, 0, "gesture")


def row(letters, y, x0, step, scale, z=3, mo="fade_in"):
    return [(f"letter_{v}", x0 + i * step, y, scale, z, 0, mo) for i, v in enumerate(letters)]


# seq -> [(name, cx, cy, scale, z, is_point, motion)]  — 캐릭터 왼쪽, 콘텐츠 오른쪽(cx>=600)
L = {
    1: [CH("zw_waving"),                                         # 인트로
        ("word_받침", 880, 300, 0.62, 3, 0, "fade_in"),
        ("word_대표7음", 880, 475, 0.56, 3, 0, "fade_in")],
    2: [CH("zw_sitting"),                                        # 받침이란 (3층 중 맨 아래)
        ("word_강", 840, 360, 0.85, 3, 0, "fade_in"),
        ("letter_ㅇ", 1080, 365, 0.6, 3, 0, "elastic_pop")],
    3: [CH("zw_point_l"),                                        # 강 = ㄱ+ㅏ+ㅇ
        ("letter_ㄱ", 615, 380, 0.8, 3, 0, "fade_in"),
        ("letter_ㅏ", 760, 380, 0.8, 3, 0, "fade_in"),
        ("letter_ㅇ", 905, 380, 0.8, 3, 0, "fade_in"),
        ("sym_arrow", 1025, 380, 0.32, 4, 0, "fade_in"),
        ("word_강", 1150, 380, 0.6, 3, 0, "elastic_pop")],
    4: [CH("zw_raising_hand")]                                   # 대표 7음 한 줄
       + row("ㄱㄴㄷㄹㅁㅂㅇ", 385, 605, 88, 0.5, 3, "fade_in"),
    5: [CH("zw_point_l"),                                        # ㄱ 받침 — 책
        ("letter_ㄱ", 720, 360, 1.1, 3, 0, "fade_in"),
        ("word_책", 1010, 365, 0.72, 3, 0, "elastic_pop")],
    6: [CH("zw_thinking"),                                       # ㄴ-산, ㄷ-옷
        ("letter_ㄴ", 640, 300, 0.85, 3, 0, "fade_in"),
        ("word_산", 850, 300, 0.6, 3, 0, "elastic_pop"),
        ("letter_ㄷ", 640, 500, 0.85, 3, 0, "fade_in"),
        ("word_옷", 850, 500, 0.6, 3, 0, "elastic_pop")],
    7: [CH("zw_point_l"),                                        # ㄹ-물, ㅁ-곰
        ("letter_ㄹ", 640, 300, 0.85, 3, 0, "fade_in"),
        ("word_물", 850, 300, 0.6, 3, 0, "elastic_pop"),
        ("letter_ㅁ", 640, 500, 0.85, 3, 0, "fade_in"),
        ("word_곰", 850, 500, 0.6, 3, 0, "elastic_pop")],
    8: [CH("zw_base"),                                           # ㅂ-밥, ㅇ-강
        ("letter_ㅂ", 640, 300, 0.85, 3, 0, "fade_in"),
        ("word_밥", 850, 300, 0.6, 3, 0, "elastic_pop"),
        ("letter_ㅇ", 640, 500, 0.85, 3, 0, "fade_in"),
        ("word_강", 850, 500, 0.6, 3, 0, "elastic_pop")],
    9: [CH("zw_point_l"),                                        # ㅋ,ㄲ → ㄱ : 부엌
        ("letter_ㅋ", 620, 300, 0.66, 3, 0, "fade_in"),
        ("letter_ㄲ", 620, 470, 0.66, 3, 0, "fade_in"),
        ("sym_arrow", 760, 385, 0.38, 4, 0, "fade_in"),
        ("letter_ㄱ", 890, 385, 1.0, 3, 0, "fade_in"),
        ("word_부엌", 1090, 385, 0.5, 3, 0, "elastic_pop")],
    10: [CH("zw_thinking")]                                      # ㅅㅈㅊㅌㅎ → ㄷ : 꽃
        + row("ㅅㅈㅊㅌㅎ", 300, 615, 82, 0.44, 3, "fade_in")
        + [("sym_arrow", 740, 480, 0.36, 4, 0, "fade_in"),
           ("letter_ㄷ", 870, 480, 0.9, 3, 0, "fade_in"),
           ("word_꽃", 1055, 480, 0.5, 3, 0, "elastic_pop")],
    11: [CH("zw_point_l"),                                       # ㅍ → ㅂ : 앞
         ("letter_ㅍ", 645, 380, 1.0, 3, 0, "fade_in"),
         ("sym_arrow", 800, 380, 0.38, 4, 0, "fade_in"),
         ("letter_ㅂ", 935, 380, 1.0, 3, 0, "fade_in"),
         ("word_앞", 1120, 380, 0.5, 3, 0, "elastic_pop")],
    12: [CH("zw_studying")]                                      # 대표 7음 정리
        + row("ㄱㄴㄷㄹㅁㅂㅇ", 385, 605, 88, 0.5, 3, "fade_in"),
    13: [CH("zw_jumping"),                                       # 마무리
         ("word_받침", 880, 300, 0.5, 3, 0, "fade_in"),
         ("word_대표7음", 880, 470, 0.46, 3, 0, "fade_in"),
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
                (name, name, typ, fp, "auto build_scene_objects_w4"))
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
