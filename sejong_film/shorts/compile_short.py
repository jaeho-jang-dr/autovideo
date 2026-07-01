# -*- coding: utf-8 -*-
"""세종 쇼츠(9:16) 컴포지터 — 플랫 레이어드: 파스텔 배경 + 애니 세종 + 자모 팝인 + 자막 + 로고 + 나레이션.
moviepy 2.x API 사용(with_duration/with_position/resized/with_effects)."""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from moviepy.video.fx import FadeIn

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
SF = os.path.join(ROOT, "sejong_film")
AUD = os.path.join(SF, "shorts", "audio")
LOGO = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
MALGUN = r"C:\Windows\Fonts\malgunbd.ttf"
W, H = 1080, 1920
LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"

def pil_to_clip(img, dur):
    arr = np.array(img.convert("RGBA"))
    return ImageClip(arr, transparent=True).with_duration(dur)

def grad_bg(c1, c2):
    base = Image.new("RGB", (W, H), c1)
    top = np.array(c1); bot = np.array(c2)
    for y in range(H):
        f = y / H
        base.paste(tuple((top * (1 - f) + bot * f).astype(int)), (0, y, W, y + 1))
    return base

def text_img(text, size, fill, stroke=(20, 25, 45), sw=8, glow=None, shadow=False, maxw=None):
    font = ImageFont.truetype(MALGUN, size)
    dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bb = dummy.textbbox((0, 0), text, font=font, stroke_width=sw)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = sw + (40 if glow else (28 if shadow else 12))
    img = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x, y = pad - bb[0], pad - bb[1]
    if glow:
        g = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dg = ImageDraw.Draw(g)
        dg.text((x, y), text, font=font, fill=glow + (255,))
        g = g.filter(ImageFilter.GaussianBlur(18))
        img = Image.alpha_composite(img, g); img = Image.alpha_composite(img, g)
        d = ImageDraw.Draw(img)
    if shadow:   # 박스 없이 부드러운 드롭 섀도(음영)
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        dsh = ImageDraw.Draw(sh)
        dsh.text((x + 5, y + 7), text, font=font, fill=(0, 0, 0, 200), stroke_width=sw, stroke_fill=(0, 0, 0, 200))
        sh = sh.filter(ImageFilter.GaussianBlur(6))
        img = Image.alpha_composite(img, sh)
        d = ImageDraw.Draw(img)
    d.text((x, y), text, font=font, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return img

GOLD = (245, 200, 75, 255)
WHITE = (255, 255, 255, 255)

# 자막(짧게) — 화면 표시용
CAP = {
    "ko": ["한글, 어떻게 만들었을까?", "자음 = 입 모양!", "모음 = 하늘·땅·사람!", "풀영상에서 만나요! ▶"],
    "en": ["How was Hangeul made?", "Consonants = your mouth!", "Vowels = sky·earth·person!", "Watch the full story! ▶"],
}
JAMO2 = ["ㄱ", "ㄴ", "ㅁ"]
JAMO3 = ["ㆍ", "ㅡ", "ㅣ"]
TITLE = {"ko": "한 글", "en": "HANGEUL"}

# 배경/로고/캐릭터
bg_img = grad_bg((38, 52, 110), (12, 22, 60))      # 짙은 남색 그라데
sejong = Image.open(os.path.join(SF, "anim", "sejong_mid_cut.png")).convert("RGBA")
logo = Image.open(LOGO).convert("RGBA").resize((100, 100), Image.LANCZOS)   # 워터마크 크기

def beat_audio(i):
    p = os.path.join(AUD, f"{LANG}_{i}.mp3")
    return AudioFileClip(p) if os.path.exists(p) else None

def pop(t):
    if t < 0.22: return 0.2 + 0.8 * (t / 0.22)
    if t < 0.33: return 1.0 + 0.07 * (1 - (t - 0.22) / 0.11)
    return 1.0

beats = []
# Beat 0: 광화문 + 세종대왕 동상 (짧은 도입, 이미지 있으면)
gw_path = os.path.join(SF, "shorts", "gwanghwamun.png")
if os.path.exists(gw_path):
    d0 = 2.6
    gw = Image.open(gw_path).convert("RGBA")
    sc = max(W / gw.width, H / gw.height)            # 세로 프레임에 cover-fit
    gw = gw.resize((int(gw.width * sc), int(gw.height * sc)), Image.LANCZOS)
    lft, tp = (gw.width - W) // 2, (gw.height - H) // 2
    gw = gw.crop((lft, tp, lft + W, tp + H))
    l0 = [pil_to_clip(gw, d0).with_effects([FadeIn(0.3)])]
    cap0 = text_img("대한민국 서울 · 광화문" if LANG == "ko" else "Gwanghwamun, Seoul", 64, WHITE, sw=6, shadow=True)
    l0.append(pil_to_clip(cap0, d0).with_position(("center", H - 340)).with_effects([FadeIn(0.3)]))
    l0.append(pil_to_clip(logo, d0).with_position((W - 100 - 28, H - 100 - 36)))
    beats.append(CompositeVideoClip(l0, size=(W, H)).with_duration(d0))

for i in range(1, 5):
    a = beat_audio(i)
    d = (a.duration + 0.5) if a else 3.0
    layers = [pil_to_clip(bg_img, d)]
    # 캐릭터: beat1·4는 크게, 2·3은 작게 옆에
    sj_h = 1050 if i in (1, 4) else 620
    sj = sejong.resize((int(sejong.width * sj_h / sejong.height), sj_h), Image.LANCZOS)
    sj_clip = pil_to_clip(sj, d).with_position(("center", H - sj.height - 60) if i in (1, 4) else (W - sj.width + 40, H - sj.height - 40))
    sj_clip = sj_clip.with_effects([FadeIn(0.3)])
    layers.append(sj_clip)
    # 타이틀(beat1) / 자모(beat2,3) / 모임(beat4)
    if i == 1:
        t = text_img(TITLE[LANG], 200, GOLD, glow=(255, 210, 90))
        layers.append(pil_to_clip(t, d).with_position(("center", 230)).with_effects([FadeIn(0.3)]))
    elif i in (2, 3):
        jamo = JAMO2 if i == 2 else JAMO3
        n = len(jamo)
        for k, j in enumerate(jamo):
            ji = text_img(j, 300, GOLD, glow=(255, 210, 90))
            jc = pil_to_clip(ji, d)
            base_w, base_h = ji.size
            x = int(W * (0.5) - (n * 300) / 2 + k * 300 + 90)
            y = 520
            st = 0.15 + k * 0.45
            jc = jc.with_position((x, y)).with_start(st).with_duration(d - st)
            jc = jc.resized(lambda tt: pop(tt))
            layers.append(jc)
    else:
        t = text_img("한글" if LANG == "ko" else "Hangeul", 240, GOLD, glow=(255, 210, 90))
        layers.append(pil_to_clip(t, d).with_position(("center", 300)).with_effects([FadeIn(0.3)]))
    # 자막(하단): 박스 없이 흰 글자 + 테두리 + 그림자(음영)
    cap = text_img(CAP[LANG][i - 1], 70, WHITE, sw=6, shadow=True, maxw=W - 120)
    layers.append(pil_to_clip(cap, d).with_position(("center", H - 340)).with_effects([FadeIn(0.25)]))
    # 로고: 우하단 워터마크 위치/크기 (모든 비트 동일)
    layers.append(pil_to_clip(logo, d).with_position((W - 100 - 28, H - 100 - 36)))
    comp = CompositeVideoClip(layers, size=(W, H)).with_duration(d)
    if a:
        comp = comp.with_audio(a)
    beats.append(comp)

final = concatenate_videoclips(beats, method="compose")
out = os.path.join(SF, "shorts", f"sejong_short_{LANG}.mp4")
final.write_videofile(out, fps=30, codec="libx264", audio_codec="aac", preset="medium", threads=4)
print("DONE:", out, f"{final.duration:.1f}s")
