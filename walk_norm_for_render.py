# -*- coding: utf-8 -*-
"""걷기 투명컷 16(497x736) → talk 포즈 규격(1024x1280·발끝 y1210·figure 높이~760)으로 재정합.
   → 렌더 시 talk 포즈와 캐릭터 크기·발끝선 일치. (독립 walk mp4는 이미 저장됨)
사용: python walk_norm_for_render.py
"""
import glob
import numpy as np
from PIL import Image

CW, CH, FEET_Y, TARGET = 1024, 1280, 1210, 760
n = 0
for p in sorted(glob.glob("assets/graphics/poses/jieun_w19_walk_*.png")):
    a = np.array(Image.open(p).convert("RGBA"))
    ys, xs = np.where(a[:, :, 3] > 0)
    if len(ys) == 0:
        continue
    crop = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    h, w = crop.shape[:2]
    sc = TARGET / h
    nw, nh = max(1, round(w * sc)), max(1, round(h * sc))
    im = Image.fromarray(crop).resize((nw, nh), Image.LANCZOS)
    cv = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
    cv.paste(im, (CW // 2 - nw // 2, FEET_Y - nh), im)
    cv.save(p)
    n += 1
print(f"걷기컷 {n}개 → {CW}x{CH}·발끝 y{FEET_Y}·figure {TARGET} 재정합 완료")
