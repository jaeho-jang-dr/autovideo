# -*- coding: utf-8 -*-
"""장면 배치 — 스틱맨(왼편 앞) · 졸라맨(중간 아주 멀리) · 졸라걸(오른편 벤치에 앉기).

★키는 **원근 규칙**으로 자동 결정한다: 키(px) = k × (발y − 지평선y)
★그리기 순서 — 먼 것부터: 졸라맨(멀리) → 벤치 가림 → 벤치에 앉은 졸라걸 → 스틱맨(앞)
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)
import interactrang as I                                    # noqa: E402
import stickman_factory as F                                # noqa: E402
from compose_interact import part_xy                        # noqa: E402

BG_KEY = "gwanghwamun_bench"
BG = "W1_2/bg/gwanghwamun_bench.png"
OUT = "W1_2/_check/scene1.png"
BENCH_BOX = (700, 380, 1270, 630)
ZOLLA_GIRL_RATIO = 0.917        # W24 원본 비율 (졸라맨 761 : 졸라걸 698)
SIT_SCALE = 0.72                # 앉으면 사람 키가 서기의 72% 로 보인다


def trim(im):
    a = np.asarray(im.convert("RGBA"))[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    return im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))


def put_standing(bg, png, x, foot_y, persp, ratio=1.0):
    """서 있는 캐릭터 — 발 위치로 키가 정해진다."""
    h = I.perspective_height(foot_y, persp["horizon_y"], persp["ref_foot_y"],
                             persp["ref_h"], ratio)
    im = trim(Image.open(png))
    im = im.resize((max(1, round(im.width * h / im.height)), int(round(h))),
                   Image.LANCZOS)
    bg.alpha_composite(im, (int(round(x - im.width / 2)),
                            int(round(foot_y - im.height))))
    return int(round(h))


def put_param(bg, pose_key, x, foot_y, persp, ratio=1.0):
    """파라메트릭 스틱맨 — 발이 그 자리에 오도록. 키도 원근 규칙."""
    h = I.perspective_height(foot_y, persp["horizon_y"], persp["ref_foot_y"],
                             persp["ref_h"], ratio)
    im = trim(Image.open("W1_2/_poses/stickman_%s.png" % pose_key))
    im = im.resize((max(1, round(im.width * h / im.height)), int(round(h))),
                   Image.LANCZOS)
    bg.alpha_composite(im, (int(round(x - im.width / 2)),
                            int(round(foot_y - im.height))))
    return int(round(h))


def put_sitting(bg, png, seat_x, seat_y, persp, ratio=1.0, turn=0.0):
    """벤치에 앉은 캐릭터 — **좌석 y 를 발 위치로 보고** 원근 키를 구한 뒤 72% 로 줄인다.
    엉덩이(세로 62% 지점)를 좌석선에 맞춘다."""
    stand = I.perspective_height(seat_y + 90, persp["horizon_y"],
                                 persp["ref_foot_y"], persp["ref_h"], ratio)
    h = int(round(stand * SIT_SCALE))
    im = Image.open(png).convert("RGBA")
    im = im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)
    hip_y = int(h * 0.62)
    if turn:
        pad = int(max(im.size) * 0.4)
        cv = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
        cv.alpha_composite(im, (pad, pad))
        cx, cy = pad + im.width / 2, pad + hip_y
        cv = cv.rotate(-turn, resample=Image.BICUBIC, center=(cx, cy))
        im, hip_y = cv, int(cy)
    bg.alpha_composite(im, (int(round(seat_x - im.width / 2)),
                            int(round(seat_y - hip_y))))
    return h


def main():
    d = I.load_anchors(BG_KEY)
    persp = d["perspective"]
    seat = d["anchors"]["bench_seat"]
    bg = Image.open(BG).convert("RGBA")
    comp = bg.copy()

    # ① 졸라맨 — 중간, **아주 멀리** (발을 지평선 가까이)
    h_far = put_standing(comp, "assets/graphics/poses/w24_zolla_man_look_r.png",
                         640, 512, persp)

    # ② 벤치로 가리기 — 멀리 있는 것은 벤치 뒤
    mask = I.make_occ_mask(BG, BENCH_BOX,
                           "W1_2/_check/bench_mask.png", I.wood_mask)
    comp = I.occlude(bg, comp, mask)

    # ③ 졸라걸 — 오른편 벤치에 앉기 (벤치보다 앞)
    h_sit = put_sitting(comp, "W1_2/_poses/stickman_zolla_girl_sit_bench.png",
                        1120, seat["y"], persp, ZOLLA_GIRL_RATIO, turn=-5)

    # ④ 스틱맨 — 제일 왼편, 앞쪽
    h_std = put_param(comp, "w1d2_card_hold", 210, 700, persp)

    dr = ImageDraw.Draw(comp)
    try:
        f = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 20)
    except Exception:
        f = None
    dr.line([(0, persp["horizon_y"]), (comp.width, persp["horizon_y"])],
            fill=(220, 40, 40, 120), width=1)

    comp.convert("RGB").save(OUT)
    print("스틱맨(왼편 앞, 발700) %dpx" % h_std)
    print("졸라맨(중간 아주 멀리, 발512) %dpx" % h_far)
    print("졸라걸(오른편 벤치 앉기) %dpx" % h_sit)
    print("→", OUT)


if __name__ == "__main__":
    main()
