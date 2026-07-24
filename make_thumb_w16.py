# -*- coding: utf-8 -*-
"""W16 썸네일 — ★전편(W15 4분할)과 다른 디자인: '취미 + 빈도' 테마.
   남이섬 메타세쿼이아 길 배경 위에 인준(자전거) 히어로 + 빈도 사다리 칩(매일→자주→가끔)
   + 하단 취미 배지 스트립(사진·낚시·피아노)으로 "취미 20가지 + 얼마나 자주"를 시각화.
   KO/EN. 1280x720 <2MB. (make_thumb_w15.py 복제·재설계)"""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"


def outline(d, xy, txt, font, fill, oc=(20, 20, 20, 255), ow=8):
    x, y = xy
    for dx in range(-ow, ow + 1, 2):
        for dy in range(-ow, ow + 1, 2):
            d.text((x + dx, y + dy), txt, font=font, fill=oc)
    d.text((x, y), txt, font=font, fill=fill)


def taegukgi(d, cx, cy, R):
    d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=3)
    d.pieslice([cx-R, cy-R, cx+R, cy+R], 180, 360, fill=(205, 40, 50, 255))
    d.pieslice([cx-R, cy-R, cx+R, cy+R], 0, 180, fill=(30, 80, 170, 255))
    rr = R/2
    d.ellipse([cx-R, cy-rr, cx, cy+rr], fill=(205, 40, 50, 255))
    d.ellipse([cx, cy-rr, cx+R, cy+rr], fill=(30, 80, 170, 255))


def cover(path, w, h):
    im = Image.open(path).convert("RGBA")
    r = max(w/im.width, h/im.height)
    im = im.resize((int(im.width*r), int(im.height*r)))
    return im.crop(((im.width-w)//2, (im.height-h)//2, (im.width-w)//2+w, (im.height-h)//2+h))


def pose_cut(pose):
    im = Image.open(f"assets/graphics/poses/injun_w16_{pose}.png").convert("RGBA")
    a = np.array(im)
    ys, xs = np.where(a[:, :, 3] > 25)
    return im.crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1))


def place_char(canvas, pose, cx, bottom_y, target_h):
    im = pose_cut(pose)
    r = target_h / im.height
    im = im.resize((int(im.width*r), int(im.height*r)))
    canvas.alpha_composite(im, (cx - im.width//2, bottom_y - im.height))


def badge(canvas, pose, cx, cy, R, ring):
    """원형 배지 안에 취미 포즈 아이콘."""
    d = ImageDraw.Draw(canvas)
    d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(255, 255, 255, 235), outline=ring+(255,), width=6)
    im = pose_cut(pose)
    r = (R*1.7) / max(im.width, im.height)
    im = im.resize((int(im.width*r), int(im.height*r)))
    # 원 안에 클립
    mask = Image.new("L", (2*R, 2*R), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 2*R, 2*R], fill=255)
    tmp = Image.new("RGBA", (2*R, 2*R), (0, 0, 0, 0))
    tmp.alpha_composite(im, (R - im.width//2, (2*R) - im.height - 4))
    tmp.putalpha(Image.composite(tmp.split()[3], Image.new("L", (2*R, 2*R), 0), mask))
    canvas.alpha_composite(tmp, (cx-R, cy-R))


def build(lang):
    canvas = cover("assets/graphics/bg/bg_w16_metasequoia.png", W, H).convert("RGBA")

    # 좌측 어둡게(텍스트 대비) — 가로 그라데이션 패널
    grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for x in range(W):
        a = int(max(0, 205 - x * 0.30))   # 왼쪽 짙게 → 오른쪽 투명
        gd.line([(x, 0), (x, H)], fill=(12, 22, 16, a))
    canvas = Image.alpha_composite(canvas, grad)
    # 상·하단 살짝 어둡게
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rectangle([0, 0, W, 92], fill=(10, 18, 14, 120))
    bd.rectangle([0, H-70, W, H], fill=(10, 18, 14, 150))
    canvas = Image.alpha_composite(canvas, band)

    # 히어로 인준(자전거 타기 = 최고의 취미) — 우측 하단정렬
    place_char(canvas, "cycling", int(W*0.76), H-6, int(H*0.86))

    d = ImageDraw.Draw(canvas)

    # 로고(좌상단) + LEARN KOREAN
    logo = Image.open("assets/drjay_ed_logo_circle.png").convert("RGBA").resize((84, 84))
    canvas.alpha_composite(logo, (24, 12))
    d = ImageDraw.Draw(canvas)
    d.text((118, 34), "LEARN KOREAN", font=ImageFont.truetype(MALGUN, 34), fill=(255, 255, 255, 255))
    # W16 배지
    d.rounded_rectangle([W-116, 18, W-24, 66], radius=12, fill=(211, 47, 47, 240))
    d.text((W-102, 24), "W16", font=ImageFont.truetype(MALGUN, 34), fill=(255, 255, 255, 255))

    # 큰 훅 타이틀 (좌측)
    if lang == "ko":
        outline(d, (40, 118), "취미 +", ImageFont.truetype(MALGUN, 104), (255, 224, 66, 255), ow=9)
        outline(d, (40, 236), "얼마나 자주?", ImageFont.truetype(MALGUN, 92), (255, 255, 255, 255), ow=9)
    else:
        outline(d, (40, 118), "HOBBIES +", ImageFont.truetype(MALGUN, 88), (255, 224, 66, 255), ow=9)
        outline(d, (40, 224), "HOW OFTEN?", ImageFont.truetype(MALGUN, 84), (255, 255, 255, 255), ow=9)

    # 빈도 사다리 칩 (매일 → 자주 → 가끔), 계단식 하강
    if lang == "ko":
        chips = [("매일", (211, 47, 47)), ("자주", (240, 140, 30)), ("가끔", (40, 120, 200))]
    else:
        chips = [("every day", (211, 47, 47)), ("often", (240, 140, 30)), ("sometimes", (40, 120, 200))]
    cf = ImageFont.truetype(MALGUN, 46)
    cx, cy = 44, 372
    for i, (txt, col) in enumerate(chips):
        tw = d.textbbox((0, 0), txt, font=cf)[2]
        x0 = cx + i * 40
        y0 = cy + i * 74
        d.rounded_rectangle([x0, y0, x0 + tw + 46, y0 + 62], radius=16, fill=col + (255,),
                            outline=(255, 255, 255, 255), width=4)
        outline(d, (x0 + 23, y0 + 6), txt, cf, (255, 255, 255, 255), ow=3)
        if i < 2:  # 하강 화살표
            d.text((x0 + tw + 54, y0 + 12), "▼", font=ImageFont.truetype(MALGUN, 40), fill=(255, 255, 255, 235))

    # 하단 취미 배지 스트립 (사진·낚시·피아노 = 취미 여러 가지 암시)
    badges = [("taking_photo", (255, 150, 60)), ("fishing", (60, 170, 200)), ("piano", (180, 110, 200))]
    bx = 470
    for pose, ring in badges:
        badge(canvas, pose, bx, H-78, 58, ring)
        bx += 132
    d = ImageDraw.Draw(canvas)
    plus = "+17가지" if lang == "ko" else "+17 more"
    outline(d, (bx - 40, H-96, ), plus, ImageFont.truetype(MALGUN, 34), (255, 224, 66, 255), ow=4)

    # 장소명 (우하단)
    place = "남이섬 · 춘천" if lang == "ko" else "Nami Island, Chuncheon"
    pf = ImageFont.truetype(MALGUN, 30)
    pw = d.textbbox((0, 0), place, font=pf)[2]
    outline(d, (W - pw - 30, H - 46), place, pf, (255, 255, 255, 255), ow=4)

    out = f"hangeul_birth_vowels/thumb_w16_{lang}_1280x720.jpg"
    canvas.convert("RGB").save(out, quality=90)
    print(f"썸네일({lang}): {out}  {os.path.getsize(out)//1024}KB  {Image.open(out).size}")
    return out


if __name__ == "__main__":
    build("ko")
    build("en")
