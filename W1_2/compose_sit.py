# -*- coding: utf-8 -*-
"""첫 상호작용 합성 — 스틱맨이 **벤치에 실제로 걸터앉는다**.

인터랙트랑 A 방향(캐릭터 → 배경) 검증.
앵커 `bench_seat`(x983, y506 실측) 에 캐릭터의 **엉덩이**를 맞춘다.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import interactrang as I                                    # noqa: E402
import stickman_factory as F                                # noqa: E402

BG = "W1_2/bg/gwanghwamun_bench.png"
BG_KEY = "gwanghwamun_bench"
OUT = "W1_2/_check"

# 벤치 좌석면(y506)에 앉았을 때의 캐릭터 키 — 배경 스케일에 맞춘다.
# 배경 768 높이에서 사람 서기 키를 약 300px 로 본다(벤치 앉는 높이와 어울리는 크기).
STAND_H = 300


def pelvis_ratio(png, pose_key):
    """포즈 PNG 안에서 **엉덩이가 어디 있는지**(0~1)를 실측한다.
    ★PART 의 기본값(0.62)을 쓰지 말고 포즈마다 실제로 잰다."""
    im = Image.open(png).convert("RGBA")
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max(), ys.max()
    p = F.POSES[pose_key]["pts"]["pelvis"]
    hr = F.POSES[pose_key].get("hr", 7.5)
    px = F.OX + p[0] * F.S
    py = F.OY + p[1] * F.S
    return (px - x0) / (x1 - x0 + 1), (py - y0) / (y1 - y0 + 1), (x0, y0, x1, y1)


def sit(pose_key, anchor_name, out_name, stand_h=STAND_H, mark=False):
    d = I.load_anchors(BG_KEY)
    a = d["anchors"][anchor_name]
    png = "W1_2/_poses/stickman_%s.png" % pose_key

    fx, fy, box = pelvis_ratio(png, pose_key)
    im = Image.open(png).convert("RGBA").crop(box)

    # 앉은 포즈의 '키'는 머리끝~발끝. 서기 키 기준으로 같은 배율을 쓴다.
    p = F.POSES[pose_key]
    hr = p.get("hr", 7.5)
    head_top = F.OY + (p["pts"]["head"][1] - hr) * F.S
    foot_bot = F.OY + max(p["pts"]["feetLeft"][1], p["pts"]["feetRight"][1]) * F.S
    body_px = foot_bot - head_top
    # 서기 기준 몸 길이(단위) — 머리끝 4.4 ~ 발끝 66
    stand_units = 66.0 - (11.0 - hr)
    scale = (stand_h / stand_units) * (F.S / F.S)          # 단위 → px
    new_h = int(round(im.height * scale * (1.0) / (im.height / (body_px))))
    s = stand_h / stand_units * 1.0
    # 단순화: 원본 1px = 1/S 단위 → 목표 배율
    s = (stand_h / stand_units) / F.S
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                   Image.LANCZOS)

    bg = Image.open(BG).convert("RGBA")
    left = int(round(a["x"] - fx * im.width))
    top = int(round(a["y"] - fy * im.height))
    bg.alpha_composite(im, (left, top))

    if mark:
        dr = ImageDraw.Draw(bg)
        dr.line([(0, a["y"]), (bg.width, a["y"])], fill=(220, 40, 40, 160), width=2)
        dr.ellipse([a["x"] - 8, a["y"] - 8, a["x"] + 8, a["y"] + 8],
                   outline=(220, 40, 40, 255), width=3)

    os.makedirs(OUT, exist_ok=True)
    q = os.path.join(OUT, out_name)
    bg.convert("RGB").save(q)
    print("%-22s 키 %dpx · 엉덩이 비율 (%.3f, %.3f) · 좌상단 (%d,%d) → %s"
          % (pose_key, im.height, fx, fy, left, top, q))
    return q


if __name__ == "__main__":
    sit("w1d2_sit_bench_l", "bench_seat", "sit_bench_L.png", mark=True)
    sit("w1d2_sit_bench_r", "bench_seat", "sit_bench_R.png", mark=True)
