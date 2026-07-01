#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_zollagirl_cutouts.py — home_vocab/zollanyeo_*.png(흰배경 잉크 졸라걸) →
투명+트림 컷아웃 assets/graphics/poses/stickman_zw_*.png 생성 + content.db 등록.
W4(받침·대표7음) 캐릭터 = 졸라걸. zollaman 컷아웃(stickman_zm_*)의 여성 짝.
투명화는 transparentize_poses 의 4모서리 flood-fill 방식 재사용(내부 흰 면 보존).
사용: python make_zollagirl_cutouts.py
"""
import os
import sys
import sqlite3
from collections import deque

import numpy as np
from PIL import Image

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
HV = os.path.join(ROOT, "home_vocab")
POSES = os.path.join(ROOT, "assets", "graphics", "poses")
DB = os.path.join(ROOT, "channel", "content.db")

# zw_<key> : zollanyeo_<src> — 중립 설명 제스처(가리키기 제외)
POSE_MAP = {
    "base": "base", "thinking": "thinking", "cheering": "cheering",
    "clapping": "clapping", "waving": "waving", "sitting": "sitting",
    "raising_hand": "raising_hand", "reading": "reading",
    "studying": "studying", "jumping": "jumping",
}


def transparentize_trim(src, tol=30, pad=8):
    img = Image.open(src).convert("RGBA")
    arr = np.array(img)
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
    im = Image.fromarray(arr, "RGBA")
    bbox = im.split()[3].getbbox()
    if bbox:
        x0, y0, x1, y1 = bbox
        im = im.crop((max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)))
    return im


def main():
    os.makedirs(POSES, exist_ok=True)
    con = sqlite3.connect(DB)
    cur = con.cursor()
    n = 0
    for key, src in POSE_MAP.items():
        sp = os.path.join(HV, f"zollanyeo_{src}.png")
        if not os.path.exists(sp):
            print(f"  MISS {sp}")
            continue
        im = transparentize_trim(sp)
        out = os.path.join(POSES, f"stickman_zw_{key}.png")
        im.save(out)
        fp = os.path.relpath(out, ROOT).replace(os.sep, "/")
        cur.execute("DELETE FROM assets WHERE file_path=?", (fp,))
        cur.execute("INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?,?,?,?,?)",
                    (f"졸라걸_{key}", f"stickman_zw_{key}", "character", fp, "make_zollagirl_cutouts (zollanyeo cutout)"))
        alpha_mean = np.array(im.split()[3]).mean()
        print(f"  OK stickman_zw_{key:14} {im.size}  alpha_mean={alpha_mean:.0f} -> {fp}")
        n += 1
    con.commit()
    con.close()
    print(f"{n} zolla-girl cutouts created + registered")


if __name__ == "__main__":
    main()
