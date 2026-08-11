# -*- coding: utf-8 -*-
"""왔다 갔다 하는 장면 — 스틱맨은 **앞에서**, 졸라맨은 **아주 멀리서**.

★원근 규칙으로 키가 자동 결정된다: 키(px) = k × (발y − 지평선y)
  두 사람은 각자의 바닥선(발 y)이 다르므로 크기가 자동으로 갈린다.
★걷기 한 스트라이드 0.75초(9프레임 · 12fps).
★그리기 순서 — 먼 것부터: 졸라맨(멀리) → 벤치 가림 → 졸라걸(앉기) → 스틱맨(앞)
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
OUT = "W1_2/clips/walk_scene.mp4"
TMP = "W1_2/_scenebuf"
BENCH_BOX = (700, 380, 1270, 630)

FPS = 12                     # 걷기 9프레임 = 0.75초
DUR = 12.0                   # 전체 길이(초)
STICK_FOOT = 700             # 스틱맨 바닥선 — 앞
ZOLLA_FOOT = 512             # 졸라맨 바닥선 — 아주 멀리
STICK_X = (150, 620)         # 왕복 구간
ZOLLA_X = (430, 900)
GIRL_RATIO = 0.917
SIT_SCALE = 0.72


def trim(im):
    a = np.asarray(im.convert("RGBA"))[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    return im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))


def w24r_walk(char):
    """★W24R 에 7캐릭터 좌/우 걷기가 **이미 다 있다**(사장님 지시 2026-08-11).

    `W24R/poses/w24r_<캐릭터>_walkr_0~N.png` / `_walkl_0~N.png`
    인준·스틱맨 9프레임 · 지은·마담제이·티쳐제이 8 · 졸라맨·졸라걸 7.
    ★새로 뽑지 마라. 이걸 그대로 쓴다.
    """
    r = [trim(Image.open(p)) for p in
         sorted(glob.glob("W24R/poses/w24r_%s_walkr_*.png" % char))]
    l = [trim(Image.open(p)) for p in
         sorted(glob.glob("W24R/poses/w24r_%s_walkl_*.png" % char))]
    if not r or not l:
        raise RuntimeError("걷기 컷 없음: " + char)
    return r, l


def pingpong(t, a, b, period):
    """a↔b 를 period 초에 한 번 왕복. (x, 오른쪽으로 가는 중인가)"""
    u = (t % period) / period
    if u < 0.5:
        return a + (b - a) * (u * 2), True
    return b + (a - b) * ((u - 0.5) * 2), False


def main():
    d = I.load_anchors(BG_KEY)
    persp = d["perspective"]
    seat = d["anchors"]["bench_seat"]
    bg = Image.open(BG).convert("RGBA")

    stick_r, stick_l = w24r_walk("stickman")        # 9프레임
    zol_r, zol_l = w24r_walk("zollaman")            # 7프레임
    print("걷기 프레임 — 스틱맨 %d · 졸라맨 %d" % (len(stick_r), len(zol_r)))

    # 벤치에 앉은 졸라걸 — 매 프레임 같으므로 미리 만든다
    stand = I.perspective_height(seat["y"] + 90, persp["horizon_y"],
                                 persp["ref_foot_y"], persp["ref_h"], GIRL_RATIO)
    gh = int(round(stand * SIT_SCALE))
    girl = Image.open("W1_2/_poses/stickman_zolla_girl_sit_bench.png").convert("RGBA")
    girl = girl.resize((max(1, round(girl.width * gh / girl.height)), gh), Image.LANCZOS)
    girl_hip = int(gh * 0.62)

    mask = I.make_occ_mask(BG, BENCH_BOX, "W1_2/_check/bench_mask.png", I.wood_mask)

    h_stick = I.perspective_height(STICK_FOOT, persp["horizon_y"],
                                   persp["ref_foot_y"], persp["ref_h"])
    h_zolla = I.perspective_height(ZOLLA_FOOT, persp["horizon_y"],
                                   persp["ref_foot_y"], persp["ref_h"])
    print("스틱맨 발 y%d → %dpx · 졸라맨 발 y%d → %dpx"
          % (STICK_FOOT, h_stick, ZOLLA_FOOT, h_zolla))

    os.makedirs(TMP, exist_ok=True)
    for f in glob.glob(os.path.join(TMP, "*.png")):
        os.remove(f)

    n = int(DUR * FPS)
    for i in range(n):
        t = i / FPS
        comp = bg.copy()

        # ① 졸라맨 — 아주 멀리서 왕복 (6초에 한 번)
        zx, zr = pingpong(t, *ZOLLA_X, period=6.0)
        seq = zol_r if zr else zol_l
        zi = seq[i % len(seq)]
        zim = zi.resize((max(1, round(zi.width * h_zolla / zi.height)),
                         int(round(h_zolla))), Image.LANCZOS)
        comp.alpha_composite(zim, (int(zx - zim.width / 2),
                                   int(ZOLLA_FOOT - zim.height)))

        # ② 벤치로 가리기
        comp = I.occlude(bg, comp, mask)

        # ③ 졸라걸 — 벤치에 앉아 있다
        comp.alpha_composite(girl, (int(1120 - girl.width / 2),
                                    int(seat["y"] - girl_hip)))

        # ④ 스틱맨 — 앞에서 왕복 (8초에 한 번)
        sx, sr = pingpong(t, *STICK_X, period=8.0)
        seq = stick_r if sr else stick_l
        si = seq[i % len(seq)]
        sim = si.resize((max(1, round(si.width * h_stick / si.height)),
                         int(round(h_stick))), Image.LANCZOS)
        comp.alpha_composite(sim, (int(sx - sim.width / 2),
                                   int(STICK_FOOT - sim.height)))

        comp.convert("RGB").save(os.path.join(TMP, "f%04d.png" % i))

    os.makedirs("W1_2/clips", exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(TMP, "f%04d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", OUT], check=True)
    print("✅ %s  %dKB · %d프레임 · %.1f초"
          % (OUT, os.path.getsize(OUT) // 1024, n, DUR))


if __name__ == "__main__":
    main()
