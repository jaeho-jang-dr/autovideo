# -*- coding: utf-8 -*-
"""배경 프레임에 40px 격자 + 좌표 라벨을 얹어 눈으로 지평선을 짚기 위한 도구."""
import sys
from PIL import Image, ImageDraw

def grid(src, dst, step=40):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    d = ImageDraw.Draw(im)
    for x in range(0, w, step):
        d.line([(x, 0), (x, h)], fill=(255, 0, 0) if x % 200 == 0 else (255, 140, 140), width=1)
        if x % 200 == 0:
            d.text((x + 2, 2), str(x), fill=(255, 0, 0))
    for y in range(0, h, step):
        d.line([(0, y), (w, y)], fill=(0, 200, 255) if y % 200 == 0 else (150, 230, 255), width=1)
        d.text((2, y + 2), str(y), fill=(0, 100, 255))
    im.save(dst)

if __name__ == "__main__":
    grid(sys.argv[1], sys.argv[2])
