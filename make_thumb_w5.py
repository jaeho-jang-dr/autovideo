# -*- coding: utf-8 -*-
"""W5 이중모음 썸네일(KO/EN) 1280x720 — 북촌 배경 + 큰 자모 + 타이틀 + 로고."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
W, H = 1280, 720
BG = os.path.join(ROOT, "assets", "graphics", "bg", "bg_w5_01.png")
LOGO = os.path.join(ROOT, "web", "public", "logo.png")
MAL = "C:/Windows/Fonts/malgunbd.ttf"


def cover(im, w, h):
    s = max(w/im.width, h/im.height)
    nw, nh = int(im.width*s), int(im.height*s)
    im = im.resize((nw, nh), Image.LANCZOS)
    return im.crop(((nw-w)//2, (nh-h)//2, (nw-w)//2+w, (nh-h)//2+h))


def make(title, subtitle, badge, out):
    base = cover(Image.open(BG).convert("RGB"), W, H)
    d = ImageDraw.Draw(base, "RGBA")
    # 하단·좌측 어둡게(대비)
    scr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scr)
    for y in range(H):
        a = int(150 * max(0, (y-H*0.35)/(H*0.65))**1.3)
        sd.line([(0, y), (W, y)], fill=(20, 18, 30, a))
    sd.rectangle([0, 0, int(W*0.46), H], fill=(20, 18, 30, 70))
    base = Image.alpha_composite(base.convert("RGBA"), scr).convert("RGB")
    d = ImageDraw.Draw(base, "RGBA")

    # 큰 자모(이중모음 대표) — 색색
    jamos = ["ㅑ", "ㅕ", "ㅛ", "ㅠ", "ㅘ", "ㅢ"]
    cols = [(255,214,102),(126,214,168),(140,196,255),(255,150,170),(196,168,255),(255,190,120)]
    jf = ImageFont.truetype(MAL, 150)
    x = 70
    for j, c in zip(jamos, cols):
        w = d.textlength(j, font=jf)
        # 외곽선
        for dx in (-3,0,3):
            for dy in (-3,0,3):
                d.text((x+dx, 300+dy), j, font=jf, fill=(20,18,30,255))
        d.text((x, 300), j, font=jf, fill=c)
        x += w + 18

    # 타이틀(상단)
    tf = ImageFont.truetype(MAL, 96)
    for dx in (-3,0,3):
        for dy in (-3,0,3):
            d.text((66+dx, 60+dy), title, font=tf, fill=(20,18,30,255))
    d.text((66, 60), title, font=tf, fill=(255,255,255))
    # 서브타이틀
    sf = ImageFont.truetype(MAL, 52)
    d.text((70, 185), subtitle, font=sf, fill=(255,236,150))

    # 배지(우하단) 한글 W5
    bf = ImageFont.truetype(MAL, 46)
    bw = d.textlength(badge, font=bf)
    d.rounded_rectangle([W-bw-64, H-96, W-30, H-32], 18, fill=(232,90,60,235))
    d.text((W-bw-48, H-88), badge, font=bf, fill=(255,255,255))

    # 로고(좌상단 작게)
    if os.path.exists(LOGO):
        lg = Image.open(LOGO).convert("RGBA")
        lg.thumbnail((110, 110), Image.LANCZOS)
        base.paste(lg, (W-lg.width-34, 30), lg)

    base.save(out, "JPEG", quality=88)
    kb = os.path.getsize(out)//1024
    print(f"{os.path.basename(out)}: {base.size} {kb}KB")


if __name__ == "__main__":
    os.makedirs("web/public/docs", exist_ok=True)
    make("이중모음 · 반모음", "두 소리가 미끄러진다! 한글 발음",
         "한글 배우기 W5", "web/public/docs/hangeul_w5_thumbnail_ko.jpg")
    make("Korean Diphthongs", "Two sounds glide together!",
         "Learn Korean W5", "web/public/docs/hangeul_w5_thumbnail_en.jpg")
