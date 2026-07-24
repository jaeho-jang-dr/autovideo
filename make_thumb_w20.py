# -*- coding: utf-8 -*-
"""W20 썸네일 — 돌발 상황 대처(이태원). 밝은 배경 + 인준(도움 포즈, 오른쪽) +
   상단 타이틀 + 하단 3요소 알약: 도와주세요(도움) · 아파요/다쳤어요(응급) · 112·119(신고).
   ★밝고 긍정적으로(무섭지 않게). W16~W19와 다른 '도움 3요소' 레이아웃. KO/EN 1280x720 <2MB.
   사용: python make_thumb_w20.py"""
import os
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"
DONG = "assets/fonts/Cafe24Dongdong.ttf"
BG = "assets/graphics/bg/w20_station.png"
POSE = "assets/graphics/poses/injun_w20_help_gesture.png"

# (ko, en, label_ko, label_en, accent)
ITEMS = [
    ("도와주세요", "Please help me", "도움", "Help",   (66, 168, 98)),
    ("아파요·다쳤어요", "I'm sick / hurt", "응급", "Sick/Hurt", (230, 150, 52)),
    ("112 · 119", "Call for help", "신고", "Call", (206, 74, 74)),
]


def F(p, s): return ImageFont.truetype(p, s)


def outline(d, xy, txt, font, fill, oc=(26, 22, 18, 255), ow=6):
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


def build(lang):
    base = cover(BG, W, H)
    # 밝기 살짝 올리고 하단 그라데이션 어둡게(글자 대비)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d0 = ImageDraw.Draw(ov)
    d0.rectangle([0, 0, W, 150], fill=(20, 24, 40, 90))
    for i in range(230):
        d0.rectangle([0, H - 230 + i, W, H - 230 + i + 1], fill=(15, 18, 30, int(150 * i / 230)))
    base.alpha_composite(ov)
    # 인준(오른쪽, 크게)
    pose = Image.open(POSE).convert("RGBA")
    ph = 620; pw = int(pose.width * ph / pose.height)
    pose = pose.resize((pw, ph))
    base.alpha_composite(pose, (W - pw + 40, H - ph - 6))
    d = ImageDraw.Draw(base)
    # 상단 타이틀
    if lang == "ko":
        outline(d, (44, 34), "돌발 상황", F(MALGUN, 92), (255, 236, 120))
        outline(d, (44, 138), "한국어", F(MALGUN, 92), (255, 255, 255))
        outline(d, (48, 250), "위급할 때 이 한마디!", F(DONG, 48), (180, 235, 255), ow=4)
    else:
        outline(d, (44, 40), "Korean for", F(MALGUN, 74), (255, 255, 255))
        outline(d, (44, 128), "Emergencies", F(MALGUN, 74), (255, 236, 120))
        outline(d, (48, 232), "Say this when it counts!", F(DONG, 44), (180, 235, 255), ow=4)
    # 하단 3요소 알약
    n = len(ITEMS); gap = 18; pw2 = (W - 80 - gap * (n - 1)) // n; y0 = H - 176
    for i, (ko, en, lk, le, ac) in enumerate(ITEMS):
        x0 = 40 + i * (pw2 + gap)
        d.rounded_rectangle([x0, y0, x0 + pw2, y0 + 150], radius=22, fill=(255, 251, 244, 240), outline=ac, width=5)
        d.rounded_rectangle([x0, y0, x0 + pw2, y0 + 44], radius=22, fill=ac)
        d.rectangle([x0, y0 + 22, x0 + pw2, y0 + 44], fill=ac)
        lab = lk if lang == "ko" else le
        lf = F(MALGUN, 28); lw = d.textlength(lab, font=lf)
        d.text((x0 + (pw2 - lw) / 2, y0 + 6), lab, font=lf, fill=(255, 255, 255))
        main = ko  # 핵심 한글은 항상 노출(그림 같은 한글)
        mf = F(DONG, 46 if len(ko) <= 6 else 34)
        mw = d.textlength(main, font=mf)
        d.text((x0 + (pw2 - mw) / 2, y0 + 66), main, font=mf, fill=(40, 40, 55))
        if lang == "en":
            sf = F(MALGUN, 20); sw = d.textlength(en, font=sf)
            d.text((x0 + (pw2 - sw) / 2, y0 + 120), en, font=sf, fill=(90, 90, 110))
    # 우하단 회차/장소
    tag = "이태원 · W20" if lang == "ko" else "Itaewon · W20"
    tf = F(MALGUN, 30); tw = d.textlength(tag, font=tf)
    outline(d, (W - tw - 30, 24), tag, tf, (255, 255, 255), ow=4)
    out = f"hangeul_birth_vowels/thumb_w20_{lang}_1280x720.jpg"
    base.convert("RGB").save(out, quality=90)
    print(f"{out}  ({os.path.getsize(out)//1024}KB)")


for lg in ("ko", "en"):
    build(lg)
