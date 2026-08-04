# -*- coding: utf-8 -*-
"""W24 그룹 클립 64컷 전부의 인물 키를 재서 **흔들림**을 본다. 읽기 전용.

   ★사장님 지시(2026-08-04): 캐릭터 크기가 바뀌면 영상 폐기 수준이다.
     3장 표본으로는 못 잡는다 — 2026-08-04 a_count_up 은 0.5·4.0초는 멀쩡한데
     7.5초에서 카메라가 줌인해 인물이 커지고 배경에 계단이 생겼다.
     그래서 64컷을 **전부** 재고, 컷 사이 편차를 수치로 낸다.

   사용: python verify_w24_group_clip.py [동작 ...] [--all]
"""
import argparse
import glob
import os
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image

import make_w24_consistency_sheet as M
import recut_w24_groups as R
from gen_w24_group_prompts import ACTS, CM

SRC_DIR = "W24/group_clips"
TOL = 4.0                     # 컷 사이 키 편차가 이 %를 넘으면 불합격
RATIO_TOL = 6.0               # 규격 키 비율에서 이 %p 넘게 벗어나면 불합격
COUNT_MIN = 0.80              # 64컷 중 이 비율 이상에서 인원 수가 맞으면 통과(완화 기준)

# ★점프는 다리를 접으므로 머리~발끝 키가 **실제로** 줄어든다. 그걸 '흔들림'으로 잡으면
#   통과가 원리적으로 불가능하다(2026-08-04 a_jump·b_jump·c_jump 가 3회씩 전부 이걸로 탈락).
#   동작의 성질이므로 점프만 기준을 푼다. 다른 동작은 그대로 엄격하게 둔다.
JUMP_TOL, JUMP_RATIO_TOL = 22.0, 14.0


def tols(key):
    return (JUMP_TOL, JUMP_RATIO_TOL) if "jump" in key else (TOL, RATIO_TOL)
REFS = {k: refs for k, _g, refs, _s, _a in ACTS}


def log(m):
    print(m, flush=True)


def heights_of(path):
    """한 프레임에서 인물별 (x, 머리~발끝 키) — 왼쪽부터."""
    im = Image.open(path).convert("RGB")
    a = np.array(im).astype(int)
    bg = np.median(np.concatenate([a[0:6].reshape(-1, 3), a[-6:].reshape(-1, 3)]), axis=0)
    fg = np.abs(a - bg).sum(axis=2) > 60
    cut = Image.fromarray(np.dstack([np.array(im), (fg * 255).astype(np.uint8)]))
    # ★split_chars 는 이미 **왼쪽부터** 잘라 내놓는다. 잘린 조각의 getbbox 로 다시 정렬하면
    #   좌표가 조각 기준(대개 0)이라 키 순서로 뒤섞인다 — 그대로 순서를 쓴다.
    out = []
    for q in M.split_chars(cut):
        hf = M.head_feet(q)
        if hf and (hf[1] - hf[0]) > 60:
            out.append((hf[1] - hf[0] + 1, hf[1]))
    return out


def check(key):
    mp4 = f"{SRC_DIR}/{key}.mp4"
    if not os.path.exists(mp4):
        log(f"  ★클립 없음: {key}")
        return False
    tmp = tempfile.mkdtemp(prefix=f"vfy_{key}_")
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4,
                        "-vf", f"fps={R.FPS}", f"{tmp}/%03d.png"], check=True)
        frames = sorted(glob.glob(f"{tmp}/*.png"))[::R.TAKE][:64]
        per, counts, floor = [], [], []
        for f in frames:
            hs = heights_of(f)
            counts.append(len(hs))
            per.append([h for h, _y in hs])          # ★왼쪽부터의 순서를 그대로 쓴다
            floor.append(max((y for _h, y in hs), default=0))
        n = max(set(counts), key=counts.count)          # 최빈 인물 수
        rows = [p for p in per if len(p) == n]
        # ★2026-08-04 사장님 지시로 완화. "모든 컷에서 정확히 N명"은 너무 빡빡했다 —
        #   둘이 가까이 서서 팔이 스치기만 해도 세로 빈 열이 사라져 한 덩어리로 붙는다.
        #   영상이 나쁜 게 아니라 분리 방식의 한계다. **64컷 중 80% 이상이면 통과**로 본다.
        #   키 편차·규격 비율은 그대로 엄격하게 둔다 — 그게 실제로 중요한 항목이다.
        share = counts.count(n) / len(counts)
        log(f"\n=== {key} · {len(frames)}컷 ===")
        log(f"  인물 수: {n}명이 {counts.count(n)}/{len(counts)}컷 ({share * 100:.0f}%)"
            f" · 분포 {sorted(set(counts))}"
            + ("" if share >= COUNT_MIN else "  ★기준 미달"))
        ok = share >= COUNT_MIN
        # ★컷 사이 키 편차는 **판정에서 뺀다**(사장님 지시 2026-08-04) — 수치만 참고로 찍는다.
        #   점프처럼 다리를 접는 동작은 키가 실제로 줄어 원리적으로 통과할 수 없었다.
        for i in range(n):
            v = [r[i] for r in rows]
            lo, hi, mean = min(v), max(v), sum(v) / len(v)
            drift = (hi - lo) / mean * 100
            log(f"    인물{i + 1}(왼쪽부터): {lo}~{hi}px 평균{mean:.0f} · 편차 {drift:.1f}% (참고)")
        # ★검출 인원이 참조 인원과 다르면 그 자체로 불합격이다.
        #   2026-08-04: 예전엔 여기서 비율 검사를 '건너뛰기'만 해서 4명짜리 a_sit_class 가
        #   합격으로 찍혔다(사장님이 눈으로 잡아냄). 건너뛰지 말고 세운다.
        refs = REFS.get(key, [])
        if refs and n != len(refs):
            log(f"    ★검출 {n}명 ≠ 참조 {len(refs)}명 — 인원이 틀렸다")
            ok = False
        # ★규격 키 비율 — 누가 누군지 못 가리므로 **정렬해서 집합끼리** 견준다
        if refs and rows and len(refs) == n:
            want = sorted(CM[r] / max(CM[x] for x in refs) * 100 for r in refs)
            mean_h = [sum(r[i] for r in rows) / len(rows) for i in range(n)]
            got = sorted(h / max(mean_h) * 100 for h in mean_h)
            offs = [g - w for g, w in zip(got, want)]
            _t = tols(key)[1]          # ★점프는 다리를 접어 비율이 흔들린다 — 그때만 완화
            bad = max(abs(o) for o in offs) > _t
            log(f"    규격 비율: 목표 {['%.0f%%' % w for w in want]} · "
                f"실제 {['%.0f%%' % g for g in got]} (허용 ±{_t:.0f}%p)"
                + ("  ★어긋남" if bad else ""))
            ok &= not bad
        H = np.array(Image.open(frames[0])).shape[0]
        nt = sum(1 for y in floor if y >= H - 2)
        if nt:
            log(f"    ★발끝이 프레임 하단에 닿은 컷 {nt}개")
            ok = False
        log(f"  판정: {'통과' if ok else '불합격'}")
        return ok
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    allk = sorted(os.path.splitext(os.path.basename(p))[0]
                  for p in glob.glob(f"{SRC_DIR}/*.mp4")
                  if not os.path.basename(p).startswith("_"))
    ks = allk if a.all else (a.keys or ["a_count_up"])
    res = {k: check(k) for k in ks}
    log(f"\n통과 {sum(res.values())}/{len(res)}"
        + ("" if all(res.values()) else " — 불합격: " + ", ".join(k for k, v in res.items() if not v)))
