# -*- coding: utf-8 -*-
"""가림(오클루전) 합성 — 캐릭터가 벤치 **뒤**에 서면 벤치에 가려진다.

★사장님 지시(2026-08-11): "배경이 먼저고 캐릭터가 먼저지만 **일부를 지우면** 그것도 가능해진다."
순서: 배경 → 캐릭터 → **벤치만 다시 덮기**
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

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
# 벤치가 있는 범위 — 등받이 위끝부터 다리 밑까지
BENCH_BOX = (700, 380, 1270, 630)


def place(pose_key, anchor, joint, stand_h, bg=None):
    fx, fy, box = part_xy(pose_key, joint)
    im = Image.open("W1_2/_poses/stickman_%s.png" % pose_key).convert("RGBA").crop(box)
    p = F.POSES[pose_key]
    hr = p.get("hr", 7.5)
    s = (stand_h / (66.0 - (11.0 - hr))) / F.S
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))),
                   Image.LANCZOS)
    base = (bg or Image.open(BG).convert("RGBA")).copy()
    left = int(round(anchor["x"] - fx * im.width))
    top = int(round(anchor["y"] - fy * im.height))
    base.alpha_composite(im, (left, top))
    return base


def mark(im, a):
    d = ImageDraw.Draw(im)
    x, y = a["x"], a["y"]
    d.line([(x - 24, y), (x + 24, y)], fill=(220, 40, 40, 220), width=3)
    d.line([(x, y - 24), (x, y + 24)], fill=(220, 40, 40, 220), width=3)
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    d = I.load_anchors(BG_KEY)
    bg = Image.open(BG).convert("RGBA")

    # ① 땅에 주저앉기 (엉덩이가 바닥)
    a = d["anchors"]["ground_dig"]
    im = place("w1d2_crouch_ground_r", a, "handRight", 340)
    mark(im, a).convert("RGB").save(os.path.join(OUT, "sit_ground.png"))
    print("① 주저앉기 → sit_ground.png")

    # ② 난간에 기대어 팔 올리기 — 난간 왼쪽 끝으로 당겨 잘리지 않게
    a2 = dict(d["anchors"]["rail_grip"])
    a2["x"] = 1258
    im = place("w1d2_lean_rail_r", a2, "handRight", 380)
    mark(im, a2).convert("RGB").save(os.path.join(OUT, "lean_rail.png"))
    print("② 난간 기대기 → lean_rail.png")

    # ③ 벤치 뒤에 서서 팔 올리기 + **벤치로 가리기**
    #    등받이 윗면(y≈390)에 손이 오게 하고, 벤치를 다시 덮는다
    a3 = {"type": "grab", "x": 1050, "y": 392}
    comp = place("w1d2_stand_behind_bench", a3, "handRight", 380)
    mask = I.make_occ_mask(BG, BENCH_BOX,
                           os.path.join(OUT, "bench_mask.png"), I.wood_mask)
    occ = I.occlude(bg, comp, mask)
    occ.convert("RGB").save(os.path.join(OUT, "behind_bench.png"))
    # 가리기 전/후 비교
    comp.convert("RGB").save(os.path.join(OUT, "behind_bench_noocc.png"))
    m = np.asarray(Image.open(mask))
    print("③ 벤치 뒤 서기 → behind_bench.png (마스크 화소 %d개)" % (m > 128).sum())


if __name__ == "__main__":
    main()
