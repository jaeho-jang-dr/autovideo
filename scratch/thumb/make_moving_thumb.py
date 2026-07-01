# -*- coding: utf-8 -*-
"""움직이는 썸네일 — 가장 핫한 3클립(S33 얼굴→S15 즉위→S48 축제) 몰아치기 + 타이틀 오버레이. 1080p.
사용: python make_moving_thumb.py ko|en"""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.fx import CrossFadeIn, CrossFadeOut, MultiplySpeed, Resize

ROOT = "D:/Entertainments/DevEnvironment/autovideo"
CLIPS = os.path.join(ROOT, "sejong_main_kf")
MALGUN = r"C:\Windows\Fonts\malgunbd.ttf"; IMPACT = r"C:\Windows\Fonts\impact.ttf"; ARIALBD = r"C:\Windows\Fonts\arialbd.ttf"
W, H = 1920, 1080
LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
SEG = [ (33, 2.4), (15, 2.4), (48, 2.8) ]   # (scene, seconds)
XF = 0.45

def cover(v):
    sc = max(W/v.w, H/v.h); v = v.resized(sc)
    x=(v.w-W)/2; y=(v.h-H)/2
    return v.cropped(x1=x, y1=y, x2=x+W, y2=y+H)

def font(p, s):
    try: return ImageFont.truetype(p, s)
    except Exception: return ImageFont.truetype(MALGUN, s)

def text_img(text, fnt, fill, sw=6, glow=None):
    d0 = ImageDraw.Draw(Image.new("RGBA",(4,4))); bb=d0.textbbox((0,0),text,font=fnt,stroke_width=sw)
    tw,th=bb[2]-bb[0]+60, bb[3]-bb[1]+60
    img=Image.new("RGBA",(tw,th),(0,0,0,0))
    if glow:
        g=Image.new("RGBA",img.size,(0,0,0,0)); ImageDraw.Draw(g).text((30-bb[0],30-bb[1]),text,font=fnt,fill=glow+(255,),stroke_width=sw+2,stroke_fill=glow+(255,)); g=g.filter(ImageFilter.GaussianBlur(12)); img.alpha_composite(g)
    s=Image.new("RGBA",img.size,(0,0,0,0)); ImageDraw.Draw(s).text((34-bb[0],37-bb[1]),text,font=fnt,fill=(0,0,0,220),stroke_width=sw,stroke_fill=(0,0,0,220)); s=s.filter(ImageFilter.GaussianBlur(5)); img.alpha_composite(s)
    ImageDraw.Draw(img).text((30-bb[0],30-bb[1]),text,font=fnt,fill=fill,stroke_width=sw,stroke_fill=(12,16,32,255))
    return img

# --- 3클립 세그먼트(살짝 줌인으로 활기) ---
segs=[]
for i,(n,sec) in enumerate(SEG):
    v = VideoFileClip(os.path.join(CLIPS, f"scene_{n}.mp4")).without_audio()
    v = cover(v)
    if v.duration < sec:  # 8초 클립이라 충분하지만 안전
        v = v.with_effects([MultiplySpeed(v.duration/sec)])
    v = v.subclipped(0, sec)
    v = v.with_effects([Resize(lambda t: 1.0 + 0.045*t)])   # 은은한 줌인
    if i>0: v = v.with_effects([CrossFadeIn(XF)])
    segs.append(v)
seq = concatenate_videoclips(segs, method="compose", padding=-XF)
total = seq.duration

# --- 하단 타이틀 밴드 + 글자 ---
band = Image.new("RGBA",(W,H),(0,0,0,0))
bd = ImageDraw.Draw(band)
for y in range(H):
    a = int(200*max(0,(y-H*0.60)/(H*0.40)))
    bd.line([(0,y),(W,y)], fill=(0,0,0,a))
band_clip = ImageClip(np.array(band)).with_duration(total)

GOLD=(255,208,74,255); WHITE=(255,255,255,255)
if LANG=="ko":
    t1=text_img("세종대왕과 한글", font(MALGUN,96), GOLD, sw=7, glow=(255,150,30))
    t2=text_img("한글은 어떻게 태어났을까?", font(MALGUN,46), WHITE, sw=5)
else:
    t1=text_img("KING SEJONG & HANGEUL", font(IMPACT,86), GOLD, sw=6, glow=(255,150,30))
    t2=text_img("How an Alphabet Was Born", font(ARIALBD,44), WHITE, sw=5)
c1=ImageClip(np.array(t1)).with_duration(total).with_position(("center", H-260)).with_effects([CrossFadeIn(0.3)])
c2=ImageClip(np.array(t2)).with_duration(total).with_position(("center", H-150)).with_effects([CrossFadeIn(0.5)])

layers=[seq, band_clip, c1, c2]
try:
    logo=Image.open(os.path.join(ROOT,"assets","drjay_ed_logo_circle.png")).convert("RGBA").resize((120,120),Image.LANCZOS)
    layers.append(ImageClip(np.array(logo)).with_duration(total).with_position((W-150, 40)))
except Exception: pass

final=CompositeVideoClip(layers, size=(W,H)).with_duration(total).with_effects([CrossFadeIn(0.3), CrossFadeOut(0.4)])
out=os.path.join(ROOT,"scratch","thumb",f"thumb_moving_{LANG}.mp4")
final.write_videofile(out, fps=30, codec="libx264", audio=False, preset="veryfast", threads=2, logger=None)
print("DONE:", out, f"{final.duration:.1f}s")
