# -*- coding: utf-8 -*-
"""투명컷 규칙 — **머리(얼굴)만 빼고 흰색은 전부 지운다.**

★사장님 확정(2026-08-13)
  "얼굴을 빼고 팔 사이, 팔과 몸 사이, 다리와 다리 사이, 다리와 몸 사이
   모두 다 투명하게 컷 하라."
  "**이거 간단한 일인데, 머리를 제외하고 흰색 다 제거하면 되잖아.**"

## ★적용 범위 — **졸라 삼총사에만** 쓴다 (사장님 못 박음 2026-08-13)
  "머리만 남기고 모든 흰색이란 것은 **이 졸라 삼총사에만** 해당되는 것이다.
   다른 캐릭터는 **흰색 옷, 몸**도 있다. 그러니 예외이다."

  쓰는 곳 — 스틱맨 · 졸라맨 · 졸라걸
  쓰면 안 되는 곳 — 지은 · 인준 · 마담제이 · 닥터제이 등 **살과 옷이 있는 캐릭터**.
  그쪽은 흰 블라우스·흰 치마가 몸이라, 흰색을 지우면 옷에 구멍이 뚫린다.
  (그쪽 규격은 `cut_w24_group.py` — 구멍을 둘러싼 **테두리 색**으로 가린다)

  아래 `TRIO` 로 빗장을 걸어 두었다. 삼총사가 아닌 파일은 건너뛴다.

## 규칙 — 이 네 가지만 남긴다
  1. **검은 선**       (잉크)
  2. **색깔**          (졸라걸 주황 머리 같은 것)
  3. **회색**          (★옷·신발·장갑 — 아래 참조)
  4. **얼굴 동그라미 속** (눈·입이 읽혀야 하므로 흰색으로 남긴다)
그 밖의 **순백**은 그것이 어디에 있든 전부 알파 0. 팔과 몸 사이든, 다리 사이든
가리지 않는다. 모양을 재서 고르지 않는다.

## ★옷·신발·장갑은 흰색으로 그리지 않는다 (사장님 지시 2026-08-13)
  "이제 옷 신발 손장갑 등을 흰색을 하지 말고, **컷아웃 하기 힘드니 회색까지만** 하자."

  흰 신발은 흰 배경과 같은 색이라 컷아웃이 갈라내지 못한다(그래서 여태 신발 속이
  뻥 뚫렸다). 앞으로 만드는 클립은 **밝은 회색**으로 그리게 프롬프트에 못 박는다
  (`motion6_defs._GREY_PARTS`). 그러면 여기서 자동으로 살아남는다.
  기준값 — 순백은 세 채널이 모두 `WHITE_TH`(235) 이상. 그보다 어두우면 회색이라 남긴다.

## 얼굴은 어떻게 찾나
선이 둘러싼 안쪽 조각들 가운데 **맨 위에 있는, 둥근(가로세로비 1.8 미만) 조각**.
머리는 언제나 몸 맨 위에 있고 동그라미다. 뒤통수(얼굴이 안 보이는 컷)에는 그런
조각이 없으므로 아무것도 안 남기고 지나간다 — 그래야 맞다.

    python W1_2/strip_white.py                     # 검사만
    python W1_2/strip_white.py --preview <폴더>    # 지울 곳을 빨갛게 칠해 보여 준다
    python W1_2/strip_white.py --fix               # 정지 포즈
    python W1_2/strip_white.py --all --fix         # ★포즈 + 동작 컷 + m6 라이브러리 전부
"""
import argparse
import glob
import os
import shutil

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

POSE_DIRS = ["W1_2/pose_cuts", "W1_2/_poses"]
CUT_DIRS = ["W1_2/motion6_cuts", "W1_2/motion6_stride"]
M6_DIR = "assets/graphics/poses"

DARK = 170                         # 이보다 어두우면 잉크(검은 선)
SAT = 40                           # 이보다 알록달록하면 색깔(주황 머리)
WHITE_TH = 235                     # ★세 채널이 모두 이 위면 '순백' — 지운다
FACE_RATIO = 1.8                   # 얼굴은 이보다 둥글다
FACE_MIN = 0.004                   # 얼굴은 그림 넓이의 이만큼은 된다

# ★이 규칙은 **졸라 삼총사 전용**이다 (사장님 못 박음 2026-08-13).
#   다른 캐릭터는 흰 옷·흰 몸이 있어 흰색을 지우면 옷에 구멍이 뚫린다.
TRIO = ("sm_", "stickman", "m6_", "zman", "zgirl", "zolla",
        "back_flip", "butt_fall", "forward_roll", "high_five", "hop_down",
        "pick_up", "reach_catch", "shoulder_arm", "sit_stand", "skid_stop",
        "tiptoe", "walk_", "run_")


def is_trio(name):
    n = os.path.basename(name).lower()
    return any(n.startswith(t) or t in n for t in TRIO)


def parts(im):
    """(남길 것, 얼굴 마스크, 지울 흰색) — 규칙 그대로."""
    a = np.array(im.convert("RGBA"))
    alpha, rgb = a[:, :, 3], a[:, :, :3].astype(int)
    on = alpha > 8
    dark = on & (rgb.max(2) < DARK)                     # ① 검은 선
    sat = on & ((rgb.max(2) - rgb.min(2)) > SAT)        # ② 색깔(주황 머리)
    grey = on & (rgb.min(2) < WHITE_TH)                 # ③ ★회색 — 옷·신발·장갑
    ink = dark | sat | grey
    if not ink.any():
        return None, None, None

    lab, n = ndimage.label(dark)
    if n == 0:
        return ink, np.zeros_like(ink), on & ~ink
    sizes = ndimage.sum(dark, lab, range(1, n + 1))
    main = lab == (int(np.argmax(sizes)) + 1)           # 몸통 선 한 덩어리
    inside = ndimage.binary_fill_holes(main) & ~main    # 선이 둘러싼 안쪽 전부

    # ③ 얼굴 = 그 안쪽 조각들 중 **맨 위에 있는 둥근 것**
    hl, hn = ndimage.label(inside)
    face = np.zeros_like(inside)
    area_all = float(main.sum())
    best = None
    for i in range(1, hn + 1):
        h = hl == i
        if h.sum() < area_all * FACE_MIN:
            continue
        ys, xs = np.nonzero(h)
        w = xs.max() - xs.min() + 1
        ht = ys.max() - ys.min() + 1
        if max(w, ht) / float(max(1, min(w, ht))) >= FACE_RATIO:
            continue
        if best is None or ys.min() < best[0]:
            best = (ys.min(), h)
    if best is not None:
        face = best[1]

    # ★얼굴을 흰색으로 칠할 때 **눈·코·입을 덮으면 안 된다**.
    #   `inside` 는 선이 둘러싼 안쪽 전부라, 머리 안에 떠 있는 눈·입 획도 거기 들어간다.
    #   그대로 흰색을 칠하면 얼굴이 백지가 된다(2026-08-13 사고).
    face = face & ~ink
    keep = ink | face
    drop = on & ~keep                                   # ★남은 흰색은 전부 지운다
    return keep, face, drop


def strip(path, fix=False, prev_dir=None, backup=True):
    im = Image.open(path).convert("RGBA")
    keep, face, drop = parts(im)
    if keep is None:
        return 0
    nd = int(drop.sum())
    if prev_dir and nd:
        a = np.array(im)
        a[:, :, 0][drop] = 240
        a[:, :, 1][drop] = 40
        a[:, :, 2][drop] = 40
        os.makedirs(prev_dir, exist_ok=True)
        Image.fromarray(a, "RGBA").convert("RGB").save(
            os.path.join(prev_dir, os.path.basename(path)))
    if not fix or not nd:
        return nd
    if backup:
        bak = os.path.splitext(path)[0] + "_v1.png"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
    a = np.array(im)
    a[:, :, 3][drop] = 0
    a[:, :, 0][face] = 255                              # 얼굴은 또렷한 흰색으로
    a[:, :, 1][face] = 255
    a[:, :, 2][face] = 255
    a[:, :, 3][face] = 255
    Image.fromarray(a, "RGBA").save(path)
    return nd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--all", action="store_true", help="포즈 + 동작 컷 + m6 전부")
    ap.add_argument("--preview", default=None)
    a = ap.parse_args()

    tot = 0
    print("정지 포즈%s" % (" · ★지운다" if a.fix else " (검사만)"))
    for d in POSE_DIRS:
        for p in sorted(glob.glob(os.path.join(d, "*.png"))):
            b = os.path.splitext(os.path.basename(p))[0]
            if b.endswith("_v1") or "sheet" in b:
                continue
            if a.names and b not in a.names:
                continue
            n = strip(p, a.fix, a.preview)
            tot += n
            if n:
                print("  %-34s 흰색 %6d화소 지움" % (b, n))

    if a.all:
        print("\n동작 컷%s" % (" · ★지운다" if a.fix else " (검사만)"))
        for base in CUT_DIRS:
            for d in sorted(glob.glob(os.path.join(base, "*"))):
                if not os.path.isdir(d) or d.endswith("_v1"):
                    continue
                k = os.path.basename(d)
                if a.names and k not in a.names:
                    continue
                fs = sorted(glob.glob(os.path.join(d, "*.png")))
                if a.fix and not os.path.isdir(d + "_v2"):
                    shutil.copytree(d, d + "_v2")       # 이 규칙 적용 전 상태
                n = sum(strip(p, a.fix, None, backup=False) for p in fs)
                tot += n
                print("  %-24s %2d프레임 · %8d화소" % (k, len(fs), n))

        print("\nm6 이동컷 라이브러리%s" % (" · ★지운다" if a.fix else ""))
        keys = {}
        for p in sorted(glob.glob(os.path.join(M6_DIR, "m6_*.png"))):
            b = os.path.basename(p)[3:-4]
            if b[-3:-2] == "_" and b[-2:].isdigit():
                keys.setdefault(b[:-3], []).append(p)
        for k in sorted(keys):
            if a.names and k not in a.names:
                continue
            fs = keys[k]
            if a.fix:
                bak = os.path.join(M6_DIR, "_v2", k)
                if not os.path.isdir(bak):
                    os.makedirs(bak, exist_ok=True)
                    for p in fs:
                        shutil.copy2(p, bak)
            n = sum(strip(p, a.fix, None, backup=False) for p in fs)
            tot += n
            print("  m6:%-21s %2d프레임 · %8d화소" % (k, len(fs), n))

    print("\n지운 흰색 %d화소%s" % (tot, "" if a.fix else " — 지우려면 --fix"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
