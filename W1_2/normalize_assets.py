# -*- coding: utf-8 -*-
"""W1-2 스틱맨 자산 통일 — 키 · 선 굵기 · 투명컷.

★사장님 지시(2026-08-11)
  "키를 맞추고 몸 선의 굵기도 같게 만들고 투명컷 해서 저장한다.
   걷기는 9프레임, 한 스트라이드당 0.75초 정도의 속도로 걷는다."

기준 = 가이드 `W24R/guides/stickman.png`
  · 키 740px
  · 선 굵기 / 키 = 0.0261

걷기는 원본 192프레임(24fps)에서 **한 스트라이드(32프레임 = 두 걸음)** 를
9프레임으로 고르게 뽑는다 → 12fps 로 재생하면 0.75초.
"""
import glob
import os

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WALK_SRC = os.path.join(ROOT, "W24R", "walk_frames", "stickman")
OUT_T = os.path.join(ROOT, "W1_2", "_poses")            # 투명본(합성용)
OUT_W = os.path.join(ROOT, "W1_2", "_poses_white")      # 흰배경본(기본 이미지용)

TARGET_H = 740
TARGET_RATIO = 0.0261        # 선 굵기 / 키 — 가이드 실측값
WALK_FRAMES = 9              # 한 스트라이드를 9컷으로
STRIDE = 32                  # 원본 24fps 기준 한 스트라이드 = 32프레임(두 걸음)
STRIDE_START = 40
INK = 26


# ── 측정 ──────────────────────────────────────────────────────────────────
def stroke_ratio(alpha):
    """선 굵기 / 키. 여러 행의 런 길이 중 25퍼센타일 — 팔다리 한 가닥의 굵기."""
    m = alpha > 8
    ys, xs = np.nonzero(m)
    if not len(xs):
        return None, None
    y0, h = ys.min(), ys.max() - ys.min() + 1
    runs = []
    for fy in np.arange(0.30, 0.96, 0.02):
        c = 0
        for v in m[y0 + int(h * fy)]:
            if v:
                c += 1
            elif c:
                runs.append(c)
                c = 0
        if c:
            runs.append(c)
    if not runs:
        return h, None
    return h, float(np.percentile(runs, 25))


# ── 굵기 맞추기 ────────────────────────────────────────────────────────────
def set_thickness(im, target_px):
    """알파를 침식/팽창해 선 굵기를 맞춘다. 양쪽에서 깎이므로 지름 차의 절반씩."""
    a = np.asarray(im)[:, :, 3]
    h, t = stroke_ratio(a)
    if not t:
        return im
    d = (target_px - t) / 2.0
    if abs(d) < 0.6:
        return im
    k = int(round(abs(d)))
    if k < 1:
        return im
    A = Image.fromarray(a)
    # MinFilter=침식(얇게) · MaxFilter=팽창(굵게). 커널은 홀수여야 한다
    size = 2 * k + 1
    A = A.filter(ImageFilter.MinFilter(size) if d < 0 else ImageFilter.MaxFilter(size))
    out = np.asarray(im).copy()
    out[:, :, 3] = np.asarray(A)
    # 잉크색을 다시 못 박는다(침식하면 가장자리가 흐려진다)
    return Image.fromarray(out, "RGBA")


def trim_scale(im, h_target):
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    if not len(xs):
        return None
    im = im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    w, h = im.size
    return im.resize((max(1, round(w * h_target / h)), h_target), Image.LANCZOS)


def white_bg(im):
    """흰 바탕에 제대로 합성 — ★알파만 보고 검정 칠하면 카드가 새까매진다."""
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    rgb, al = a[:, :, :3], a[:, :, 3:4] / 255.0
    return Image.fromarray((255 * (1 - al) + rgb * al).astype(np.uint8), "RGB")


def cut_white(im):
    """흰 배경 원본 → 투명. 스틱맨은 검은 선뿐이라 밝기 하나로 가른다."""
    g = np.asarray(im.convert("L"), np.float32)
    al = np.clip((225.0 - g) / 55.0, 0, 1)
    rgb = np.full(g.shape + (3,), INK, np.uint8)
    return Image.fromarray(np.dstack([rgb, (al * 255).astype(np.uint8)]), "RGBA")


# ── 본작업 ────────────────────────────────────────────────────────────────
def main():
    os.makedirs(OUT_T, exist_ok=True)
    os.makedirs(OUT_W, exist_ok=True)
    target_px = TARGET_RATIO * TARGET_H          # ≈ 19.3px

    # 1) 걷기 — 한 스트라이드를 9컷으로
    fs = sorted(glob.glob(os.path.join(WALK_SRC, "*.png")))
    idx = [STRIDE_START + round(STRIDE * i / WALK_FRAMES) for i in range(WALK_FRAMES)]
    print("걷기 원본 %d프레임 → 고른 프레임 %s" % (len(fs), [i + 1 for i in idx]))
    for k, i in enumerate(idx):
        im = cut_white(Image.open(fs[i]))
        im = trim_scale(im, TARGET_H)
        im = set_thickness(im, target_px)
        im = trim_scale(im, TARGET_H)            # 굵기 조정 뒤 키 다시 맞춤
        im.save(os.path.join(OUT_T, "stickman_w1d2_walk_r_%d.png" % k))
        im.transpose(Image.FLIP_LEFT_RIGHT).save(
            os.path.join(OUT_T, "stickman_w1d2_walk_l_%d.png" % k))

    # 2) 정지 포즈 — 키만 맞춘다(굵기는 이미 기준값)
    for p in sorted(glob.glob(os.path.join(OUT_T, "stickman_w1d2_*.png"))):
        if "_walk_" in p:
            continue
        im = trim_scale(Image.open(p).convert("RGBA"), TARGET_H)
        im = set_thickness(im, target_px)
        im = trim_scale(im, TARGET_H)
        im.save(p)

    # 3) 흰 배경본
    for p in sorted(glob.glob(os.path.join(OUT_T, "stickman_w1d2_*.png"))):
        white_bg(Image.open(p)).save(os.path.join(OUT_W, os.path.basename(p)))

    # 4) 검증
    print("\n%-30s %5s %7s %8s" % ("파일", "키", "선굵기", "굵기/키"))
    bad = 0
    for p in sorted(glob.glob(os.path.join(OUT_T, "stickman_w1d2_*.png"))):
        h, t = stroke_ratio(np.asarray(Image.open(p))[:, :, 3])
        r = t / h if (h and t) else 0
        flag = "" if abs(r - TARGET_RATIO) < 0.004 and h == TARGET_H else "  ★어긋남"
        if flag:
            bad += 1
        print("%-30s %5d %7.1f %8.4f%s" % (os.path.basename(p)[9:30], h, t or 0, r, flag))
    print("\n기준 키 %d · 굵기/키 %.4f · 어긋난 것 %d개" % (TARGET_H, TARGET_RATIO, bad))
    print("걷기 %d프레임 · 12fps 재생 = 한 스트라이드 %.2f초"
          % (WALK_FRAMES, WALK_FRAMES / 12))


if __name__ == "__main__":
    main()
