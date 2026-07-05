# -*- coding: utf-8 -*-
"""정주행 쇼츠 — 플랫 레이어드 + 기존 Veo 모션 클립(정지 아님) 9:16 빌더.
그린 배경 + 제목 + 중앙 모션 클립(scene_X.mp4, 자연속도 트림) + 자막 + 로고.
새 Flow 생성 없음(이미 생성된 씬 클립 재사용). 사용: python binge_watching/make_binge_short_motion.py <ko|en>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (VideoFileClip, AudioFileClip, ImageClip,
                     CompositeVideoClip, concatenate_videoclips)

CG = "binge_watching"
LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
ADIR = f"{CG}/_ko_sunhi" if LANG == "ko" else f"{CG}/_en_emma"
SRT = f"{CG}/binge_watching.{LANG}.srt"
MALGUN = r"C:\Windows\Fonts\malgunbd.ttf"; ARIALBD = r"C:\Windows\Fonts\arialbd.ttf"
FONT = MALGUN if LANG == "ko" else ARIALBD

W, H = 1080, 1920
BG = (212, 230, 213)
TITLE_COL = (22, 34, 26); CAP_COL = (28, 66, 42)
TITLE = {"ko": "밤샘 정주행\n내 몸엔 무슨 일이?", "en": "Binge-Watching\n& Your Body"}[LANG]

# 비트: 씬번호(=오디오/자막 인덱스 = scene_X.mp4 모션클립)
BEATS = [0, 2, 20]

# 중앙 모션 클립 배치(16:9)
CW = 1000; CH = int(CW * 720 / 1280)         # 1000x562
CX = (W - CW) // 2; CY = 604; PAD = 14

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

try:
    LG = Image.open("assets/drjay_ed_logo_circle.png").convert("RGBA").resize((124, 124), Image.LANCZOS)
except Exception:
    LG = None

def base_frame(caption):
    """정지 배경: 그린 + 흰 카드(클립자리) + 제목 + 자막 + 로고"""
    cv = Image.new("RGBA", (W, H), BG + (255,))
    d = ImageDraw.Draw(cv)
    d.rectangle([CX-PAD, CY-PAD, CX+CW+PAD, CY+CH+PAD], fill=(255, 255, 255, 255))
    ti = text_block(TITLE, 74, TITLE_COL + (255,), W-160)
    cv.alpha_composite(ti, ((W - ti.width)//2, 96))
    ci = text_block(caption, 52, CAP_COL + (255,), W-140)
    cy = CY + CH + PAD + 46
    cv.alpha_composite(ci, ((W - ci.width)//2, cy))
    if LG is not None:
        cv.alpha_composite(LG, ((W - LG.width)//2, H - 178))
    return np.array(cv.convert("RGB"))

clips = []
for sc in BEATS:
    ap = os.path.join(ADIR, f"{sc:03d}.mp3")
    ac = AudioFileClip(ap)
    dur = ac.duration + 0.5
    # 모션 클립: 자연속도로 beat 길이만큼 트림(초과 시 가용범위)
    v = VideoFileClip(f"{CG}/scene_{sc}.mp4").without_audio()
    end = min(dur, v.duration)
    v = v.subclipped(0, end).resized((CW, CH)).with_position((CX, CY))
    if end < dur:  # 클립이 짧으면 마지막 프레임 홀드
        v = v.with_duration(dur)
    bg = ImageClip(base_frame(cues[sc])).with_duration(dur)
    comp = CompositeVideoClip([bg, v], size=(W, H)).with_duration(dur).with_audio(ac.with_start(0.22))
    clips.append(comp)

final = concatenate_videoclips(clips, method="compose")
out = os.path.join(CG, f"binge_short_motion_{LANG}.mp4")
final.write_videofile(out, fps=30, codec="libx264", audio_codec="aac", preset="medium", threads=4)
print("MOTION SHORT DONE:", out, f"{final.duration:.1f}s")
final.close()
for c in clips:
    try: c.close()
    except Exception: pass
