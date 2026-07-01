#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""segment_organs.py — vocal_organ_v2.png 의 5개 조음 구조물을 색 기준으로 정확히 분리.
출력: web/public/docs/vorg_<part>.png (full-canvas 투명 레이어). 부위별 독립 애니메이션용.
재실행: python segment_organs.py
"""
import os
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "web", "public", "docs", "vocal_organ_v2.png")
OUT = os.path.join(ROOT, "web", "public", "docs")

im = Image.open(SRC).convert("RGB")
W, H = im.size
arr = np.array(im).astype(int)
R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]


def color_mask(target, tol):
    d = np.sqrt((R - target[0]) ** 2 + (G - target[1]) ** 2 + (B - target[2]) ** 2)
    return d < tol


def save_layer(mask, name, feather=2.0):
    rgba = np.dstack([np.array(im), (mask * 255).astype("uint8")])
    layer = Image.fromarray(rgba, "RGBA")
    if feather:
        a = layer.split()[3].filter(ImageFilter.GaussianBlur(feather))
        layer.putalpha(a)
    layer.save(os.path.join(OUT, f"vorg_{name}.png"))
    print(f"  {name:10} px={int(mask.sum()):>7}")


yy, xx = np.mgrid[0:H, 0:W]

# 입술(코랄 레드) → 윗/아랫입술 분리 (가운데 치아 높이 ~405 기준)
lips = color_mask((254, 104, 80), 80)
save_layer(lips & (yy < 405), "lip_upper")
save_layer(lips & (yy >= 405), "lip_lower")

# 치아(순백 253,253,253): 최소채널 임계 + 입안 영역 박스
mn = np.minimum(np.minimum(R, G), B)
teeth = (mn > 235) & (xx > 485) & (xx < 610) & (yy > 350) & (yy < 478)
save_layer(teeth, "teeth", feather=1.0)

# 혀(분홍)
save_layer(color_mask((247, 147, 171), 60), "tongue")

# 입천장(연보라)
save_layer(color_mask((209, 193, 238), 55), "palate")

# 목구멍(진적색)
save_layer(color_mask((134, 29, 43), 70), "throat")

print("DONE — 6 organ layers (vorg_*.png)")
