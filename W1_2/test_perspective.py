# -*- coding: utf-8 -*-
"""원근 법칙 검증 — 같은 캐릭터를 여러 깊이에 세워 본다.

★지평선 법칙: 키(px) = k × (발y − 지평선y)
  같은 키의 사람은 발이 어디에 있든 **머리끝이 지평선에 온다.**
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import interactrang as I                                    # noqa: E402

BG = "W1_2/bg/gwanghwamun_bench.png"
OUT = "W1_2/_check/perspective.png"

HORIZON = 480          # 실측 — 잔디/하늘 경계
REF_FOOT = 630         # 벤치 앞 바닥
REF_H = 380            # 그 자리에 섰을 때의 키

POSE = "W1_2/_poses/stickman_w1d2_walk_r_0.png"


def main():
    bg = Image.open(BG).convert("RGBA")
    src = Image.open(POSE).convert("RGBA")
    d = ImageDraw.Draw(bg)

    # 지평선 그리기
    d.line([(0, HORIZON), (bg.width, HORIZON)], fill=(220, 40, 40, 200), width=2)
    try:
        f = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 22)
    except Exception:
        f = None
    d.text((14, HORIZON - 30), "지평선 y=%d (카메라 눈높이)" % HORIZON,
           font=f, fill=(220, 40, 40, 255))

    # 여러 깊이에 같은 사람을 세운다
    for x, foot in [(180, 740), (360, 690), (520, 640), (640, 600),
                    (720, 560), (790, 525), (840, 502)]:
        h = I.perspective_height(foot, HORIZON, REF_FOOT, REF_H)
        im = src.resize((max(1, round(src.width * h / src.height)), int(h)),
                        Image.LANCZOS)
        bg.alpha_composite(im, (int(x - im.width / 2), int(foot - im.height)))
        d.line([(x - 6, foot), (x + 6, foot)], fill=(40, 120, 220, 220), width=2)
        d.text((x - 16, foot + 6), "%d" % h, font=f, fill=(40, 120, 220, 255))

    bg.convert("RGB").save(OUT)
    print("지평선 %d · 기준 발 %d → 키 %d  (k=%.3f)"
          % (HORIZON, REF_FOOT, REF_H, REF_H / (REF_FOOT - HORIZON)))
    for foot in (740, 640, 560, 502):
        print("  발 y=%3d → 키 %3.0fpx"
              % (foot, I.perspective_height(foot, HORIZON, REF_FOOT, REF_H)))
    print("→", OUT)


if __name__ == "__main__":
    main()
