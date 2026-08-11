# -*- coding: utf-8 -*-
"""원근 배치 — **발 위치만 주면 키가 자동으로 정해진다.**

앵커 JSON 의 `perspective`(지평선·기준점)를 읽어 쓴다.
캐릭터 하나(졸라맨)를 여러 깊이에 세워 규칙을 보인다.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import interactrang as I                                    # noqa: E402

BG_KEY = "gwanghwamun_bench"
BG = "W1_2/bg/gwanghwamun_bench.png"
OUT = "W1_2/_check/depth_one.png"
# 조수 — 졸라맨 서기(W24 원본). 앉기가 아니라 서기 컷을 쓴다.
POSE = "assets/graphics/poses/w24_zolla_man_look_r.png"
RATIO = 1.0            # 졸라맨 기준. 졸라걸이면 0.917


def put(bg, src, x, foot_y, persp, ratio=1.0):
    h = I.perspective_height(foot_y, persp["horizon_y"],
                             persp["ref_foot_y"], persp["ref_h"], ratio)
    im = src.resize((max(1, round(src.width * h / src.height)), int(round(h))),
                    Image.LANCZOS)
    bg.alpha_composite(im, (int(round(x - im.width / 2)),
                            int(round(foot_y - im.height))))
    return int(round(h))


def main():
    d = I.load_anchors(BG_KEY)
    persp = d["perspective"]
    bg = Image.open(BG).convert("RGBA")
    src = Image.open(POSE).convert("RGBA")
    # 캐릭터 잘라내기(여백 제거)
    import numpy as np
    a = np.asarray(src)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    src = src.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))

    dr = ImageDraw.Draw(bg)
    try:
        f = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 20)
    except Exception:
        f = None
    dr.line([(0, persp["horizon_y"]), (bg.width, persp["horizon_y"])],
            fill=(220, 40, 40, 190), width=2)
    dr.text((14, persp["horizon_y"] - 28),
            "지평선 y=%d" % persp["horizon_y"], font=f, fill=(220, 40, 40, 255))

    spots = [(150, 730, "앞"), (330, 660, "벤치 앞"), (480, 600, "중간"),
             (600, 545, "멀리"), (680, 505, "저 끝")]
    for x, foot, lab in spots:
        h = put(bg, src, x, foot, persp, RATIO)
        dr.line([(x - 8, foot), (x + 8, foot)], fill=(40, 120, 220, 220), width=2)
        dr.text((x - 30, foot + 6), "%s %dpx" % (lab, h), font=f,
                fill=(40, 120, 220, 255))

    bg.convert("RGB").save(OUT)
    k = persp["ref_h"] / (persp["ref_foot_y"] - persp["horizon_y"])
    print("k = %.3f  (지평선 %d · 기준 발 %d → %dpx)"
          % (k, persp["horizon_y"], persp["ref_foot_y"], persp["ref_h"]))
    for x, foot, lab in spots:
        print("  %-6s 발 y=%3d → 키 %3.0fpx"
              % (lab, foot, I.perspective_height(foot, persp["horizon_y"],
                                                 persp["ref_foot_y"], persp["ref_h"])))
    print("→", OUT)


if __name__ == "__main__":
    main()
