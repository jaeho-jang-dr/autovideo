# -*- coding: utf-8 -*-
"""정면 달리기 → 한 스트라이드 투명컷 → **뒷머리로 바꿔 후면 달리기까지**.

★사장님 지시(2026-08-12): "정면 달리기를 8초짜리 하나 만들어서 한 스트라이드 잘라서
  정면 달리기·후면 달리기로 투명컷 스틸동영상으로 만들자. 머리만 리버스 하면
  후면 달려 나가기로 바꿀 수도 있다."

## 왜 머리만 바꾸면 되는가
`run_front.mp4` 는 몸이 **정확히 0도**(motion6_defs.FRONT_LOCK)라 좌우가 대칭이다.
스틱맨은 뒤에서 보면 머리가 **그냥 빈 동그라미**다(EXIT_TURN 의 180도 규격과 같다).
그러니 얼굴(눈 2·입 1)만 지우면 같은 몸이 그대로 뒷모습으로 읽힌다.

## 정지 구간을 잘라내고 찾는다
Flow 가 기준 이미지 자세로 시작하고 끝나서 **앞 0~9 · 뒤 176~191 프레임이 정지**다.
전체에서 주기를 찾으면 이 정지 구간이 섞여 주기가 틀어진다 → window 로 잘라 넣는다.

    python W1_2/make_run_front_cuts.py
"""
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

import stride_motion6 as S                                  # noqa: E402

# ★달리기 구간만. 앞뒤 정지 프레임을 뺀다(실측 2026-08-12).
WINDOW = (10, 176)
FRONT = "run_front"
BACK = "run_back"
# 머리는 전체 키의 위에서 24% 안에 든다(guide_front 실측: 원 지름 ≈ 0.20H)
HEAD_FRAC = 0.24


def back_head(im):
    """정면 컷의 얼굴을 지워 **뒷머리(빈 동그라미)** 로 바꾼다.

    ★눈·입을 '성분'으로 골라 지우면 안티에일리어싱 테두리가 옅게 남는다.
      대신 **선(윤곽)이 둘러싼 안쪽을 통째로 흰색으로 채운다.**

    몸·머리 윤곽은 한 덩어리로 이어져 있고 눈·입만 떨어진 섬이다. 그 덩어리의
    구멍을 메우면(fill_holes) 머리는 꽉 찬 원반이 되고, 거기서 윤곽선을 빼면
    **머리 안쪽 전체**(눈·입·잔재 포함)가 남는다. 그걸 흰색으로 덮는다.
    ★높이 띠를 쓰지 않으므로 프레임마다 머리 위치가 달라져도 안 깨진다.
      팔·몸통이 만드는 삼각형 안쪽도 같이 칠해지지만 그쪽은 이미 흰색이라 변화가 없다.
    """
    a = np.array(im.convert("RGBA"))
    alpha = a[:, :, 3]
    ink = (alpha > 100) & (a[:, :, :3].max(2) < 170)
    lab, n = ndimage.label(ink)
    if n == 0:
        return Image.fromarray(a, "RGBA"), 0

    sizes = ndimage.sum(ink, lab, range(1, n + 1))
    outline = lab == (int(np.argmax(sizes)) + 1)      # 가장 큰 덩어리 = 몸+머리 윤곽선
    inside = ndimage.binary_fill_holes(outline) & ~outline
    if not inside.any():
        return Image.fromarray(a, "RGBA"), 0

    a[inside, 0:3] = 255                              # 흰색 · 불투명 (cut_white 의 hole 과 같게)
    a[inside, 3] = 255
    return Image.fromarray(a, "RGBA"), int(inside.sum())


def make_back():
    src = os.path.join(S.OUT, FRONT)
    dst = os.path.join(S.OUT, BACK)
    os.makedirs(dst, exist_ok=True)
    for f in glob.glob(os.path.join(dst, "*.png")):
        os.remove(f)
    fs = sorted(glob.glob(os.path.join(src, "*.png")))
    tot = []
    for p in fs:
        im, k = back_head(Image.open(p))
        im.save(os.path.join(dst, os.path.basename(p).replace(FRONT, BACK)))
        tot.append(k)
    print("  %-14s %d컷 · 머리 안쪽 채운 화소 %d~%d px/컷 (컷마다 비슷해야 정상)"
          % (BACK, len(fs), min(tot), max(tot)))
    return fs, tot


def side_by_side(fps=24, loops=4):
    """정면·후면을 나란히 놓고 돌려 본다 — 몸이 같고 머리만 다른지 눈으로 확인."""
    ff = sorted(glob.glob(os.path.join(S.OUT, FRONT, "*.png")))
    bb = sorted(glob.glob(os.path.join(S.OUT, BACK, "*.png")))
    if not ff or len(ff) != len(bb):
        return
    W, H, k = 900, 860, 0
    d = os.path.join(S.TMP, "run_front_pair")
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, "*.png")):
        os.remove(f)
    for _ in range(loops):
        for pf, pb in zip(ff, bb):
            cv = Image.new("RGB", (W, H), (255, 255, 255))
            for j, p in enumerate((pf, pb)):
                im = Image.open(p).convert("RGBA")
                t = im.resize((max(1, round(im.width * 760 / im.height)), 760), Image.LANCZOS)
                cv.paste(t, (j * W // 2 + (W // 2 - t.width) // 2, 40), t)
            cv.save(os.path.join(d, "f%03d.png" % k))
            k += 1
    out = os.path.join(S.SRC, "run_front_pair.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(fps),
                    "-i", os.path.join(d, "f%03d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", out], check=True)
    print("     대조본 %s  %d컷×%d회 · %dfps" % (out, len(ff), loops, fps))


def main():
    print("[1] 한 스트라이드 뽑기 (창 %s — 앞뒤 정지 구간 제외)" % (WINDOW,))
    S.one(FRONT, window=WINDOW)
    print("[2] 뒷머리 파생")
    make_back()
    print("[3] 순환 확인본")
    S.make_loop(FRONT, fps=24)
    S.make_loop(BACK, fps=24)
    side_by_side()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
