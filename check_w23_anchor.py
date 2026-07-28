# -*- coding: utf-8 -*-
"""W23 상호작용 5종 × 배경 앵커 합성 사전검사 (2026-07-27).

정규화 포즈(1024x1280 · 키770 · 발끝1209)를 렌더 규격(CHAR_SCALE 0.561, 1280x720)으로 얹고
**손이 실제로 앵커 높이(y≈300~360)·앵커 x(≈380 좌 / ≈850 우)에 닿는지**를 잰다.

출력: scratch/w23_anchor_check.png  (앵커 가이드선 + 손 위치 표시)
사용: python check_w23_anchor.py
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
POSE_DIR = "W23/poses_still_norm"
BG_DIR = "assets/graphics/bg"
W, H = 1280, 720
SCALE = 0.561
FEET_SRC = 1209
ANCHOR_L, ANCHOR_R = 380, 850          # 배경 앵커 x
BAND = (300, 360)                      # 손 높이 밴드
OUT = "scratch/w23_anchor_check.png"

# 포즈 → (배경키, 앵커쪽) — W23_scenario.md H-2 매칭표
PAIRS = [
    ("lean_rail",    "panda_deck",      "L", "데크 난간"),
    ("lean_rail",    "fountain_square", "L", "분수 돌턱"),
    ("hand_on_post", "rose_arch",       "L", "아치 벽돌기둥"),
    ("hand_on_post", "notice_plaza",    "R", "석조 기둥"),
    ("tap_board",    "park_cafe",       "L", "카페 달력보드"),
    ("point_board",  "notice_plaza",    "L", "광장 안내판"),
    ("lean_bench",   "picnic_lawn",     "R", "피크닉 테이블"),
    ("lean_bench",   "fountain_square", "R", "분수광장 벤치"),
]


def pose_metrics(key):
    """렌더 규격으로 축소했을 때의 몸통중심·손끝 x 오프셋(캔버스 픽셀)."""
    a = np.array(Image.open(f"{POSE_DIR}/injun_w23_{key}.png").convert("RGBA"))
    al = a[:, :, 3] > 0
    ys = np.where(al.any(axis=1))[0]
    # 몸통 중심 x (엉덩이~허리 띠)
    band = al[int(ys.min() + (ys.max() - ys.min()) * 0.42):int(ys.min() + (ys.max() - ys.min()) * 0.72)]
    bx = np.where(band.any(axis=0))[0]
    cx = int(bx.mean())
    # 손 높이 밴드를 원본 좌표로 환산 — 캔버스 y = FEET_SRC*SCALE - (FEET_SRC - src_y)*SCALE
    feet_cv = FEET_SRC * SCALE
    y0 = int(FEET_SRC - (feet_cv - BAND[0]) / SCALE)
    y1 = int(FEET_SRC - (feet_cv - BAND[1]) / SCALE)
    seg = al[max(0, y0):min(a.shape[0], y1)]
    xs = np.where(seg.any(axis=0))[0]
    if len(xs) == 0:
        return cx, None, None
    return cx, int(xs.min()), int(xs.max())          # 몸통중심, 밴드 내 최좌단, 최우단


def main():
    os.makedirs("scratch", exist_ok=True)
    f = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 15)
    fb = ImageFont.truetype(r"C:\Windows\Fonts\malgunbd.ttf", 19)
    cols, cw, ch = 2, W // 2, H // 2 + 30
    rws = (len(PAIRS) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cw, rws * ch + 46), (245, 245, 242))
    d0 = ImageDraw.Draw(sheet)
    d0.text((12, 13), "W23 상호작용 앵커 합성 검사 — 초록=앵커x(380/850) · 노랑밴드=손높이 300~360 · 빨강점=실제 손끝",
            font=fb, fill=(25, 25, 25))
    print(f"{'포즈':14s} {'배경':16s} 쪽  손끝x   서는x    앵커차")
    for i, (pk, bk, side, label) in enumerate(PAIRS):
        cx, hxmin, hxmax = pose_metrics(pk)
        anchor = ANCHOR_L if side == "L" else ANCHOR_R
        # 손이 앵커에 닿도록 서는 x 를 역산 (좌측 앵커면 최좌단 손, 우측이면 최우단 손)
        hand_src = hxmin if side == "L" else hxmax
        off = (hand_src - cx) * SCALE                 # 몸통중심 기준 손끝 오프셋(캔버스px)
        stand_x = int(round(anchor - off))

        cv = Image.open(f"{BG_DIR}/bg_w23_{bk}.png").convert("RGB").resize((W, H), Image.LANCZOS)
        pose = Image.open(f"{POSE_DIR}/injun_w23_{pk}.png").convert("RGBA")
        pw, ph = round(pose.width * SCALE), round(pose.height * SCALE)
        pim = pose.resize((pw, ph), Image.LANCZOS)
        cv = cv.convert("RGBA")
        cv.alpha_composite(pim, (stand_x - round(cx * SCALE), round(FEET_SRC * SCALE) - ph))
        d = ImageDraw.Draw(cv)
        d.rectangle((0, BAND[0], W, BAND[1]), outline=(240, 200, 40), width=2)
        d.line((anchor, 0, anchor, H), fill=(40, 200, 110), width=2)
        hx = stand_x + round(off)
        d.ellipse((hx - 7, (BAND[0] + BAND[1]) // 2 - 7, hx + 7, (BAND[0] + BAND[1]) // 2 + 7),
                  outline=(230, 40, 40), width=3)
        cell = cv.convert("RGB").resize((cw, H // 2), Image.LANCZOS)
        cx0, cy0 = (i % cols) * cw, (i // cols) * ch + 46
        sheet.paste(cell, (cx0, cy0))
        d0.text((cx0 + 6, cy0 + H // 2 + 4),
                f"{pk} + {bk} ({label}, {'좌' if side=='L' else '우'}앵커) · 서는 x={stand_x}",
                font=f, fill=(20, 20, 20))
        print(f"{pk:14s} {bk:16s} {side}   {off:+7.1f} {stand_x:6d}   앵커 {anchor}")
    sheet.save(OUT)
    print("\n검사 시트:", OUT, sheet.size)


if __name__ == "__main__":
    main()
