# -*- coding: utf-8 -*-
"""W1-2 썸네일 — **모음만으로 만든 낱말 15개**(광화문광장).

★매회 다른 디자인 (사장님 원칙 [[thumbnail-vary-each-episode]])
   W21 상단 타이틀+하단 3알약 / W22 좌캐릭터+우 2단카드 / W23 중앙+좌제목+3버튼
   W24 실제 씬+리본 배지+진행 바
   → W1-2 는 **낱말 타일**이 주인공이다. 이 회차의 알맹이가 "자음 없이 모음만으로
     이만큼 말이 된다" 이므로, 낱말을 격자로 깔고 그 위에 큰 제목을 얹는다.
     배경은 본편 광화문 분수 장면(캐릭터가 가운데 서 있는 프레임).

  python W1_2/make_thumb_w1d2.py           # 시안 4개
  python W1_2/make_thumb_w1d2.py --pick 2  # 확정본 저장(ko/en)
"""
import argparse
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"
DONG = "assets/fonts/Cafe24Dongdong.ttf"
VIDEO = "W1_2/w1d2_final_en_r1.mp4"
OUT = "W1_2/_thumb"
# 배경 후보 — 광화문 분수 터널(캐릭터가 가운데, 위쪽이 비어 제목 자리가 넉넉하다)
FRAMES = [105.0, 62.0, 240.0, 330.0]

WORDS = ["아이", "이", "위", "오이", "유아", "우유", "이유", "오",
         "우와", "야외", "야유", "아우", "여우", "아야", "여유"]
TITLE = {"ko": ("자음 0개", "모음만으로 15낱말"),
         "en": ("ZERO consonants", "15 words from vowels alone")}


def F(p, s):
    return ImageFont.truetype(p, s)


def outline(d, xy, txt, font, fill, oc=(18, 16, 12), ow=5):
    x, y = xy
    for dx in range(-ow, ow + 1, 2):
        for dy in range(-ow, ow + 1, 2):
            d.text((x + dx, y + dy), txt, font=font, fill=oc)
    d.text((x, y), txt, font=font, fill=fill)


def grab(t, out):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.1f" % t, "-i", VIDEO,
                    "-frames:v", "1", "-vf", "scale=%d:%d" % (W, H), out], check=True)
    return out


def build(bg_path, lang, out):
    im = Image.open(bg_path).convert("RGB")
    # 아래쪽을 어둡게 깔아 낱말 타일이 뜨게 한다
    sc = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sc)
    sd.rectangle([0, H - 250, W, H], fill=(12, 14, 22, 190))
    # ★본편 프레임에는 좌상단 **텍스트박스**가 찍혀 있다. 제목과 겹치므로
    #   상단에도 띠를 깔아 덮는다(2026-08-18 시안 1에서 발견).
    sd.rectangle([0, 0, W, 232], fill=(12, 14, 22, 205))
    im = Image.alpha_composite(im.convert("RGBA"), sc).convert("RGB")
    d = ImageDraw.Draw(im)

    big, sub = F(DONG if os.path.exists(DONG) else MALGUN, 92), F(MALGUN, 40)
    t1, t2 = TITLE[lang]
    outline(d, (54, 40), t1, big, (255, 232, 84))
    outline(d, (58, 148), t2, sub, (255, 255, 255), ow=4)

    # ── 낱말 타일 (아래 두 줄)
    f = F(MALGUN, 38)
    x, y, pad = 54, H - 215, 16
    for w in WORDS:
        tw = d.textlength(w, font=f)
        bw = tw + pad * 2
        if x + bw > W - 54:
            x, y = 54, y + 82
        d.rounded_rectangle([x, y, x + bw, y + 62], 14,
                            fill=(255, 255, 255, 235), outline=(255, 210, 60), width=3)
        d.text((x + pad, y + 8), w, font=f, fill=(24, 26, 36))
        x += bw + 12
    im.save(out, quality=92)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pick", type=int)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.pick:
        bg = grab(FRAMES[a.pick - 1], os.path.join(OUT, "_bg.png"))
        for lang in ("ko", "en"):
            p = build(bg, lang, "W1_2/w1d2_thumb_%s.jpg" % lang)
            print("확정 →", p, "%.1fKB" % (os.path.getsize(p) / 1024))
        return
    for i, t in enumerate(FRAMES, 1):
        bg = grab(t, os.path.join(OUT, "_bg%d.png" % i))
        p = build(bg, "ko", os.path.join(OUT, "cand%d.jpg" % i))
        print("시안 %d (%.0f초) → %s" % (i, t, p))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
