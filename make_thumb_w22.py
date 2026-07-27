# -*- coding: utf-8 -*-
"""W22 썸네일 — 여행 경험·미래 계획(하늘 전망대). 노을 전망 배경 + 지은(왼쪽) +
   오른쪽에 과거→미래 2단 카드('가 본 적이 있어요' ↓ '할 계획이에요').
   ★W21(상단 타이틀 + 하단 3알약)과 레이아웃을 일부러 다르게 — 매회 다른 디자인 원칙.
   KO/EN 1280x720 <2MB."""
import os
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"
DONG = "assets/fonts/Cafe24Dongdong.ttf"
BG = "assets/graphics/bg/bg_w22_sunset_city.png"
POSE = "assets/graphics/poses/jieun_w22_present_right.png"

# (한글 표현, 영문 설명, KO 라벨, EN 라벨, 악센트색)
CARDS = [
    ("가 본 적이 있어요", "I've been there", "경험 · 과거", "Experience · Past", (58, 150, 168)),
    ("할 계획이에요", "I'm planning to", "계획 · 미래", "Plans · Future", (232, 122, 74)),
]


def F(p, s): return ImageFont.truetype(p, s)


def outline(d, xy, txt, font, fill, oc=(24, 20, 16, 255), ow=6):
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


def fit(d, txt, path, maxw, start, floor=22):
    """maxw 안에 들어올 때까지 폰트 크기를 줄인다."""
    s = start
    while s > floor and d.textlength(txt, font=F(path, s)) > maxw:
        s -= 2
    return F(path, s)


def build(lang):
    base = cover(BG, W, H)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d0 = ImageDraw.Draw(ov)
    # 왼쪽 세로 그라데이션(캐릭터·제목 가독성) + 상단 살짝 어둡게
    for x in range(560):
        d0.rectangle([x, 0, x + 1, H], fill=(18, 16, 30, int(150 * (1 - x / 560))))
    d0.rectangle([0, 0, W, 178], fill=(18, 16, 30, 95))   # 부제(2줄째)까지 덮어야 경계가 안 걸린다
    base.alpha_composite(ov)

    # 지은 — 왼쪽 아래, 오른쪽(카드 쪽)을 바라보는 포즈
    pose = Image.open(POSE).convert("RGBA")
    bb = pose.getbbox()
    if bb:
        pose = pose.crop(bb)
    ph = 566
    pw = int(pose.width * ph / pose.height)
    pose = pose.resize((pw, ph))
    base.alpha_composite(pose, (16, H - ph - 2))

    d = ImageDraw.Draw(base)
    if lang == "ko":
        outline(d, (40, 22), "여행 이야기", F(MALGUN, 76), (255, 232, 120))
        outline(d, (44, 112), "가 봤어요 · 갈 거예요", F(DONG, 44), (185, 238, 255), ow=4)
    else:
        outline(d, (40, 26), "Travel Talk", F(MALGUN, 70), (255, 232, 120))
        outline(d, (44, 110), "Been there · Going there", F(DONG, 38), (185, 238, 255), ow=4)

    # 오른쪽 2단 카드 (과거 → 미래)
    x0, cw = 556, 700
    ys = [196, 424]
    for i, (ko, en, lk, le, ac) in enumerate(CARDS):
        y0 = ys[i]
        d.rounded_rectangle([x0, y0, x0 + cw, y0 + 172], radius=26, fill=(255, 252, 246, 242),
                            outline=ac, width=6)
        d.rounded_rectangle([x0, y0, x0 + cw, y0 + 50], radius=26, fill=ac)
        d.rectangle([x0, y0 + 26, x0 + cw, y0 + 50], fill=ac)
        lab = lk if lang == "ko" else le
        lf = F(MALGUN, 28)
        d.text((x0 + (cw - d.textlength(lab, font=lf)) / 2, y0 + 9), lab, font=lf, fill=(255, 255, 255))
        mf = fit(d, ko, DONG, cw - 44, 58)
        d.text((x0 + (cw - d.textlength(ko, font=mf)) / 2, y0 + 62), ko, font=mf, fill=(38, 38, 52))
        sf = F(MALGUN, 24)
        d.text((x0 + (cw - d.textlength(en, font=sf)) / 2, y0 + 134), en, font=sf, fill=(96, 96, 116))

    # 카드 사이 화살표(과거 → 미래)
    ax, ay = x0 + cw // 2, ys[0] + 172 + 12
    d.polygon([(ax - 30, ay), (ax + 30, ay), (ax, ay + 40)], fill=(255, 232, 120),
              outline=(40, 34, 28), width=3)

    tag = "하늘 전망대 · W22" if lang == "ko" else "Sky Observatory · W22"
    tf = F(MALGUN, 28)
    outline(d, (W - d.textlength(tag, font=tf) - 26, H - 46), tag, tf, (255, 255, 255), ow=4)

    out = f"hangeul_birth_vowels/thumb_w22_{lang}_1280x720.jpg"
    base.convert("RGB").save(out, quality=90)
    print(f"{out}  ({os.path.getsize(out)//1024}KB)")


for lg in ("ko", "en"):
    build(lg)
