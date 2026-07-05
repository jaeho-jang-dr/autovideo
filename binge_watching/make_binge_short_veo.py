# -*- coding: utf-8 -*-
"""정주행 쇼츠 — Veo 9:16 네이티브 모션 클립(shorts_src/scene_X.mp4) 기반 빌더.
그린 배경 + 제목 + 중앙 세로 모션 클립 + 자막 + 로고(✦워터마크 덮기).
역공학 화이트보드 스타일. 사용: python binge_watching/make_binge_short_veo.py <ko|en>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (VideoFileClip, AudioFileClip, ImageClip,
                     CompositeVideoClip, concatenate_videoclips)

CG = "binge_watching"; SRC = "shorts_src"
LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
ADIR = f"{CG}/_ko_sunhi" if LANG == "ko" else f"{CG}/_en_emma"
SRT = f"{CG}/binge_watching.{LANG}.srt"
MALGUN = r"C:\Windows\Fonts\malgunbd.ttf"; ARIALBD = r"C:\Windows\Fonts\arialbd.ttf"
FONT = MALGUN if LANG == "ko" else ARIALBD

W, H = 1080, 1920
BG = (212, 230, 213); TITLE_COL = (22, 34, 26); CAP_COL = (28, 66, 42)
TITLE = {"ko": "밤샘 정주행\n내 몸엔 무슨 일이?", "en": "Binge-Watching\n& Your Body"}[LANG]
BEATS = [0, 2, 20]

# 세로 클립 배치 (9:16 720x1280 → 카드)
CH = 1330; CW = round(CH * 720 / 1280)       # 748x1330
CX = (W - CW) // 2; CY = 296; PAD = 10

def parse(p):
    out = []
    for blk in open(p, encoding="utf-8").read().strip().split("\n\n"):
        L = blk.strip().split("\n")
        if len(L) >= 3: out.append(" ".join(L[2:]))
    return out
cues = parse(SRT)

def wrap(txt, font, maxw, d):
    words = txt.split(" "); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def text_block(txt, size, fill, maxw):
    font = ImageFont.truetype(FONT, size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    lines = []
    for seg in txt.split("\n"): lines += wrap(seg, font, maxw, tmp)
    asc, desc = font.getmetrics(); lh = asc + desc + 14
    im = Image.new("RGBA", (maxw + 20, lh*len(lines) + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        lw = d.textlength(l, font=font); x = (im.width - lw)/2; y = 10 + i*lh
        d.text((x, y), l, font=font, fill=fill)
    return im

LOGO_SZ = 132
try:
    LG = Image.open("assets/drjay_ed_logo_circle.png").convert("RGBA").resize((LOGO_SZ, LOGO_SZ), Image.LANCZOS)
except Exception:
    LG = None

# ✦ Veo 워터마크(9:16 클립) 실측 위치 = 가로 0.817·세로 0.900 → 로고 중심을 거기에 맞춰 덮음
WM_X = CX + round(0.817 * CW) - LOGO_SZ // 2
WM_Y = CY + round(0.900 * CH) - LOGO_SZ // 2

def base_frame(caption):
    cv = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(cv)
    d.rectangle([CX-PAD, CY-PAD, CX+CW+PAD, CY+CH+PAD], fill=(255, 255, 255, 255))  # 카드
    ti = text_block(TITLE, 72, TITLE_COL + (255,), W-150)
    cv.alpha_composite(ti, ((W - ti.width)//2, 86))
    ci = text_block(caption, 50, CAP_COL + (255,), W-120)
    cy = CY + CH + PAD + 34
    if cy + ci.height > H - 40: cy = H - 40 - ci.height
    cv.alpha_composite(ci, ((W - ci.width)//2, cy))
    return np.array(cv.convert("RGB"))

def logo_overlay(dur):
    if LG is None: return None
    return ImageClip(np.array(LG), transparent=True).with_duration(dur).with_position((WM_X, WM_Y))

clips = []
for sc in BEATS:
    ap = os.path.join(ADIR, f"{sc:03d}.mp3")
    ac = AudioFileClip(ap); dur = ac.duration + 0.5
    v = VideoFileClip(f"{SRC}/scene_{sc}.mp4").without_audio()
    end = min(dur, v.duration)
    v = v.subclipped(0, end).resized((CW, CH)).with_position((CX, CY))
    if end < dur: v = v.with_duration(dur)
    layers = [ImageClip(base_frame(cues[sc])).with_duration(dur), v]
    lo = logo_overlay(dur)
    if lo is not None: layers.append(lo)
    comp = CompositeVideoClip(layers, size=(W, H)).with_duration(dur).with_audio(ac.with_start(0.22))
    clips.append(comp)

final = concatenate_videoclips(clips, method="compose")
out = os.path.join(CG, f"binge_short_veo_{LANG}.mp4")
final.write_videofile(out, fps=30, codec="libx264", audio_codec="aac", preset="medium", threads=4)
print("VEO SHORT DONE:", out, f"{final.duration:.1f}s")
final.close()
for c in clips:
    try: c.close()
    except Exception: pass
