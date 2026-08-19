# -*- coding: utf-8 -*-
"""배경마다 **원근을 푼다** — 자리가 정해지면 키가 정해지게.

★사장님 지시(2026-08-13)
  "너는 컴퓨터이니 숫자·위치·좌표에 아주 정확해야 하고 민감해야 한다.
   캐릭터는 기준 키가 있고 시작하는 키가 있고, **표준 700**, **머리의 아래위 높이가
   비율을 정하는 척도**가 되고, **각 배경마다의 원근 정도에 따라 그 배경에서의 위치·
   키의 정도가 결정되고 계산된다.** 그러니 캐릭터가 어느 곳에 딱 서면 **벌써 계산된
   비율의 키로** 서야 하는 것이다. 이동도 마찬가지다. 대각선으로 이동하면 좌표가
   달라지면서 **캐릭터의 키도 달라지는** 것이다."

## 푸는 식 — 두 점이면 무대가 정해진다
땅을 내려다보는 카메라에서, 땅 위 한 점의 **발 y** 와 그 자리에 선 사람의 **화면 키**는
둘 다 거리에 반비례한다. 그래서

    키 = K × (발y − 지평선)

두 점을 알면 K 와 지평선이 풀린다. 우리가 아는 두 점은 —

  ① **화면 맨 앞** — 발이 화면 바닥(y=720)에 닿을 때 **키 = 700** (사장님 확정 표준)
  ② **땅의 끝**   — `measure_ground` 로 실측한 지평선 y. 거기서 키 = 0

  → 지평선 = 실측값,  K = 700 / (720 − 지평선)

이 한 줄로 배경마다 다른 원근이 잡힌다. 광장처럼 땅이 멀리 뻗은 배경은 K 가 작아
멀리 갈수록 확 작아지고, 좌판처럼 담이 가까운 배경은 K 가 커서 조금만 가도 작아진다.

## 나오는 것 — 앵커 파일의 `stage` 칸
    "stage": { "horizon": 544, "k": 3.977, "front_h": 700 }

    python W1_2/stage_solve.py            # 배경마다 풀어서 표로 보여준다
    python W1_2/stage_solve.py --write    # 앵커 파일에 적는다
    python W1_2/stage_solve.py --sheet    # 캐릭터를 여러 자리에 세운 확인 그림
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
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

ANCHOR_DIR = "assets/anchors"
BG_DIR = "W1_2/bg"
OUT = "W1_2/_stage"
FONT = r"C:\Windows\Fonts\malgun.ttf"
W, H = 1280, 720

# ★표준 — 화면 맨 앞(발이 y=720)에 선 **스틱맨의 키 700** (사장님 확정 2026-08-13)
FRONT_H = 700.0
# 캐릭터별 실물 키 비율 (char_heights · 스틱맨 700 을 1.0 으로)
CHAR_RATIO = {"stickman": 1.000, "zman": 711 / 700.0, "zgirl": 651 / 700.0}
SUB_MAX_H = 600.0                  # 보조역 상한 (사장님 확정)


class BgStage(object):
    """배경 하나의 무대 — 발 y ↔ 키를 서로 옮긴다."""

    def __init__(self, horizon, front_h=FRONT_H, floor_y=H):
        self.horizon = float(horizon)
        self.front_h = float(front_h)
        self.k = self.front_h / max(1.0, floor_y - self.horizon)

    def h_at(self, foot_y, who="stickman"):
        """그 자리에 선 사람의 **화면 키** — 자리가 정해지면 키가 정해진다."""
        return max(0.0, self.k * (foot_y - self.horizon)) * CHAR_RATIO.get(who, 1.0)

    def foot_at(self, h, who="stickman"):
        """그 키로 보이려면 발이 있어야 할 **화면 y**."""
        return self.horizon + h / (self.k * CHAR_RATIO.get(who, 1.0))

    def walkable(self, foot_y):
        return self.horizon + 2 <= foot_y <= H


def load(bg):
    p = os.path.join(ANCHOR_DIR, bg + ".json")
    if not os.path.exists(p):
        return {}, p
    with open(p, encoding="utf-8") as f:
        return json.load(f), p


def bgs_all():
    return sorted(set(
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join(BG_DIR, "*.mp4"))
        + glob.glob(os.path.join(BG_DIR, "*.png"))
        if not os.path.basename(p).startswith("_")))


def first_frame(bg):
    png = os.path.join(BG_DIR, bg + ".png")
    if os.path.exists(png):
        return Image.open(png).convert("RGB").resize((W, H), Image.LANCZOS)
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_f.png")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i",
                    os.path.join(BG_DIR, bg + ".mp4"), "-frames:v", "1", tmp],
                   check=True)
    return Image.open(tmp).convert("RGB").resize((W, H), Image.LANCZOS)


def sheet(bg, st):
    """같은 캐릭터를 여러 자리에 세워 **키가 자리대로 정해지는지** 눈으로 본다."""
    import render_show as R
    cv = first_frame(bg).convert("RGBA")
    poses = R.load_poses()
    im = R.img(poses["sm_arms_out_wide"])
    d = ImageDraw.Draw(cv)
    f = ImageFont.truetype(FONT, 15)

    ys = [H - 6, H - 60, H - 130, H - 210]
    ys += [round(st.horizon + (H - st.horizon) * r) for r in (0.30, 0.16, 0.07)]
    xs = [150, 340, 540, 740, 900, 1030, 1150]
    for x, y in zip(xs, sorted(ys, reverse=True)):
        h = st.h_at(y)
        if h < 8:
            continue
        s = min(1.0, h / im.height)
        w2 = max(1, int(im.width * s))
        h2 = max(1, int(im.height * s))
        cv.alpha_composite(im.resize((w2, h2), Image.LANCZOS),
                           (int(x - w2 / 2), int(y - h2)))
        d.line([(x - 46, y), (x + 46, y)], fill=(230, 40, 40), width=2)
        d.text((x - 44, y + 3), "발%d 키%d" % (y, round(h)), font=f, fill=(210, 0, 0))
    d.line([(0, st.horizon), (W, st.horizon)], fill=(0, 130, 255), width=2)
    d.text((10, st.horizon - 24), "지평선 y=%d" % st.horizon,
           font=ImageFont.truetype(FONT, 19), fill=(0, 90, 220))
    d.text((10, 8), "%s — 앞줄(발720) 키 %d · K=%.3f"
           % (bg, FRONT_H, st.k), font=ImageFont.truetype(FONT, 21),
           fill=(255, 235, 0))
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "%s_stage.png" % bg)
    cv.convert("RGB").save(p)
    return p


def main():
    write = "--write" in sys.argv
    do_sheet = "--sheet" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    print("%-17s %7s %7s   %s" % ("배경", "지평선", "K", "발 y 별 스틱맨 키"))
    for bg in (args or bgs_all()):
        doc, p = load(bg)
        g = doc.get("ground")
        if not g:
            print("  %-15s ★땅 실측이 없다 — measure_ground.py 를 먼저 돌려라" % bg)
            continue
        st = BgStage(g["horizon"])
        row = " ".join("%d:%d" % (y, round(st.h_at(y)))
                       for y in (720, 680, 640, 600, 560))
        print("  %-15s %7d %7.3f   %s" % (bg, st.horizon, st.k, row))

        if write:
            doc["stage"] = {"horizon": st.horizon, "k": round(st.k, 4),
                            "front_h": FRONT_H, "sub_max_h": SUB_MAX_H,
                            "note": "키 = k × (발y − 지평선). 앞줄(발 720) 스틱맨 700 "
                                    "기준으로 실측 지평선에서 푼 값."}
            with open(p, "w", encoding="utf-8") as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
        if do_sheet:
            print("      확인 그림 →", sheet(bg, st))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
