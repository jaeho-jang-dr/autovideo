#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""build_character_cutouts.py — 지은·인준·닥터제이·마담제이 투명 컷아웃 라이브러리 + content.db 등록.
- 이미 투명한 포즈는 그대로 복사, 불투명(베이스 등)은 4모서리 flood-fill 로 배경만 투명화(내부 흰색 보존).
- 출력: assets/characters/cutouts/<char>_<pose>.png, type='character', name_en='cut_<char>_<pose>'
재실행: python build_character_cutouts.py
"""
import os
import sys
import glob
import sqlite3
from collections import deque

import numpy as np
from PIL import Image

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "assets", "characters", "cutouts")
DB = os.path.join(ROOT, "channel", "content.db")
os.makedirs(OUT, exist_ok=True)


def is_transparent(im):
    a = np.array(im.convert("RGBA"))[:, :, 3]
    return a.min() == 0 and a.mean() < 250


def transparentize(im, tol=42):
    arr = np.array(im.convert("RGBA"))
    h, w = arr.shape[:2]
    rgb = arr[:, :, :3].astype(int)
    corners = np.array([rgb[0, 0], rgb[0, w - 1], rgb[h - 1, 0], rgb[h - 1, w - 1]])
    bg = np.median(corners, axis=0)
    seen = np.zeros((h, w), bool)
    a = arr[:, :, 3].copy()
    dq = deque([(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)])
    while dq:
        y, x = dq.popleft()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y, x]:
            continue
        seen[y, x] = True
        if np.abs(rgb[y, x] - bg).max() > tol:
            continue
        a[y, x] = 0
        dq.append((y + 1, x)); dq.append((y - 1, x)); dq.append((y, x + 1)); dq.append((y, x - 1))
    arr[:, :, 3] = a
    return Image.fromarray(arr, "RGBA")


# char -> [(pose_key, source_path), ...]  (teaching/사용용 핵심 포즈 + 베이스)
def collect():
    HV = os.path.join(ROOT, "home_vocab")
    CH = os.path.join(ROOT, "assets", "characters")
    sets = {}
    # 지은(학생, 교복) — 이미 투명 포즈 다수
    jieun = [("base", f"{HV}/jieun_base_front.png")]
    for pose in ["pointing", "cheering", "clapping", "raising_hand", "reading",
                 "thinking", "waving", "bowing", "sitting", "studying", "drawing", "jumping"]:
        for cand in (f"{HV}/jieun_{pose}.png", f"{HV}/character_{pose}.png"):
            if os.path.exists(cand):
                jieun.append((pose, cand)); break
    sets["jieun"] = jieun
    # 인준(학생) — base + 교육/활동 포즈
    injun = []
    for key, cand in [("base", f"{HV}/injun_base_front.png"), ("base", f"{HV}/injun_navy_front.png")]:
        if os.path.exists(cand):
            injun.append((key, cand)); break
    for pose, fname in [("cheering", "injun_cheering_outdoor"), ("reading", "injun_reading_bench"),
                        ("waving", "injun_waving_park"), ("hiking", "injun_hiking"),
                        ("baseball", "injun_baseball"), ("bicycle", "injun_bicycle"),
                        ("camping", "injun_camping"), ("fishing", "injun_fishing")]:
        cand = f"{HV}/{fname}.png"
        if os.path.exists(cand):
            injun.append((pose, cand))
    sets["injun"] = injun
    # 닥터제이(의사) — 베이스(포즈는 Flow 생성분이 들어오면 추가됨)
    drj = []
    for key, cand in [("base_front", f"{CH}/dr_jay_base_front.png"), ("base_side", f"{CH}/dr_jay_base_side.png")]:
        if os.path.exists(cand):
            drj.append((key, cand))
    for pose in ["pointing", "presenting", "thinking", "cheering", "holding_book", "waving"]:
        cand = f"{CH}/dr_jay_{pose}.png"
        if os.path.exists(cand):
            drj.append((pose, cand))
    sets["dr_jay"] = drj
    # 마담제이(선생님)
    mdj = []
    for key, cand in [("base_front", f"{CH}/madam_jay_base_front.png"), ("base_side", f"{CH}/madam_jay_base_side.png")]:
        if os.path.exists(cand):
            mdj.append((key, cand))
    for pose in ["pointing", "presenting", "thinking", "cheering", "holding_book", "waving"]:
        cand = f"{CH}/madam_jay_{pose}.png"
        if os.path.exists(cand):
            mdj.append((pose, cand))
    sets["madam_jay"] = mdj
    return sets


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    sets = collect()
    total = 0
    for char, items in sets.items():
        for pose, src in items:
            im = Image.open(src).convert("RGBA")
            if not is_transparent(im):
                im = transparentize(im)
            outname = f"{char}_{pose}.png"
            outp = os.path.join(OUT, outname)
            im.save(outp)
            fp = os.path.relpath(outp, ROOT).replace(os.sep, "/")
            name_en = f"cut_{char}_{pose}"
            cur.execute("DELETE FROM assets WHERE file_path=?", (fp,))
            cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?,?,?,?,?)",
                        (f"{char}_{pose}", name_en, "character", fp, "build_character_cutouts (transparent)"))
            total += 1
        print(f"  {char}: {len(items)} cutouts")
    con.commit()
    con.close()
    print(f"TOTAL {total} transparent cutouts registered -> {os.path.relpath(OUT, ROOT)}")


if __name__ == "__main__":
    main()
