#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""setup_w2_han.py — KO-W02(2-1) 26씬에 한강 배경(bg_w2_01..13, 2씬당 1장) + 장소명을 입힌다.

한강은 넓고 트인 풍경이라 '여백 넉넉' 요구에 부합. compile_stickman이 scene_bg로 BG_DIR/{key}.png를 로드.
재실행: python setup_w2_han.py
"""
import os
import json
import math
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")
EP = "KO-W02"


def main():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    rows = con.execute("SELECT seq, image_prompt FROM scenes WHERE episode=? ORDER BY seq", (EP,)).fetchall()
    n = 0
    for r in rows:
        spec = json.loads(r["image_prompt"]) if r["image_prompt"] else {}
        bgkey = f"bg_w2_{math.ceil(r['seq'] / 2):02d}"          # 26씬 → 13장(2씬당 1장)
        bgpath = os.path.join(ROOT, "assets", "graphics", "bg", bgkey + ".png")
        spec["bg"] = bgkey
        spec["place_en"] = "Han River"
        cur.execute("UPDATE scenes SET image_prompt=? WHERE episode=? AND seq=?",
                    (json.dumps(spec, ensure_ascii=False), EP, r["seq"]))
        n += 1
        if not os.path.exists(bgpath):
            print(f"  [WARN] s{r['seq']}: bg file missing {bgkey}.png")
    con.commit()
    con.close()
    print(f"{EP}: {n} scenes → 한강 배경(bg_w2_01..13) + place_en='Han River' 적용")


if __name__ == "__main__":
    main()
