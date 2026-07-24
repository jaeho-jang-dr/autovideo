# -*- coding: utf-8 -*-
"""W19 썸네일 — ★앞 회차와 다른 '논리 체인(logic chain)' 레이아웃.
   설악산(울산바위) 배경 위에 상단 타이틀 + 지은(설득 포즈, 오른쪽) +
   하단에 3단 논리 흐름 알약: 제 생각에는(주장) → 왜냐하면(근거) → 따라서(결론).
   W16(빈도 사다리)·W17(대비 화살표)·W18(감정 카드)와 완전히 다른 흐름형.
   KO/EN. 1280x720 <2MB. 사용: python make_thumb_w19.py"""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"
DONG = "assets/fonts/Cafe24Dongdong.ttf"
BG = "assets/graphics/bg/w19_ulsan.png"
POSE = "assets/graphics/poses/jieun_w19_persuade.png"

# (ko, en, label_ko, label_en, accent_rgb)
STEPS = [
    ("제 생각에는", "In my opinion", "주장", "Claim",      (66, 128, 206)),
    ("왜냐하면",   "Because",       "근거", "Reason",     (230, 150, 52)),
    ("따라서",     "Therefore",     "결론", "Conclusion", (66, 168, 98)),
]


def F(path, sz): return ImageFont.truetype(path, sz)


def outline(d, xy, txt, font, fill, oc=(28, 24, 20, 255), ow=6):
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


def pose_cut(path):
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    ys, xs = np.where(a[:, :, 3] > 25)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def round_mask(size, rad):
    m = Image.new("L", size, 0); d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=rad, fill=255)
    return m


def ctext(d, cx, y, txt, font, fill, oc=(28, 24, 20, 255), ow=3):
    w = d.textlength(txt, font=font)
    outline(d, (cx - w / 2, y), txt, font, fill, oc, ow)


def build(lang):
    base = cover(BG, W, H)
    # 상단 스크림(타이틀 대비)
    scr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(scr)
    for y in range(H):
        a = int(max(0, 165 * (1 - y / 320))) if y < 320 else 0
        sd.line([(0, y), (W, y)], fill=(30, 24, 18, a))
    # 하단 스크림(논리 체인 대비)
    for y in range(H):
        a = int(max(0, 150 * ((y - 430) / 290))) if y > 430 else 0
        sd.line([(0, y), (W, y)], fill=(28, 22, 16, min(150, a)))
    base.alpha_composite(scr)

    # ── 지은 (설득 포즈, 오른쪽 하단) — 먼저 배치, 텍스트가 위로
    im = pose_cut(POSE); ph = 600
    r = ph / im.height; im = im.resize((max(1, int(im.width * r)), ph))
    px = W - im.width - 24; py = H - ph + 6
    # 부드러운 흰 외곽(분리감)
    glow = Image.new("RGBA", (im.width + 24, im.height + 24), (0, 0, 0, 0))
    ga = np.array(im)[:, :, 3]
    sil = Image.fromarray(ga).resize((im.width + 24, im.height + 24))
    gl = Image.new("RGBA", glow.size, (255, 255, 255, 220)); glow.paste(gl, (0, 0), sil)
    glow = glow.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(6))
    base.alpha_composite(glow, (px - 12, py - 12))
    base.alpha_composite(im, (px, py))

    d = ImageDraw.Draw(base)

    # ── 타이틀 (상단 좌)
    if lang == "ko":
        outline(d, (52, 28), "의견과 설득", F(DONG, 98), (255, 236, 168), ow=7)
        outline(d, (56, 148), "논리적으로 말하기", F(MALGUN, 48), (255, 255, 255), ow=5)
    else:
        outline(d, (52, 32), "Opinions & Persuasion", F(MALGUN, 70), (255, 236, 168), ow=7)
        outline(d, (56, 132), "Speak Korean Logically", F(MALGUN, 44), (255, 255, 255), ow=5)
    # 회차 배지
    badge = "W19 · 설악산" if lang == "ko" else "W19 · Seoraksan"
    bf = F(MALGUN, 30); bw = d.textlength(badge, font=bf)
    by = 214 if lang == "ko" else 198
    d.rounded_rectangle([54, by, 54 + bw + 34, by + 48], radius=24, fill=(210, 78, 66, 235))
    d.text((71, by + 7), badge, font=bf, fill=(255, 255, 255))

    # ── 논리 체인 (하단 좌·중앙)
    pw, phh, gap, rad = 236, 104, 44, 28
    x0, top = 46, 556
    lab_f = F(MALGUN, 30)
    txt_ko = F(DONG, 52); txt_en = F(MALGUN, 33)
    for i, (ko, en, lk, le, ac) in enumerate(STEPS):
        cx = x0 + i * (pw + gap)
        # 화살표(알약 사이)
        if i > 0:
            ax = cx - gap - 4; ay = top + phh // 2
            d.polygon([(ax, ay - 16), (ax + 22, ay), (ax, ay + 16)], fill=(255, 255, 255, 255))
            d.polygon([(ax, ay - 16), (ax + 22, ay), (ax, ay + 16)], outline=(28, 24, 20), width=3)
        # 라벨 칩(알약 위)
        lab = lk if lang == "ko" else le
        lw = d.textlength(lab, font=lab_f)
        d.rounded_rectangle([cx + pw / 2 - lw / 2 - 16, top - 52, cx + pw / 2 + lw / 2 + 16, top - 8],
                            radius=18, fill=ac + (255,))
        d.text((cx + pw / 2 - lw / 2, top - 48), lab, font=lab_f, fill=(255, 255, 255))
        # 메인 알약
        d.rounded_rectangle([cx, top, cx + pw, top + phh], radius=rad, fill=(255, 252, 246, 250))
        d.rounded_rectangle([cx, top, cx + pw, top + phh], radius=rad, outline=ac + (255,), width=6)
        word = ko if lang == "ko" else en
        wf = txt_ko if lang == "ko" else txt_en
        ww = d.textlength(word, font=wf)
        while ww > pw - 22 and wf.size > 22:
            wf = ImageFont.truetype(DONG if lang == "ko" else MALGUN, wf.size - 2)
            ww = d.textlength(word, font=wf)
        d.text((cx + (pw - ww) / 2, top + (phh - wf.size) / 2 - 6), word, font=wf, fill=(40, 34, 28))

    out = base.convert("RGB")
    p = f"hangeul_birth_vowels/thumb_w19_{lang}_1280x720.jpg"
    q = 92; out.save(p, quality=q)
    while os.path.getsize(p) > 2 * 1024 * 1024 and q > 60:
        q -= 6; out.save(p, quality=q)
    print(f"  {p}  ({os.path.getsize(p)//1024}KB, q{q}, {out.size[0]}x{out.size[1]})")


print("W19 논리 체인 썸네일:")
for lg in ("ko", "en"):
    build(lg)
