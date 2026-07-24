# -*- coding: utf-8 -*-
"""W15 썸네일 — ★전편과 다른 디자인: 사계절 4분할.
   봄(선작지왓)·여름(돈내코)·가을(영실기암)·겨울(백록담) 4쿼드런트에 각 계절 옷 지은 배치,
   중앙 대각선 리본에 큰 훅. 한 산에서 사계절을 보여주는 주제를 시각화.
   KO/EN. 1280x720 <2MB."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"
DONG = "assets/fonts/Cafe24Dongdong.ttf"


def outline(d, xy, txt, font, fill, oc=(20, 20, 20, 255), ow=8):
    x, y = xy
    for dx in range(-ow, ow + 1, 2):
        for dy in range(-ow, ow + 1, 2):
            d.text((x + dx, y + dy), txt, font=font, fill=oc)
    d.text((x, y), txt, font=font, fill=fill)


def taegukgi(d, cx, cy, R):
    d.ellipse([cx-R, cy-R, cx+R, cy+R], fill=(255,255,255,255), outline=(20,20,20,255), width=3)
    d.pieslice([cx-R, cy-R, cx+R, cy+R], 180, 360, fill=(205,40,50,255))
    d.pieslice([cx-R, cy-R, cx+R, cy+R], 0, 180, fill=(30,80,170,255))
    rr = R/2
    d.ellipse([cx-R, cy-rr, cx, cy+rr], fill=(205,40,50,255))
    d.ellipse([cx, cy-rr, cx+R, cy+rr], fill=(30,80,170,255))


def cover(path, w, h):
    im = Image.open(path).convert("RGBA")
    r = max(w/im.width, h/im.height)
    im = im.resize((int(im.width*r), int(im.height*r)))
    return im.crop(((im.width-w)//2, (im.height-h)//2, (im.width-w)//2+w, (im.height-h)//2+h))


def place_char(canvas, pose, box, target_h):
    """box=(x0,y0,x1,y1) 안에 캐릭터를 target_h 높이로 하단정렬 배치."""
    im = Image.open(f"assets/graphics/poses/jieun_w15_{pose}.png").convert("RGBA")
    a = np.array(im)
    ys, xs = np.where(a[:, :, 3] > 25)
    im = im.crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1))
    r = target_h / im.height
    im = im.resize((int(im.width*r), int(im.height*r)))
    x0, y0, x1, y1 = box
    cx = (x0 + x1)//2
    canvas.alpha_composite(im, (cx - im.width//2, y1 - im.height))


def build(lang):
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hw, hh = W//2, H//2
    # 4분할 배경 (봄/여름/가을/겨울)
    quads = [("bg_w15_seonjakji", (0, 0)), ("bg_w15_donnaeko", (hw, 0)),
             ("bg_w15_yeongsil", (0, hh)), ("bg_w15_baengnokdam", (hw, hh))]
    for bgk, (ox, oy) in quads:
        canvas.paste(cover(f"assets/graphics/bg/{bgk}.png", hw, hh), (ox, oy))
    d0 = ImageDraw.Draw(canvas)
    # 분할선(흰색)
    d0.line([(hw, 0), (hw, H)], fill=(255, 255, 255, 255), width=6)
    d0.line([(0, hh), (W, hh)], fill=(255, 255, 255, 255), width=6)
    # 각 쿼드런트 계절 옷 지은 (하단정렬, 화면 약 40%)
    ch = int(hh * 0.82)
    place_char(canvas, "spring_base",   (0, 0, hw, hh), ch)
    place_char(canvas, "summer_base",   (hw, 0, W, hh), ch)
    place_char(canvas, "autumn_base",   (0, hh, hw, H), ch)
    place_char(canvas, "winterpad_base", (hw, hh, W, H), ch)
    d = ImageDraw.Draw(canvas)

    # 계절 라벨(각 모서리 작은 칩)
    labels = [("봄", 20, 16, (255,150,180)), ("여름", hw+20, 16, (80,180,220)),
              ("가을", 20, hh+14, (220,130,40)), ("겨울", hw+20, hh+14, (90,120,200))]
    for txt, lx, ly, col in labels:
        f = ImageFont.truetype(MALGUN, 40)
        tw = d.textbbox((0,0), txt, font=f)[2]
        d.rounded_rectangle([lx, ly, lx+tw+24, ly+54], radius=12, fill=col+(255,))
        outline(d, (lx+12, ly+4), txt, f, (255,255,255,255), ow=3)

    # 중앙 대각 리본 + 큰 훅
    ribbon = Image.new("RGBA", (W, H), (0,0,0,0))
    rd = ImageDraw.Draw(ribbon)
    rd.polygon([(0, H*0.36), (W, H*0.26), (W, H*0.52), (0, H*0.62)], fill=(211,47,47,238))
    canvas = Image.alpha_composite(canvas, ribbon)
    d = ImageDraw.Draw(canvas)

    # LEARN KOREAN 작은 배너(좌상 리본 위)
    f_ban = ImageFont.truetype(MALGUN, 40)
    taegukgi(d, 44, H//2-96, 22)
    d.text((74, H//2-116), "LEARN KOREAN", font=f_ban, fill=(255,255,255,255))

    hook_ko = "사계절"
    if lang == "ko":
        outline(d, (W//2-250, H//2-70), "날씨와 사계절", ImageFont.truetype(MALGUN, 92), (255,224,66,255), ow=9)
        outline(d, (W//2-150, H//2+34), "봄·여름·가을·겨울", ImageFont.truetype(MALGUN, 46), (255,255,255,255), ow=5)
    else:
        outline(d, (W//2-330, H//2-74), "WEATHER & 4 SEASONS", ImageFont.truetype(MALGUN, 76), (255,224,66,255), ow=8)
        outline(d, (W//2-300, H//2+30), "spring · summer · fall · winter", ImageFont.truetype(MALGUN, 42), (255,255,255,255), ow=5)

    # 장소(하단 중앙)
    place = "한라산 · 제주" if lang == "ko" else "Hallasan · Jeju"
    outline(d, (W//2-120, H-52), place, ImageFont.truetype(MALGUN, 32), (255,255,255,255), ow=4)

    out = f"hangeul_birth_vowels/thumb_w15_{lang}_1280x720.jpg"
    canvas.convert("RGB").save(out, quality=90)
    print(f"썸네일({lang}): {out}  {os.path.getsize(out)//1024}KB")
    return out


if __name__ == "__main__":
    build("ko")
    build("en")
