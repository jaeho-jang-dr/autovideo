#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
generate_w3_props.py — 3주차 소품: 휴지(tissue) + 공기 puff(airpuff) 잉크 스타일 PNG + DB 등록.
휴지 실험(거센소리에 휴지가 '확' 흔들림) 연출용. assets/graphics/objects/. type='object'.
재실행: python generate_w3_props.py
"""
import os
import sys
import math
import sqlite3

from PIL import Image, ImageDraw, ImageFilter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
ODIR = os.path.join(ROOT, "assets", "graphics", "objects")
DB = os.path.join(ROOT, "channel", "content.db")
INK = (32, 32, 32, 255)
SS = 2


def _new(w, h):
    img = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def draw_tissue():
    """휴지 한 장 — 흰 사각 시트 + 잉크 윤곽 + 펄럭이는 아래 가장자리."""
    img, d = _new(360, 420)
    s = SS
    x0, y0, x1, y1 = 70 * s, 50 * s, 290 * s, 330 * s
    # 시트(흰색) — 아래 가장자리는 물결
    top = [(x0, y0), (x1, y0)]
    wave = []
    n = 14
    for i in range(n + 1):
        t = i / n
        x = x1 + (x0 - x1) * t
        y = y1 + math.sin(t * math.pi * 3) * 14 * s
        wave.append((x, y))
    poly = top + wave
    d.polygon(poly, fill=(252, 252, 250, 255))
    d.line(poly + [poly[0]], fill=INK, width=int(2.2 * s), joint="curve")
    # 접힘 선 2개
    for fx in (0.36, 0.64):
        xx = x0 + (x1 - x0) * fx
        d.line([(xx, y0 + 8 * s), (xx, y1 - 10 * s)], fill=(120, 120, 120, 150), width=int(1.3 * s))
    return img.resize((360, 420), Image.LANCZOS)


def draw_airpuff():
    """공기 '확' — 입에서 세게 나오는 바람. 오른쪽으로 벌어지는 곡선 호 + 작은 퍼프."""
    img, d = _new(420, 320)
    s = SS
    cx, cy = 70 * s, 160 * s
    # 벌어지는 호 3개 (바람결)
    for k, (rad, spread) in enumerate([(120, 0.55), (175, 0.7), (235, 0.85)]):
        pts = []
        for i in range(25):
            a = (-spread + 2 * spread * i / 24) * math.pi / 2 * 0.6
            x = cx + math.cos(a) * rad * s
            y = cy + math.sin(a) * rad * s
            pts.append((x, y))
        d.line(pts, fill=(60, 60, 60, 235 - k * 30), width=int((3.2 - k * 0.5) * s), joint="curve")
    # 끝의 작은 퍼프 원
    for (px, py, r) in [(330, 95, 16), (360, 160, 20), (330, 225, 16)]:
        d.ellipse([px * s - r * s, py * s - r * s, px * s + r * s, py * s + r * s],
                  outline=(60, 60, 60, 230), width=int(2.4 * s))
    return img.resize((420, 320), Image.LANCZOS)


def main():
    os.makedirs(ODIR, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    has = "created_at" in {r[1] for r in cur.execute("pragma table_info(assets)")}
    items = [("휴지", "tissue", draw_tissue), ("공기 분출", "airpuff", draw_airpuff)]
    for name_kr, key, fn in items:
        fn_img = fn()
        out = os.path.join(ODIR, f"obj_{key}.png")
        fn_img.save(out)
        fp = f"graphics/objects/obj_{key}.png"
        cur.execute("DELETE FROM assets WHERE file_path=?", (fp,))
        if has:
            cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt, created_at) "
                        "VALUES (?,?,?,?,?, datetime('now'))", (name_kr, f"obj_{key}", "object", fp, "generate_w3_props.py"))
        else:
            cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?,?,?,?,?)",
                        (name_kr, f"obj_{key}", "object", fp, "generate_w3_props.py"))
        print(f"  obj_{key} -> {out} {fn_img.size}")
    con.commit()
    con.close()
    print("2 W3 props generated + registered")


if __name__ == "__main__":
    main()
