# -*- coding: utf-8 -*-
"""정주행 쇼츠 — 플랫 레이어드(그린 배경 + 클린 두들 + 제목 + 자막 + 로고) 9:16 빌더.
승인 디자인(shorts_preview_ko.png) 재현. 3비트: 씬0(couch+TV)·씬2(빛나는TV)·씬20(별먹는뇌).
사용: python binge_watching/make_binge_short_flat.py <ko|en>"""
import os, re, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip, ImageClip, concatenate_videoclips

CG = "binge_watching"
LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
ADIR = f"{CG}/_ko_sunhi" if LANG == "ko" else f"{CG}/_en_emma"
SRT = f"{CG}/binge_watching.{LANG}.srt"
MALGUN = r"C:\Windows\Fonts\malgunbd.ttf"; ARIALBD = r"C:\Windows\Fonts\arialbd.ttf"
FONT = MALGUN if LANG == "ko" else ARIALBD

W, H = 1080, 1920
BG = (212, 230, 213)                 # 프리뷰 파스텔 그린
TITLE_COL = (22, 34, 26)             # 진한 먹색
CAP_COL = (28, 66, 42)               # 진한 초록먹
TITLE = {"ko": "밤샘 정주행\n내 몸엔 무슨 일이?", "en": "Binge-Watching\n& Your Body"}[LANG]

# 비트: (씬번호=오디오/자막 인덱스, 두들 이미지)
BEATS = [
    (0,  f"{CG}/Whiteboard_doodle__couch_and_TV_202607021959.jpeg"),
    (2,  f"{CG}/Couch_facing_glowing_TV_202607022044.jpeg"),
    (20, f"{CG}/Brain_eating_shining_stars_202607022004.jpeg"),
]

def parse(p):
    out = []
    for blk in open(p, encoding="utf-8").read().strip().split("\n\n"):
        L = blk.strip().split("\n")
        if len(L) < 3: continue
        out.append(" ".join(L[2:]))
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

def text_block(txt, size, fill, maxw, sw=0, stroke=(255,255,255)):
    """중앙정렬 다행 텍스트 → RGBA PNG"""
    font = ImageFont.truetype(FONT, size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    lines = []
    for seg in txt.split("\n"): lines += wrap(seg, font, maxw, tmp)
    asc, desc = font.getmetrics(); lh = asc + desc + 14
    im = Image.new("RGBA", (maxw + 2*sw + 20, lh*len(lines) + 2*sw + 20), (0,0,0,0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        lw = d.textlength(l, font=font); x = (im.width - lw)/2; y = 10 + sw + i*lh
        d.text((x, y), l, font=font, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return im

def logo():
    try:
        return Image.open("assets/drjay_ed_logo_circle.png").convert("RGBA").resize((124,124), Image.LANCZOS)
    except Exception:
        return None
LG = logo()

def build_frame(doodle_path, caption):
    canvas = Image.new("RGB", (W, H), BG)
    # 두들 (흰 배경 카드 그대로, 상단-중앙)
    dood = Image.open(doodle_path).convert("RGB")
    dh = 980; dw = int(dood.width * dh / dood.height)
    if dw > W-120: dw = W-120; dh = int(dood.height * dw / dood.width)
    dood = dood.resize((dw, dh), Image.LANCZOS)
    dx = (W - dw)//2; dy = 372
    # 살짝 흰 카드 테두리로 깔끔하게
    pad = 16
    card = Image.new("RGB", (dw+2*pad, dh+2*pad), (255,255,255))
    canvas.paste(card, (dx-pad, dy-pad))
    canvas.paste(dood, (dx, dy))
    canvas = canvas.convert("RGBA")
    # 제목 (상단)
    ti = text_block(TITLE, 74, TITLE_COL + (255,), W-160, sw=0)
    canvas.alpha_composite(ti, ((W - ti.width)//2, 96))
    # 자막 (하단)
    ci = text_block(caption, 52, CAP_COL + (255,), W-140, sw=0)
    cy = dy + dh + pad + 44
    if cy + ci.height > H - 210: cy = H - 210 - ci.height
    canvas.alpha_composite(ci, ((W - ci.width)//2, cy))
    # 로고 (하단 중앙)
    if LG is not None:
        canvas.alpha_composite(LG, ((W - LG.width)//2, H - 176))
    return np.array(canvas.convert("RGB"))

clips = []
for sc, dpath in BEATS:
    ap = os.path.join(ADIR, f"{sc:03d}.mp3")
    ac = AudioFileClip(ap)
    dur = ac.duration + 0.45          # 앞뒤 여유
    frame = build_frame(dpath, cues[sc])
    clip = ImageClip(frame).with_duration(dur).with_audio(ac.with_start(0.20))
    clips.append(clip)

final = concatenate_videoclips(clips, method="compose")
out = os.path.join(CG, f"binge_short_flat_{LANG}.mp4")
final.write_videofile(out, fps=30, codec="libx264", audio_codec="aac",
                      preset="medium", threads=4)
print("FLAT SHORT DONE:", out, f"{final.duration:.1f}s")
final.close()
for c in clips:
    try: c.close()
    except Exception: pass
