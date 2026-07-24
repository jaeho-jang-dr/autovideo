# -*- coding: utf-8 -*-
"""W19 지은(등산복) 포즈: 흰배경 플러드필 컷아웃(등산화 보존) → 단일배율 정규화(발끝 정렬·키 통일)
   → assets/graphics/poses/jieun_w19_<key>.png (1024x1024 RGBA). 걷기컷과 함께 쓰는 talk 포즈.
1) 컷아웃+측정:  python cutout_jieun_w19.py measure
2) 정규화 저장:  python cutout_jieun_w19.py apply
"""
import os, glob, sys
import numpy as np
from scipy import ndimage
from PIL import Image

ROOT = "D:/Entertainments/DevEnvironment/autovideo"
SRC = os.path.join(ROOT, "home_vocab/w19")          # jieun_w19_*.png (bg 하위폴더 제외)
DST = os.path.join(ROOT, "assets/graphics/poses")
CANVAS_W = 1024
CANVAS_H = 1280        # 팔 든 포즈가 머리 위로 뻗어도 안 잘리게 세로 여유
FEET_Y = 1210          # 발끝 정렬선
TARGET_BODY = 770      # ★머리끝~발끝 몸높이 통일값(팔 든 것 제외)


def cutout(src):
    arr = np.array(Image.open(src).convert("RGBA"))
    rgb = arr[:, :, :3].astype(int)
    lo = rgb.min(axis=2); hi = rgb.max(axis=2)
    white = (lo > 200) & ((hi - lo) < 30)           # 밝고 무채색 = 흰배경
    lbl, n = ndimage.label(white)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    border.discard(0)
    arr[np.isin(lbl, list(border)), 3] = 0
    ys, xs = np.where(arr[:, :, 3] > 0)
    if len(ys) == 0:
        return None
    return arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def body_metrics(crop):
    """머리끝~발끝 몸높이(얇게 든 팔·손가락 제외) + 몸통 중심 x 감지.
    상단부터 스캔: 폭이 몸통폭의 절반 이상이고 세로로 지속되는 첫 행 = 머리끝."""
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
    files = sorted(f for f in glob.glob(os.path.join(SRC, "jieun_w19_*.png")))
    print(f"대상 {len(files)}개  모드={mode}")
    rows = []
    for p in files:
        k = os.path.splitext(os.path.basename(p))[0]
        crop = cutout(p)
        if crop is None:
            print(f"  {k}: 빈 이미지"); continue
        h, w = crop.shape[:2]
        rows.append((k, w, h, crop))
    # 몸높이(머리끝~발끝) 감지 = 통일 기준
    rows = [(k, w, h, crop) + body_metrics(crop)[1:] for (k, w, h, crop) in rows]  # +(span, cx)
    spans = [r[4] for r in rows]
    med = int(np.median(spans))
    print(f"감지 몸높이(머리끝~발끝): min {min(spans)} / 중앙 {med} / max {max(spans)} → 전부 {TARGET_BODY}로 통일")
    for k, w, h, _, span, _ in rows:
        flag = "  ⚠몸높이편차" if abs(span - med) / med * 100 > 6 else ""
        print(f"  {k:26s} bbox {w}x{h}  몸높이 {span}{flag}")
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
    print(f"정규화 저장 완료: {len(rows)}개 (몸높이 {TARGET_BODY}px 통일, 발끝 y{FEET_Y}, 캔버스 {CANVAS_W}x{CANVAS_H}) → {DST}/jieun_w19_*.png")


if __name__ == "__main__":
    main()
