# -*- coding: utf-8 -*-
"""빠진 개별 포즈를 **같은 영상 안에서** 자동으로 찾아 채운다 (2026-08-03).

★사장님 지시: "포즈를 캐릭터 모양이 달라지지 않게 똑같이 만드는 것이 무엇보다 중요."
  → 새로 생성하지 않는다. **같은 그룹 영상의 다른 프레임**에서 뽑으면 모양이 절대 안 변한다.

빠지는 이유는 하나뿐이다 — 그 프레임에서 두 사람이 손을 잡거나 겹쳐 **한 덩어리**가 됐다.
그래서 목표 프레임 둘레를 훑어 **깨끗이 갈라진 프레임**을 찾아 대신 쓴다.

사용:
  python fix_w24_missing_poses.py --dry
  python fix_w24_missing_poses.py
"""
import argparse
import glob
import os

import numpy as np
from PIL import Image

import split_w24_group_poses as S

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)


def log(m):
    print(m, flush=True)


def clean_at(key, cut):
    """그 컷에서 그룹 인원수만큼 덩어리가 깨끗이 갈라졌는지 본다."""
    p = f"{S.CUTS}/{key}/{cut:02d}.png"
    if not os.path.exists(p):
        return None
    members = S.members_of(key)
    rgba = np.array(Image.open(p).convert("RGBA"))
    bs = S.blobs_of(rgba, len(members))
    if len(bs) < len(members):
        return None
    w = rgba.shape[1]
    if any((b["x1"] - b["x0"]) > w * 0.62 for b in bs[:len(members)]):
        return None
    return len(bs)


def find_cut(key, target):
    """목표 컷에서 가까운 순서로 훑어 깨끗한 컷을 찾는다."""
    order = sorted(range(64), key=lambda c: (abs(c - target), c))
    for c in order:
        if clean_at(key, c):
            return c
    return None


def main(dry):
    want = {}
    for k, c, m in S.PLAN:
        for ch, ps in m.items():
            want[(ch, ps)] = (k, c)
    have = {os.path.basename(p)[4:-4] for p in glob.glob(f"{S.OUT_DIR}/{S.PREFIX}_*.png")}
    miss = [(ch, ps, k, c) for (ch, ps), (k, c) in want.items() if f"{ch}_{ps}" not in have]
    log(f"빠진 포즈 {len(miss)}장 — 같은 영상에서 대체 프레임을 찾는다\n")

    # 같은 (영상, 대체컷) 끼리 모아 한 번에 뽑는다
    jobs = {}
    for ch, ps, k, target in sorted(miss):
        alt = find_cut(k, target)
        if alt is None:
            log(f"  ★{k} 전체에서 깨끗한 컷을 못 찾음 — {ch} {ps}")
            continue
        log(f"  {ch:12s} {ps:16s} {k}:{target:02d} → **{k}:{alt:02d}**")
        jobs.setdefault((k, alt), {})[ch] = ps

    log("")
    made = 0
    for (k, cut), mapping in sorted(jobs.items()):
        made += S.extract(k, cut, mapping, dry)
    log(f"\n{'(모의) ' if dry else ''}채운 포즈 {made}장")
    if not dry:
        tot = len(glob.glob(f"{S.OUT_DIR}/{S.PREFIX}_*.png"))
        log(f"개별 포즈 합계 {tot}장 / 계획 {len(want)}장")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    main(ap.parse_args().dry)
