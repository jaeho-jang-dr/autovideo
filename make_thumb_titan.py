# -*- coding: utf-8 -*-
"""titan_science 썸네일 — KO/EN 각 3시안.

★매회 다른 구성으로 만든다(같은 템플릿 반복 금지).
★1280x720 · 2MB 미만 · 한글은 malgun.ttf 절대경로.
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "titan_science", "_thumb")
OUT = os.path.join(ROOT, "titan_science", "_thumb", "out")
KFONT = r"C:\Windows\Fonts\malgun.ttf"
KFONT_B = r"C:\Windows\Fonts\malgunbd.ttf"
EFONT_B = r"C:\Windows\Fonts\arialbd.ttf"
W, H = 1280, 720

RED = (206, 58, 48)
CREAM = (247, 242, 231)
INK = (28, 26, 24)


def f(path, size):
    return ImageFont.truetype(path, size)


def base(name, darken_bottom=0.0, blur=0.0):
    im = Image.open(os.path.join(SRC, name)).convert("RGB").resize((W, H), Image.LANCZOS)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    if darken_bottom:
        ov = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(ov)
        for y in range(H):
            t = max(0.0, (y - H * 0.42) / (H * 0.58))
            d.line([(0, y), (W, y)], fill=int(255 * darken_bottom * t ** 1.4))
        im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, ov)
    return im


def outline(d, xy, text, font, fill, ow=6, oc=(0, 0, 0)):
    x, y = xy
    for dx in range(-ow, ow + 1, 2):
        for dy in range(-ow, ow + 1, 2):
            if dx * dx + dy * dy <= ow * ow:
                d.text((x + dx, y + dy), text, font=font, fill=oc)
    d.text(xy, text, font=font, fill=fill)


def tag(d, xy, text, font, bg=RED, fg=(255, 255, 255), pad=(18, 10)):
    x, y = xy
    w = d.textlength(text, font=font)
    h = font.size
    d.rounded_rectangle([x, y, x + w + pad[0] * 2, y + h + pad[1] * 2], 10, fill=bg)
    d.text((x + pad[0], y + pad[1] - 2), text, font=font, fill=fg)
    return x + w + pad[0] * 2


# ── 시안 A — 성벽 위 손가락 · 아래 굵은 카피 ───────────────────────────
def ko_a():
    im = base("f6.png", darken_bottom=0.80)
    d = ImageDraw.Draw(im)
    tag(d, (56, 44), "물리학이 밝힌 설계", f(KFONT_B, 34))
    outline(d, (56, 430), "스티로폼보다", f(KFONT_B, 96), CREAM, 7)
    outline(d, (56, 536), "가볍다", f(KFONT_B, 118), (255, 214, 92), 8)
    d.text((420, 566), "60m 거인의 몸",
           font=f(KFONT_B, 44), fill=CREAM)
    return im


def en_a():
    im = base("f6.png", darken_bottom=0.80)
    d = ImageDraw.Draw(im)
    tag(d, (56, 44), "THE PHYSICS BEHIND IT", f(EFONT_B, 32))
    outline(d, (56, 430), "LIGHTER THAN", f(EFONT_B, 84), CREAM, 7)
    outline(d, (56, 528), "STYROFOAM", f(EFONT_B, 112), (255, 214, 92), 8)
    d.text((58, 654), "a 60-meter giant", font=f(EFONT_B, 40), fill=CREAM)
    return im


# ── 시안 B — 성벽 스케일 · 오른쪽 크림 패널 ───────────────────────────
def ko_b():
    im = base("f20.png")
    d = ImageDraw.Draw(im)
    d.rectangle([700, 0, W, H], fill=CREAM)
    d.rectangle([694, 0, 700, H], fill=RED)
    d.text((736, 96), "60m 거인은", font=f(KFONT_B, 66), fill=INK)
    d.text((736, 176), "왜", font=f(KFONT_B, 66), fill=INK)
    d.text((806, 176), "가벼워야", font=f(KFONT_B, 66), fill=RED)
    d.text((736, 256), "했을까?", font=f(KFONT_B, 66), fill=INK)
    d.line([(736, 372), (1204, 372)], fill=RED, width=5)
    for i, s in enumerate(["10배 커지면", "무게는 1,000배", "뼈는 100배뿐"]):
        d.text((736, 404 + i * 62), s, font=f(KFONT, 46), fill=INK)
    return im


def en_b():
    im = base("f20.png")
    d = ImageDraw.Draw(im)
    d.rectangle([700, 0, W, H], fill=CREAM)
    d.rectangle([694, 0, 700, H], fill=RED)
    d.text((736, 96), "WHY A 60m", font=f(EFONT_B, 62), fill=INK)
    d.text((736, 168), "GIANT MUST", font=f(EFONT_B, 62), fill=INK)
    d.text((736, 240), "BE LIGHT", font=f(EFONT_B, 62), fill=RED)
    d.line([(736, 356), (1204, 356)], fill=RED, width=5)
    for i, s in enumerate(["10x taller", "1,000x heavier", "only 100x stronger"]):
        d.text((736, 392 + i * 62), s, font=f(EFONT_B, 42), fill=INK)
    return im


# ── 시안 C — 열 방출 · 중앙 대비 ──────────────────────────────────────
def ko_c():
    im = base("f455.png", darken_bottom=0.55)
    d = ImageDraw.Draw(im)
    outline(d, (54, 54), "걷기 전에", f(KFONT_B, 78), CREAM, 7)
    outline(d, (54, 148), "스스로 익는다", f(KFONT_B, 100), (255, 140, 90), 8)
    tag(d, (54, 610), "열역학이 막아선 거인", f(KFONT_B, 40))
    return im


def en_c():
    im = base("f455.png", darken_bottom=0.55)
    d = ImageDraw.Draw(im)
    outline(d, (54, 54), "IT COOKS ITSELF", f(EFONT_B, 76), CREAM, 7)
    outline(d, (54, 148), "BEFORE IT WALKS", f(EFONT_B, 88), (255, 140, 90), 8)
    tag(d, (54, 616), "THERMODYNAMICS SAYS NO", f(EFONT_B, 36))
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    made = []
    for name, fn in [("ko_A", ko_a), ("ko_B", ko_b), ("ko_C", ko_c),
                     ("en_A", en_a), ("en_B", en_b), ("en_C", en_c)]:
        p = os.path.join(OUT, "titan_%s.jpg" % name)
        fn().save(p, quality=92, optimize=True)
        made.append((name, os.path.getsize(p)))
    for n, s in made:
        print("  %-6s %6.0f KB %s" % (n, s / 1024, "★2MB 초과" if s > 2 * 1024 * 1024 else ""))
    # 시안 대조 시트
    sheet = Image.new("RGB", (640 * 3, 360 * 2), (20, 20, 20))
    for i, (n, _) in enumerate(made):
        sheet.paste(Image.open(os.path.join(OUT, "titan_%s.jpg" % n)).resize((640, 360)),
                    ((i % 3) * 640, (i // 3) * 360))
    sheet.save(os.path.join(OUT, "contact.jpg"), quality=88)
    print(os.path.join(OUT, "contact.jpg"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
