# -*- coding: utf-8 -*-
"""인터랙트랑 A 방향 합성 — 앵커에 캐릭터의 **지정 부위**를 맞춘다.

앵커 type 이 어느 부위를 맞출지 정한다:
  sit → pelvis · grab/touch → hand · ground → hand · stand → feet
부위 위치는 **포즈마다 관절 좌표에서 실측**한다(고정 비율을 쓰지 않는다).
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import interactrang as I                                    # noqa: E402
import stickman_factory as F                                # noqa: E402

BG_KEY = "gwanghwamun_bench"
BG = "W1_2/bg/gwanghwamun_bench.png"
OUT = "W1_2/_check"
STAND_H = 340                # 배경(768 높이)에서 서기 키

# 앵커 type → 포즈에서 쓸 관절 이름
JOINT = {"sit": "pelvis", "grab": None, "touch": None,
         "ground": None, "stand": None, "lean": "chest"}


def part_xy(pose_key, joint):
    """포즈 PNG(잘라낸 것) 안에서 그 관절이 어디인지 0~1 비율로 돌려준다."""
    png = "W1_2/_poses/stickman_%s.png" % pose_key
    im = Image.open(png).convert("RGBA")
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())
    p = F.POSES[pose_key]["pts"][joint]
    px = F.OX + p[0] * F.S
    py = F.OY + p[1] * F.S
    return (px - x0) / (x1 - x0 + 1), (py - y0) / (y1 - y0 + 1), (x0, y0, x1, y1)


def compose(pose_key, anchor_name, joint, out_name, stand_h=STAND_H, mark=True):
    d = I.load_anchors(BG_KEY)
    a = d["anchors"][anchor_name]
    fx, fy, box = part_xy(pose_key, joint)

    im = Image.open("W1_2/_poses/stickman_%s.png" % pose_key).convert("RGBA").crop(box)
    p = F.POSES[pose_key]
    hr = p.get("hr", 7.5)
    # 서기 기준 단위 길이(머리끝~발끝) = 66 - (11 - hr)
    stand_units = 66.0 - (11.0 - hr)
    s = (stand_h / stand_units) / F.S
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                   Image.LANCZOS)

    bg = Image.open(BG).convert("RGBA")
    left = int(round(a["x"] - fx * im.width))
    top = int(round(a["y"] - fy * im.height))
    bg.alpha_composite(im, (left, top))

    if mark:
        dr = ImageDraw.Draw(bg)
        x, y = a["x"], a["y"]
        dr.line([(x - 26, y), (x + 26, y)], fill=(220, 40, 40, 220), width=3)
        dr.line([(x, y - 26), (x, y + 26)], fill=(220, 40, 40, 220), width=3)
        dr.ellipse([x - 10, y - 10, x + 10, y + 10], outline=(220, 40, 40, 255), width=3)

    os.makedirs(OUT, exist_ok=True)
    q = os.path.join(OUT, out_name)
    bg.convert("RGB").save(q)
    print("%-24s %-12s 부위비율(%.3f,%.3f) 키%dpx → %s"
          % (pose_key, anchor_name, fx, fy, im.height, q))
    return q


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.parse_args()
    # 난간 잡기 — 오른손이 난간 앵커에
    compose("w1d2_grab_rail_r", "rail_grip", "handRight", "grab_rail_R.png")
    # 앉기 — 엉덩이가 좌석 앵커에 (크기 키움)
    compose("w1d2_sit_bench_l", "bench_seat", "pelvis", "sit_bench_L2.png")
