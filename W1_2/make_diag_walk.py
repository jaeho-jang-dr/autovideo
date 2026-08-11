# -*- coding: utf-8 -*-
"""대각선 걷기 — 멀리서 가까이 오면서 옆으로 이동한다.

★핵심: 발 y 가 프레임마다 바뀌므로 **원근 규칙이 매 프레임 키를 다시 계산**한다.
  멀 때는 작고, 다가올수록 커진다. 손으로 크기를 조절하지 않는다.

★걷기 속도도 원근을 따른다 — 멀리 있을 때는 화면상 이동이 느리고 가까울수록 빠르다.
  같은 보폭이라도 원근 때문에 화면에서 다르게 보이기 때문이다.
"""
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import interactrang as I                                    # noqa: E402

BG_KEY = "gwanghwamun_bench"
BG = "W1_2/bg/gwanghwamun_bench.png"
OUT = "W1_2/clips/diag_walk.mp4"
TMP = "W1_2/_diagbuf"
BENCH_BOX = (700, 380, 1270, 630)
FPS = 12
GIRL_RATIO = 0.917
SIT_SCALE = 0.72


def trim(im):
    a = np.asarray(im.convert("RGBA"))[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    return im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))


def w24r_walk(char):
    r = [trim(Image.open(p)) for p in
         sorted(glob.glob("W24R/poses/w24r_%s_walkr_*.png" % char))]
    l = [trim(Image.open(p)) for p in
         sorted(glob.glob("W24R/poses/w24r_%s_walkl_*.png" % char))]
    return r, l


def ease(t):
    return t * t * (3 - 2 * t)


def main():
    d = I.load_anchors(BG_KEY)
    persp = d["perspective"]
    seat = d["anchors"]["bench_seat"]
    bg = Image.open(BG).convert("RGBA")
    stick_r, stick_l = w24r_walk("stickman")
    zol_r, zol_l = w24r_walk("zollaman")

    # 벤치에 앉은 졸라걸(고정)
    stand = I.perspective_height(seat["y"] + 90, persp["horizon_y"],
                                 persp["ref_foot_y"], persp["ref_h"], GIRL_RATIO)
    gh = int(round(stand * SIT_SCALE))
    girl = Image.open("W1_2/_poses/stickman_zolla_girl_sit_bench.png").convert("RGBA")
    girl = girl.resize((max(1, round(girl.width * gh / girl.height)), gh), Image.LANCZOS)
    girl_hip = int(gh * 0.62)
    mask = I.make_occ_mask(BG, BENCH_BOX, "W1_2/_check/bench_mask.png", I.wood_mask)

    # ── 대각선 경로 (사장님 지시 2026-08-11) ─────────────────────────────
    #  **왼편에서 우측으로 걸으면서 저 멀리 대각선 우측 끝으로 걸어 나간다.**
    #  발 y 가 올라가므로(멀어지므로) 원근 규칙이 키를 계속 줄인다 → **안 보일 때까지**.
    # ★화면 **밖으로 완전히 나갈 때까지** 간다 — x 를 화면 폭(1376)보다 크게 잡는다
    S_FROM, S_TO = (120, 730), (1560, 486)       # (x, 발y) — 왼편 앞 → 우측 화면 밖
    # ★**깊이(전후방)는 그대로, 좌우만 빠르게**(사장님 지시 2026-08-11).
    #   두 축을 분리한다 — 좌우는 앞부분에서 빨리 지나가고(X_POW<1),
    #   깊이(발 y)는 등속으로 천천히 물러난다.
    X_POW = 0.42
    DUR = 10.0
    n = int(DUR * FPS)

    os.makedirs(TMP, exist_ok=True)
    for f in glob.glob(os.path.join(TMP, "*.png")):
        os.remove(f)

    for i in range(n):
        u = i / max(1, n - 1)
        comp = bg.copy()

        # ★두 축 분리 — 좌우는 빠르게(앞부분에서 성큼), 깊이는 등속으로 천천히
        ux = u ** X_POW
        sx = S_FROM[0] + (S_TO[0] - S_FROM[0]) * ux
        sy = S_FROM[1] + (S_TO[1] - S_FROM[1]) * u
        sh = I.perspective_height(sy, persp["horizon_y"], persp["ref_foot_y"],
                                  persp["ref_h"])
        si = stick_r[i % len(stick_r)]           # 오른쪽 걷기
        sim = si.resize((max(1, round(si.width * sh / si.height)), int(round(sh))),
                        Image.LANCZOS)

        # ★멀리 가면 벤치 **뒤**로 지나가야 한다 — 벤치 바닥선(y630)보다 위면 가려진다
        behind = sy < 630
        if behind:
            comp.alpha_composite(sim, (int(sx - sim.width / 2), int(sy - sim.height)))
            comp = I.occlude(bg, comp, mask)
        else:
            comp = I.occlude(bg, comp, mask)

        # 졸라걸 — 벤치에 앉아 있다
        comp.alpha_composite(girl, (int(1120 - girl.width / 2),
                                    int(seat["y"] - girl_hip)))

        if not behind:                            # 아직 벤치보다 앞이면 맨 위에 그린다
            comp.alpha_composite(sim, (int(sx - sim.width / 2), int(sy - sim.height)))

        comp.convert("RGB").save(os.path.join(TMP, "f%04d.png" % i))

    os.makedirs("W1_2/clips", exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(TMP, "f%04d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", OUT], check=True)

    h0 = I.perspective_height(S_FROM[1], persp["horizon_y"], persp["ref_foot_y"],
                              persp["ref_h"])
    h1 = I.perspective_height(S_TO[1], persp["horizon_y"], persp["ref_foot_y"],
                              persp["ref_h"])
    print("스틱맨 걸어나감  %3.0fpx → %3.0fpx  (발 y%d→%d)"
          % (h0, h1, S_FROM[1], S_TO[1]))
    print("✅ %s  %dKB · %d프레임 · %.1f초"
          % (OUT, os.path.getsize(OUT) // 1024, n, DUR))


if __name__ == "__main__":
    main()
