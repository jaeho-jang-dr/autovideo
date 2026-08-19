# -*- coding: utf-8 -*-
"""빈 블록 **3 · 6 · 10 · 12** 를 캐릭터로 채운다.

★사장님 지적(2026-08-14)
  "블록에 아무것도 없고 배경만 있다는 게 말이 되나? 이것 한글 교육 동영상이야."
  "이거 모두 다 잘 써야 하는 중요한 장소 씬이구만."

이 네 블록에 오늘 배우는 여덟 단어 중 **여섯 개**가 들어 있다 — 전체의 45%다.
배경만 두면 강의의 절반이 빈 그림이 된다.

## 무대는 배경마다 따로 잰다
사람이 그려진 배경은 실루엣 발밑으로, 사람이 없는 배경은 **기하로** 잡는다
(땅과 벽이 만나는 선 = 지평선, 화면 앞 400px = 우리 나레이터 규격).

## 걸음
정상 걸음은 **한 스트라이드 1초**. 거리도 같이 맞춘다 — 한 스트라이드가 나아가는
거리는 대략 **제 키의 0.75배**다. 시간만 늘리고 거리를 그대로 두면 발이 미끄러진다.

## 자세
말할 때 **정면 차렷**(`sit_stand_front_02`), 가리킬 때 **손 든 컷**(`high_five_36`).
걷기 컷을 그대로 세워 두면 옆모습으로 서서 말하게 된다.

    python W1_2/blocks_scene.py 3          # 하나만
    python W1_2/blocks_scene.py --all      # 넷 다
    python W1_2/blocks_scene.py 6 --check  # 크기만
"""
import argparse
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

W, H, FPS = 1280, 720, 24
STRIDE_SEC = 1.0                          # ★정상 걸음
CPS = 32.0                                # walk_side 64컷 = 2스트라이드
STAND = ("sit_stand_front", 2)
POINT = ("high_five", 36)
SIT = ("sit_stand_front", 40)             # 앉은 자세

# 블록 = 배경 · 길이 · 지평선 · 앞줄키 · 걷는 발y(먼·중간·앞) · 동선
BLOCKS = {
 3: dict(bg="W1_2/bg/plaza_gate.mp4", sec=34.0, hor=440.0, front=400.0,
         ys=(585.0, 640.0, 700.0),
         plan=[(1.0, "walk", 300, 530, 1), (13.0, "talk", 530, 530, 1),
               (13.5, "step", 530, 645, 1), (14.0, "step", 645, 760, 1),
               (23.0, "point", 760, 760, 1), (23.5, "walk", 760, 910, 2),
               (34.0, "point", 910, 910, 2)]),
 6: dict(bg="W1_2/bg/stall_cuke.mp4", sec=60.0, hor=430.0, front=400.0,
         ys=(575.0, 635.0, 700.0),
         plan=[(1.2, "walk", 260, 500, 1), (16.0, "point", 500, 500, 1),
               (17.0, "walk", 500, 730, 1), (31.0, "point", 730, 730, 1),
               (32.0, "walk", 730, 880, 2), (45.0, "talk", 880, 880, 2),
               (46.0, "walk", 880, 620, 1), (60.0, "sit", 620, 620, 1)]),
 10: dict(bg="W1_2/bg/bench_pair.png", sec=40.0, hor=430.0, front=400.0,
          ys=(575.0, 635.0, 700.0),
          plan=[(1.0, "walk", 300, 530, 1), (14.0, "talk", 530, 530, 1),
                (14.6, "step", 530, 640, 1), (26.0, "point", 640, 640, 1),
                (26.6, "walk", 640, 790, 2), (40.0, "talk", 790, 790, 2)]),
 12: dict(bg="W1_2/bg/dusk_lanterns.mp4", sec=46.0, hor=445.0, front=400.0,
          ys=(590.0, 645.0, 700.0),
          plan=[(1.0, "walk", 300, 530, 1), (17.0, "point", 530, 530, 1),
                (18.0, "walk", 530, 760, 1), (32.0, "talk", 760, 760, 1),
                (32.5, "walk", 760, 910, 2), (43.0, "point", 910, 910, 2),
                (46.0, "talk", 910, 910, 2)]),
}


def cuts(d):
    return [Image.open(p).convert("RGBA")
            for p in sorted(glob.glob(os.path.join("W1_2/motion6_cuts", d, "*.png")))]


def bg_frames(bg, n, tag):
    dd = os.path.join("W1_2/_blk", tag)
    os.makedirs(dd, exist_ok=True)
    if bg.endswith(".png"):
        return [bg] * n
    if not glob.glob(dd + "/*.png"):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", bg,
                        "-vf", "scale=%d:%d" % (W, H), os.path.join(dd, "f%03d.png")], check=True)
    fs = sorted(glob.glob(dd + "/*.png"))
    pp = fs + fs[::-1]
    return [pp[i % len(pp)] for i in range(n)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ns", nargs="*", type=int)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    ns = sorted(BLOCKS) if a.all else (a.ns or [3])

    walk = cuts("walk_side")
    stand = cuts(STAND[0])[STAND[1]]
    point = cuts(POINT[0])[POINT[1]]
    sit = cuts(SIT[0])[SIT[1]]

    for n in ns:
        b = BLOCKS[n]
        hor, k = b["hor"], b["front"] / (H - b["hor"])
        ys = b["ys"]

        def h_at(y):
            return max(8.0, k * (y - hor))

        def put(cv, src, x, y):
            hh = h_at(y)
            s = hh / float(src.height)
            im = src.resize((max(1, round(src.width * s)), max(1, round(hh))), Image.LANCZOS)
            al = np.asarray(im)[:, :, 3] > 8
            rows = np.nonzero(al.any(1))[0]
            sole = int(rows[-1]) if len(rows) else im.height - 1
            cv.paste(im, (int(round(x - im.width / 2.0)), int(round(y)) - sole), im)

        tag = "b%02d" % n
        if a.check:
            bgs = bg_frames(b["bg"], 1, tag)
            cv = Image.open(bgs[0]).convert("RGB")
            for x, y in ((300, ys[0]), (640, ys[1]), (980, ys[2])):
                put(cv, stand, x, y)
                ImageDraw.Draw(cv).text((x - 42, y + 4), "y%d h%d" % (y, h_at(y)), fill=(255, 60, 60))
            p = "W1_2/_check/%s_fit.png" % tag
            cv.save(p)
            print("  %s  지평선 %.0f · k %.3f" % (p, hor, k))
            continue

        nf = int(b["sec"] * FPS)
        bgs = bg_frames(b["bg"], nf, tag)
        od = os.path.join("W1_2/_blk", tag + "_out")
        os.makedirs(od, exist_ok=True)
        for f in glob.glob(od + "/*.png"):
            os.remove(f)
        t0, seg = 0.0, 0
        for i in range(nf):
            t = i / float(FPS)
            while seg < len(b["plan"]) - 1 and t >= b["plan"][seg][0]:
                t0 = b["plan"][seg][0]
                seg += 1
            t1, what, xa, xb, yi = b["plan"][seg]
            u = 0.0 if t1 <= t0 else min(1.0, max(0.0, (t - t0) / (t1 - t0)))
            x = xa + (xb - xa) * u
            y = ys[yi]
            if what in ("walk", "step"):
                st = (t - t0) / STRIDE_SEC
                src = walk[int(st * CPS) % len(walk)]
                if xb < xa:
                    src = ImageOps.mirror(src)
            elif what == "point":
                src = point
            elif what == "sit":
                src = sit
            else:
                src = stand
            cv = Image.open(bgs[i]).convert("RGB")
            put(cv, src, x, y)
            cv.save(os.path.join(od, "f%04d.png" % i))
        v = 1 + len(glob.glob("W1_2/motion6/block%d_v*.mp4" % n))
        out = "W1_2/motion6/block%d_v%d.mp4" % (n, v)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                        "-i", os.path.join(od, "f%04d.png"), "-c:v", "libx264",
                        "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out], check=True)
        print("  %s  %d프레임 · %.1f초" % (out, nf, nf / float(FPS)))
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main())
