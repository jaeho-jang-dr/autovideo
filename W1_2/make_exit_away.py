# -*- coding: utf-8 -*-
"""왼편 앞에서 **설명하다가 → 오른쪽으로 달려 → 돌아서서 → 뒤 구석으로 사라진다.**

★사장님 지시(2026-08-11): "뒤로 달려 나가면서 그것만 실행하고, 좌표를 저 멀리
  또 오른편으로 이동하면서 사이즈를 줄이면 우측으로 달려 나가는 것처럼 만들 수 있다."

다리 동작이 약해도 상관없다 — **좌표 이동 + 원근 축소**가 동시에 일어나면
달려 나가는 것으로 읽힌다. 그 세 가지가 한 프레임 안에서 같이 변해야 한다.

★크기는 손으로 정하지 않는다. **발 y 를 움직이면 원근 규칙이 키를 정한다.**

## 네 구간
| 구간 | 하는 일 | 발 y | 키 |
|---|---|---|---|
| talk | 왼편 앞에 서서 설명(입모양 순환) | 706 고정 | 573 고정 |
| run  | 측면으로 오른쪽으로 달려 나간다   | 706 고정 | 573 고정 |
| turn | 90도 → 180도(뒷모습)로 돈다      | 706 고정 | 573 고정 |
| away | 뒷모습 스트라이드로 멀어진다      | 706→497 | 573→43 |

## 이음매가 안 튀게 하는 법
- **키**: talk·run·turn 이 전부 발 y=706 위에 있으므로 원근 키가 같다. away 도
  발 y=706 에서 시작하니 세 이음매 모두 키가 **같은 값**으로 이어진다.
- **x**: 각 구간의 x 를 앞 구간이 끝난 값에서 이어 받는다.
- **속도**: away 구간의 **처음 속도**에 달리기 속도를 맞춘다.
  away 는 x = X0 + (X1-X0)*(1-(1-u)^1.9) 이므로 u=0 에서 속도는 (X1-X0)*1.9/T.
  달리기는 정지에서 출발하니 0 → v 로 등가속하고 회전 구간은 v 로 등속.
      v * (T_away/1.9 + T_run/2 + T_turn) = X1 - X_START
  이 v 를 쓰면 talk→run(0에서 출발)·run→turn·turn→away 세 이음매의
  **속도까지** 연속이 된다.
"""
import argparse
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import interactrang as I                                     # noqa: E402

BG_KEY = "gwanghwamun_bench"
BG = "W1_2/bg/gwanghwamun_bench.png"
BENCH_BOX = (700, 380, 1270, 630)
CUTS = "W1_2/motion6_stride"
EXIT_CUTS = "W1_2/motion6_cuts/run_exit"
FPS = 24

# ★실측(2026-08-11 컨택트시트) — run_exit 64컷 중
#   00 = 측면 정지 · 01~23 = 오른쪽 측면 달리기 · 24~31 = 90→180 회전 · 32~63 = 뒷모습
SIDE_RANGE = (0, 24)
TURN_RANGE = (24, 32)

# 말하는 입모양 순환 — 같은 것이 연달아 오지 않게 섞어 둔 고정 패턴
TALK_POSES = ",".join("W1_2/_poses/stickman_w1d2_mouth_%s.png" % k
                      for k in ("a", "i", "o", "u", "yeo"))
TALK_ORDER = (0, 2, 1, 4, 0, 3, 1, 2, 4, 1, 0, 2, 3, 0, 4, 1)
TALK_HOLD = 4                                    # 4프레임(=6회/초)마다 입이 바뀐다


def _trim(im):
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    return im.crop((int(xs.min()), int(ys.min()),
                    int(xs.max()) + 1, int(ys.max()) + 1))


def load_cuts(key):
    return [_trim(Image.open(p).convert("RGBA"))
            for p in sorted(glob.glob(os.path.join(CUTS, key, "*.png")))]


def load_range(d, lo, hi):
    """디렉터리의 컷을 **번호 순서대로** lo~hi-1 만 가져온다.

    ★구간을 벗어나면 안 된다 — 측면 구간에 뒷모습이 섞이면 달려 나가는 방향이 깨진다.
    """
    fs = sorted(glob.glob(os.path.join(d, "*.png")))[lo:hi]
    if not fs:
        raise SystemExit("컷 없음: %s [%d:%d]" % (d, lo, hi))
    return [_trim(Image.open(p).convert("RGBA")) for p in fs]


def load_poses(spec):
    out = []
    for p in [s.strip() for s in spec.split(",") if s.strip()]:
        if not os.path.exists(p):
            raise SystemExit("포즈 없음: " + p)
        out.append(_trim(Image.open(p).convert("RGBA")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default="run_exit_back")
    ap.add_argument("--secs", type=float, default=5.0, help="멀어지는 구간(초)")
    ap.add_argument("--out", default="W1_2/clips/run_away_exit.mp4")
    ap.add_argument("--talk", type=float, default=0.0,
                    help="앞에 붙일 '설명하는' 정지 구간(초)")
    ap.add_argument("--talk-pose", default=TALK_POSES,
                    help="설명 구간에 쓸 포즈 PNG(쉼표로 여러 장 = 입모양 순환)")
    ap.add_argument("--run", type=float, default=0.0,
                    help="측면 달리기 구간(초)")
    ap.add_argument("--turn", type=float, default=0.0,
                    help="90→180 회전 구간(초)")
    a = ap.parse_args()

    d = I.load_anchors(BG_KEY)
    p = d["perspective"]
    bg = Image.open(BG).convert("RGBA")
    away_cuts = load_cuts(a.key)
    if not away_cuts:
        raise SystemExit("컷 없음: " + a.key)
    mask = I.make_occ_mask(BG, BENCH_BOX, "W1_2/_check/bench_mask.png", I.wood_mask)

    # 출발: 화면 왼쪽 앞(가깝다) · 도착: 오른쪽 뒤 구석(지평선 가까이 = 아주 작다)
    X0, Y0 = 430.0, 706.0
    X1, Y1 = 1330.0, 497.0

    n_talk = int(round(a.talk * FPS))
    n_run = int(round(a.run * FPS))
    n_turn = int(round(a.turn * FPS))
    n_away = int(a.secs * FPS)
    T_run, T_turn, T_away = n_run / FPS, n_turn / FPS, n_away / FPS

    # ★달리기 속도 v — away 구간 첫 속도와 같아지도록 푼다(위 주석 참조)
    v = (X1 - X0) / (T_away / 1.9 + T_run / 2.0 + T_turn) if n_away else 0.0
    x_run_end = X0 + 0.5 * v * T_run            # 정지→v 등가속으로 간 거리
    x_turn_end = x_run_end + v * T_turn         # v 등속

    talk_poses = load_poses(a.talk_pose) if n_talk else []
    side_cuts = load_range(EXIT_CUTS, *SIDE_RANGE) if n_run else []
    turn_cuts = load_range(EXIT_CUTS, *TURN_RANGE) if n_turn else []

    # ── 프레임 대본: (구간이름, 컷, x, 발y) ────────────────────────────────
    plan = []
    for i in range(n_talk):                       # ① 설명 — 제자리, 입만 움직인다
        k = TALK_ORDER[(i // TALK_HOLD) % len(TALK_ORDER)] % len(talk_poses)
        plan.append(("talk", talk_poses[k], X0, Y0))
    for i in range(n_run):                        # ② 측면 달리기 — 발 y 고정
        t = i / FPS
        plan.append(("run", side_cuts[min(len(side_cuts) - 1,
                                          int(i * len(side_cuts) / n_run))],
                     X0 + 0.5 * v * t * t / T_run, Y0))
    for i in range(n_turn):                       # ③ 90→180 회전 — 발 y 고정
        plan.append(("turn", turn_cuts[min(len(turn_cuts) - 1,
                                           int(i * len(turn_cuts) / n_turn))],
                     x_run_end + v * i / FPS, Y0))
    for i in range(n_away):                       # ④ 멀어진다 — 발 y 가 키를 정한다
        u = i / max(1, n_away - 1)
        # 멀어질수록 화면상 이동이 느려져야 자연스럽다 — 앞부분에서 성큼 나간다
        ux = 1.0 - (1.0 - u) ** 1.9
        plan.append(("away", away_cuts[i % len(away_cuts)],
                     x_turn_end + (X1 - x_turn_end) * ux, Y0 + (Y1 - Y0) * ux))

    tmp = "W1_2/_awaybuf"
    os.makedirs(tmp, exist_ok=True)
    for f in glob.glob(os.path.join(tmp, "*.png")):
        os.remove(f)

    seams = set()
    acc = 0
    for k in (n_talk, n_run, n_turn):
        if k:
            seams.add(max(0, acc - 1))
            seams.add(acc)
            acc += k
    rows, prev = [], None
    n = len(plan)
    for i, (seg, c, x, fy) in enumerate(plan):
        h = I.perspective_height(fy, p["horizon_y"], p["ref_foot_y"], p["ref_h"])
        w = max(1, round(c.width * h / c.height))          # ★비율 유지로만 축소
        sim = c.resize((w, max(1, int(round(h)))), Image.LANCZOS)

        comp = bg.copy()
        behind = fy < 630                      # 벤치 바닥선보다 위 = 벤치 뒤
        if behind:
            comp.alpha_composite(sim, (int(x - sim.width / 2), int(fy - sim.height)))
            comp = I.occlude(bg, comp, mask)
        else:
            comp = I.occlude(bg, comp, mask)
            comp.alpha_composite(sim, (int(x - sim.width / 2), int(fy - sim.height)))
        comp.convert("RGB").save(os.path.join(tmp, "f%04d.png" % i))

        if i in seams or i % max(1, n // 10) == 0 or i == n - 1 or seg != prev:
            rows.append((i / FPS, seg, x, fy, h, i in seams))
        prev = seg

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(tmp, "f%04d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", a.out], check=True)

    print("  %-6s %-6s %-7s %-7s %-6s" % ("시간", "구간", "x", "발y", "키px"))
    for t, seg, x, fy, h, sm in sorted(set(rows)):
        print("  %5.2fs %-6s %6.1f  %6.1f  %5.1f  %s"
              % (t, seg, x, fy, h, "← 이음매" if sm else ""))
    print("  달리기 속도 v=%.1f px/s · away 첫 속도 %.1f px/s (같아야 안 튄다)"
          % (v, (X1 - x_turn_end) * 1.9 / T_away if n_away else 0))
    print("  구간 프레임 talk %d · run %d(컷%d) · turn %d(컷%d) · away %d(컷%d)"
          % (n_talk, n_run, len(side_cuts), n_turn, len(turn_cuts),
             n_away, len(away_cuts)))
    print("✅ %s  %dKB · %d프레임 · %.2f초"
          % (a.out, os.path.getsize(a.out) // 1024, n, n / FPS))


if __name__ == "__main__":
    main()
