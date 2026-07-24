# -*- coding: utf-8 -*-
"""거북목·운동손상 영/한 썸네일 4개 생성 (히어로컷 + 대비 강한 타이틀 오버레이). 1280x720."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FB = r"C:\Windows\Fonts\malgunbd.ttf"   # bold
W, H = 1280, 720
LOGO = "assets/drjay_ed_logo_circle.png"

def cover(im, w, h):
    r = max(w / im.width, h / im.height)
    im2 = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
    x = (im2.width - w) // 2; y = (im2.height - h) // 2
    return im2.crop((x, y, x + w, y + h))

def vgrad(w, h, top_a, bot_a, top=True):
    g = Image.new("L", (1, h))
    for y in range(h):
        t = y / (h - 1)
        a = int(top_a + (bot_a - top_a) * t)
        g.putpixel((0, y), a)
    return g.resize((w, h))

def fit_font(text, size, maxw):
    while size > 30:
        f = ImageFont.truetype(FB, size)
        if ImageDraw.Draw(Image.new("RGB",(10,10))).textlength(text, font=f) <= maxw: return f
        size -= 2
    return ImageFont.truetype(FB, size)

def draw_stroke(d, xy, text, font, fill, stroke=(20,20,20), sw=6):
    x, y = xy
    d.text((x, y), text, font=font, fill=fill, stroke_width=sw, stroke_fill=stroke)

def make(hero, title_lines, accent, sub, out):
    img = cover(Image.open(hero).convert("RGB"), W, H)
    # 상단 스크림(주석박스 가림) + 하단 강한 스크림
    top = Image.new("RGB",(W,220),(10,10,15)); img.paste(top,(0,0),vgrad(W,220,150,0))
    bot = Image.new("RGB",(W,420),(8,8,12)); img.paste(bot,(0,H-420),vgrad(W,420,0,225))
    d = ImageDraw.Draw(img)
    # 타이틀(하단, 2줄)
    maxw = W - 120
    y = H - 60
    fs = 96 if len(max(title_lines,key=len)) < 14 else 78
    fonts = [fit_font(t, fs, maxw) for t in title_lines]
    lh = max(f.size for f in fonts) + 12
    y -= lh * len(title_lines)
    for t, f in zip(title_lines, fonts):
        # accent 단어는 노랑
        if accent and accent in t:
            pre, post = t.split(accent, 1)
            x = 60
            draw_stroke(d,(x,y),pre,f,(255,255,255)); x += d.textlength(pre,font=f)
            draw_stroke(d,(x,y),accent,f,(255,214,10)); x += d.textlength(accent,font=f)
            draw_stroke(d,(x,y),post,f,(255,255,255))
        else:
            draw_stroke(d,(60,y),t,f,(255,255,255))
        y += lh
    # 서브타이틀
    sf = fit_font(sub, 40, maxw)
    draw_stroke(d,(62,H-58),sub,sf,(230,230,235),sw=4)
    # 로고 코너
    try:
        lg = Image.open(LOGO).convert("RGBA").resize((110,110))
        img.paste(lg,(W-130,24),lg)
    except Exception: pass
    img.save(out, quality=92)
    print("saved", out, flush=True)

TN = "scratch/thumb/tn_hero.jpg"; WK = "scratch/thumb/wk_hero.jpg"
make(TN, ["거북목,", "목엔 12kg 매달린다"], "12kg", "15도만 숙여도 — 목 통증의 과학", "turtle_neck_science/thumb_ko.jpg")
make(TN, ["Text Neck:", "12kg on Your Neck"], "12kg", "The science of forward head posture", "turtle_neck_science/thumb_en.jpg")
make(WK, ["운동만 하면", "왜 아플까?"], "왜 아플까?", "웨이트 트레이닝 부상의 통증 과학", "workout_injury_science/thumb_ko.jpg")
make(WK, ["Why Does", "Working Out Hurt?"], "Hurt?", "The science of exercise injury", "workout_injury_science/thumb_en.jpg")
print("THUMBS_DONE", flush=True)
