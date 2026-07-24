# -*- coding: utf-8 -*-
"""W20 인준(캐주얼) 포즈: 흰배경 플러드필 컷아웃(옷·신발 내부 흰색 보존) → 단일배율 정규화
   (발끝 정렬·머리끝~발끝 몸높이 770 통일) → assets/graphics/poses/injun_w20_<key>.png (1024x1280 RGBA).
   ★걷기컷(injun_w20_walk_*, 몸높이 ~779·발끝 y1208)과 키 일치.
1) 컷아웃+측정:  python cutout_injun_w20.py measure
2) 정규화 저장:  python cutout_injun_w20.py apply
"""
import os, glob, sys
import numpy as np
from scipy import ndimage
from PIL import Image

ROOT = "D:/Entertainments/DevEnvironment/autovideo"
SRC = os.path.join(ROOT, "home_vocab/w20")          # injun_w20_*.png (bg 하위폴더 제외)
DST = os.path.join(ROOT, "assets/graphics/poses")
CANVAS_W = 1024
CANVAS_H = 1280        # 팔 든 포즈가 머리 위로 뻗어도 안 잘리게 세로 여유
FEET_Y = 1209          # 발끝 정렬선(걷기컷 y1208과 일치)
TARGET_BODY = 770      # ★머리끝~발끝 몸높이 통일값(팔 든 것 제외)


def cutout(src):
    arr = np.array(Image.open(src).convert("RGBA"))
    rgb = arr[:, :, :3].astype(int)
    lo = rgb.min(axis=2); hi = rgb.max(axis=2)
    white = (lo > 200) & ((hi - lo) < 30)           # 밝고 무채색 = 흰배경
    lbl, n = ndimage.label(white)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    border.discard(0)
    arr[np.isin(lbl, list(border)), 3] = 0          # ① 테두리에 붙은 바깥 배경 제거

    # ② 팔과 몸통 사이·팔과 얼굴 사이에 '갇힌' 배경 흰색 제거(운동화 보존).
    ys0, xs0 = np.where(arr[:, :, 3] > 0)
    if len(ys0) == 0:
        return None
    top, bot = ys0.min(), ys0.max()
    ch = max(1, bot - top)
    foot_line = bot - int(0.15 * ch)                # 바닥 15% = 운동화 보호대(이 아래는 안 지움)
    remain = white & (arr[:, :, 3] > 0)             # 아직 남은(갇힌) 흰색
    lbl2, n2 = ndimage.label(remain)
    for cid in range(1, n2 + 1):
        cy, cx = np.where(lbl2 == cid)
        if len(cy) < 150:                            # 아주 작은 얼룩·눈 하이라이트는 무시
            continue
        if int(cy.mean()) < foot_line:               # 발(운동화)보다 위에 있는 갇힌 흰색 = 배경 구멍
            arr[cy, cx, 3] = 0

    ys, xs = np.where(arr[:, :, 3] > 0)
    if len(ys) == 0:
        return None
    return arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def body_metrics(crop):
    """머리끝~발끝 몸높이(얇게 든 팔·손가락 제외) + 몸통 중심 x 감지."""
    alpha = crop[:, :, 3] > 0
    w = alpha.sum(axis=1).astype(float)             # 행별 폭
    H = len(w)
    torso = np.median(w[int(H * 0.42):int(H * 0.72)]) or w.max()  # 몸통/엉덩이 폭
    thr = max(0.5 * torso, 0.12 * w.max())
    head_top = 0
    for y in range(H):
        if w[y] >= thr and np.mean(w[y:y + 22] >= thr * 0.6) > 0.6:  # 지속되는 큰 폭 = 머리(든 손 blob 배제)
            head_top = y
            break
    body_span = (H - 1) - head_top
    band = alpha[int(H * 0.42):int(H * 0.72)]
    bx = np.where(band.any(axis=0))[0]
    cx = int(bx.mean()) if len(bx) else crop.shape[1] // 2
    return head_top, body_span, cx


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "measure"
    files = sorted(f for f in glob.glob(os.path.join(SRC, "injun_w20_*.png"))
                   if "_walk_" not in os.path.basename(f))
    print(f"대상 {len(files)}개  모드={mode}")
    rows = []
    for p in files:
        k = os.path.splitext(os.path.basename(p))[0]
        crop = cutout(p)
        if crop is None:
            print(f"  {k}: 빈 이미지"); continue
        h, w = crop.shape[:2]
        rows.append((k, w, h, crop))
    rows = [(k, w, h, crop) + body_metrics(crop)[1:] for (k, w, h, crop) in rows]  # +(span, cx)
    spans = [r[4] for r in rows]
    med = int(np.median(spans))
    print(f"감지 몸높이(머리끝~발끝): min {min(spans)} / 중앙 {med} / max {max(spans)} → 전부 {TARGET_BODY}로 통일")
    for k, w, h, _, span, _ in rows:
        flag = "  ⚠몸높이편차" if abs(span - med) / med * 100 > 6 else ""
        print(f"  {k:28s} bbox {w}x{h}  몸높이 {span}{flag}")
    if mode != "apply":
        return
    for k, w, h, crop, span, cx in rows:
        scale = TARGET_BODY / span
        nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
        im = Image.fromarray(crop).resize((nw, nh), Image.LANCZOS)
        canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
        x = CANVAS_W // 2 - round(cx * scale)
        y = FEET_Y - nh
        canvas.paste(im, (x, y), im)
        canvas.save(os.path.join(DST, f"{k}.png"))
    print(f"정규화 저장 완료: {len(rows)}개 (몸높이 {TARGET_BODY}px, 발끝 y{FEET_Y}, 캔버스 {CANVAS_W}x{CANVAS_H}) → {DST}/injun_w20_*.png")


if __name__ == "__main__":
    main()
