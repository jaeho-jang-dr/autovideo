# -*- coding: utf-8 -*-
"""W21 마담제이 걷기/인사 프레임 → 투명 컷아웃 + 정규화(발끝 정렬·몸높이 770 통일).
배경=옅은 회색 텍스처(프레임별 밝기 다름)·발밑 그림자·Veo 반짝이 제거,
흰 치마/신발은 검정 외곽선으로 닫혀 있어 보존.

오른 걷기: walk_frames/w_064,068,...,092 → mj_w21_walk_r1..r8
왼 걷기 : 위를 좌우반전                    → mj_w21_walk_l1..l8
정면 인사: wave_frames/v_018,028,...,088   → mj_w21_greet1..8

  python cutout_madam_w21.py            # 컷아웃+정규화 저장
"""
import os
import numpy as np
from scipy import ndimage
from PIL import Image

ROOT = "D:/Entertainments/DevEnvironment/autovideo"
WALKDIR = os.path.join(ROOT, "home_vocab/w21/walk_frames")
WAVEDIR = os.path.join(ROOT, "home_vocab/w21/wave_frames")
DST = os.path.join(ROOT, "assets/graphics/poses")

CANVAS_W, CANVAS_H = 1024, 1280
FEET_Y = 1209
TARGET_BODY = 770

WALK_FRAMES = [124, 128, 132, 136, 140, 144, 148, 152]
GREET_FRAMES = [18, 28, 38, 48, 58, 68, 78, 88]


def cutout(src):
    """옅은 회색 배경 컷아웃(밝기+채도 기반).
    ① 테두리 플러드필로 바깥 배경 + 발밑 그림자 제거(밝은 무채색은 통과, 외곽선/피부/코랄이 봉인).
    ② 갇힌 밝은 무채색 포켓(다리 사이 흰 아티팩트) 제거 — 얼굴(위)·치마(대면적)·신발(아래)은 보존.
    ③ 최대 연결성분만 유지."""
    im = Image.open(src).convert("RGBA")
    arr = np.array(im)
    rgb = arr[:, :, :3].astype(int)
    H, W = rgb.shape[:2]
    bright = rgb.mean(axis=2)
    sat = rgb.max(axis=2) - rgb.min(axis=2)

    # ① 밝은 무채색 = 배경/그림자로 통과 가능(피부 sat>48·코랄·머리 제외, 흰치마/신발은 외곽선으로 봉인)
    passable = (bright > 145) & (sat < 48)
    lbl, n = ndimage.label(passable)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    border.discard(0)
    arr[np.isin(lbl, list(border)), 3] = 0    # 바깥 배경 + 그림자 + 반짝이 제거

    # 캐릭터 bbox(그림자 제거 후) → 세로 상대위치로 포켓 판정
    ys0, xs0 = np.where(arr[:, :, 3] > 0)
    if len(ys0) == 0:
        return None
    top, bot = ys0.min(), ys0.max()
    ch = max(1, bot - top)

    # ② 갇힌 '회색(배경색)' 포켓만 제거(다리 사이). 흰치마/신발(bright>238)·피부(sat>=14)는 보존
    achr = (arr[:, :, 3] > 0) & (sat < 14) & (bright > 150) & (bright <= 238)
    lbl2, n2 = ndimage.label(achr)
    for cid in range(1, n2 + 1):
        cy, cx = np.where(lbl2 == cid)
        a = len(cy)
        if a < 300 or a >= 2500:              # 작은 피부 얼룩·큰 치마는 건드리지 않음
            continue
        rel = (cy.mean() - top) / ch
        if 0.56 < rel < 0.85:                 # 치마 아래~신발 위 = 다리 사이 배경 포켓
            arr[cy, cx, 3] = 0

    # ③ 최대 연결성분만 유지(잔여 얼룩 제거)
    solid = arr[:, :, 3] > 0
    lbl3, n3 = ndimage.label(solid)
    if n3 > 1:
        sizes = ndimage.sum(np.ones_like(lbl3), lbl3, range(1, n3 + 1))
        keep = int(np.argmax(sizes)) + 1
        arr[(lbl3 != keep) & (lbl3 != 0), 3] = 0

    ys, xs = np.where(arr[:, :, 3] > 0)
    if len(ys) == 0:
        return None
    return arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def body_span_cx(crop):
    alpha = crop[:, :, 3] > 0
    w = alpha.sum(axis=1).astype(float)
    H = len(w)
    torso = np.median(w[int(H * 0.42):int(H * 0.72)]) or w.max()
    thr = max(0.5 * torso, 0.12 * w.max())
    head_top = 0
    for y in range(H):
        if w[y] >= thr and np.mean(w[y:y + 22] >= thr * 0.6) > 0.6:
            head_top = y
            break
    span = (H - 1) - head_top
    band = alpha[int(H * 0.42):int(H * 0.72)]
    bx = np.where(band.any(axis=0))[0]
    cx = int(bx.mean()) if len(bx) else crop.shape[1] // 2
    return span, cx


def normalize(crop):
    span, cx = body_span_cx(crop)
    scale = TARGET_BODY / span
    h, w = crop.shape[:2]
    nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    im = Image.fromarray(crop).resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    x = CANVAS_W // 2 - round(cx * scale)
    y = FEET_Y - nh
    canvas.paste(im, (x, y), im)
    return canvas


def main():
    os.makedirs(DST, exist_ok=True)
    # 오른 걷기
    for i, fr in enumerate(WALK_FRAMES, 1):
        crop = cutout(os.path.join(WALKDIR, f"w_{fr:03d}.png"))
        canvas = normalize(crop)
        canvas.save(os.path.join(DST, f"mj_w21_walk_r{i}.png"))
        canvas.transpose(Image.FLIP_LEFT_RIGHT).save(os.path.join(DST, f"mj_w21_walk_l{i}.png"))
        print(f"  walk {fr:03d} -> mj_w21_walk_r{i}.png / _l{i}.png")
    # 정면 인사
    for i, fr in enumerate(GREET_FRAMES, 1):
        crop = cutout(os.path.join(WAVEDIR, f"v_{fr:03d}.png"))
        canvas = normalize(crop)
        canvas.save(os.path.join(DST, f"mj_w21_greet{i}.png"))
        print(f"  wave {fr:03d} -> mj_w21_greet{i}.png")
    print("완료: 오른걷기8 + 왼걷기8 + 인사8 =", len(WALK_FRAMES) * 2 + len(GREET_FRAMES), "개 →", DST)


if __name__ == "__main__":
    main()
