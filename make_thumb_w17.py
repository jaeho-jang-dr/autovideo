# -*- coding: utf-8 -*-
"""W17 썸네일 — ★전편들과 다른 디자인: '존댓말 ↔ 반말 + 축약어' 테마.
   불국사 석가탑 배경 위에 티쳐제이(compare 포즈, 체크셔츠 style4) 히어로 +
   '존댓말 →(금색 화살표) 반말' 대비 + 하단 축약어 말풍선 3개(생축·아아·꿀잼).
   W16(빈도 사다리)와 완전히 다른 레이아웃(대비 화살표 + 말풍선 알약).
   KO/EN. 1280x720 <2MB. (make_thumb_w16.py 복제·재설계)"""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"
DONG = "assets/fonts/Cafe24Dongdong.ttf"
BG = "assets/graphics/bg/w17_bg_seokgatap.png"


def F(path, sz):
    return ImageFont.truetype(path, sz)


def outline(d, xy, txt, font, fill, oc=(20, 20, 20, 255), ow=8):
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
    im = Image.open(f"assets/graphics/poses/tj_w17_{pose}.png").convert("RGBA")
    a = np.array(im)
    ys, xs = np.where(a[:, :, 3] > 25)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def place_char(canvas, pose, cx, bottom_y, target_h, margin=12):
    im = pose_cut(pose)
    r = target_h / im.height
    im = im.resize((int(im.width * r), int(im.height * r)))
    cx = int(min(max(cx, im.width // 2 + margin), W - im.width // 2 - margin))  # 잘림 방지 클램프
    canvas.alpha_composite(im, (cx - im.width // 2, bottom_y - im.height))


def pill(d, cx, cy, big, small, col):
    """축약어 말풍선(알약): 큰 슬랭 + 작은 뜻."""
    bf = F(DONG, 52); sf = F(MALGUN, 24)
    bw = d.textbbox((0, 0), big, font=bf)[2]
    sw = d.textbbox((0, 0), small, font=sf)[2]
    w = max(bw, sw) + 56
    h = 118
    x0, y0 = cx - w // 2, cy - h // 2
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=30, fill=col + (245,),
                        outline=(255, 255, 255, 255), width=5)
    outline(d, (cx - bw // 2, y0 + 12), big, bf, (255, 255, 255, 255), ow=3)
    d.text((cx - sw // 2, y0 + 74), small, font=sf, fill=(255, 255, 255, 255))


def build(lang):
    canvas = cover(BG, W, H).convert("RGBA")

    # 좌측 텍스트 대비 — 부드러운 라운드 카드(패널) + 상·하단 밴드 (W16의 좌측 그라데이션과 다른 룩)
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(band)
    bd.rectangle([0, 0, W, 88], fill=(12, 20, 30, 120))
    bd.rectangle([0, H - 150, W, H], fill=(12, 20, 30, 130))
    canvas = Image.alpha_composite(canvas, band)

    # 히어로 티쳐제이(compare = 존댓말↔반말 비교) — 우측 하단정렬(잘림 클램프)
    place_char(canvas, "compare", int(W * 0.80), H - 4, int(H * 0.80))

    d = ImageDraw.Draw(canvas)

    # 로고(좌상단) + LEARN KOREAN
    logo = Image.open("assets/drjay_ed_logo_circle.png").convert("RGBA").resize((80, 80))
    canvas.alpha_composite(logo, (22, 8))
    d = ImageDraw.Draw(canvas)
    d.text((112, 28), "LEARN KOREAN", font=F(MALGUN, 32), fill=(255, 255, 255, 255))
    # W17 배지(우상단)
    d.rounded_rectangle([W - 116, 14, W - 22, 64], radius=12, fill=(211, 47, 47, 245))
    d.text((W - 102, 20), "W17", font=F(MALGUN, 34), fill=(255, 255, 255, 255))

    # 타이틀 카드(반투명 라운드 패널) — 좌측
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([28, 120, 716, 356], radius=34, fill=(15, 25, 38, 165))
    canvas = Image.alpha_composite(canvas, card)
    d = ImageDraw.Draw(canvas)

    GOLD = (255, 214, 64, 255)
    if lang == "ko":
        # 1줄: 존댓말 →(금) 반말
        outline(d, (52, 138), "존댓말", F(MALGUN, 92), (255, 255, 255, 255), ow=8)
        outline(d, (352, 128), "→", F(MALGUN, 104), GOLD, ow=8)
        outline(d, (470, 138), "반말", F(MALGUN, 92), GOLD, ow=8)
        # 2줄: 축약어까지 익혀요!
        outline(d, (52, 256), "+ 축약어까지!", F(MALGUN, 76), (255, 255, 255, 255), ow=8)
    else:
        outline(d, (52, 150), "POLITE", F(MALGUN, 80), (255, 255, 255, 255), ow=8)
        outline(d, (330, 138), "→", F(MALGUN, 96), GOLD, ow=8)
        outline(d, (440, 150), "CASUAL", F(MALGUN, 80), GOLD, ow=8)
        outline(d, (52, 258), "+ K-SLANG!", F(MALGUN, 74), (255, 255, 255, 255), ow=8)

    # 하단 축약어 말풍선 3개 (생축 · 아아 · 꿀잼) — 슬랭이라 KO/EN 공통, 뜻만 언어별
    if lang == "ko":
        pills = [("생축", "생일 축하해", (231, 76, 120)),
                 ("아아", "아이스 아메리카노", (150, 100, 60)),
                 ("꿀잼", "진짜 재미있다", (240, 160, 30))]
    else:
        pills = [("생축", "happy bday", (231, 76, 120)),
                 ("아아", "iced americano", (150, 100, 60)),
                 ("꿀잼", "so fun!", (240, 160, 30))]
    px = 120
    for big, small, col in pills:
        pill(d, px, H - 78, big, small, col)
        px += 210

    # 장소명(우하단)
    place = "불국사 · 경주" if lang == "ko" else "Bulguksa, Gyeongju"
    pf = F(MALGUN, 30)
    pw = d.textbbox((0, 0), place, font=pf)[2]
    outline(d, (W - pw - 28, H - 44), place, pf, (255, 255, 255, 255), ow=4)

    out = f"hangeul_birth_vowels/thumb_w17_{lang}_1280x720.jpg"
    canvas.convert("RGB").save(out, quality=90)
    print(f"썸네일({lang}): {out}  {os.path.getsize(out)//1024}KB  {Image.open(out).size}")
    return out


if __name__ == "__main__":
    build("ko")
    build("en")
