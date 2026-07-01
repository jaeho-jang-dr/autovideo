# -*- coding: utf-8 -*-
"""세종대왕과 한글 — 본편(16:9) 컴포지터.
37장면을 10개 anchor 모션클립에 매핑 → 장면별 클립(나레이션 길이에 맞춰 미세 슬로우) +
자막(한/영, 박스X) + 로고(우하단=Veo 워터마크 덮기) + 과학장면(27~30) 정확한 자모 오버레이.
moviepy 2.x.  사용: python compile_main.py ko|en"""
import os, re, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import (ImageClip, VideoFileClip, AudioFileClip, CompositeVideoClip,
                     concatenate_videoclips)
from moviepy.video.fx import FadeIn, MultiplySpeed, CrossFadeIn

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
SF = os.path.join(ROOT, "sejong_film")
MAIN = os.path.join(SF, "main")
CLIPS = os.path.join(ROOT, "sejong_main")             # scene_1..10.mp4
AUD = os.path.join(MAIN, "audio")
LOGO = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
MALGUN = r"C:\Windows\Fonts\malgunbd.ttf"
W, H = 1920, 1080
LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"

GOLD = (245, 200, 75, 255); WHITE = (255, 255, 255, 255)

# 기본 이미지(클립 없을 때 폴백 스틸)
BASE = {1: "m01_gwanghwamun", 2: "m02_child_read", 3: "m03_child_book", 4: "m04_youth_study",
        5: "m05_throne", 6: "m06_jiphyeonjeon", 7: "m07_people", 8: "m08_seogga_night",
        9: "m09_secret", 10: "m10_old_legacy"}

# 장면(1~37) → anchor 클립
SCENE_CLIP = {1:2,2:2,3:2,4:3,5:2, 6:4,7:4,8:4,9:4,10:4,
              11:5,12:6,13:6,14:7,15:7,16:5,
              17:8,18:8,19:8,20:8,21:8,22:6,23:6,24:6,25:8,26:8,
              27:9,28:9,29:9,30:9,31:10,
              32:10,33:10,34:10,35:10,36:10,37:10}

# 과학장면 자모 오버레이 (정확한 한글, AI 아님)
SCI_JAMO = {27: ["ㄱ", "ㄴ", "ㅁ"], 28: ["ㄴ", "ㄷ", "ㅌ"], 29: ["ㆍ", "ㅡ", "ㅣ"], 30: ["ㅏ", "ㅓ", "ㅗ", "ㅜ"]}

TITLE = {"ko": ("세종대왕과 한글", "한글은 어떻게 태어났을까?"),
         "en": ("King Sejong & Hangeul", "How were the letters born?")}

# ---------- 텍스트 ----------
def _wrap(text, font, maxw):
    words = text.split(" "); lines = []; cur = ""
    dummy = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    for w in words:
        t = (cur + " " + w).strip()
        if dummy.textlength(t, font=font) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def text_img(text, size, fill, sw=6, shadow=True, glow=None, maxw=None):
    font = ImageFont.truetype(MALGUN, size)
    lines = _wrap(text, font, maxw) if maxw else [text]
    asc, desc = font.getmetrics(); lh = asc + desc + 8
    dummy = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    tw = max(dummy.textlength(l, font=font) for l in lines)
    pad = sw + (40 if glow else 26)
    img = Image.new("RGBA", (int(tw) + pad * 2, lh * len(lines) + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    def draw_all(dd, ox, oy, col, scol):
        for i, l in enumerate(lines):
            lw = dd.textlength(l, font=font); x = (img.width - lw) / 2 + ox; y = pad + i * lh + oy
            dd.text((x, y), l, font=font, fill=col, stroke_width=sw, stroke_fill=scol)
    if glow:
        g = Image.new("RGBA", img.size, (0, 0, 0, 0)); dg = ImageDraw.Draw(g)
        draw_all(dg, 0, 0, glow + (255,), glow + (255,)); g = g.filter(ImageFilter.GaussianBlur(16))
        img = Image.alpha_composite(img, g); img = Image.alpha_composite(img, g); d = ImageDraw.Draw(img)
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
        draw_all(ds, 4, 6, (0, 0, 0, 200), (0, 0, 0, 200)); sh = sh.filter(ImageFilter.GaussianBlur(6))
        img = Image.alpha_composite(img, sh); d = ImageDraw.Draw(img)
    draw_all(d, 0, 0, fill, (20, 25, 45, 255))
    return img

def pil_clip(img, dur):
    return ImageClip(np.array(img.convert("RGBA")), transparent=True).with_duration(dur)

def cover_fit(clip):
    sc = max(W / clip.w, H / clip.h); clip = clip.resized(sc)
    x = (clip.w - W) / 2; y = (clip.h - H) / 2
    return clip.cropped(x1=x, y1=y, x2=x + W, y2=y + H)

# ---------- 시나리오 파싱 ----------
ko, en = {}, {}; cur = None
for line in open(os.path.join(SF, "sejong_scenario_light.md"), encoding="utf-8"):
    m = re.match(r"^\s*(\d+)\.\s+KO\s+(.*)$", line)
    if m: cur = int(m.group(1)); ko[cur] = m.group(2).strip(); continue
    m2 = re.match(r"^\s*EN\s+(.*)$", line)
    if m2 and cur is not None: en[cur] = m2.group(1).strip()
CAP = ko if LANG == "ko" else en
SCENES = sorted(ko)

logo = Image.open(LOGO).convert("RGBA").resize((110, 110), Image.LANCZOS)
LOGO_POS = (W - 110 - 40, H - 110 - 34)

def scene_visual(n, dur):
    c = SCENE_CLIP[n]; p = os.path.join(CLIPS, f"scene_{c}.mp4")
    if os.path.exists(p):
        v = cover_fit(VideoFileClip(p).without_audio())
        speed = v.duration / dur
        return v.with_effects([MultiplySpeed(speed)]).subclipped(0, dur)
    # 폴백: 기본 이미지 스틸
    im = Image.open(os.path.join(MAIN, BASE[c] + ".png")).convert("RGB")
    return cover_fit(ImageClip(np.array(im)).with_duration(dur))

def caption_layer(n, dur):
    cap = text_img(CAP[n], 50, WHITE, sw=5, shadow=True, maxw=W - 320)
    return pil_clip(cap, dur).with_position(("center", H - cap.height - 70)).with_effects([CrossFadeIn(0.3)])

def jamo_layer(n, dur):
    out = []
    js = SCI_JAMO.get(n)
    if not js: return out
    nn = len(js); span = 220
    for k, j in enumerate(js):
        ji = text_img(j, 200, GOLD, glow=(255, 210, 90), shadow=False)
        x = int(W * 0.5 - (nn * span) / 2 + k * span + (span - ji.width) / 2)
        st = 0.3 + k * 0.5
        c = (pil_clip(ji, max(0.1, dur - st)).with_start(st)
             .with_position((x, 250)).with_effects([CrossFadeIn(0.25)]))
        out.append(c)
    return out

def aud(n):
    p = os.path.join(AUD, f"{LANG}_{n:02d}.mp3")
    return AudioFileClip(p) if os.path.exists(p) else None

# ---------- 타이틀 카드 (광화문 clip1) ----------
def title_card():
    d = 4.5; p = os.path.join(CLIPS, "scene_1.mp4")
    if os.path.exists(p):
        v = cover_fit(VideoFileClip(p).without_audio())
        base = v.with_effects([MultiplySpeed(v.duration / d)]).subclipped(0, d)
    else:
        im = Image.open(os.path.join(MAIN, "m01_gwanghwamun.png")).convert("RGB")
        base = cover_fit(ImageClip(np.array(im)).with_duration(d))
    t1, t2 = TITLE[LANG]
    L = [base.with_effects([FadeIn(0.4)])]
    ti = text_img(t1, 120, GOLD, glow=(255, 210, 90), shadow=True, maxw=W - 200)
    L.append(pil_clip(ti, d).with_position(("center", 300)).with_effects([CrossFadeIn(0.5)]))
    sub = text_img(t2, 58, WHITE, sw=5, shadow=True, maxw=W - 300)
    L.append(pil_clip(sub, d).with_position(("center", 470)).with_effects([CrossFadeIn(0.7)]))
    L.append(pil_clip(logo, d).with_position(LOGO_POS))
    return CompositeVideoClip(L, size=(W, H)).with_duration(d)

# ---------- 장면 빌드 ----------
segs = [title_card()]
for n in SCENES:
    a = aud(n); d = (a.duration + 0.45) if a else 3.5
    layers = [scene_visual(n, d)]
    layers += jamo_layer(n, d)
    layers.append(caption_layer(n, d))
    layers.append(pil_clip(logo, d).with_position(LOGO_POS))
    comp = CompositeVideoClip(layers, size=(W, H)).with_duration(d)
    if a: comp = comp.with_audio(a)
    segs.append(comp)

final = concatenate_videoclips(segs, method="compose")
out = os.path.join(MAIN, f"sejong_main_{LANG}.mp4")
final.write_videofile(out, fps=30, codec="libx264", audio_codec="aac", preset="medium", threads=4)
print("DONE:", out, f"{final.duration:.1f}s ({final.duration/60:.1f}분)")
