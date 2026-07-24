# -*- coding: utf-8 -*-
"""W7 숫자·날짜·시간 썸네일(KO/EN) 1280x720 — 인사동 배경 + 졸라걸 + 인사말 알약 + 타이틀."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H = 1280, 720
BG = os.path.join(ROOT, "assets", "graphics", "bg", "bg_w8_01.png")
CHAR = os.path.join(ROOT, "assets", "graphics", "poses", "injun_wave_right.png")
LOGO = os.path.join(ROOT, "web", "public", "logo.png")
MAL = "C:/Windows/Fonts/malgunbd.ttf"
DONG = os.path.join(ROOT, "assets", "fonts", "Cafe24Dongdong.ttf")
OUT = os.path.join(ROOT, "web", "public", "docs")
os.makedirs(OUT, exist_ok=True)


def cover(im, w, h):
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2; y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def pill(d, cx, cy, text, font, fill, tcol=(255, 255, 255)):
    b = d.textbbox((0, 0), text, font=font)
    tw, th = b[2] - b[0], b[3] - b[1]
    padx, pady = 30, 16
    x0, y0 = cx - tw // 2 - padx, cy - th // 2 - pady
    x1, y1 = cx + tw // 2 + padx, cy + th // 2 + pady
    d.rounded_rectangle([x0, y0, x1, y1], radius=(y1 - y0) // 2, fill=fill)
    d.text((cx - tw // 2 - b[0], cy - th // 2 - b[1]), text, font=font, fill=tcol)


def make(title, badge_l, badge_r, greet, out):
    base = cover(Image.open(BG).convert("RGB"), W, H).convert("RGBA")
    # 왼쪽 어둡게(캐릭터/타이틀 가독)
    scr = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(scr)
    sd.rectangle([0, 0, int(W * 0.5), H], fill=(24, 20, 32, 90))
    for y in range(H):
        a = int(120 * max(0, (y - H * 0.4) / (H * 0.6)) ** 1.3)
        sd.line([(0, y), (W, y)], fill=(20, 18, 30, a))
    base = Image.alpha_composite(base, scr)
    d = ImageDraw.Draw(base, "RGBA")
    # 졸라걸 캐릭터(좌하단)
    if os.path.exists(CHAR):
        ch = Image.open(CHAR).convert("RGBA")
        bb = ch.getbbox()                        # 투명 여백 제거(정규화 캔버스 대응)
        if bb:
            ch = ch.crop(bb)
        sc = 520 / ch.height
        ch = ch.resize((int(ch.width * sc), int(ch.height * sc)), Image.LANCZOS)
        base.alpha_composite(ch, (70, H - ch.height - 20))
        d = ImageDraw.Draw(base, "RGBA")
    # 타이틀
    tf = ImageFont.truetype(MAL, 74)
    for line, yy in zip(title, [70, 158]):
        d.text((70, yy), line, font=tf, fill=(255, 255, 255),
               stroke_width=5, stroke_fill=(30, 26, 40))
    # 인사말 알약(우측)
    gf = ImageFont.truetype(DONG if os.path.exists(DONG) else MAL, 62)
    cols = [(46, 125, 107), (180, 85, 45), (70, 110, 180)]
    for i, (g, c) in enumerate(zip(greet, cols)):
        pill(d, 900, 300 + i * 118, g, gf, (*c, 255))
    # 배지
    bf = ImageFont.truetype(MAL, 30)
    pill(d, 70 + d.textbbox((0, 0), badge_l, font=bf)[2] // 2 + 34, 700 - 300 + 300, "", bf, (0, 0, 0, 0))
    pill(d, 130, 40, badge_l, bf, (255, 205, 90, 255), (40, 30, 10))
    br_w = d.textbbox((0, 0), badge_r, font=bf)[2]
    pill(d, W - br_w // 2 - 60, 40, badge_r, bf, (30, 26, 40, 230))
    # 로고
    if os.path.exists(LOGO):
        lg = Image.open(LOGO).convert("RGBA"); lg.thumbnail((96, 96))
        base.alpha_composite(lg, (W - lg.width - 24, H - lg.height - 24))
    base.convert("RGB").save(out, quality=92)
    print("saved", out)


if __name__ == "__main__":
    make(["숫자·날짜와", "시간 말하기"], "초급 · 8주차", "★ 한국어 공부",
         ["하나 둘 셋", "일 이 삼", "월 화 수"],
         os.path.join(OUT, "hangeul_w8_thumbnail_ko.jpg"))
    make(["Numbers, Dates", "& Time"], "Beginner · W8", "★ Learn Korean",
         ["하나 둘 셋", "일 이 삼", "월 화 수"],
         os.path.join(OUT, "hangeul_w8_thumbnail_en.jpg"))
