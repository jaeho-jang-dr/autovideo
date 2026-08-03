# -*- coding: utf-8 -*-
"""W24 개별 포즈 결함 2건 수정 (사장님 지시 2026-08-03).

① 스틱맨 머리 → **투명으로 통일.**
   `*_sit_*` 3장만 머리 원 안쪽이 흰색으로 채워져 나왔다(원본 영상에서 그 부분이 밝아서
   컷아웃 규칙의 '밝기>232 = 전경'에 걸렸다). 나머지 컷은 투명이라 통일해야 한다.
   → 머리 영역에서 **둘러싸인 밝은 무채색 덩어리**를 찾아 알파 0 으로 만든다.

② 졸라맨 `lift_block_up` → 머리가 팔에 가려 검은 덩어리로 보인다.
   같은 영상(`a_stack_block`)에서 **머리 윤곽이 보이는 프레임**을 찾아 교체한다.
   (새로 생성하지 않는다 — 캐릭터 모양이 달라지면 안 되므로)

사용: python fix_w24_pose_defects.py
"""
import glob
import os

import numpy as np
from PIL import Image
from scipy import ndimage

import split_w24_group_poses as S

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)


def log(m):
    print(m, flush=True)


def clear_head(path):
    """머리 안쪽의 둘러싸인 밝은 무채색 영역을 투명으로."""
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    al = a[:, :, 3] > 40
    rgb = a[:, :, :3].astype(int)
    lo = rgb.min(2); sat = rgb.max(2) - lo
    ys, _ = np.where(al)
    if not len(ys):
        return 0
    top, bot = ys.min(), ys.max()
    head_lim = top + (bot - top) * 0.30          # 상단 30% = 머리
    bright = al & (lo > 200) & (sat < 30)
    lbl, n = ndimage.label(bright)
    cleared = 0
    for i in range(1, n + 1):
        hy, _hx = np.where(lbl == i)
        if len(hy) < 300:
            continue
        if hy.mean() <= head_lim:
            a[lbl == i, 3] = 0
            cleared += len(hy)
    if cleared:
        Image.fromarray(a).save(path)
    return cleared


def head_visible_score(key, cut, char):
    """그 컷에서 char 의 머리 윤곽이 얼마나 보이는지 — 머리 영역의 '검지 않은' 비율."""
    p = f"{S.CUTS}/{key}/{cut:02d}.png"
    if not os.path.exists(p):
        return -1
    rgba = np.array(Image.open(p).convert("RGBA"))
    members = S.members_of(key)
    bs = S.blobs_of(rgba, len(members))
    if len(bs) < len(members):
        return -1
    w = rgba.shape[1]
    if any((b["x1"] - b["x0"]) > w * 0.62 for b in bs[:len(members)]):
        return -1
    from scipy.optimize import linear_sum_assignment
    cost = np.zeros((len(bs), len(members)))
    for i, b in enumerate(bs):
        _, sc = S.classify(rgba, b, members)
        for j, c in enumerate(members):
            cost[i, j] = -sc.get(c, 0.0)
    ri, ci = linear_sum_assignment(cost)
    named = {members[j]: bs[i] for i, j in zip(ri, ci)}
    b = named.get(char)
    if b is None:
        return -1
    m = b["mask"].copy()
    hy = b["y0"] + int((b["y1"] - b["y0"]) * 0.24)
    m[hy:, :] = False
    px = rgba[:, :, :3][m].astype(int)
    if len(px) < 200:
        return -1
    # 머리 영역이 온통 새까맣지 않고 밝은 부분(얼굴)이 섞여 있어야 좋다
    return float((px.max(1) > 140).mean())


def main():
    log("① 스틱맨 머리 투명 통일")
    for p in sorted(glob.glob(f"{S.OUT_DIR}/{S.PREFIX}_stickman_*.png")):
        n = clear_head(p)
        log(f"   {os.path.basename(p):34s} {'투명화 %d px' % n if n else '변화 없음(이미 투명)'}")

    log("\n② 졸라맨 lift_block_up — 머리가 보이는 프레임 찾기")
    best = (-1, None)
    for c in range(64):
        s = head_visible_score("a_stack_block", c, "zolla_man")
        if s > best[0]:
            best = (s, c)
    log(f"   최적 컷 {best[1]:02d} (머리 밝은 비율 {best[0]:.2f})")
    if best[0] < 0.10:
        log("   ★어느 컷에서도 머리가 가려져 있다 → 영상 재생성이 필요하다")
    else:
        S.extract("a_stack_block", best[1], {"zolla_man": "lift_block_up"})
        clear_head(f"{S.OUT_DIR}/{S.PREFIX}_zolla_man_lift_block_up.png")
    log("\n완료")


if __name__ == "__main__":
    main()
