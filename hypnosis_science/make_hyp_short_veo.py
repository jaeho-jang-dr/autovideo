# -*- coding: utf-8 -*-
"""최면 쇼츠 — Veo 9:16 카툰 모션클립(hyp_short/scene_X.mp4) 풀프레임 합성 (한/영).
풀프레임 클립 + 제목(외곽선) + 자막(반투명 밴드) + 로고(✦워터마크 덮기).
사용: python hypnosis_science/make_hyp_short_veo.py <ko|en>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (VideoFileClip, AudioFileClip, ImageClip,
                     CompositeVideoClip, concatenate_videoclips)

HS = "hypnosis_science"; SRC = "hyp_short"
LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
ADIR = f"{HS}/_ko_sunhi" if LANG == "ko" else f"{HS}/_en_emma"
SRT = f"{HS}/hypnosis_science.{LANG}.srt"
MALGUN = r"C:\Windows\Fonts\malgunbd.ttf"; ARIALBD = r"C:\Windows\Fonts\arialbd.ttf"
FONT = MALGUN if LANG == "ko" else ARIALBD

W, H = 1080, 1920
TITLE = {"ko": "최면, 마술일까\n과학일까?", "en": "Hypnosis:\nMagic or Science?"}[LANG]
# 비트: (scene번호=hyp_short/scene_N.mp4, 나레이션 02d_11.mp3, 자막 srt cue index)
BEATS = [(2, 0), (13, 11), (15, 13)]

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

def text_img(txt, size, fill, maxw, sw, stroke):
    font = ImageFont.truetype(FONT, size)
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    lines = []
    for seg in txt.split("\n"): lines += wrap(seg, font, maxw, tmp)
    asc, desc = font.getmetrics(); lh = asc + desc + 16
    im = Image.new("RGBA", (maxw + 2*sw + 20, lh*len(lines) + 2*sw + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        lw = d.textlength(l, font=font); x = (im.width - lw)/2; y = 10 + sw + i*lh
        d.text((x, y), l, font=font, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return im

LOGO_SZ = 128
try:
    LG = Image.open("assets/drjay_ed_logo_circle.png").convert("RGBA").resize((LOGO_SZ, LOGO_SZ), Image.LANCZOS)
except Exception:
    LG = None
WM_X = round(0.817 * W) - LOGO_SZ // 2   # 풀프레임 기준 ✦ 워터마크 위치
WM_Y = round(0.900 * H) - LOGO_SZ // 2

def overlay_frame(caption):
    """제목(상단 외곽선) + 자막(하단 반투명 밴드) + 로고 → 투명 오버레이 PNG"""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # 제목 (상단, 흰색 큰 글씨 + 진한 외곽선)
    ti = text_img(TITLE, 82, (255, 255, 255, 255), W-140, sw=10, stroke=(20, 20, 40, 255))
    ov.alpha_composite(ti, ((W - ti.width)//2, 70))
    # 자막 밴드 (하단 반투명)
    ci = text_img(caption, 50, (255, 255, 255, 255), W-150, sw=6, stroke=(15, 15, 30, 255))
    band_h = ci.height + 60
    # 짧은 자막은 하단(-150), 긴 자막(4줄+)은 로고 위로 올려 ✦워터마크 로고와 충돌 방지
    band_y = min(H - band_h - 150, WM_Y - 12 - band_h)
    band = Image.new("RGBA", (W, band_h), (10, 12, 24, 165))
    ov.alpha_composite(band, (0, band_y))
    ov.alpha_composite(ci, ((W - ci.width)//2, band_y + 30))
    # 로고 (워터마크 덮기)
    if LG is not None:
        ov.alpha_composite(LG, (WM_X, WM_Y))
    return np.array(ov)

clips = []
for sc, cue in BEATS:
    ap = os.path.join(ADIR, f"{sc:02d}_11.mp3")
    ac = AudioFileClip(ap); dur = ac.duration + 0.5
    v = VideoFileClip(f"{SRC}/scene_{sc}.mp4").without_audio()
    end = min(dur, v.duration)
    v = v.subclipped(0, end).resized((W, H))
    if end < dur: v = v.with_duration(dur)
    ov = ImageClip(overlay_frame(cues[cue]), transparent=True).with_duration(dur)
    comp = CompositeVideoClip([v, ov], size=(W, H)).with_duration(dur).with_audio(ac.with_start(0.22))
    clips.append(comp)

final = concatenate_videoclips(clips, method="compose")
out = os.path.join(HS, f"hyp_short_veo_{LANG}.mp4")
final.write_videofile(out, fps=30, codec="libx264", audio_codec="aac", preset="medium", threads=4)
print("HYP SHORT DONE:", out, f"{final.duration:.1f}s")
final.close()
for c in clips:
    try: c.close()
    except Exception: pass
