# -*- coding: utf-8 -*-
"""최면 쇼츠 (16:9 클립 '적당히' 크롭 → 9:16, 자막 아래로). KO/EN.
나레이션: _ko_sunhi/NN_11.mp3 · _en_emma/NN_11.mp3 (Azure 선희/Emma, 이미 1.1x).
사용: python hypnosis_science/make_hypnosis_short.py <ko|en>"""
import os, re, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, CompositeAudioClip
from moviepy.video.fx import MultiplySpeed as VideoMultiplySpeed

ROOT = "D:/Entertainments/DevEnvironment/autovideo"
HS = os.path.join(ROOT, "hypnosis_science")
LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
MALGUN = r"C:\Windows\Fonts\malgunbd.ttf"; ARIALBD = r"C:\Windows\Fonts\arialbd.ttf"
FONT = MALGUN if LANG == "ko" else ARIALBD
W, H = 1080, 1920
BG = (14, 12, 24)                     # 최면 분위기 어두운 남보라
SCENES = [2, 14, 15]                  # 훅(오해)→반전(통증↓)→마무리(의료활용)
CROP_X = {2: 100, 14: 100, 15: 100}
VID_W, VID_H = 1080, 720
VIDEO_Y = 360
SUB_Y = 1500
ADIR = os.path.join(HS, "_ko_sunhi") if LANG == "ko" else os.path.join(HS, "_en_emma")
TITLE = {"ko": "최면, 진짜\n과학일까?", "en": "Is Hypnosis\nReal Science?"}[LANG]

# 씬 텍스트(자막) = 시나리오에서
scenes = {}; cur = None
for line in open(os.path.join(HS, "scenario.txt"), encoding="utf-8"):
    s = line.strip(); m = re.match(r"\[Scene (\d+)\]", s)
    if m: cur = int(m.group(1)); scenes[cur] = {}
    elif s.startswith("text_en:") and cur: scenes[cur]["en"] = s[8:].strip()
    elif s.startswith("text:") and cur: scenes[cur]["ko"] = s[5:].strip()

def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True).stdout.strip())
    except Exception: return 0.0
def wrap(txt, font, maxw, d):
    words = txt.split(" "); lines = []; cur = ""
    for w in words:
        t = (cur+" "+w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines
def text_png(txt, size, fill, maxw, sw=5):
    font = ImageFont.truetype(FONT, size); tmp = ImageDraw.Draw(Image.new("RGBA",(4,4)))
    lines = []
    for seg in txt.split("\n"): lines += wrap(seg, font, maxw, tmp)
    asc, desc = font.getmetrics(); lh = asc+desc+8
    im = Image.new("RGBA", (maxw+60, lh*len(lines)+30), (0,0,0,0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        lw = d.textlength(l, font=font); x = (im.width-lw)/2; y = 15+i*lh
        d.text((x,y), l, font=font, fill=fill, stroke_width=sw, stroke_fill=(8,6,14,255))
    return im
def logo_clip(dur_):
    try:
        lg = Image.open(os.path.join(ROOT,"assets","drjay_ed_logo_circle.png")).convert("RGBA").resize((110,110),Image.LANCZOS)
        return ImageClip(np.array(lg), transparent=True).with_duration(dur_)
    except Exception: return None

segs = []; auds = []; t = 0.0
for sc in SCENES:
    ap = os.path.join(ADIR, f"{sc:02d}_11.mp3")
    ac = AudioFileClip(ap) if os.path.exists(ap) else None
    seglen = ac.duration if ac else 6.0
    v = VideoFileClip(os.path.join(HS, f"scene_{sc}.mp4")).without_audio()
    if v.w != 1280 or v.h != 720: v = v.resized(new_size=(1280,720))
    cx = CROP_X.get(sc, 100)
    v = v.cropped(x1=cx, y1=0, width=VID_W, height=VID_H)
    v = v.with_effects([VideoMultiplySpeed(v.duration/seglen)]).with_position((0, VIDEO_Y))
    layers = [v]
    lg = logo_clip(seglen)
    if lg is not None:
        layers.append(lg.with_position((1727-1080//2 if False else 900, VIDEO_Y+597-55)))  # 워터마크 근처 우하단
    ti = text_png(TITLE, 66, (230,220,255,255), W-120, sw=6)
    layers.append(ImageClip(np.array(ti)).with_duration(seglen).with_position(("center",120)))
    ci = text_png(scenes[sc][LANG], 50, (255,235,140,255), W-120, sw=5)
    layers.append(ImageClip(np.array(ci)).with_duration(seglen).with_position(("center", SUB_Y - ci.size[1]//2)))
    comp = CompositeVideoClip(layers, size=(W,H), bg_color=BG).with_duration(seglen).with_start(t)
    segs.append(comp)
    if ac: auds.append(ac.with_start(t))
    t += seglen

final = CompositeVideoClip(segs, size=(W,H), bg_color=BG).with_duration(t)
if auds: final = final.with_audio(CompositeAudioClip(auds))
out = os.path.join(HS, f"hypnosis_short_{LANG}.mp4")
tmpa = os.path.join(HS, f"_short_{LANG}.m4a")
final.write_videofile(out, fps=30, codec="libx264", audio_codec="aac", preset="medium", threads=4, temp_audiofile=tmpa, remove_temp=True)
print("SHORT DONE:", out, f"{final.duration:.1f}s")
final.close()
for s in segs:
    try: s.close()
    except Exception: pass
