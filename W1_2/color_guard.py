# -*- coding: utf-8 -*-
"""수문장 컷에 **실제 교대의식 복색**을 입힌다.

★사장님 지시(2026-08-13) — 국가유산진흥원 공식 복식도를 보고 정하심
  "붉은색 모자와 검정 챙, 붉은색 도포와 노랑색 속옷과 고동색 가죽 팔토시.
   창은 나무색으로 하고 창끝은 투명. 신발도 고동색 가죽신."

## 어떻게 부위를 갈라내나
선화라 색 정보가 없다. **모양과 자리**로 가른다.

  ① 창    — 갓 꼭대기보다 위에서 시작하는 열 (`cut_motion6.body_top` 과 같은 잣대)
            그 위 끝 7% 는 창끝 쇠 → **투명**, 나머지는 나무색
  ② 얼굴  — 선이 둘러싼 안쪽 중 **맨 위의 둥근 것** → 흰색 (눈·코·입은 잉크라 안 덮는다)
  ③ 갓    — 얼굴보다 위에서 시작하는 안쪽 조각들
            납작한 것(가로세로 2.5 이상) = 챙 → 검정 / 나머지 = 모자 → 붉은색
  ④ 도포  — 얼굴 아래에서 제일 넓은 안쪽 조각 → 붉은색
  ⑤ 속옷  — 남은 안쪽 조각 전부 → 노랑
  ⑥ 팔·신발 — **굵은 획**만 골라 고동색. 가는 윤곽선은 검정으로 둔다.
            머리 동그라미도 굵지만 얼굴에 걸치므로 빼 놓는다.

    python W1_2/color_guard.py --one          # 전·후면 한 장씩만 칠해 확인
    python W1_2/color_guard.py --all          # 확정 뒤 전량
"""
import argparse
import glob
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

from cut_motion6 import body_top, SPECK, FACE_RATIO, FACE_MIN   # noqa: E402

# ── 복색 (국가유산진흥원 복식도 기준)
INK = (26, 26, 26)          # 윤곽선 · 눈코입
RED = (196, 44, 44)         # 모자 · 도포
BLACK = (30, 30, 30)        # 갓 챙
YELLOW = (232, 190, 60)     # 속옷(철릭)
LEATHER = (112, 68, 38)     # 고동색 가죽 — 팔토시 · 신발
WOOD = (166, 124, 78)       # 창대
WHITE = (255, 255, 255)     # 얼굴

ROBE_MIN = 0.30             # 제일 넓은 조각의 이만큼 되면 도포(그 아래는 속옷)
TIP = 0.07                  # 창 위 끝 이만큼이 창끝 쇠 — 투명
THICK = 4                   # 이 반지름으로 깎아 남으면 '굵은 획'(팔·신발)


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def color_cut(path):
    g = np.asarray(Image.open(path).convert("L")).astype(np.float32)
    ink = g < 170
    if not ink.any():
        return None
    # ★티끌은 **몸 밖에 있는 것만** 턴다.
    #   눈·코·입은 머리 테두리와 떨어진 작은 조각이라, 크기만 보고 털면 같이 지워진다
    #   (그래서 정면 얼굴이 백지로 나왔다 — 2026-08-13). 몸 실루엣 안에 들어 있으면
    #   아무리 작아도 남긴다.
    lab, n = ndimage.label(ink)
    sz = ndimage.sum(ink, lab, range(1, n + 1))
    big = lab == (int(np.argmax(sz)) + 1)
    sil = ndimage.binary_fill_holes(big)
    keep = big.copy()
    for i in range(1, n + 1):
        if sz[i - 1] >= sz.max() * SPECK:
            keep |= lab == i                       # 창·검처럼 큰 것
        else:
            c = lab == i
            if (c & ~sil).sum() == 0:
                keep |= c                          # ★몸 안쪽 — 눈·코·입
    ink = keep

    top = body_top((ink * 255).astype(np.uint8))
    cols = np.nonzero(ink.any(0))[0]
    firsty = np.array([np.nonzero(ink[:, c])[0][0] for c in cols])
    pc = cols[firsty < top - 12]
    band = np.zeros(ink.shape[1], bool)
    if len(pc):
        band[max(0, pc.min() - 2):pc.max() + 3] = True

    # ① 창 — 자루째(선 + 속) 잡고, 위 끝은 창끝 쇠라 떼어 낸다
    # ★자른 자리를 비율(7%)로 잡았더니 정면은 자루가 뭉텅 잘리고 후면은 쇠 윤곽이
    #   남았다. 창끝은 **자루보다 굵다** — 굵어지는 곳까지가 쇠다.
    pole_all = ndimage.binary_fill_holes(ink & band[None, :])
    pole = np.zeros_like(pole_all)
    tip = np.zeros_like(pole_all)
    if pole_all.any():
        py = np.nonzero(pole_all.any(1))[0]
        w = pole_all.sum(1).astype(float)
        lo = py[0] + int((py[-1] - py[0]) * 0.4)
        shaft = float(np.median(w[lo:py[-1] + 1]))
        cutline = py[0] + max(2, int((py[-1] - py[0]) * 0.02))
        for y in range(py[0], py[0] + int((py[-1] - py[0]) * 0.25)):
            if w[y] > shaft * 1.25:
                cutline = y + 1
        tip[:cutline] = pole_all[:cutline]
        pole[cutline:] = pole_all[cutline:]

    body = ink & ~band[None, :]
    bl, bn = ndimage.label(body)
    main = body
    if bn:
        bs = ndimage.sum(body, bl, range(1, bn + 1))
        main = bl == (int(np.argmax(bs)) + 1)
    inside = ndimage.binary_fill_holes(main) & ~main
    hl, hn = ndimage.label(inside)

    # ② 얼굴 — 맨 위의 둥근 조각
    area = float(main.sum())
    parts, face, fy = [], None, 10 ** 9
    for i in range(1, hn + 1):
        h = hl == i
        s = int(h.sum())
        ys, xs = np.nonzero(h)
        w, ht = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        parts.append((int(ys.min()), s, w, ht, h))
        if s < area * FACE_MIN:
            continue
        if max(w, ht) / float(max(1, min(w, ht))) >= FACE_RATIO:
            continue
        if ys.min() < fy:
            fy, face = ys.min(), h
    if face is None:
        face = np.zeros_like(inside)
        fy = top
    face = face & ~ink

    # ③④⑤ 갓 · 도포 · 속옷
    # ★각도에 흔들리지 않는 잣대로만 가른다 (정면·후면이 같게 나와야 한다).
    #   갓  — 얼굴 꼭대기보다 위에서 시작하는 조각. 그중 **제일 아래까지 내려온 것이 챙**
    #         이고 그 위가 모자다. 챙은 언제나 갓의 아랫단이라 각도와 무관하다.
    #         (납작한 정도로 갈랐더니 정면은 둘 다 검정, 후면은 둘 다 붉게 나왔다)
    #   도포 — 얼굴 아래 조각 중 **넓은 것 전부**. 앞자락이 갈라져 조각이 둘이므로
    #         '제일 큰 하나'만 잡으면 한쪽만 붉어진다.
    #   속옷 — 남은 좁은 조각(깃·소매 끝)
    hat_r = np.zeros_like(inside)     # 모자(붉은색)
    hat_b = np.zeros_like(inside)     # 챙(검정)
    robe = np.zeros_like(inside)
    inner = np.zeros_like(inside)

    hats = [p for p in parts if p[0] <= fy and not (p[4] & face).any()]
    if hats:
        # ★맨 위에서 시작하는 조각이 모자, 나머지가 챙. 앞뒤 어느 각도에서도 같다.
        #   (아랫단으로 갈랐더니 후면은 모자와 챙의 아랫단이 같아 둘 다 검게 나왔다)
        hi = min(p[0] for p in hats)
        for y0, s, w, ht, h in hats:
            if y0 <= hi + 4:
                hat_r |= h                            # 위 = 모자(붉은색)
            else:
                hat_b |= h                            # 아래 = 챙(검정)

    lows = [p for p in parts if p[0] > fy and not (p[4] & face).any()]
    if lows:
        big = max(p[1] for p in lows)
        for y0, s, w, ht, h in lows:
            if s >= big * ROBE_MIN:
                robe |= h                             # 넓은 것 = 도포
            else:
                inner |= h                            # 좁은 것 = 속옷

    # ⑥ 팔 · 신발 — 굵은 획만. 머리 동그라미는 뺀다
    thick = ndimage.binary_opening(ink, disk(THICK))
    tl, tn = ndimage.label(thick)
    head_zone = ndimage.binary_dilation(face, disk(12))
    leather = np.zeros_like(thick)
    for i in range(1, tn + 1):
        c = tl == i
        if (c & head_zone).any():                     # 머리 동그라미 — 검정으로 둔다
            continue
        leather |= c

    # ── 칠하기
    H, W = ink.shape
    rgb = np.zeros((H, W, 3), np.uint8)
    a = np.zeros((H, W), np.float32)
    for m, c in ((hat_r, RED), (hat_b, BLACK), (robe, RED), (inner, YELLOW),
                 (pole, WOOD), (face, WHITE), (leather, LEATHER)):
        rgb[m] = c
        a[m] = 1.0
    rest = ink & ~leather & ~tip                      # 나머지 선은 검정
    rgb[rest] = INK
    a[rest] = 1.0
    a[tip] = 0.0                                      # ★창끝 쇠 — 투명
    a = np.clip(ndimage.gaussian_filter(a, 0.5) * 1.6, 0, 1)
    return Image.fromarray(np.dstack([rgb, (a * 255).astype(np.uint8)]), "RGBA")


def sheet(items, out):
    F = ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf", 26)
    tiles = []
    for t, im in items:
        b = np.asarray(im)[:, :, 3]
        ys, xs = np.nonzero(b > 8)
        c = im.crop((xs.min() - 8, ys.min() - 8, xs.max() + 9, ys.max() + 9))
        s = 640.0 / c.height
        tiles.append((t, c.resize((round(c.width * s), 640), Image.LANCZOS)))
    TW = max(t.width for _, t in tiles) + 40
    sh = Image.new("RGB", (TW * len(tiles), 700), (238, 236, 231))
    d = ImageDraw.Draw(sh)
    for i, (t, im) in enumerate(tiles):
        sh.paste(im, (i * TW + (TW - im.width) // 2, 44), im)
        d.text((i * TW + TW // 2, 8), t, fill=(20, 20, 20), font=F, anchor="ma")
    sh.save(out)
    print(out, sh.size)


# 칠할 컷 묶음 — (컷 폴더, 원본 프레임 폴더, 쓸 프레임 범위)
SETS = [
    ("W1_2/motion6_cuts/perf_guard_march", "W1_2/_m6buf/perf_guard_march", (0, 64)),
    ("W1_2/motion6_cuts/perf_guard_away_half", "W1_2/_m6buf/perf_guard_away", (3, 35)),
]


def paint_all():
    """컷 폴더를 **색 입힌 것으로 갈아 끼운다.** 키 규격(갓끝~발 740)은 그대로."""
    from cut_motion6 import trim_scale, TARGET_H
    for od, sd, (a, b) in SETS:
        fs = sorted(glob.glob(os.path.join(sd, "*.png")))[a:b]
        if not fs:
            print("  ★원본 없음:", sd)
            continue
        key = os.path.basename(od)
        old = sorted(glob.glob(os.path.join(od, "*.png")))
        for f in old:
            os.remove(f)
        hs = []
        for i, p in enumerate(fs):
            im = trim_scale(color_cut(p), TARGET_H, True)
            im.save(os.path.join(od, "%s_%02d.png" % (key, i)))
            al = np.asarray(im)[:, :, 3]
            ys = np.nonzero((al > 8).any(1))[0]
            hs.append(int(ys[-1] - body_top(al) + 1))
        print("  %-26s %2d컷 칠함 (이전 %d장 대체) · 키 %d~%d"
              % (key, len(fs), len(old), min(hs), max(hs)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--one", action="store_true", help="전·후면 한 장씩만")
    ap.add_argument("--all", action="store_true", help="컷 전량을 색 입힌 것으로 교체")
    a = ap.parse_args()
    if a.one:
        items = [("정면 (회전 클립 f016)", color_cut("W1_2/_pick/guard_turn_raw/f016.png")),
                 ("후면 (걷기 f011)", color_cut("W1_2/_m6buf/perf_guard_away/f011.png"))]
        sheet(items, "W1_2/_check/guard_color_try.png")
    if a.all:
        print("수문장 컷 색 입히기")
        paint_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
