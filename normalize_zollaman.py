# -*- coding: utf-8 -*-
"""졸라맨 포즈 컷아웃 크기 정규화 — 머리~발 높이를 일정하게(base 기준 644),
발을 캔버스 중심+322에 정렬. 팔 든 포즈도 몸통 크기 일치. 재사용."""
import numpy as np, sys, os
from PIL import Image
from scipy import ndimage
TARGET = 644; FEET_OFF = 322

def head_top(alpha):
    it = 11
    er = ndimage.binary_erosion(alpha, iterations=it)
    lbl, n = ndimage.label(er)
    if n == 0: return int(np.where(alpha.any(axis=1))[0].min())
    sizes = ndimage.sum(er, lbl, range(1, n+1))
    head = int(np.argmax(sizes)) + 1
    hy = np.where((lbl == head).any(axis=1))[0]
    return max(0, int(hy.min()) - it)

def normalize(path, out=None):
    im = Image.open(path).convert("RGBA"); a = np.asarray(im)
    al = a[:, :, 3] > 40
    rows = np.where(al.any(axis=1))[0]
    if len(rows) == 0: return
    feet = int(rows.max()); ht = head_top(al); body = feet - ht
    if body < 50: body = feet - int(rows.min())
    sc = TARGET / body
    nw, nh = max(1, int(im.width * sc)), max(1, int(im.height * sc))
    im2 = im.resize((nw, nh), Image.LANCZOS); a2 = np.asarray(im2); al2 = a2[:, :, 3] > 40
    r2 = np.where(al2.any(axis=1))[0]; feet2 = int(r2.max()); ht2 = int(ht * sc)
    bc = ht2 + TARGET // 2
    bm = al2[max(0, feet2 - int(nh * 0.12)):feet2 + 1]
    fx = int(np.where(bm.any(axis=0))[0].mean()) if bm.any() else nw // 2
    Hc = 2 * max(bc, nh - bc) + 20; Wc = 2 * max(fx, nw - fx) + 20
    canvas = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    canvas.alpha_composite(im2, (Wc // 2 - fx, Hc // 2 - bc))
    canvas.save(out or path)
    return sc

if __name__ == "__main__":
    for p in sys.argv[1:]:
        s = normalize(p, p.replace(".png", "_norm.png"))
        print(f"  {os.path.basename(p)}: x{s:.2f}")
