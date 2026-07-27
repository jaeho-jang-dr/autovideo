# -*- coding: utf-8 -*-
"""W21 썸네일 — 인물 묘사(성수동). 밝은 성수동 배경 + 마담제이(제시 포즈, 오른쪽) +
   상단 타이틀 + 하단 3요소 알약: 외모 · 성격 · '-고'로 잇기. 밝고 긍정적. KO/EN 1280x720 <2MB."""
import os
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"
DONG = "assets/fonts/Cafe24Dongdong.ttf"
BG = "assets/graphics/bg/bg_w21_flower_cafe.png"
POSE = "assets/graphics/poses/mj_w21_present_right.png"

ITEMS = [
    ("키가 크고 예뻐요", "Looks", "외모", "Looks", (66, 168, 98)),
    ("친절하고 착해요", "Personality", "성격", "Personality", (230, 150, 52)),
    ("'-고'로 잇기", "Link with -고", "문법", "Grammar", (206, 74, 74)),
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
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d0 = ImageDraw.Draw(ov)
    d0.rectangle([0, 0, W, 150], fill=(20, 24, 40, 80))
    for i in range(230):
        d0.rectangle([0, H - 230 + i, W, H - 230 + i + 1], fill=(15, 18, 30, int(150 * i / 230)))
    base.alpha_composite(ov)
    # 마담제이(오른쪽, 크게)
    pose = Image.open(POSE).convert("RGBA")
    bb = pose.getbbox()
    if bb: pose = pose.crop(bb)
    ph = 640; pw = int(pose.width * ph / pose.height)
    pose = pose.resize((pw, ph))
    base.alpha_composite(pose, (W - pw - 20, H - ph - 4))
    d = ImageDraw.Draw(base)
    if lang == "ko":
        outline(d, (44, 30), "인물 묘사", F(MALGUN, 92), (255, 236, 120))
        outline(d, (44, 134), "한국어", F(MALGUN, 92), (255, 255, 255))
        outline(d, (48, 246), "외모와 성격, 한 문장으로!", F(DONG, 46), (180, 235, 255), ow=4)
    else:
        outline(d, (44, 36), "Describe", F(MALGUN, 80), (255, 255, 255))
        outline(d, (44, 130), "People", F(MALGUN, 80), (255, 236, 120))
        outline(d, (48, 234), "Looks & personality in Korean!", F(DONG, 40), (180, 235, 255), ow=4)
    n = len(ITEMS); gap = 18; pw2 = (W - 80 - gap * (n - 1)) // n; y0 = H - 176
    for i, (ko, en, lk, le, ac) in enumerate(ITEMS):
        x0 = 40 + i * (pw2 + gap)
        d.rounded_rectangle([x0, y0, x0 + pw2, y0 + 150], radius=22, fill=(255, 251, 244, 240), outline=ac, width=5)
        d.rounded_rectangle([x0, y0, x0 + pw2, y0 + 44], radius=22, fill=ac)
        d.rectangle([x0, y0 + 22, x0 + pw2, y0 + 44], fill=ac)
        lab = lk if lang == "ko" else le
        lf = F(MALGUN, 28); lw = d.textlength(lab, font=lf)
        d.text((x0 + (pw2 - lw) / 2, y0 + 6), lab, font=lf, fill=(255, 255, 255))
        main = ko
        mf = F(DONG, 44 if len(ko) <= 6 else 32)
        mw = d.textlength(main, font=mf)
        d.text((x0 + (pw2 - mw) / 2, y0 + 66), main, font=mf, fill=(40, 40, 55))
        if lang == "en":
            sf = F(MALGUN, 20); sw = d.textlength(en, font=sf)
            d.text((x0 + (pw2 - sw) / 2, y0 + 120), en, font=sf, fill=(90, 90, 110))
    tag = "성수동 · W21" if lang == "ko" else "Seongsu-dong · W21"
    tf = F(MALGUN, 30); tw = d.textlength(tag, font=tf)
    outline(d, (W - tw - 30, 24), tag, tf, (255, 255, 255), ow=4)
    out = f"hangeul_birth_vowels/thumb_w21_{lang}_1280x720.jpg"
    base.convert("RGB").save(out, quality=90)
    print(f"{out}  ({os.path.getsize(out)//1024}KB)")


for lg in ("ko", "en"):
    build(lg)
