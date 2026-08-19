# -*- coding: utf-8 -*-
"""블록 3 — 광화문 앞 (34초) · 첫 단어 **아이** 와 **이**.

★사장님 지시(2026-08-14) "이거 모두 다 잘 써야 하는 중요한 장소 씬이구만.
  만들어서 하나하나 보여라. 3부터 만들어서 보여줘 봐 — 캐릭터 워크와 동영상."

## 무대 실측 (`W1_2/_check/pg_grid.png`)
이 배경에는 **사람이 없다.** 비둘기와 해태 석상뿐이라 실루엣으로 못 잰다.
그래서 기하로 잡았다 — 문 아랫단이 땅과 만나는 **y 440 을 지평선**으로 두고,
우리 나레이터 규격(화면 앞 400px)에 맞춰 기울기를 푼다.

  키 = 1.538 × (발y − 440)
    발y 700 → 400 (앞에서 설명하는 자리)
    발y 560 → 185 (계단 앞 먼 자리)

  밟을 수 있는 땅 — y 545~715. 좌우 해태 석상 자리(x<170, x>1120)는 피한다.

## 동작 — 세 문장에 맞춰
  ① 왼쪽에서 걸어 들어와 가운데 왼편에 선다 → **아이** 를 소개
  ② 오른쪽으로 두 걸음, 한 걸음마다 **아** — **이** 를 끊어 준다
  ③ 가운데 오른편으로 걸어가 제 입을 가리키며 **이**(치아)

    python W1_2/block3_scene.py            # 렌더
    python W1_2/block3_scene.py --check    # 크기만 확인
"""
import argparse
import glob
import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

BG = "W1_2/bg/plaza_gate.mp4"
TMP = "W1_2/_b3"
W, H, FPS = 1280, 720, 24
SEC = 34.0

HOR, K = 440.0, 1.538
NEAR, MID, FAR = 700.0, 640.0, 585.0
# ★정상 걸음 = 한 스트라이드 **1초** (사장님 지적 2026-08-14 "너무 빠르다").
#   달리기는 0.3초, 수문장 행진은 0.3초였지만 **평범하게 걷는 것은 1초**다.
#   0.42초로 뒀더니 종종거리며 뛰어가는 것처럼 보였다.
STRIDE_SEC = 1.0                        # 걷기 한 스트라이드
CPS = 32.0                              # 스트라이드당 컷 수 (walk_side 64컷 = 2스트라이드)


def h_at(y):
    return max(8.0, K * (y - HOR))


def cuts(d):
    return [Image.open(p).convert("RGBA")
            for p in sorted(glob.glob(os.path.join("W1_2/motion6_cuts", d, "*.png")))]


def bg_frames(n):
    dd = os.path.join(TMP, "bg")
    os.makedirs(dd, exist_ok=True)
    if not glob.glob(dd + "/*.png"):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", BG,
                        os.path.join(dd, "f%03d.png")], check=True)
    fs = sorted(glob.glob(dd + "/*.png"))
    pp = fs + fs[::-1]
    return [pp[i % len(pp)] for i in range(n)]


def put(cv, src, x, y, flip=False):
    """발바닥을 y 에 딱 붙이고, 키는 그 자리가 정한다."""
    if flip:
        src = ImageOps.mirror(src)
    h = h_at(y)
    k = h / float(src.height)
    im = src.resize((max(1, round(src.width * k)), max(1, round(h))), Image.LANCZOS)
    a = np.asarray(im)[:, :, 3] > 8
    rows = np.nonzero(a.any(1))[0]
    sole = int(rows[-1]) if len(rows) else im.height - 1
    cv.paste(im, (int(round(x - im.width / 2.0)), int(round(y)) - sole), im)


# ★말할 때는 **정면 차렷**, 가리킬 때는 **손 든 컷**을 쓴다 (2026-08-14).
#   앞판에서 걷기 컷을 그대로 세워 놔서 옆모습으로 서서 말했다.
STAND = ("sit_stand_front", 2)           # 정면 차렷
POINT = ("high_five", 36)                # 손 들어 가리키기

# ── 동선 — (끝나는 시각, 무엇, 시작x, 끝x, 발y)
#   ★시작 x 를 화면 안으로 들였다 — 180 이면 해태 석상에 겹쳐 잘려 보였다.
# ★거리도 걸음에 맞춘다. 이 무대의 한 스트라이드는 대략 **키의 0.75배**니
#   발y 640(키 307)에서 230px, 발y 700(키 400)에서 300px 이다.
#   시간만 늘리고 거리를 그대로 두면 발이 땅에서 미끄러진다.
PLAN = [
    (1.0,  "walk",  300.0, 530.0, MID),      # 한 스트라이드 = 230px
    (13.0, "talk",  530.0, 530.0, MID),      # ① 아이 소개
    (13.5, "step",  530.0, 645.0, MID),      # ② 아 —  (반 스트라이드)
    (14.0, "step",  645.0, 760.0, MID),      #    이    (반 스트라이드)
    (23.0, "point", 760.0, 760.0, MID),      #    따라 해 보세요 (손 들고)
    (23.5, "walk",  760.0, 910.0, NEAR),     # ③ 앞으로 반 스트라이드
    (34.0, "point", 910.0, 910.0, NEAR),     #    이(치아) 가리키기
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    walk = cuts("walk_side")
    stand = cuts(STAND[0])[STAND[1]]
    point = cuts(POINT[0])[POINT[1]]
    print("컷 — 걷기 %d · 정면차렷 %s · 가리키기 %s" % (len(walk), STAND, POINT))

    if a.check:
        bgs = bg_frames(1)
        cv = Image.open(bgs[0]).convert("RGB")
        for x, y in ((300, FAR), (640, MID), (980, NEAR)):
            put(cv, stand, x, y)
            ImageDraw.Draw(cv).text((x - 40, y + 4), "y%d h%d" % (y, h_at(y)), fill=(255, 60, 60))
        cv.save("W1_2/_check/b3_fit.png")
        print("W1_2/_check/b3_fit.png")
        return 0

    n = int(SEC * FPS)
    bgs = bg_frames(n)
    od = os.path.join(TMP, "out")
    os.makedirs(od, exist_ok=True)
    for f in glob.glob(od + "/*.png"):
        os.remove(f)
    t0 = 0.0
    seg = 0
    for i in range(n):
        t = i / float(FPS)
        while seg < len(PLAN) - 1 and t >= PLAN[seg][0]:
            t0 = PLAN[seg][0]
            seg += 1
        t1, what, xa, xb, y = PLAN[seg]
        u = 0.0 if t1 <= t0 else min(1.0, max(0.0, (t - t0) / (t1 - t0)))
        x = xa + (xb - xa) * u
        if what in ("walk", "step"):
            st = (t - t0) / STRIDE_SEC
            src = walk[int(st * CPS) % len(walk)]
        elif what == "point":
            src = point
        else:
            src = stand
        cv = Image.open(bgs[i]).convert("RGB")
        put(cv, src, x, y)
        cv.save(os.path.join(od, "f%04d.png" % i))

    v = 1 + len(glob.glob("W1_2/motion6/block3_v*.mp4"))
    out = "W1_2/motion6/block3_v%d.mp4" % v
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(od, "f%04d.png"), "-c:v", "libx264",
                    "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], check=True)
    print("%s  %d프레임 · %.1f초" % (out, n, n / float(FPS)))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
