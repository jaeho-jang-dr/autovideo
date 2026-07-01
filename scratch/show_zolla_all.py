# -*- coding: utf-8 -*-
"""졸라맨/졸라녀/페어 3장을 한 장의 비교 시트로 합쳐 보여주기(일회성)."""
import os
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS = [("졸라맨", "zollaman_base.png"),
         ("졸라녀(수정)", "zollanyeo_base.png"),
         ("페어(표준)", "zolla_pair_base.png")]


def trim(path, thr=20):
    im = Image.open(path).convert("RGB")
    bg = Image.new("RGB", im.size, (255, 255, 255))
    diff = ImageChops.difference(im, bg).convert("L").point(lambda x: 255 if x > thr else 0)
    bbox = diff.getbbox()
    return im.crop(bbox) if bbox else im


imgs = [trim(os.path.join(ROOT, "home_vocab", f)) for _, f in ITEMS]
H = max(i.height for i in imgs)


# 리사이즈 금지(무변형) — 원본 픽셀 크기 그대로, 바닥정렬로 배치
gap, pad, label_h = 90, 50, 80
W = pad * 2 + sum(i.width for i in imgs) + gap * 2
Hc = pad * 2 + label_h + H
canvas = Image.new("RGB", (W, Hc), (255, 255, 255))
draw = ImageDraw.Draw(canvas)
try:
    font = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 44)
except Exception:
    font = ImageFont.load_default()

x = pad
for (label, _), im in zip(ITEMS, imgs):
    canvas.paste(im, (x, pad + label_h + (H - im.height)))
    tb = draw.textbbox((0, 0), label, font=font)
    tw = tb[2] - tb[0]
    draw.text((x + (im.width - tw) // 2, pad + 12), label, fill=(25, 25, 25), font=font)
    x += im.width + gap

out = os.path.join(ROOT, "home_vocab", "_zolla_all_three.png")
canvas.save(out)
print(f"[OK] 3장 비교 시트 저장: {canvas.size} -> {os.path.relpath(out, ROOT)}")
