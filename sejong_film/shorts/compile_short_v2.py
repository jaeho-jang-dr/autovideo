# -*- coding: utf-8 -*-
"""세종 쇼츠 v2 (9:16) — 서가 글쓰기 모션클립 3개 연결 + 머리 주위 불규칙 자모(70%) + 자막/로고/나레이션.
- 배경: Veo 모션 클립(sejong_short/scene_1..3.mp4) 크로스페이드 연결, 은은하게(소프트 베일).
- 자모: 정확한 malgun 한글 자모가 인물 머리 위·주변을 불규칙 경로로 떠다님(70% 반투명).
- 인물은 장면 안에서 중앙 밴드 → 상단 글자/하단 자막과 안 겹침.
moviepy 2.x API."""
import os, sys, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import (ImageClip, VideoFileClip, AudioFileClip, CompositeVideoClip,
                     concatenate_videoclips, concatenate_audioclips)
from moviepy.video.fx import FadeIn, CrossFadeIn, CrossFadeOut, MultiplySpeed

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
SF = os.path.join(ROOT, "sejong_film")
AUD = os.path.join(SF, "shorts", "audio")
CLIPS = os.path.join(ROOT, "sejong_short")           # scene_1..3.mp4
LOGO = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
MALGUN = r"C:\Windows\Fonts\malgunbd.ttf"
W, H = 1080, 1920
LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
random.seed(42)

GOLD = (245, 200, 75, 255)
WHITE = (255, 255, 255, 255)

# ---------- 텍스트 이미지(박스 없이 흰글자+테두리+음영 / 또는 자모 글로우) ----------
def text_img(text, size, fill, stroke=(20, 25, 45), sw=8, glow=None, shadow=False):
    font = ImageFont.truetype(MALGUN, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bb = dummy.textbbox((0, 0), text, font=font, stroke_width=sw)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = sw + (44 if glow else (28 if shadow else 12))
    img = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x, y = pad - bb[0], pad - bb[1]
    if glow:
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dg = ImageDraw.Draw(g)
        dg.text((x, y), text, font=font, fill=glow + (255,))
        g = g.filter(ImageFilter.GaussianBlur(16))
        img = Image.alpha_composite(img, g); img = Image.alpha_composite(img, g)
        d = ImageDraw.Draw(img)
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dsh = ImageDraw.Draw(sh)
        dsh.text((x + 5, y + 7), text, font=font, fill=(0, 0, 0, 200), stroke_width=sw, stroke_fill=(0, 0, 0, 200))
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        img = Image.alpha_composite(img, sh)
        d = ImageDraw.Draw(img)
    d.text((x, y), text, font=font, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return img

def pil_clip(img, dur):
    return ImageClip(np.array(img.convert("RGBA")), transparent=True).with_duration(dur)

# ---------- 자막/타이틀 카피 ----------
CAP = {
    "ko": ["한글, 어떻게 만들었을까?", "자음 = 입 모양!", "모음 = 하늘·땅·사람!", "풀영상에서 만나요! ▶"],
    "en": ["How was Hangeul made?", "Consonants = your mouth!", "Vowels = sky·earth·person!", "Watch the full story! ▶"],
}
TITLE1 = {"ko": "한 글", "en": "HANGEUL"}
TITLE4 = {"ko": "한글", "en": "Hangeul"}

# ---------- 떠다니는 자모(머리 위·주변, 불규칙) ----------
FLY_JAMO = ["ㄱ", "ㄴ", "ㅁ", "ㅂ", "ㅅ", "ㅇ", "ㅈ", "ㅎ", "ㅏ", "ㅓ", "ㅗ", "ㅜ", "ㅡ", "ㅣ", "ㆍ"]

def build_fly_jamo(total_dur):
    """인물 머리 위·주변(상단~중단)을 불규칙하게 떠다니는 70% 반투명 자모 클립 리스트."""
    clips = []
    chosen = random.sample(FLY_JAMO, 10)
    for j in chosen:
        size = random.randint(105, 180)
        img = text_img(j, size, GOLD, glow=(255, 215, 100), sw=4)
        gw, gh = img.size
        # 앵커: 머리 위·주변 영역(상단 띠), 자막(하단)·맨아래는 피함
        ax = random.uniform(120, W - 120)
        ay = random.uniform(230, 780)
        Ax, Ay = random.uniform(60, 170), random.uniform(50, 150)
        Bx, By = random.uniform(20, 70), random.uniform(20, 70)
        wx, wy = random.uniform(0.5, 1.2), random.uniform(0.5, 1.2)
        wx2, wy2 = random.uniform(1.4, 2.6), random.uniform(1.4, 2.6)
        px, py, px2, py2 = [random.uniform(0, 6.28) for _ in range(4)]
        drift = random.uniform(-14, 14)   # 전체적 가로 흐름
        def pos(t, ax=ax, ay=ay, Ax=Ax, Ay=Ay, Bx=Bx, By=By, wx=wx, wy=wy,
                wx2=wx2, wy2=wy2, px=px, py=py, px2=px2, py2=py2, gw=gw, gh=gh, drift=drift):
            x = ax + Ax * math.sin(wx * t + px) + Bx * math.sin(wx2 * t + px2) + drift * t
            y = ay + Ay * math.sin(wy * t + py) + By * math.cos(wy2 * t + py2)
            return (x - gw / 2, y - gh / 2)
        sc_a = random.uniform(0.06, 0.12); sc_w = random.uniform(0.8, 1.5); sc_p = random.uniform(0, 6.28)
        c = (pil_clip(img, total_dur)
             .with_position(pos)
             .with_opacity(0.7)
             .resized(lambda t, sc_a=sc_a, sc_w=sc_w, sc_p=sc_p: 1.0 + sc_a * math.sin(sc_w * t + sc_p))
             .with_effects([FadeIn(0.5)]))
        clips.append(c)
    return clips

# ---------- 클립(커버핏 + 비트 길이에 맞춰 미세 슬로우) ----------
def cover_fit(clip):
    sc = max(W / clip.w, H / clip.h)
    clip = clip.resized(sc)
    x = (clip.w - W) / 2; y = (clip.h - H) / 2
    return clip.cropped(x1=x, y1=y, x2=x + W, y2=y + H)

def beat_clip(scene_n, dur, start):
    """scene_n 모션클립을 커버핏 → 비트 길이(dur)에 맞춰 속도 조정(정지 프레임 방지) → start 배치."""
    p = os.path.join(CLIPS, f"scene_{scene_n}.mp4")
    if not os.path.exists(p):
        raise SystemExit(f"[ERR] {p} 없음 — 클립 생성 먼저.")
    v = cover_fit(VideoFileClip(p).without_audio())
    speed = v.duration / dur            # dur>v.duration → speed<1(슬로우) → 끝까지 모션
    v = v.with_effects([MultiplySpeed(speed)]).subclipped(0, dur)
    return v.with_start(start)

# ---------- 오디오 ----------
def beat_audio(i):
    p = os.path.join(AUD, f"{LANG}_{i}.mp3")
    return AudioFileClip(p) if os.path.exists(p) else None

logo_img = Image.open(LOGO).convert("RGBA").resize((100, 100), Image.LANCZOS)

# 비트 길이 = 나레이션 + 여유
beat_durs, audios = [], []
for i in range(1, 5):
    a = beat_audio(i)
    audios.append(a)
    beat_durs.append((a.duration + 0.5) if a else 3.0)
B_total = sum(beat_durs)

# ----- Segment A: 광화문 도입(있으면) -----
segA = None
gw_path = os.path.join(SF, "shorts", "gwanghwamun.png")
if os.path.exists(gw_path):
    d0 = 3.4
    gw = Image.open(gw_path).convert("RGBA")
    sc = max(W / gw.width, H / gw.height)
    gw = gw.resize((int(gw.width * sc), int(gw.height * sc)), Image.LANCZOS)
    lft, tp = (gw.width - W) // 2, (gw.height - H) // 2
    gw = gw.crop((lft, tp, lft + W, tp + H))
    la = [pil_clip(gw, d0).with_effects([FadeIn(0.3)])]
    cap0 = text_img("대한민국 서울 · 광화문" if LANG == "ko" else "Gwanghwamun, Seoul", 62, WHITE, sw=6, shadow=True)
    la.append(pil_clip(cap0, d0).with_position(("center", H - 360)).with_effects([FadeIn(0.3)]))
    la.append(pil_clip(logo_img, d0).with_position((W - 128, H - 136)))
    segA = CompositeVideoClip(la, size=(W, H)).with_duration(d0)

# ----- Segment B: 비트별 서가 모션 클립 + 떠다니는 자모 + 비트별 텍스트 -----
# 비트→클립 배정(끝까지 모션, 정지 프레임 없음): 1=와이드, 2=붓적심, 3·4=미소(CTA)
BEAT_SCENE = {1: 1, 2: 2, 3: 3, 4: 2}
layers = []
t_cursor = 0.0
for i in range(1, 5):
    layers.append(beat_clip(BEAT_SCENE[i], beat_durs[i - 1], t_cursor))
    t_cursor += beat_durs[i - 1]
# 서가 은은하게(소프트 베일) → 글자·자모 가독성↑, 꿈결 느낌
layers.append(pil_clip(Image.new("RGBA", (W, H), (255, 252, 245, 70)), B_total))
layers += build_fly_jamo(B_total)   # 머리 위·주변 불규칙 70% 자모

t0 = 0.0
for i in range(1, 5):
    d = beat_durs[i - 1]
    # 상단 타이틀(더 위로) — beat1/4만
    if i == 1:
        ti = text_img(TITLE1[LANG], 184, GOLD, glow=(255, 210, 90))
        layers.append(pil_clip(ti, d).with_start(t0).with_position(("center", 70)).with_effects([CrossFadeIn(0.3)]))
    elif i == 4:
        ti = text_img(TITLE4[LANG], 200, GOLD, glow=(255, 210, 90))
        layers.append(pil_clip(ti, d).with_start(t0).with_position(("center", 90)).with_effects([CrossFadeIn(0.3)]))
    # 하단 자막(박스 없이 흰글자+테두리+음영)
    cap = text_img(CAP[LANG][i - 1], 68, WHITE, sw=6, shadow=True)
    layers.append(pil_clip(cap, d).with_start(t0).with_position(("center", H - 360)).with_effects([CrossFadeIn(0.25)]))
    t0 += d

# 로고: 우하단 워터마크
layers.append(pil_clip(logo_img, B_total).with_position((W - 128, H - 136)))

segB = CompositeVideoClip(layers, size=(W, H)).with_duration(B_total)
# 나레이션(비트 순서대로, 0.5s 여유 포함)
aud_segs = []
for i, a in enumerate(audios):
    if a is None: continue
    aud_segs.append(a.with_start(sum(beat_durs[:i])))
if aud_segs:
    from moviepy import CompositeAudioClip
    segB = segB.with_audio(CompositeAudioClip(aud_segs))

# ----- 최종 연결 -----
parts = [p for p in (segA, segB) if p is not None]
final = concatenate_videoclips(parts, method="compose")
out = os.path.join(SF, "shorts", f"sejong_short_{LANG}.mp4")
final.write_videofile(out, fps=30, codec="libx264", audio_codec="aac", preset="medium", threads=4)
print("DONE:", out, f"{final.duration:.1f}s")
