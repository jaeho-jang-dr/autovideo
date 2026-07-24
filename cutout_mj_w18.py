# -*- coding: utf-8 -*-
"""W18 마담제이 포즈: 흰배경 플러드필 컷아웃(신발 보존) → 크기 정규화(발끝 정렬·키 통일)
   → assets/graphics/poses/mj_w18_*.png (1024x1024 RGBA, 발끝 y=966, 서기 키≈897 목표).
1) 먼저 컷아웃+측정만: python cutout_mj_w18.py measure
2) 정규화 저장:        python cutout_mj_w18.py apply
"""
import os, glob, sys
import numpy as np
from scipy import ndimage
from PIL import Image

ROOT = "D:/Entertainments/DevEnvironment/autovideo"
SRC = os.path.join(ROOT, "assets/graphics/poses/mj_w18_src")
DST = os.path.join(ROOT, "assets/graphics/poses")
CANVAS = 1024
FEET_Y = 966          # tj_w17 규격 계승
TARGET_H = 897        # 서기 인물 목표 높이(발끝~머리끝)


def cutout(src):
    arr = np.array(Image.open(src).convert("RGBA"))
    rgb = arr[:, :, :3].astype(int)
    lo = rgb.min(axis=2); hi = rgb.max(axis=2)
    # 배경 = 밝고(>195) 무채색(채도 낮음, 채널차<30) — 흰(255)·연회색(207) 모두 포함.
    # 테두리에 연결된 것만 제거 → 내부 흰 치마·크림 얼굴은 검정 외곽선에 둘러싸여 보존됨.
    white = (lo > 195) & ((hi - lo) < 30)
    lbl, n = ndimage.label(white)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    border.discard(0)
    bg = np.isin(lbl, list(border))
    arr[bg, 3] = 0
    ys, xs = np.where(arr[:, :, 3] > 0)
    if len(ys) == 0:
        return None
    crop = arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return crop


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "measure"
    files = sorted(glob.glob(os.path.join(SRC, "mj_w18_*.png")))
    print(f"대상 {len(files)}개  모드={mode}")
    rows = []
    for p in files:
        k = os.path.splitext(os.path.basename(p))[0]
        crop = cutout(p)
        if crop is None:
            print(f"  {k}: 빈 이미지"); continue
        h, w = crop.shape[:2]
        rows.append((k, w, h, crop))
    hs = [h for _, _, h, _ in rows]
    if hs:
        print(f"컷아웃 높이 분포: min {min(hs)} / 중앙 {int(np.median(hs))} / max {max(hs)} (편차 {max(hs)-min(hs)})")
    for k, w, h, _ in rows:
        print(f"  {k:22s} {w}x{h}")
    if mode != "apply":
        return
    # ★단일 스케일 정규화: agy가 몸 스케일을 이미 일관되게 뽑았으므로(비팔올림 ~867),
    #   개별 bbox 정규화(팔올림 포즈 왜곡) 대신 '가장 큰 포즈가 캔버스에 딱 맞는' 단일 배율을 전체 적용.
    #   → 모든 포즈의 몸 크기 동일 유지 + 팔올림(cheer)은 자연히 위로 뻗음(잘림 0). 발끝 y=FEET_Y 정렬.
    max_h = max(h for _, _, h, _ in rows)
    scale = FEET_Y / max_h
    for k, w, h, crop in rows:
        nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
        im = Image.fromarray(crop).resize((nw, nh), Image.LANCZOS)
        canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        x = (CANVAS - nw) // 2
        y = FEET_Y - nh
        canvas.paste(im, (max(0, x), max(0, y)), im)
        canvas.save(os.path.join(DST, f"{k}.png"))
    body = round(max(h for _, _, h, _ in rows if h < 900) * scale)
    print(f"정규화 저장 완료: {len(rows)}개 (단일배율 {scale:.3f}, 서기 몸높이≈{body}px, 발끝 y{FEET_Y}) → {DST}/mj_w18_*.png")


if __name__ == "__main__":
    main()
