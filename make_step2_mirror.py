# -*- coding: utf-8 -*-
"""걷기1(step_1.png)에서 걷기2를 '다리·팔 좌우반사'로 생성.
 - 허리 아래(다리) 영역을 몸 중심축(x) 기준으로 좌우 미러 → 앞다리↔뒷다리 교차
 - 어깨~허리 옆 팔 영역도 미러 → 앞팔↔뒷팔 교차 (크로스크로울)
 - 머리·몸통·배낭은 원본 유지 → 계속 오른쪽 향함
사용: python make_step2_mirror.py
"""
import numpy as np
from PIL import Image
import os
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")

im = Image.open("scratch/w19_walk/step_1.png").convert("RGBA")
a = np.array(im)
H, W = a.shape[:2]
al = a[:, :, 3]
ys, xs = np.where(al > 0)
top, bot = ys.min(), ys.max()
fh = bot - top

# 허리 y (자켓 밑단 아래=다리 시작). 인물 높이의 약 0.55 지점
waist = top + int(fh * 0.55)
# 어깨 y (팔 상단)
shoulder = top + int(fh * 0.30)

def center_x_at(y0, y1):
    seg = al[y0:y1]
    yy, xx = np.where(seg > 0)
    return int(round(xx.mean())) if len(xx) else W // 2

def mirror_band(arr, y0, y1, cx):
    """arr의 [y0:y1) 행을 x=cx 기준으로 좌우 반사한 새 배열 반환(그 밴드만)."""
    band = arr[y0:y1].copy()
    out = np.zeros_like(band)
    bh, bw = band.shape[:2]
    for x in range(bw):
        sx = 2 * cx - x
        if 0 <= sx < bw:
            out[:, x] = band[:, sx]
    return out

# 다리: 허리 아래 전체를 hip 중심으로 미러
hip_cx = center_x_at(waist - 4, waist + 4)
step2 = a.copy()
step2[waist:bot + 1] = mirror_band(a, waist, bot + 1, hip_cx)

# 팔 미러는 자켓 얼룩을 만들어서 생략 → 다리만 교차(원본 팔 유지). 깨끗함 우선.

Image.fromarray(step2).save("scratch/w19_walk/step_2.png")
print("걷기2(다리·팔 미러) 저장 → step_2.png")

# 비교 이미지
a1 = Image.open("scratch/w19_walk/step_1.png").convert("RGBA")
a2 = Image.fromarray(step2)
w = max(a1.width, a2.width); h = max(a1.height, a2.height); pad = 24
cv = Image.new("RGB", (w * 2 + pad * 3, h + 60), (250, 250, 250))
from PIL import ImageDraw, ImageFont
d = ImageDraw.Draw(cv)
try: f = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 30)
except: f = None
cv.paste(a1, (pad, 50 + (h - a1.height)), a1)
cv.paste(a2, (pad * 2 + w, 50 + (h - a2.height)), a2)
d.text((pad + 20, 10), "걷기1 (원본)", font=f, fill=(200, 50, 50))
d.text((pad * 2 + w + 20, 10), "걷기2 (다리·팔 미러)", font=f, fill=(50, 90, 200))
cv.save("scratch/w19_walk/step12_compare.png")
print("비교 → step12_compare.png", cv.size)
