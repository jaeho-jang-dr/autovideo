# -*- coding: utf-8 -*-
"""정주행 쇼츠 (기존 16:9 클립 '적당히' 크롭 → 9:16, 아래 빈칸에 자막 내림).
- 과한 크롭 금지: 1280x720 → 1080x720 픽셀단위 크롭(업스케일 없음=화질보존).
- 아래쪽은 배경 여백, 자막을 그 여백(아래)으로 내림. 상단 제목.
- 나레이션: _ko_sunhi / _en_emma (Azure 선희/엠마) 1.1x.
사용: python binge_watching/make_binge_short_crop.py <ko|en>"""
import os, re, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, CompositeAudioClip
from moviepy.video.fx import MultiplySpeed as VideoMultiplySpeed

CG = "binge_watching"
ROOT = "."
LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
ADIR = f"{CG}/_ko_sunhi" if LANG == "ko" else f"{CG}/_en_emma"
SRT = f"{CG}/binge_watching.{LANG}.srt"
MALGUN = r"C:\Windows\Fonts\malgunbd.ttf"; ARIALBD = r"C:\Windows\Fonts\arialbd.ttf"
FONT = MALGUN if LANG == "ko" else ARIALBD

W, H = 1080, 1920                 # 9:16 (720p 원본 보존 위해 4K 대신 1080)
BG = (18, 22, 28)                 # 어두운 차콜 배경 (여백)
SCENES = [0, 2, 20]
# 16:9(1280x720) → 1080x720 크롭 시작 x (씬별): 하품(2)은 얼굴이 왼쪽 → 왼쪽정렬, 나머지 중앙
CROP_X = {0: 100, 2: 0, 20: 100}
VID_W, VID_H = 1080, 720
VIDEO_Y = 360                     # 영상 상단 y (제목 아래)
TITLE = {"ko": "밤샘 정주행\n내 몸엔 무슨 일이?", "en": "Binge-Watching\n& Your Body"}[LANG]
SUB_Y = 1500                      # 자막 세로 중심(아래로 내림)

def parse(p):
    out = []
    for blk in open(p, encoding="utf-8").read().strip().split("\n\n"):
        L = blk.strip().split("\n")
        if len(L) < 3: continue
        m = re.match(r"(\d+):(\d+):([\d,\.]+) --> (\d+):(\d+):([\d,\.]+)", L[1])
        f = lambda h, mi, se: int(h)*3600+int(mi)*60+float(se.replace(",", "."))
        out.append((f(m[1], m[2], m[3]), f(m[4], m[5], m[6]), " ".join(L[2:])))
    return out
cues = parse(SRT)

def sped_audio(src, factor, dst):
    """ffmpeg atempo로 1.1배속 나레이션 생성 후 경로 반환."""
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-filter:a", f"atempo={factor}",
                    "-c:a", "libmp3lame", "-q:a", "2", dst], check=True)
    return dst

def wrap(txt, font, maxw, d):
    words = txt.split(" "); lines = []; cur = ""
    for w in words:
        t = (cur+" "+w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def text_png(txt, size, fill, maxw, sw=5):
    """박스 없이 글자만 (외곽선 스트로크로 가독성 확보)."""
    font = ImageFont.truetype(FONT, size); tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    lines = []
    for seg in txt.split("\n"): lines += wrap(seg, font, maxw, tmp)
    asc, desc = font.getmetrics(); lh = asc+desc+8
    im = Image.new("RGBA", (maxw+60, lh*len(lines)+30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        lw = d.textlength(l, font=font); x = (im.width-lw)/2; y = 15+i*lh
        d.text((x, y), l, font=font, fill=fill, stroke_width=sw, stroke_fill=(10, 12, 16, 255))
    return im

def logo_clip(dur):
    try:
        lg = Image.open(os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")).convert("RGBA").resize((110, 110), Image.LANCZOS)
        return ImageClip(np.array(lg), transparent=True).with_duration(dur)
    except Exception:
        return None

segs = []; auds = []; t = 0.0
for sc in SCENES:
    sc_path = os.path.join(CG, f"scene_{sc}.mp4")
    st, ed, txt = cues[sc]
    ap = os.path.join(ADIR, f"{sc:03d}.mp3")
    if os.path.exists(ap):
        sp = os.path.join("scratch", f"binge_crop_{LANG}_{sc:03d}.mp3")
        os.makedirs("scratch", exist_ok=True)
        sped_audio(ap, 1.1, sp)
        ac = AudioFileClip(sp)
        seglen = ac.duration
    else:
        ac = None; seglen = (ed-st)/1.1

    # 영상: 1280x720 → 1080x720 크롭(픽셀단위, 업스케일 없음)
    v = VideoFileClip(sc_path).without_audio()
    if v.w != 1280 or v.h != 720:
        v = v.resized(new_size=(1280, 720))
    cx = CROP_X.get(sc, 100)
    v = v.cropped(x1=cx, y1=0, width=VID_W, height=VID_H)
    # 나레이션 길이에 맞춰 속도 동기화
    v = v.with_effects([VideoMultiplySpeed(v.duration/seglen)])
    v = v.with_position((0, VIDEO_Y))

    layers = [v]
    # 워터마크(✦, 1151,597@1280) 덮기 겸 로고 — 중앙크롭(cx=100)일 때만 프레임 안에 있음
    lg = logo_clip(seglen)
    if lg is not None:
        wm_x = 1151 - cx - 55; wm_y = VIDEO_Y + 597 - 55
        wm_x = max(0, min(W-110, wm_x))
        layers.append(lg.with_position((wm_x, wm_y)))
    # 제목(상단)
    ti = text_png(TITLE, 66, (255, 255, 255, 255), W-120, sw=6)
    layers.append(ImageClip(np.array(ti)).with_duration(seglen).with_position(("center", 120)))
    # 자막(아래 여백으로 내림)
    ci = text_png(txt, 52, (255, 230, 120, 255), W-120, sw=5)
    layers.append(ImageClip(np.array(ci)).with_duration(seglen).with_position(("center", SUB_Y - ci.size[1]//2)))

    comp = CompositeVideoClip(layers, size=(W, H), bg_color=BG).with_duration(seglen).with_start(t)
    segs.append(comp)
    if ac: auds.append(ac.with_start(t))
    t += seglen

final = CompositeVideoClip(segs, size=(W, H), bg_color=BG).with_duration(t)
temp_audio = f"{CG}/temp_crop_{LANG}.m4a"
if auds: final = final.with_audio(CompositeAudioClip(auds))
out = os.path.join(CG, f"binge_short_crop_{LANG}.mp4")
final.write_videofile(out, fps=30, codec="libx264", audio_codec="aac", preset="medium",
                      threads=4, temp_audiofile=temp_audio, remove_temp=True)
print("SHORT DONE:", out, f"{final.duration:.1f}s")
final.close()
for s in segs:
    try: s.close()
    except Exception: pass
