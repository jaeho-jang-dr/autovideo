#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
build_scene_objects_w3.py — KO-W03(거센소리와 된소리) 16씬 에셋 배치 → content.db scene_objects.
캐릭터 = DB의 **실제 졸라맨**(home_vocab/zollaman_* → 투명 컷아웃 stickman_zm_*.png).
v2 구조(인트로/복습/거센·된소리/발음연습/휴지실험/비교/정리) + gesture 손짓 전환.
글자(ㄱㄷㅂㅈㅅ/ㅋㅌㅍㅊ/ㄲㄸㅃㅆㅉ) + 단어 + 가획/쌍자음 다이어그램 + 휴지/공기 소품. 1280x720.
재실행: python hangeul_birth_vowels/build_scene_objects_w3.py
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
EP = "KO-W03"
SEARCH = ["assets/graphics", "assets/graphics/poses", "assets/graphics/letters", "assets/graphics/objects"]


def CH(pose, cx=300, cy=395, sc=0.64):
    """메인 졸라맨(zollaman 컷아웃) — motion='gesture'. gesture[0] 과 일치시킴."""
    return ("stickman_" + pose, cx, cy, sc, 5, 0, "gesture")


def row(letters, y, x0, step, scale, z=3, mo="elastic_pop"):
    return [(f"letter_{v}", x0 + i * step, y, scale, z, 0, mo) for i, v in enumerate(letters)]


def evo(a, b, y, x0=640, sc=0.7):
    return [(f"letter_{a}", x0, y, sc, 3, 0, "write"),
            ("sym_arrow", x0 + 150, y, 0.34, 4, 0, "elastic_pop"),
            (f"letter_{b}", x0 + 290, y, sc, 3, 0, "write")]


# seq -> [(name, cx, cy, scale, z, is_point, motion)]
# 사용자 요청 반영: 가리키기 포즈 제거(중립 CH), 중간 흔들리는 객체(airpuff) 전부 제거,
# 글자/단어는 진동 없는 fade_in, 타조/포도/치마는 작게+띄어쓰기, 중복 씬 통합으로 15씬.
L = {
    1: [CH("zm_waving"),                                         # 인트로
        ("word_거센소리", 875, 300, 0.62, 3, 0, "fade_in"),
        ("word_된소리", 875, 475, 0.62, 3, 0, "fade_in")],
    2: [CH("zm_sitting"),                                        # 복습(앉아 회상)
        ("word_예사소리", 880, 250, 0.50, 3, 0, "fade_in")]
       + row("ㄱㄷㅂㅈㅅ", 445, 660, 112, 0.5, 3, "fade_in"),
    3: [CH("zm_cheering"),                                       # 거센소리란
        ("word_거센소리", 875, 380, 0.72, 3, 0, "fade_in")],
    4: [CH("zm_base"),                                           # 가획 ㄱ→ㅋ
        ("letter_ㄱ", 660, 385, 1.15, 3, 0, "write"),
        ("sym_arrow", 840, 385, 0.5, 4, 0, "fade_in"),
        ("letter_ㅋ", 1010, 385, 1.15, 3, 0, "write")],
    5: [CH("zm_base")]                                           # 가획 ㄷ→ㅌ, ㅂ→ㅍ, ㅈ→ㅊ
       + evo("ㄷ", "ㅌ", 290) + evo("ㅂ", "ㅍ", 430) + evo("ㅈ", "ㅊ", 565),
    6: [CH("zm_base"),                                           # 거센 발음연습 ㅋ(코)
        ("letter_ㅋ", 720, 360, 1.2, 3, 0, "write"),
        ("word_코", 1010, 365, 0.8, 3, 0, "fade_in")],
    7: [CH("zm_base")]                                           # 발음연습 ㅌㅍㅊ
       + row("ㅌㅍㅊ", 300, 700, 150, 0.62, 3, "fade_in")
       + [("word_타조", 650, 515, 0.42, 3, 0, "fade_in"),       # 작게 + 띄어쓰기(간격 230)
          ("word_포도", 880, 515, 0.42, 3, 0, "fade_in"),
          ("word_치마", 1110, 515, 0.42, 3, 0, "fade_in")],
    8: [CH("zm_cheering"),                                       # 된소리란
        ("word_된소리", 880, 380, 0.64, 3, 0, "fade_in")],
    9: [CH("zm_base"),                                           # 쌍자음 ㄱ+ㄱ→ㄲ
        ("letter_ㄱ", 620, 380, 0.85, 3, 0, "write"),
        ("sym_plus", 730, 380, 0.34, 4, 0, "fade_in"),
        ("letter_ㄱ", 830, 380, 0.85, 3, 0, "write"),
        ("sym_arrow", 935, 380, 0.38, 4, 0, "fade_in"),
        ("letter_ㄲ", 1070, 380, 0.95, 3, 0, "write")],
    10: [CH("zm_base")]                                          # 쌍자음 ㄷ→ㄸ, ㅂ→ㅃ, ㅅ→ㅆ, ㅈ→ㅉ
        + row("ㄷㅂㅅㅈ", 300, 650, 168, 0.46, 3, "fade_in")
        + row("ㄸㅃㅆㅉ", 480, 650, 168, 0.62, 3, "write"),
    11: [CH("zm_base"),                                          # 된소리 발음연습 ㄲ(까치)
         ("letter_ㄲ", 720, 360, 1.15, 3, 0, "write"),
         ("word_까치", 1015, 365, 0.72, 3, 0, "fade_in")],
    12: [CH("zm_base")]                                          # 발음연습 ㄸㅃㅆㅉ
        + row("ㄸㅃㅆㅉ", 300, 670, 145, 0.5, 3, "fade_in")
        + [("word_꼬리", 640, 515, 0.5, 3, 0, "fade_in"),
           ("word_땅", 850, 515, 0.58, 3, 0, "fade_in"),
           ("word_빵", 1010, 515, 0.58, 3, 0, "fade_in"),
           ("word_짜", 1165, 515, 0.58, 3, 0, "fade_in")],
    13: [CH("zm_thinking"),                                      # 휴지 실험! ㅋ vs ㄲ (정지 휴지)
         ("obj_tissue", 470, 392, 0.5, 6, 0, "fade_in"),
         ("letter_ㅋ", 760, 350, 0.95, 3, 0, "write"),
         ("letter_ㄲ", 1085, 350, 0.95, 3, 0, "write")],
    14: [CH("zm_thinking"),                                      # 비교+연습 ㄱ-ㅋ-ㄲ / 개-캐-깨(통합)
         ("letter_ㄱ", 660, 305, 0.78, 3, 0, "write"),
         ("letter_ㅋ", 860, 305, 0.78, 3, 0, "write"),
         ("letter_ㄲ", 1060, 305, 0.78, 3, 0, "write"),
         ("word_개", 660, 510, 0.62, 3, 0, "fade_in"),
         ("word_캐", 860, 510, 0.62, 3, 0, "fade_in"),
         ("word_깨", 1060, 510, 0.62, 3, 0, "fade_in")],
    15: [CH("zm_cheering"),                                      # 마무리(축하)
         ("word_거센소리", 880, 285, 0.50, 3, 0, "fade_in"),
         ("word_된소리", 880, 460, 0.50, 3, 0, "fade_in"),
         ("obj_sparkle", 1090, 235, 0.55, 4, 0, "fade_in")],
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
                (name, name, typ, fp, "auto build_scene_objects_w3"))
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
