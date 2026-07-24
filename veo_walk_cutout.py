# -*- coding: utf-8 -*-
"""Veo 걷기 영상 → 8프레임 추출 → 흰배경 투명 컷아웃 → 엉덩이/발끝 정합.
결과: assets/graphics/poses/jieun_w19_walk_r_0..7.png (오른쪽걷기) + 검증 시트.
사용: python veo_walk_cutout.py
"""
import os, subprocess
import numpy as np
from PIL import Image
from scipy import ndimage
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
VID = "prompts_for_veo/scene_1.mp4"
OUT = "scratch/w19_walk"
os.makedirs(f"{OUT}/vc", exist_ok=True)

# 1) 8프레임 추출 (한 사이클 근처 구간을 촘촘히)
N = 8
T0, T1 = 0.7, 2.3
frames = []
for i in range(N):
    t = T0 + (T1 - T0) * i / (N - 1)
    p = f"{OUT}/vc/raw_{i}.png"
    subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", VID, "-frames:v", "1", p],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    frames.append(np.array(Image.open(p).convert("RGBA")))


def cutout(a):
    rgb = a[:, :, :3].astype(int); lo = rgb.min(2); hi = rgb.max(2)
    white = (lo > 200) & ((hi - lo) < 30)
    lbl, _ = ndimage.label(white)
    b = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1]); b.discard(0)
    a[np.isin(lbl, list(b)), 3] = 0
    pure = (a[:, :, 0] > 244) & (a[:, :, 1] > 244) & (a[:, :, 2] > 242); a[pure, 3] = 0
    ys, xs = np.where(a[:, :, 3] > 0)
    if len(ys) == 0: return None
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


cuts = [cutout(f) for f in frames]
cuts = [c for c in cuts if c is not None]

# 2) 정합: 공통 캔버스, 발끝 하단, 엉덩이(55%밴드) 중심 x
CW = max(c.shape[1] for c in cuts) + 120
CH = max(c.shape[0] for c in cuts) + 16
reg = []
for i, c in enumerate(cuts):
    ch, cw = c.shape[:2]
    band = c[int(ch * 0.50):int(ch * 0.60)]
    by, bx = np.where(band[:, :, 3] > 0)
    hip = int(bx.mean()) if len(bx) else cw // 2
    cv = np.zeros((CH, CW, 4), np.uint8)
    ox = CW // 2 - hip; oy = CH - ch - 6
    ox = max(0, min(ox, CW - cw)); cv[oy:oy + ch, ox:ox + cw] = c
    Image.fromarray(cv).save(f"assets/graphics/poses/jieun_w19_walk_r_{i}.png")
    reg.append(Image.fromarray(cv))
print(f"오른쪽 걷기 컷아웃 {len(reg)}개 (캔버스 {CW}x{CH})")

# 3) 검증 시트(체크무늬 배경 = 투명 확인)
def checker(w, h, s=20):
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        for x in range(w):
            px[x, y] = (200, 200, 200) if ((x // s + y // s) % 2 == 0) else (170, 170, 170)
    return im
sheet = checker(CW * len(reg), CH)
for i, p in enumerate(reg): sheet.paste(p, (i * CW, 0), p)
sheet.save(f"{OUT}/veo_cut_contact.png")
print("검증 시트 → veo_cut_contact.png")
