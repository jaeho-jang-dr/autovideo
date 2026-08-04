# -*- coding: utf-8 -*-
"""W24 그룹 클립(8초) → 투명 컷 64장. ★크기는 절대 건드리지 않는다.

   ★사장님 지시(2026-08-04):
     - "함부로 크롭하거나 키우지 마라" → **리사이즈 없음.** 원본 픽셀 그대로 잘라낸다.
     - "캐릭터 크기가 바뀌면 폐기 수준" → 크롭 상자를 **64컷 전부 동일**하게 쓴다.
       프레임마다 따로 bbox 를 잡으면 같은 인물이 컷마다 커졌다 작아진다.

   컷아웃 기준은 컷랑(cutrang.cutout_char)과 같다 — "밝고 무채색이 아닌 것 = 캐릭터".
   다만 컷랑은 **가장 큰 덩어리 하나만** 남긴다(워터마크 제거용). 그룹 컷은 2~3명이 떨어져
   있어서 그대로 쓰면 한 명만 남는다 → **일정 크기 이상인 덩어리는 전부** 남기고, 작은 것
   (Veo 워터마크·잔점)만 버린다.

   출력: W24/group_cuts_v2/<동작>/00.png … 63.png   (기존 group_cuts 는 건드리지 않는다)
   사용: python recut_w24_groups.py [동작 ...] [--all] [--dry]
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import tempfile

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

SRC_DIR = "W24/group_clips"
OUT_DIR = "W24/group_cuts_v2"
FPS = 24
TAKE = 3                    # 192프레임 중 3장에 1장 = 64컷
MIN_BLOB = 2500             # 이보다 작은 덩어리는 인물이 아니다(워터마크·잔점)

# ★앉은 동작은 컷을 0.75배로 줄인다 (사장님 지시 2026-08-04).
#   Veo 는 `SEATED HEIGHT LOCK`(앉으면 선 키의 75%)을 세 번 시도해도 지키지 않았다 —
#   앉은 인물을 선 인물과 같은 키로 그린다(실측: 인준 앉기 638px vs 서기 612~651px).
#   프롬프트로 안 되니 **컷 단계에서 규격에 맞춰 축소**한다. 확대가 아니라 축소라 화질은 안 상한다.
SEATED_SCALE = 0.75
# ★둘러싸인 구멍은 메운다. 컷랑 기본값 8000 은 **머리 속(지름 180px ≈ 25,000px²)보다 작아서**
#   얼굴이 통째로 뚫리고 눈·입까지 날아갔다(2026-08-04 실측). 얼굴이 들어가도록 넉넉히 올린다.
#   열린 틈(발 사이·팔 사이)은 이미지 가장자리와 이어져 있어 '구멍'으로 잡히지 않으므로 안전하다.
HOLE_FILL_MAX = 60000


def log(m):
    print(m, flush=True)


def alpha_of(rgb):
    """밝고 무채색(=배경) 이 아닌 것 = 캐릭터. 인물 덩어리는 **전부** 남긴다."""
    a = rgb.astype(int)
    lo, hi = a.min(axis=2), a.max(axis=2)
    fg = ~((lo > 168) & ((hi - lo) < 45))
    lbl, n = ndimage.label(fg)
    if n == 0:
        return None, 0
    sizes = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
    keep = {i + 1 for i, s in enumerate(sizes) if s >= MIN_BLOB}
    if not keep:
        return None, 0
    m = np.isin(lbl, list(keep))
    filled = ndimage.binary_fill_holes(m)
    hl, hn = ndimage.label(filled & ~m)
    if hn:
        hs = ndimage.sum(np.ones_like(hl), hl, range(1, hn + 1))
        small = {i + 1 for i, s in enumerate(hs) if s < HOLE_FILL_MAX}
        if small:
            m |= np.isin(hl, list(small))
    return m, len(keep)


def recut(key, dry):
    mp4 = f"{SRC_DIR}/{key}.mp4"
    if not os.path.exists(mp4):
        log(f"  ★클립 없음: {mp4}")
        return False
    tmp = tempfile.mkdtemp(prefix=f"recut_{key}_")
    try:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4,
                        "-vf", f"fps={FPS}", f"{tmp}/%03d.png"], check=True)
        frames = sorted(glob.glob(f"{tmp}/*.png"))[::TAKE][:64]
        if len(frames) < 64:
            log(f"  ★프레임 부족: {len(frames)}장 (192프레임 8초가 맞는지 확인)")
        masks, counts = [], []
        for f in frames:
            m, c = alpha_of(np.array(Image.open(f).convert("RGB")))
            masks.append(m)
            counts.append(c)
        good = [(f, m) for f, m in zip(frames, masks) if m is not None]
        if not good:
            log("  ★인물 검출 실패")
            return False
        # ★크롭 상자 = 64컷 전체의 합집합. 전 컷에 같은 상자를 쓴다(크기 흔들림 방지)
        union = np.zeros_like(good[0][1])
        for _f, m in good:
            union |= m
        ys, xs = np.where(union)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        H = np.array(Image.open(frames[0])).shape[0]
        touch = " ★발끝이 프레임 하단에 닿음" if y1 >= H - 2 else ""
        sc = SEATED_SCALE if ("sit" in key) else 1.0    # ★앉은 동작만 축소
        out = f"{OUT_DIR}/{key}"
        if not dry:
            shutil.rmtree(out, ignore_errors=True)
            os.makedirs(out, exist_ok=True)
            for i, (f, m) in enumerate(good):
                rgb = np.array(Image.open(f).convert("RGB"))
                rgba = np.dstack([rgb, (m * 255).astype(np.uint8)])
                im = Image.fromarray(rgba[y0:y1, x0:x1])
                if sc != 1.0:      # ★앉기 축소 — 64컷에 **같은 배율**을 써야 컷 사이가 안 흔들린다
                    im = im.resize((max(1, round(im.width * sc)),
                                    max(1, round(im.height * sc))), Image.LANCZOS)
                im.save(f"{out}/{i:02d}.png")
            # ★크롭 위치를 남긴다 — 미리보기에서 **원래 화면의 그 자리**에 되돌려 놓기 위해서다.
            W = np.array(Image.open(frames[0])).shape[1]
            json.dump(dict(x=int(x0), y=int(y0), w=int(round((x1 - x0) * sc)),
                           h=int(round((y1 - y0) * sc)), scale=sc,
                           frame_w=int(W), frame_h=int(H), cuts=len(good)),
                      open(f"{out}/_crop.json", "w"), indent=1)
        cs = sorted(set(counts))
        log(f"  {key:<16} {len(good)}컷 · 크롭 {x1 - x0}x{y1 - y0}"
            + (f" ×{sc} → {round((x1-x0)*sc)}x{round((y1-y0)*sc)}" if sc != 1.0 else "")
            + f" · 인물덩어리 {cs}{touch}")
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main(keys, dry):
    os.makedirs(OUT_DIR, exist_ok=True)
    log(f"{'(모의) ' if dry else ''}=== W24 그룹 클립 재컷팅 (리사이즈 없음) ===")
    ok = sum(bool(recut(k, dry)) for k in keys)
    log(f"\n{ok}/{len(keys)} 동작 완료 → {OUT_DIR}/")
    return 0 if ok == len(keys) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    allk = sorted(os.path.splitext(os.path.basename(p))[0]
                  for p in glob.glob(f"{SRC_DIR}/*.mp4")
                  if not os.path.basename(p).startswith("_"))
    raise SystemExit(main(allk if a.all else (a.keys or allk), a.dry))
