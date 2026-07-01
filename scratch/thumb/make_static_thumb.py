# -*- coding: utf-8 -*-
"""세종 본편 정지 썸네일(영/한) — S33 강렬 얼굴 기반. 4K(3840x2160) 네이티브 렌더 + YT 1280x720."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
ROOT = "D:/Entertainments/DevEnvironment/autovideo"
OUT = os.path.join(ROOT, "scratch", "thumb")
MALGUN = r"C:\Windows\Fonts\malgunbd.ttf"
IMPACT = r"C:\Windows\Fonts\impact.ttf"
ARIALBD = r"C:\Windows\Fonts\arialbd.ttf"
S = 3                       # 스케일 (1280x720 -> 3840x2160)
W, H = 1280*S, 720*S

def font(path, sz):
    try: return ImageFont.truetype(path, sz)
    except Exception: return ImageFont.truetype(MALGUN, sz)

def cover(im):
    # 1280x720 소스를 4K로 업스케일(LANCZOS) + 언샤프으로 선명화
    sc = max(W/im.width, H/im.height)
    im = im.resize((int(im.width*sc), int(im.height*sc)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=110, threshold=2))
    l = int((im.width-W)*0.62); t = (im.height-H)//2
    return im.crop((l, t, l+W, t+H))

def draw_text(base, xy, text, fnt, fill, stroke=(10,10,15), sw=8, shadow=True, glow=None, anchor="lm"):
    d = ImageDraw.Draw(base); x, y = xy
    if glow:
        g = Image.new("RGBA", base.size, (0,0,0,0)); dg = ImageDraw.Draw(g)
        dg.text((x,y), text, font=fnt, fill=glow+(255,), stroke_width=sw+2, stroke_fill=glow+(255,), anchor=anchor)
        g = g.filter(ImageFilter.GaussianBlur(14*S)); base.alpha_composite(g)
    if shadow:
        sh = Image.new("RGBA", base.size, (0,0,0,0)); ds = ImageDraw.Draw(sh)
        ds.text((x+5*S,y+7*S), text, font=fnt, fill=(0,0,0,220), stroke_width=sw, stroke_fill=(0,0,0,220), anchor=anchor)
        sh = sh.filter(ImageFilter.GaussianBlur(5*S)); base.alpha_composite(sh)
    ImageDraw.Draw(base).text((x,y), text, font=fnt, fill=fill, stroke_width=sw, stroke_fill=stroke, anchor=anchor)

def build(lang):
    base = cover(Image.open(os.path.join(OUT, "cand_33.jpg")).convert("RGB")).convert("RGBA")
    base = ImageEnhance.Contrast(base).enhance(1.08)
    base = ImageEnhance.Color(base).enhance(1.12)
    # 좌측 어둡게(그라디언트)
    grad = Image.new("L", (W, 1), 0)
    for x in range(W):
        grad.putpixel((x,0), int(235*max(0, 1-(x/(W*0.66)))))
    grad = grad.resize((W, H))
    dark = Image.new("RGBA", (W,H), (5,7,16,255)); dark.putalpha(grad); base.alpha_composite(dark)
    # 하단 비네트
    vg = Image.new("L",(1,H),0)
    for y in range(H): vg.putpixel((0,y), int(150*max(0,(y-H*0.6)/(H*0.4))))
    vg = vg.resize((W,H)); vv=Image.new("RGBA",(W,H),(0,0,0,255)); vv.putalpha(vg); base.alpha_composite(vv)
    # 한글 자모 액센트
    jf = font(MALGUN, 66*S)
    for ch,xx,yy in [("ㅎ",70,60),("ㅏ",150,55),("ㄴ",232,66),("ㄱ",312,52),("ㅡ",392,70),("ㄹ",470,58)]:
        draw_text(base,(xx*S,yy*S),ch,jf,(255,225,120,255),sw=4*S,shadow=True,glow=(255,190,60),anchor="lm")
    GOLD=(255,208,74,255); WHITE=(255,255,255,255)
    if lang=="ko":
        draw_text(base,(70*S,300*S),"세종대왕과",font(MALGUN,118*S),WHITE,sw=9*S,glow=(20,30,60),anchor="lm")
        draw_text(base,(70*S,420*S),"한글",font(MALGUN,150*S),GOLD,sw=10*S,glow=(255,150,30),anchor="lm")
        draw_text(base,(74*S,545*S),"한글은 어떻게 태어났을까?",font(MALGUN,50*S),WHITE,sw=6*S,anchor="lm")
    else:
        draw_text(base,(70*S,285*S),"KING SEJONG",font(IMPACT,104*S),WHITE,sw=8*S,glow=(20,30,60),anchor="lm")
        draw_text(base,(70*S,400*S),"& HANGEUL",font(IMPACT,132*S),GOLD,sw=9*S,glow=(255,150,30),anchor="lm")
        draw_text(base,(74*S,530*S),"How an Alphabet Was Born",font(ARIALBD,48*S),WHITE,sw=6*S,anchor="lm")
    # 로고(우하단)
    try:
        logo=Image.open(os.path.join(ROOT,"assets","drjay_ed_logo_circle.png")).convert("RGBA").resize((110*S,110*S),Image.LANCZOS)
        base.alpha_composite(logo,(W-130*S,H-130*S))
    except Exception: pass
    rgb=base.convert("RGB")
    p4=os.path.join(OUT,f"thumb_{lang}_4k.jpg"); rgb.save(p4,quality=93); print("saved",p4,rgb.size)
    yt=rgb.resize((1280,720),Image.LANCZOS); pyt=os.path.join(OUT,f"thumb_{lang}_yt.jpg"); yt.save(pyt,quality=92); print("saved",pyt,"(YT 1280x720)")

build("ko"); build("en")
print("DONE")
