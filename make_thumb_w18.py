# -*- coding: utf-8 -*-
"""W18 썸네일 — ★앞 회차와 다른 '감정 플래시카드' 레이아웃.
   전주 한옥(은행나무) 배경 위에 상단 타이틀 + 마담제이 4감정 표정 카드 4장
   (기쁘다=노랑 / 슬프다=파랑 / 긴장되다=주황 / 속상하다=로즈), 각 무드 컬러.
   W16(빈도 사다리)·W17(대비 화살표+말풍선)과 완전히 다른 카드형.
   KO/EN. 1280x720 <2MB. 사용: python make_thumb_w18.py"""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"
DONG = "assets/fonts/Cafe24Dongdong.ttf"
BG = "assets/graphics/bg/w18_bg_hyanggyo.png"

CARDS = [  # (pose, ko, en, mood_rgb, accent_rgb)
    ("smile_big",   "기쁘다", "Happy",   (255, 246, 214), (245, 190, 60)),
    ("sad",         "슬프다", "Sad",     (222, 236, 250), (86, 150, 224)),
    ("tense",       "긴장되다", "Nervous", (255, 234, 210), (240, 150, 60)),
    ("heavy_heart", "속상하다", "Upset",   (250, 224, 226), (226, 90, 100)),
]


def F(path, sz): return ImageFont.truetype(path, sz)


def outline(d, xy, txt, font, fill, oc=(30, 25, 22, 255), ow=6):
    x, y = xy
    for dx in range(-ow, ow + 1, 2):
        for dy in range(-ow, ow + 1, 2):
            d.text((x + dx, y + dy), txt, font=font, fill=oc)
    d.text((x, y), txt, font=font, fill=fill)


def cover(path, w, h):
    im = Image.open(path).convert("RGBA")
    r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r), int(im.height * r)))
    return im.crop(((im.width - w) // 2, (im.height - h) // 2,
                    (im.width - w) // 2 + w, (im.height - h) // 2 + h))


def pose_cut(pose):
    im = Image.open(f"assets/graphics/poses/mj_w18_{pose}.png").convert("RGBA")
    a = np.array(im)
    ys, xs = np.where(a[:, :, 3] > 25)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def round_mask(size, rad):
    m = Image.new("L", size, 0); d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=rad, fill=255)
    return m


def build(lang):
    base = cover(BG, W, H)
    # 따뜻한 상단 스크림(타이틀 대비)
    scr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(scr)
    for y in range(H):
        a = int(max(0, 150 * (1 - y / 300))) if y < 300 else 0
        sd.line([(0, y), (W, y)], fill=(35, 25, 20, a))
    base.alpha_composite(scr)
    d = ImageDraw.Draw(base)

    # ── 타이틀 (상단)
    if lang == "ko":
        outline(d, (54, 30), "감정 표현", F(DONG, 96), (255, 240, 180), ow=7)
        outline(d, (58, 140), "세밀한 마음 묘사", F(MALGUN, 46), (255, 255, 255), ow=5)
    else:
        outline(d, (54, 34), "Korean Emotions", F(MALGUN, 82), (255, 240, 180), ow=7)
        outline(d, (58, 138), "Feelings & Subtle Nuances", F(MALGUN, 42), (255, 255, 255), ow=5)
    # 회차 배지
    badge = "W18 · 전주 한옥마을" if lang == "ko" else "W18 · Jeonju Hanok"
    bf = F(MALGUN, 30); bw = d.textlength(badge, font=bf)
    d.rounded_rectangle([54, 205, 54 + bw + 34, 253], radius=24, fill=(226, 90, 100, 235))
    d.text((71, 212), badge, font=bf, fill=(255, 255, 255))

    # ── 감정 카드 4장 (하단)
    n = len(CARDS); gap = 20
    cw = (W - 48 * 2 - gap * (n - 1)) // n
    ch = 380
    cy = H - ch - 26
    for i, (pose, ko, en, mood, accent) in enumerate(CARDS):
        cx = 48 + i * (cw + gap)
        card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
        cd.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=26, fill=mood + (245,))
        cd.rounded_rectangle([0, 0, cw - 1, ch - 1], radius=26, outline=accent + (255,), width=5)
        # 캐릭터(카드 안, 상단)
        im = pose_cut(pose); th = ch - 92
        r = th / im.height; im = im.resize((max(1, int(im.width * r)), th))
        if im.width > cw - 16:
            r2 = (cw - 16) / im.width; im = im.resize((cw - 16, max(1, int(im.height * r2))))
        card.alpha_composite(im, ((cw - im.width) // 2, 10))
        # 단어 바(하단)
        cd.rounded_rectangle([10, ch - 76, cw - 10, ch - 12], radius=18, fill=accent + (255,))
        word = ko if lang == "ko" else en
        wf = F(DONG if lang == "ko" else MALGUN, 46 if lang == "ko" else 40)
        ww = cd.textlength(word, font=wf)
        cd.text(((cw - ww) / 2, ch - 74), word, font=wf, fill=(255, 255, 255))
        card.putalpha(Image.composite(card.split()[3], Image.new("L", card.size, 0), round_mask((cw, ch), 26)))
        base.alpha_composite(card, (cx, cy))

    out = base.convert("RGB")
    p = f"hangeul_birth_vowels/thumb_w18_{lang}_1280x720.jpg"
    q = 92
    out.save(p, quality=q)
    while os.path.getsize(p) > 2 * 1024 * 1024 and q > 60:
        q -= 6; out.save(p, quality=q)
    print(f"  {p}  ({os.path.getsize(p)//1024}KB, q{q})")


print("W18 감정 플래시카드 썸네일:")
for lg in ("ko", "en"):
    build(lg)
