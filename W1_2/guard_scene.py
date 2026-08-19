# -*- coding: utf-8 -*-
"""수문장 교대 씬 — **멀리서 다가와 · 돌아서서 멀어졌다가 · 다시 걸어와 선다.**

★사장님 지시(2026-08-13) "만든 배경 수문장 행진부터 제대로 만들어서 보자.
  가능한 한 멀리 갔다가 돌아왔다가 하자."

## 무대 실측 (`W1_2/_check/gate_ground.png`)
  키 = **1.352 × (발y − 408)** — 배경에 그려진 실루엣 사람들을 자로 삼아 맞췄다.
  잔차 4.5px. 발y 700 에서 395px 로, 우리 나레이터 기준 400 과 맞아떨어진다.

  ※길 경계선을 이어 구한 소실점은 y=321 이라 이 값과 다르다. 그림이라 기하가
    정확하지 않은 것인데, **캐릭터는 배경 사람들 옆에 서야 하므로** 사람 쪽을 따랐다.

  걷는 길 — 발y 430(키 30, 저 문 앞)에서 700(키 395, 화면 앞)까지.
  길 한가운데 x = −0.27y + 775.5 (좌우 경계선의 가운데)

## 배경
`perf_guard_gate.mp4` 는 Flow 가 8초에 좌우 12px 흘려 놔서 `stabilize_bg.py` 로
고정했다(남은 흔들림 2px). 16초를 채우려고 **앞으로 8초 + 거꾸로 8초**로 잇는다 —
그냥 두 번 돌리면 열린 문이 갑자기 닫혀 튄다. 거꾸로 이으면 문이 열렸다 닫히는
자연스러운 움직임이 된다.

## 걸음 — 한 스트라이드 0.2초, 좌표는 거기에 물려 돈다
★사장님 지시 "한 스트라이드의 속도를 0.2초 정도로 빠르게 걷고, 원근을 이용한
  좌표 이동도 걷기 속도에 착착 맞추어서 하자."

**시간이 좌표를 끌지 않는다. 걸음이 좌표를 끈다.**
스트라이드마다 땅에서 실제로 나아가는 거리는 늘 같다(보폭 L = 0.75 × 제 키).
핀홀 기하로 풀면, 깊이 Z 와 화면의 u(=발y − 지평선) 는 `Z = f·Hc/u` 이므로

    1/u₂ = 1/u₁ − L/(f·Hc)

즉 **1/u 가 스트라이드마다 똑같이 줄어든다.** 그래서 좌표는 y 가 아니라 **1/u 를
일정하게 밀어** 정한다. 그러면 멀리서는 화면에서 찔끔, 가까이 와서는 성큼성큼
움직이는 진짜 원근 이동이 된다(가까울수록 한 걸음이 화면을 많이 먹는다).

  보폭 계수 α=0.75 · 초점거리 f≈1108px(가로 1280, 화각 60도) · K=1.352
  → 스트라이드당 Δ(1/u) = α·K/f = 9.15e-4
  발y 435→700 이면 Δ(1/u)=0.0336 이라 **약 37스트라이드**, 0.2초씩이면 7.3초.
  땅으로 치면 37 × 0.75 × 키 ≈ 47m — 저 문까지의 거리와 얼추 맞는다.

컷은 시간이 아니라 **스트라이드 진행률**로 넘긴다.
  정면 행진 64컷 = 4스트라이드 → 16컷/스트라이드
  후면 걷기 32컷 = 약 1.5스트라이드 → 21컷/스트라이드

    python W1_2/guard_scene.py
"""
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

from cut_motion6 import body_top                    # noqa: E402
from color_guard import color_cut                   # noqa: E402  ★복색을 입힌 컷

BG = "W1_2/bg/perf_guard_gate.mp4"
OUT = "W1_2/motion6/guard_scene.mp4"
TMP = "W1_2/_guard"
W, H, FPS = 1280, 720, 24

K, HOR = 1.352, 408.0                # 키 = K × (발y − HOR)
FAR, NEAR = 435.0, 700.0             # 걸을 수 있는 발y 범위
CUT_H = 740.0                        # 컷의 잉크 키(갓끝~발)

STRIDE_SEC = 0.30                    # ★한 스트라이드 0.3초 (사장님 지정)
STAND_CUT = 63                       # ★서 있는 모습은 **정면** — 행진 마지막 컷(차렷)
ALPHA, FOCAL = 0.75, 1108.0          # 보폭 ÷ 키 · 초점거리(px)
BETA = ALPHA * K / FOCAL             # 스트라이드당 1/u 가 줄어드는 양
CPS = {"march": 16.0, "away": 21.0}  # 스트라이드당 컷 수

MARCH = "assets/graphics/poses/m6_guard_march_%02d.png"
AWAY = "assets/graphics/poses/m6_guard_away_%02d.png"
TURN = os.path.join(TMP, "turn")     # 회전 컷 — 여기서 만든다


def path_x(y):
    return -0.27 * y + 775.5


def stand_h(y):
    return max(6.0, K * (y - HOR))


def make_turn_cuts():
    """`guard_turn` 8초 클립에서 **정면 → 후면** 180도 회전만 컷으로 뽑는다.

    회전 클립의 0~88프레임이 정면에서 뒤통수까지다(사장님이 88·96 을 고르신 그 구간).
    거기서 10장을 고르면 반 바퀴가 된다. 되돌아설 때는 이 컷을 거꾸로 쓴다.
    """
    src = "W1_2/_pick/guard_turn_raw"
    os.makedirs(TURN, exist_ok=True)
    if len(glob.glob(os.path.join(TURN, "*.png"))) == 10:
        return sorted(glob.glob(os.path.join(TURN, "*.png")))
    for f in glob.glob(os.path.join(TURN, "*.png")):
        os.remove(f)
    for i, n in enumerate(range(0, 89, 10)):
        cut = color_cut(os.path.join(src, "f%03d.png" % (n + 1)))
        a = np.asarray(cut)[:, :, 3]
        ys, xs = np.nonzero(a > 8)
        cut = cut.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
        a = np.asarray(cut)[:, :, 3]
        k = CUT_H / max(1, (a.shape[0] - body_top(a)))
        cut = cut.resize((max(1, round(cut.width * k)),
                          max(1, round(cut.height * k))), Image.LANCZOS)
        cut.save(os.path.join(TURN, "t%02d.png" % i))
    return sorted(glob.glob(os.path.join(TURN, "*.png")))


def load(pat, n):
    return [Image.open(pat % i).convert("RGBA") for i in range(n)]


def bg_frames():
    d = os.path.join(TMP, "bg")
    os.makedirs(d, exist_ok=True)
    if len(glob.glob(os.path.join(d, "*.png"))) != 192:
        for f in glob.glob(os.path.join(d, "*.png")):
            os.remove(f)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", BG,
                        os.path.join(d, "f%03d.png")], check=True)
    fs = sorted(glob.glob(os.path.join(d, "*.png")))
    return fs + fs[::-1]                      # 앞으로 8초 + 거꾸로 8초 = 16초


def strides_between(ya, yb):
    """두 발y 사이가 **몇 스트라이드**인지 — 1/u 차이를 스트라이드당 몫으로 나눈다."""
    return abs(1.0 / (ya - HOR) - 1.0 / (yb - HOR)) / BETA


def y_at(ya, yb, u):
    """걸음 진행률 u(0~1) 일 때의 발y — **1/u 를 일정하게 민다**(등속 보행)."""
    ia, ib = 1.0 / (ya - HOR), 1.0 / (yb - HOR)
    return HOR + 1.0 / (ia + (ib - ia) * u)


def y_before(y, strides):
    """`y` 에서 **뒤로 몇 스트라이드** 물러난 자리의 발y."""
    return HOR + 1.0 / (1.0 / (y - HOR) + strides * BETA)


START = y_before(NEAR, 5)                 # ★다섯 발 뒤 — 여기서 시작한다

# ── 동선 — (무엇, 시작 발y, 끝 발y, 걸리는 시간). 걷는 구간은 시간을 걸음이 정한다.
# ★사장님 지시(2026-08-13) "정면으로 보고 다섯 발 정도만 앞으로 끝까지 걸어 와서,
#   뒤로 돌아 멀리 갔다가, 다시 돌아 오는 것을 끝으로 만들자."
PLAN = [
    ("stand_far", START, START, 0.5),         # 정면으로 서 있다가
    ("walk_in", START, NEAR, None),           # 다섯 발 걸어 화면 앞까지
    ("stand", NEAR, NEAR, 0.4),
    ("turn_away", NEAR, NEAR, 0.4),           # 뒤로 돌아
    ("walk_out", NEAR, FAR, None),            # 저 문 앞까지 멀리
    ("turn_back", FAR, FAR, 0.4),             # 되돌아서서
    ("walk_in2", FAR, NEAR, None),            # 다시 걸어와
    ("stand", NEAR, NEAR, 0.8),               # 정면으로 선다 — 끝
]


def main():
    march = load(MARCH, 64)
    away = load(AWAY, 32)
    turn = [Image.open(p).convert("RGBA") for p in make_turn_cuts()]
    # 구간마다 걸리는 시간을 **걸음이** 정한다 — 걷는 구간은 스트라이드 수 × 0.2초
    segs, t = [], 0.0
    for what, ya, yb, dur in PLAN:
        if dur is None:
            ns = strides_between(ya, yb)
            dur = ns * STRIDE_SEC
        segs.append((t, t + dur, what, ya, yb))
        t += dur
    total = t
    print("구간          시작   끝   발y        스트라이드")
    for t0, t1, what, ya, yb in segs:
        ns = strides_between(ya, yb) if what.startswith("walk") else 0
        print("  %-11s %5.1f %5.1f  %4.0f→%4.0f  %5.1f" % (what, t0, t1, ya, yb, ns))
    print("  합계 %.1f초\n" % total)

    bgs = bg_frames()
    n = int(round(total * FPS))
    od = os.path.join(TMP, "out")
    os.makedirs(od, exist_ok=True)
    for f in glob.glob(os.path.join(od, "*.png")):
        os.remove(f)

    log = []
    for i in range(n):
        t = i / float(FPS)
        t0, t1, what, ya, yb = segs[-1]
        for s in segs:
            if t < s[1]:
                t0, t1, what, ya, yb = s
                break
        u = 0.0 if t1 <= t0 else min(1.0, max(0.0, (t - t0) / (t1 - t0)))

        if what.startswith("walk"):
            y = y_at(ya, yb, u)               # ★1/u 를 일정하게 — 등속 보행
            # 컷은 **스트라이드 진행률**로 넘긴다 (0.2초에 한 스트라이드)
            st = (t - t0) / STRIDE_SEC
            if what == "walk_out":
                src = away[int(st * CPS["away"]) % len(away)]
            else:
                src = march[int(st * CPS["march"]) % len(march)]
        else:
            y = ya
            if what == "turn_away":
                src = turn[min(len(turn) - 1, int(u * len(turn)))]
            elif what == "turn_back":
                src = turn[::-1][min(len(turn) - 1, int(u * len(turn)))]
            else:
                src = march[STAND_CUT]        # ★서 있을 때는 정면 차렷
        h = stand_h(y)

        k = h / CUT_H
        cw = max(1, round(src.width * k))
        ch = max(1, round(src.height * k))
        ch_im = src.resize((cw, ch), Image.LANCZOS)
        # 발을 땅에 붙인다 — 컷 아래끝이 곧 발바닥
        cx = path_x(y)
        cv = Image.open(bgs[i % len(bgs)]).convert("RGB")   # 앞·뒤로 계속 오간다
        cv.paste(ch_im, (int(cx - cw / 2), int(y - ch)), ch_im)
        cv.save(os.path.join(od, "f%03d.png" % i))
        if i % 24 == 0:
            log.append((t, what, y, h))

    print("시각  구간         발y   키")
    for t, w, y, h in log:
        print("%4.1f  %-11s %4.0f %4.0f" % (t, w, y, h))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(od, "f%03d.png"), "-c:v", "libx264",
                    "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    OUT], check=True)
    print("\n%s  %d프레임 · %dfps · %.1f초" % (OUT, n, FPS, n / float(FPS)))


if __name__ == "__main__":
    main()
