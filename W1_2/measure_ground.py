# -*- coding: utf-8 -*-
"""배경마다 **걸어 다닐 수 있는 땅**을 실측한다 — 캐릭터랑이 쓸 지도.

★사장님 지시(2026-08-13)
  "정확하게 배경을 실측하고 움직여야지. **갈 수 있는 곳, 비어 있는 곳으로만** 움직인다.
   막혀 있으면 앉거나 서 있는다. 캐릭터랑은 배경마다 **움직일 수 있는 곳**을 알아야 하고,
   **대각선 끝점과 수평선의 위치, 발이 놓일 수 있는 범위** 등에 대해서 다 알고 캐릭터를
   움직인다."
  "대각선으로 달리면서 왼 앞에서 오른 저 끝 뒤로 가서 사라지는 것 — 그러나 **땅에 발은
   항상 디뎌야** 하고 원근법에 맞아야 한다. 원근을 계산해서 90에서 사라질 수도 있고
   10에서 사라질 수도 있고, **벽에 닿으면 200에서 사라질 수도 있는** 리얼리티."

## 무엇을 재는가 — 세로줄마다 '땅의 위쪽 끝'
화면을 세로줄(가로 16px)로 잘라, 아래에서 위로 올라가며 **땅이 끝나는 y** 를 찾는다.
그 위는 담·건물·나무·물이라 발을 디딜 수 없다.

  ground_top[x]  그 x 에서 발을 놓을 수 있는 **가장 위(가장 먼) y**
  floor_bot[x]   그 x 에서 발을 놓을 수 있는 **가장 아래(가장 가까운) y** (보통 화면 바닥)

땅을 가르는 법 — 아래쪽 두 줄(화면 바닥 근처)의 색을 **땅의 색 견본**으로 삼고,
위로 올라가며 색이 그 견본에서 멀어지는 지점을 땅의 끝으로 본다. 포장·잔디·흙처럼
바닥은 위아래로 이어진 한 덩어리라 이 방법이 잘 듣는다.

## 나오는 것 — `assets/anchors/<배경>.json` 의 `ground` 칸
    "ground": {
      "cols": 80,                    # 세로줄 개수 (16px 간격)
      "top":  [610, 608, ...],       # 줄마다 땅의 위쪽 끝 y
      "bot":  [720, 720, ...],       # 줄마다 땅의 아래쪽 끝 y
      "horizon": 452,                # 지평선 y (땅이 가장 멀리 가는 곳)
      "far_h": 34                    # 그 자리에서의 스틱맨 화면 키
    }

    python W1_2/measure_ground.py               # 전부 재고 확인 그림까지
    python W1_2/measure_ground.py steps_seat    # 하나만
    python W1_2/measure_ground.py --write       # 앵커 파일에 적는다
"""
import glob
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

BG_DIR = "W1_2/bg"
ANCHOR_DIR = "assets/anchors"
OUT = "W1_2/_ground"
FONT = r"C:\Windows\Fonts\malgun.ttf"
W, H = 1280, 720
STEP = 16                          # 세로줄 간격 (1280 ÷ 16 = 80줄)
SMALL_H = 45                       # 세로도 이만큼으로 줄여 잰다 (720 ÷ 16)
TOL = 60                           # 땅 색 견본에서 이만큼 벌어지면 땅이 아니다


def first_frame(bg):
    mp4 = os.path.join(BG_DIR, bg + ".mp4")
    png = os.path.join(BG_DIR, bg + ".png")
    if os.path.exists(png):
        return Image.open(png).convert("RGB").resize((W, H), Image.LANCZOS)
    tmp = os.path.join(OUT, "_f.png")
    os.makedirs(OUT, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mp4,
                    "-frames:v", "1", tmp], check=True)
    return Image.open(tmp).convert("RGB").resize((W, H), Image.LANCZOS)


def measure(im):
    """세로줄마다 (땅 위쪽 끝, 땅 아래쪽 끝).

    ★바닥 한 곳의 색과 견주면 **포장 이음매**에서 멈춰 버린다(1차 실측: 광장이
      바닥 80px 만 잡혔다). 땅은 멀어질수록 색이 **천천히** 변하고, 담·물·나무는
      **갑자기** 바뀐다. 그래서 고정 견본이 아니라 **바로 아래 줄과 견준다**.
      한 줄이 튀는 것(이음매)은 무시하고, **여러 줄이 이어서 튈 때만** 땅의 끝으로 본다.
    """
    # ★작게 줄여서 잰다 — 16×16 덩어리로 뭉개면 **포장 이음매가 사라지고**
    #   담·물·나무처럼 진짜로 다른 것만 남는다. 1차 실측이 줄마다 들쭉날쭉했던 이유다.
    cols = W // STEP
    small = np.asarray(im.resize((cols, SMALL_H), Image.BOX)).astype(np.float32)
    tops, bots = [], []
    for c in range(cols):
        col = small[:, c]                          # 아래에서 위로 훑는다
        ref = col[SMALL_H - 3:].mean(axis=0)       # 이 줄 맨 아래 = 땅 색 견본
        top = SMALL_H
        for y in range(SMALL_H - 1, -1, -1):
            if float(np.abs(col[y] - ref).sum()) > TOL:
                break
            top = y
        tops.append(int(round(top * H / float(SMALL_H))))
        bots.append(H)
    return tops, bots


def draw_check(im, tops, bots, bg, horizon):
    cv = im.copy()
    d = ImageDraw.Draw(cv)
    for i, (t, b) in enumerate(zip(tops, bots)):
        x = i * STEP + STEP // 2
        if t < b:
            d.line([(x, t), (x, b - 1)], fill=(60, 220, 120), width=3)   # 밟을 수 있는 곳
        else:
            d.line([(x, H - 6), (x, H - 1)], fill=(230, 60, 60), width=3)  # 못 밟음
    d.line([(0, horizon), (W, horizon)], fill=(0, 120, 255), width=2)
    f = ImageFont.truetype(FONT, 20)
    d.text((10, 8), "%s — 초록 = 발을 디딜 수 있는 곳 · 파랑 = 지평선 y=%d"
           % (bg, horizon), font=f, fill=(255, 240, 0))
    return cv


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--write" in sys.argv
    bgs = args or sorted(set(
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join(BG_DIR, "*.mp4"))
        + glob.glob(os.path.join(BG_DIR, "*.png"))
        if not os.path.basename(p).startswith("_")))

    os.makedirs(OUT, exist_ok=True)
    print("%-18s %6s %6s %6s  %s" % ("배경", "지평선", "가장먼발", "가장가까운", "밟을수있는줄"))
    for bg in bgs:
        im = first_frame(bg)
        tops, bots = measure(im)
        walk = [t for t in tops if t < H]
        if not walk:
            print("  %-16s ★땅을 못 찾음" % bg)
            continue
        horizon = min(walk)                       # 땅이 가장 멀리 닿는 y = 지평선
        near = max(bots)
        cv = draw_check(im, tops, bots, bg, horizon)
        cv.save(os.path.join(OUT, "%s.png" % bg))
        print("  %-16s %6d %6d %6d  %d/%d줄"
              % (bg, horizon, horizon, near, len(walk), len(tops)))

        if write:
            p = os.path.join(ANCHOR_DIR, bg + ".json")
            doc = {}
            if os.path.exists(p):
                with open(p, encoding="utf-8") as f:
                    doc = json.load(f)
            doc.setdefault("bg", bg)
            doc.setdefault("canvas", [W, H])
            doc["ground"] = {"step": STEP, "top": tops, "bot": bots,
                             "horizon": horizon,
                             "note": "measure_ground.py 실측 — 세로줄마다 발을 디딜 수 "
                                     "있는 y 범위. top 이 가장 먼 곳, bot 이 가장 가까운 곳."}
            with open(p, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
    print("\n확인 그림 → %s%s" % (OUT, "  · 앵커에 기록함" if write else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
