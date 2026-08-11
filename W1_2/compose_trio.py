# -*- coding: utf-8 -*-
"""세 캐릭터 배치 — 스틱맨은 벤치 **뒤에 서고**, 졸라맨·졸라걸은 벤치에 **나란히 앉는다**.

★사장님 지시(2026-08-11): "졸라맨과 졸라걸을 배경 한 구석에 세워 놓거나 앉혀 놓거나
  무슨 동작을 하게 하거나 그렇게 **조수**로 시키자."

키 규격 — 서기 100 기준. 앉기는 **의자를 뺀 사람 키**로 재서 맞춘다.
그리기 순서 — 배경 → 뒤에 선 사람 → 앉은 사람 → **벤치 다시 덮기**(가림)
"""
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)
import interactrang as I                                    # noqa: E402
import stickman_factory as F                                # noqa: E402
from compose_interact import part_xy                        # noqa: E402

BG_KEY = "gwanghwamun_bench"
BG = "W1_2/bg/gwanghwamun_bench.png"
OUT = "W1_2/_check"
BENCH_BOX = (700, 380, 1270, 630)

# 화면에서의 서기 키(px). 이 배경(768 높이)에 어울리는 크기.
STAND_H = 380
# W24 원본 비율 — 졸라맨 761 : 졸라걸 698
ZOLLA_RATIO = {"zolla_man_sit_bench": 1.000, "zolla_girl_sit_bench": 0.917}
# 앉기는 서기의 몇 %로 보이나 — 사람 키(머리끝~발끝)가 앉으면 줄어든다
SIT_SCALE = 0.72


def paste_param(base, pose_key, x, y, joint, stand_h):
    """파라메트릭 포즈(스틱맨)를 관절 기준으로 놓는다."""
    fx, fy, box = part_xy(pose_key, joint)
    im = Image.open("W1_2/_poses/stickman_%s.png" % pose_key).convert("RGBA").crop(box)
    p = F.POSES[pose_key]
    hr = p.get("hr", 7.5)
    s = (stand_h / (66.0 - (11.0 - hr))) / F.S
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                   Image.LANCZOS)
    base.alpha_composite(im, (int(round(x - fx * im.width)),
                              int(round(y - fy * im.height))))
    return im.height


def paste_zolla(base, key, seat_x, seat_y, height, turn=0.0):
    """졸라 앉기 컷 — **엉덩이가 좌석선**에 오게 놓는다.
    의자를 뺀 컷이라 세로 비율의 약 62% 지점이 엉덩이다.

    turn — 서로 **마주 보게 조금 트는** 각도(도). +는 오른쪽으로, -는 왼쪽으로.
           ★엉덩이(회전 중심)를 기준으로 돌려야 좌석에서 안 뜬다.
    """
    im = Image.open("W1_2/_poses/stickman_%s.png" % key).convert("RGBA")
    s = height / im.height
    im = im.resize((max(1, round(im.width * s)), height), Image.LANCZOS)
    hip_y = int(height * 0.62)
    if turn:
        # 회전 중심을 엉덩이에 두고 돌린다 — 캔버스를 넉넉히 잡아 잘리지 않게
        pad = int(max(im.size) * 0.4)
        cv = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
        cv.alpha_composite(im, (pad, pad))
        cx, cy = pad + im.width / 2, pad + hip_y
        cv = cv.rotate(-turn, resample=Image.BICUBIC, center=(cx, cy))
        im, hip_y = cv, int(cy)
    base.alpha_composite(im, (int(round(seat_x - im.width / 2)),
                              int(round(seat_y - hip_y))))
    return im.width


def main():
    os.makedirs(OUT, exist_ok=True)
    d = I.load_anchors(BG_KEY)
    seat = d["anchors"]["bench_seat"]
    bg = Image.open(BG).convert("RGBA")
    comp = bg.copy()

    # ★그리기 순서 (2026-08-11 사장님 지적으로 바로잡음)
    #     ①뒤에 서기 → ②벤치로 가리기 → ③두 명 앉히기
    #   앉은 사람은 벤치 **앞**에 있으므로 가림 뒤에 그린다.
    #   전에는 앉은 사람까지 벤치가 덮어 벤치 뒤에 숨은 것처럼 보였다.

    # ① 스틱맨 — 벤치 **뒤**에 서서 등받이에 팔을 올린다(등받이 윗면 y≈392)
    paste_param(comp, "w1d2_stand_behind_bench", 1050, 392, "handRight", STAND_H)

    # ② 벤치를 다시 덮어 **뒤에 선 사람만** 가린다
    mask = I.make_occ_mask(BG, BENCH_BOX,
                           os.path.join(OUT, "bench_mask.png"), I.wood_mask)
    comp = I.occlude(bg, comp, mask)

    # ③ 졸라맨·졸라걸 — 좌석선(y506)에 나란히. 벤치보다 **앞**이라 가림 뒤에 그린다
    sit_h_man = int(STAND_H * SIT_SCALE * ZOLLA_RATIO["zolla_man_sit_bench"])
    sit_h_girl = int(STAND_H * SIT_SCALE * ZOLLA_RATIO["zolla_girl_sit_bench"])
    # ★붙여 앉히고 **서로 마주 보게** 조금씩 튼다(사장님 지시 2026-08-11).
    #   ★각도는 **5도**. 12도로 돌렸더니 앉은 자세는 몸통이 엉덩이 위에 얹혀 있어
    #     상체가 크게 쏠리고 미끄러지듯 누워 보였다.
    paste_zolla(comp, "zolla_man_sit_bench", 930, seat["y"], sit_h_man, turn=+5)
    paste_zolla(comp, "zolla_girl_sit_bench", 1120, seat["y"], sit_h_girl, turn=-5)

    occ = comp
    comp.convert("RGB").save(os.path.join(OUT, "trio_bench.png"))
    print("스틱맨 서기 %dpx · 졸라맨 앉기 %dpx · 졸라걸 앉기 %dpx"
          % (STAND_H, sit_h_man, sit_h_girl))
    print("→ trio_bench.png (가림 적용) · trio_noocc.png (가림 전)")


if __name__ == "__main__":
    main()
