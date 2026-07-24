# -*- coding: utf-8 -*-
"""W20 배경을 정확히 1280x720으로 통일(cover 크롭: 종횡비 유지하며 꽉 채우고 중앙 크롭).
   agy는 1376x768 등으로 뱉으므로 렌더 규격(1280x720)에 맞춘다. 인플레이스 덮어쓰기."""
import glob, os
from PIL import Image

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"; os.chdir(ROOT)
TW, TH = 1280, 720
n = 0
for p in sorted(glob.glob("home_vocab/w20/bg/w20_*.png")):
    im = Image.open(p).convert("RGB")
    if im.size == (TW, TH):
        continue
    w, h = im.size
    scale = max(TW / w, TH / h)
    nw, nh = round(w * scale), round(h * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    left = (nw - TW) // 2
    top = (nh - TH) // 2
    im = im.crop((left, top, left + TW, top + TH))
    im.save(p)
    n += 1
    print(f"  resized {os.path.basename(p)} {w}x{h} -> {TW}x{TH}")
print(f"완료: {n}개 1280x720 통일")
