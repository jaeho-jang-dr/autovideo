# -*- coding: utf-8 -*-
"""W24 그룹 동작 영상 → ★192프레임에서 3장 중 1장 = 64컷 투명컷 (2026-08-03).

사장님 확정 원칙: **8초 × 24fps = 192프레임 → 3프레임마다 하나 = 64컷.**

★컷랑(`cutrang.py`)의 `cutout_char` 는 **최대 덩어리 하나만** 남긴다(단일 캐릭터 전용).
  그룹은 2~3명이 서로 떨어져 있어 덩어리가 여러 개다 → 그대로 쓰면 한 명만 남는다.
  그래서 이 파일은 **상위 N개 덩어리를 모두 살리는** 그룹 전용 컷아웃이다.

전경 판정(실측 재조정, 2026-08-03):
  ★스튜디오 배경은 **완전 무채색**이다(채도 median 3 · **max 8**). 밝기는 비네팅 때문에 106~223.
  `fg = (채도 > 12) | (밝기최소 < 100) | (밝기최소 > 232)`
    · 채도>12  → 살색·베이지·주황머리·시안발광·컬러옷 (배경은 절대 못 넘는다)
    · 밝기<100 → 검은 윤곽선 (배경 최소 106)
    · 밝기>232 → 흰 블라우스·흰 치마·흰 운동화 (배경 최대 223)
  실측: 의자씬 상위2덩어리=인물2(83935·56352, 다음 495) / 잉크씬 상위3=3인(다음 113).
  ※예전 `밝기<75 | 채도>60` 은 잉크 캐릭터엔 맞았지만 **컬러 인물의 살색·베이지를 배경으로 잘라
    몸에 구멍이 뚫렸다.** 채도 기준을 배경 실측값(max 8)에 맞춰 낮춰서 해결.

정렬: 카메라가 고정이므로 **64컷 공통 바운딩박스**로 잘라 낸다 → 컷끼리 흔들리지 않는다.
크기: 첫 프레임(팔 내린 중립 자세)의 가장 큰 덩어리 높이를 그룹 최장신 규격 px 에 맞춘다.

사용:
  python cut_w24_group.py --all
  python cut_w24_group.py a_write_jamo
"""
import argparse
import glob
import os
import shutil
import subprocess

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

SRC_DIR = "W24/group_clips"
OUT_DIR = "W24/group_cuts"
TMP_DIR = "W24/_gframes"
FPS = 24
TOTAL = 192          # 8초
STEP = 3             # ★3장 중 1장
NCUT = TOTAL // STEP  # 64

DARK_TH = 100        # 이보다 어두우면 전경(검은 윤곽선). 배경 최소 106.
SAT_TH = 12          # 이보다 채도가 있으면 전경. 배경 채도 max 8.
BRIGHT_TH = 232      # 이보다 밝으면 전경(흰 옷·흰 신발). 배경 최대 223.
MIN_RATIO = 0.05     # 최대 덩어리 대비 이 비율 미만은 잡음
SPECK_MAX = 400      # 이보다 작은 구멍 = 안티에일리어싱 티끌. 무조건 메운다.
HOLE_FILL_MAX = 16000  # 얼굴/머리 안쪽 후보의 상한. 이보다 크면 무조건 투명으로 남긴다.
HEAD_ZONE = 0.42     # 전경 상단에서 이 비율 안에 있는 구멍만 '머리 안쪽' 후보로 본다.

# W24_concept.md 키 규격 — 그룹 최장신 기준
SPEC = {"zolla_man": 761, "stickman": 749, "zolla_girl": 697,
        "injun": 770, "jieun": 706, "teacher_jay": 749, "madam_jay": 693}
GROUPS = {
    "a_write_jamo": (3, 761), "a_stack_block": (3, 761), "a_count_up": (3, 761),
    "b_ask_price": (2, 770), "b_hold_strap": (2, 770), "b_point_way": (2, 770),
    "b_highfive": (2, 770),
    "c_talk_sit": (2, 749), "c_weather_look": (2, 749),
    "c_emotion_face": (2, 749), "c_nod_agree": (2, 749),
    # ★씬 전환용 점프 (같은 캐릭터가 이어질 때)
    "a_jump": (3, 761), "b_jump": (2, 770), "c_jump": (2, 749),
    # ★교실(전시실) 앉기 3박자 + 수료식 꽃다발
    "a_sit_class": (3, 761), "b_sit_class": (2, 770), "c_sit_class": (2, 749),
    "flower_give": (2, 770),   # 티쳐제이749 + 인준770 → 최장신은 인준
}


def log(m):
    print(m, flush=True)


def explode(video, tmp):
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-i", video, "-vf", f"fps={FPS}",
                    "-frames:v", str(TOTAL), f"{tmp}/%05d.png"],
                   capture_output=True)
    return sorted(glob.glob(f"{tmp}/*.png"))


def mask_of(arr, nchar):
    """상위 nchar 덩어리를 모두 살리는 전경 마스크."""
    rgb = arr[:, :, :3].astype(int)
    lo = rgb.min(axis=2)
    sat = rgb.max(axis=2) - lo
    fg = (sat > SAT_TH) | (lo < DARK_TH) | (lo > BRIGHT_TH)
    lbl, n = ndimage.label(fg)
    if n == 0:
        return None
    sizes = ndimage.sum(np.ones_like(lbl), lbl, range(1, n + 1))
    order = np.argsort(sizes)[::-1]
    keep = [i + 1 for i in order[:nchar] if sizes[i] >= sizes[order[0]] * MIN_RATIO]
    m = np.isin(lbl, keep)

    # ★★사장님 지시(2026-08-03): **완벽하게 투명컷.**
    #   의자 살 사이 · 팔과 몸 사이 · 의자와 몸 사이는 **전부 투명**이어야 영상이 또렷하다.
    #   전경 판정이 색으로 정확해졌으므로(흰 옷·살색이 이미 전경) 남은 '구멍'은 전부 진짜 배경이다.
    #   → **안티에일리어싱 티끌만 메우고 나머지는 손대지 않는다.**
    #   예외 하나 — **흰 옷 안쪽의 그늘**은 채워야 한다. 흰 블라우스·흰 치마의 접힌 그늘은
    #   중간 회색(≈200)이라 배경 범위(106~223)와 겹쳐 구멍으로 뚫린다.
    #   구분법: **구멍을 둘러싼 테두리 색**을 본다.
    #     · 흰 옷 안쪽 구멍  → 테두리가 밝은 무채색(흰 천)      → 메운다
    #     · 의자 살 사이 틈  → 테두리가 갈색 나무(채도 높음)    → 그대로 투명
    holes = ndimage.binary_fill_holes(m) & ~m
    hl, hn = ndimage.label(holes)
    fill = []
    for i in range(1, hn + 1):
        h = hl == i
        if h.sum() <= SPECK_MAX:               # 티끌 — 무조건 메움
            fill.append(i)
            continue
        ring = ndimage.binary_dilation(h, iterations=3) & m   # 구멍을 감싼 전경 테두리
        if ring.sum() < 40:
            continue
        r_lo = lo[ring].mean()
        r_sat = sat[ring].mean()
        if r_lo > 225 and r_sat < 25:          # 테두리가 흰 천 → 옷 안쪽 그늘
            fill.append(i)
    if fill:
        m = m | np.isin(hl, fill)
    return m


def bbox(m):
    ys, xs = np.where(m)
    if not len(ys):
        return None
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def tallest_blob_h(m):
    lbl, n = ndimage.label(m)
    if n == 0:
        return 0
    best = 0
    for i in range(1, n + 1):
        ys, _ = np.where(lbl == i)
        if len(ys):
            best = max(best, ys.max() - ys.min() + 1)
    return best


def run(key):
    video = f"{SRC_DIR}/{key}.mp4"
    if not os.path.exists(video):
        log(f"★영상 없음: {video}")
        return False
    nchar, spec_h = GROUPS[key]
    out = f"{OUT_DIR}/{key}"
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out, exist_ok=True)

    log(f"\n=== {key}  ({nchar}인 · 최장신 {spec_h}px) ===")
    frames = explode(video, TMP_DIR)
    log(f"  프레임 {len(frames)}장 추출 (목표 {TOTAL})")
    if len(frames) < TOTAL:
        log(f"  ※{TOTAL}장에 못 미침 — 있는 만큼으로 진행")

    picks = frames[::STEP][:NCUT]
    log(f"  3장 중 1장 → {len(picks)}컷 선택")

    # 1차: 마스크 계산 + 공통 바운딩박스
    masks, arrs = [], []
    for p in picks:
        a = np.array(Image.open(p).convert("RGB"))
        m = mask_of(a, nchar)
        if m is None:
            log(f"  ★전경 없음: {os.path.basename(p)}")
            return False
        masks.append(m)
        arrs.append(a)
    boxes = [bbox(m) for m in masks]
    x0 = min(b[0] for b in boxes); y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes); y1 = max(b[3] for b in boxes)
    log(f"  공통 박스 ({x0},{y0})-({x1},{y1}) = {x1-x0}x{y1-y0}")

    # 크기 통일 — 첫 컷(중립 자세)의 최장 덩어리 높이를 규격에 맞춘다
    h0 = tallest_blob_h(masks[0])
    scale = spec_h / h0 if h0 else 1.0
    log(f"  첫 컷 최장신 {h0}px → 규격 {spec_h}px  (배율 {scale:.3f})")

    for i, (a, m) in enumerate(zip(arrs, masks)):
        rgba = np.dstack([a, (m * 255).astype(np.uint8)])
        im = Image.fromarray(rgba[y0:y1, x0:x1], "RGBA")
        w = max(1, round(im.width * scale)); h = max(1, round(im.height * scale))
        im = im.resize((w, h), Image.LANCZOS)
        im.save(f"{out}/{i:02d}.png")
    shutil.rmtree(TMP_DIR, ignore_errors=True)
    sz = Image.open(f"{out}/00.png").size
    log(f"✅ {out}/  {len(picks)}컷 · {sz[0]}x{sz[1]}")
    return True


def main(keys):
    os.makedirs(OUT_DIR, exist_ok=True)
    ok, bad = [], []
    for k in keys:
        (ok if run(k) else bad).append(k)
    log(f"\n완료 {len(ok)}/{len(keys)}")
    if bad:
        log(f"실패: {', '.join(bad)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    main(list(GROUPS) if a.all else (a.keys or ["a_write_jamo"]))
