# -*- coding: utf-8 -*-
"""마담제이 W11 포즈 사이즈 정규화: 머리 높이 기준으로 캐릭터 크기 통일 + 균일 캔버스(머리 위치 고정).
   들쑥날쑥한 크기를 없애 렌더 시 일관된 캐릭터 크기. (투명 컷아웃 전제)"""
import glob, os
import numpy as np
from PIL import Image

CW, CH = 1000, 1320       # 균일 캔버스
HEAD_TOP_Y = 70           # 머리 꼭대기 고정 y
TARGET_HEAD = 210         # 머리(정수리~목) 높이 통일 목표 px

def head_height(mask):
    ys, xs = np.where(mask)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    crop = mask[y0:y1+1, x0:x1+1]
    H = crop.shape[0]
    roww = crop.sum(axis=1).astype(float)
    k = max(3, H // 60)
    sm = np.convolve(roww, np.ones(k)/k, mode="same")
    top = max(8, int(H * 0.45))
    seg = sm[:top]
    peak = int(seg.argmax())                 # 얼굴 최대폭
    after = seg[peak:]
    if len(after) < 3: return max(8, int(H*0.22)), (y0,y1,x0,x1)
    neck = peak + int(after.argmin())        # 목(폭 최소)
    hh = max(8, neck)
    return hh, (y0, y1, x0, x1)

def process(f):
    im = Image.open(f).convert("RGBA")
    a = np.array(im)[..., 3] > 16
    if a.sum() < 100: return "빈이미지"
    hh, (y0, y1, x0, x1) = head_height(a)
    crop = im.crop((x0, y0, x1+1, y1+1))
    scale = TARGET_HEAD / hh
    nw, nh = max(1, int(crop.width*scale)), max(1, int(crop.height*scale))
    crop = crop.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    # 머리 꼭대기 = HEAD_TOP_Y, 가로 중앙
    px = (CW - nw) // 2
    py = HEAD_TOP_Y
    if py + nh > CH:                          # 캔버스 넘으면 위로 당김
        py = max(0, CH - nh)
    canvas.alpha_composite(crop, (px, py))
    canvas.save(f)
    return f"head={hh}px scale={scale:.2f} size={nw}x{nh}"

n = 0
for f in sorted(glob.glob("assets/graphics/poses/madam_jay_w11_*.png")):
    r = process(f); n += 1
    print(os.path.basename(f), "→", r, flush=True)
print(f"정규화 완료 {n}개 (머리 {TARGET_HEAD}px, 캔버스 {CW}x{CH})")
