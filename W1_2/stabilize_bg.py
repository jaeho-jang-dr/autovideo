# -*- coding: utf-8 -*-
"""배경 동영상 **카메라 고정** — Flow 가 흔들어 놓은 것을 되돌린다.

★왜 필요한가
프롬프트에 "Camera locked" 를 박아도 Flow 는 좌우로 흘린다. `perf_guard_gate` 는
80px 나 흘렀다. 배경이 흐르면 그 위에 얹은 캐릭터는 **발이 땅에서 미끄러진다** —
발이 땅에 붙어 있어야 한다는 규칙이 그대로 깨진다.

## 재는 법
위상상관(phase correlation)으로 프레임마다 첫 프레임 대비 (dx, dy) 를 잰다.
하늘·깃발처럼 움직이는 것 말고 **먼 벽·문 언저리 가로띠**를 기준으로 삼는다.

## 되돌리는 법
잰 만큼 반대로 밀고, 밀린 가장자리가 안 보이도록 여백만큼 잘라 낸 뒤 원래 크기로
되돌린다. 잘라 내는 만큼 그림이 조금 커지지만(최대 흔들림 × 2), 발이 붙는 쪽이
훨씬 중요하다.

    python W1_2/stabilize_bg.py perf_guard_gate
    python W1_2/stabilize_bg.py perf_guard_gate --band 300 420
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

BG = "W1_2/bg"
TMP = "W1_2/_bgstab"
W, H = 1280, 720


MAXSH = 40                 # 이보다 크게 흔들릴 리 없다


def match_shift(g, tpl, box, lim=MAXSH):
    """정적인 조각 하나를 **직접 맞춰** 흔들린 양을 잰다.

    ★위상상관은 쓰지 않는다 — 돌바닥 이음선·벽돌·깃대처럼 같은 무늬가 되풀이되면
      상관면에 가짜 봉우리가 여러 개 생겨 엉뚱하게 잡힌다. 실제로 이 배경은
      8초에 좌우 12px 밖에 안 흘렀는데 위상상관은 ±60px 로 읽었고, 그대로 되돌렸다가
      흔들림이 되레 커졌다(검산이 잡아냄, 2026-08-13).
    """
    y0, y1, x0, x1 = box
    bs, bv = (0, 0), -9.0
    for dy in range(-12, 13):
        for dx in range(-lim, lim + 1):
            w = g[y0 + dy:y1 + dy, x0 + dx:x1 + dx]
            if w.shape != tpl.shape:
                continue
            w = (w - w.mean()) / (w.std() + 1e-6)
            v = float((w * tpl).mean())
            if v > bv:
                bv, bs = v, (dx, dy)
    return bs


def run(key, band, fps=24):
    src = os.path.join(BG, key + ".mp4")
    if not os.path.exists(src):
        print("★없음:", src)
        return 1
    d = os.path.join(TMP, key)
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(d)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                    os.path.join(d, "f%03d.png")], check=True)
    fs = sorted(glob.glob(os.path.join(d, "*.png")))
    y0, y1 = band
    box = (y0, y1, 540, 760)                        # 문 지붕 언저리 — 정적이고 대비가 세다

    g0 = np.asarray(Image.open(fs[0]).convert("L"), float)
    tpl = g0[box[0]:box[1], box[2]:box[3]]
    tpl = (tpl - tpl.mean()) / (tpl.std() + 1e-6)
    sh = [match_shift(np.asarray(Image.open(p).convert("L"), float), tpl, box)
          for p in fs]
    dx = np.array([s[0] for s in sh])
    dy = np.array([s[1] for s in sh])
    m = int(max(abs(dx).max(), abs(dy).max())) + 4
    print("  %s  %d프레임 · 좌우 %d~%d · 상하 %d~%d → 여백 %dpx 잘라냄"
          % (key, len(fs), dx.min(), dx.max(), dy.min(), dy.max(), m))

    od = os.path.join(d, "_fix")
    os.makedirs(od, exist_ok=True)
    for i, p in enumerate(fs):
        im = Image.open(p).convert("RGB")
        # 잰 만큼 반대로 민다 → 가장자리 여백을 잘라 내고 원래 크기로
        # ★부호 — `match_shift` 는 **그 조각이 어디로 옮겨 갔는지**(+dx)를 준다.
        #   PIL AFFINE 의 c·f 는 출력 좌표를 입력 좌표로 옮기는 값이라, c=+dx 면
        #   그림이 왼쪽으로 dx 만큼 되밀린다 — 그것이 되돌리는 방향이다.
        #   (반대로 넣으면 흔들림이 두 배가 된다. 검산이 잡아낸다)
        im = im.transform(im.size, Image.AFFINE, (1, 0, dx[i], 0, 1, dy[i]),
                          resample=Image.BICUBIC)
        im = im.crop((m, m, im.width - m, im.height - m)).resize((W, H), Image.LANCZOS)
        im.save(os.path.join(od, "f%03d.png" % i))

    raw = os.path.join(BG, key + "_raw.mp4")
    if not os.path.exists(raw):
        shutil.copy2(src, raw)                      # 원본은 남긴다
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(fps),
                    "-i", os.path.join(od, "f%03d.png"), "-c:v", "libx264",
                    "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    src], check=True)

    # 검산 — 고친 뒤 다시 재 본다
    ff = sorted(glob.glob(os.path.join(od, "*.png")))
    t2 = np.asarray(Image.open(ff[0]).convert("L"), float)[box[0]:box[1], box[2]:box[3]]
    t2 = (t2 - t2.mean()) / (t2.std() + 1e-6)
    s2 = [match_shift(np.asarray(Image.open(p).convert("L"), float), t2, box)
          for p in ff]
    print("  검산 — 남은 흔들림 좌우 %d~%d · 상하 %d~%d px  (원본 %s)"
          % (min(s[0] for s in s2), max(s[0] for s in s2),
             min(s[1] for s in s2), max(s[1] for s in s2), os.path.basename(raw)))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="+")
    ap.add_argument("--band", nargs=2, type=int, default=[300, 420],
                    help="흔들림을 잴 가로띠 (기본 300~420 — 먼 벽 언저리)")
    a = ap.parse_args()
    print("배경 카메라 고정")
    for k in a.keys:
        run(k, a.band)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
