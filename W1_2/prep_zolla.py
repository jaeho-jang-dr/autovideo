# -*- coding: utf-8 -*-
"""W24 졸라맨·졸라걸 앉기 컷에서 **의자를 빼고** 키를 맞춘다.

★W24 규격은 "앉기 컷아웃엔 의자 포함"이라 벤치에 앉히려면 의자를 지워야 한다.
★키는 **머리끝~발끝만** 잰다 — 의자를 포함해 bbox 로 재면 틀린다.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

SRC = "assets/graphics/poses"
OUT = "W1_2/_poses"
PAIRS = [("w24_zolla_man_sit_look_front", "zolla_man_sit_bench"),
         ("w24_zolla_girl_sit_look_front", "zolla_girl_sit_bench")]


def is_wood(a):
    """의자 나무색 — 갈색 계열 전부.

    ★어두운 갈색(102,50,23)까지 잡아야 의자 다리가 지워진다(2026-08-11 실측).
      캐릭터는 검정 선 + 흰 면뿐이라(머리카락은 따로 보호) 갈색은 전부 의자다.
    """
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    brownish = (r > g + 10) & (g >= b - 4) & (r > b + 22)
    return brownish & (r > 45) & (r < 235)


def strip_chair(png):
    """의자를 지운다.

    ★색만으로는 못 가른다 — 졸라걸 **주황 머리(213,118,31)** 가 나무색 판정에
      그대로 걸려 머리카락이 깎였다(2026-08-11 실측). 그래서 **머리 영역(위 22%)은
      건드리지 않는다.** 의자는 항상 몸통 아래에 있다.
    """
    im = Image.open(png).convert("RGBA")
    a = np.asarray(im).copy()
    al = a[:, :, 3]
    ys, xs = np.nonzero(al > 8)
    y0, h = int(ys.min()), int(ys.max() - ys.min() + 1)
    protect = np.zeros(al.shape, bool)
    protect[:y0 + int(h * 0.22)] = True            # ★머리·머리카락 보호

    rgb = a[:, :, :3]
    wood = is_wood(rgb) & (al > 8) & ~protect
    # ★의자의 회색 금속·그림자 잔재도 지운다. 캐릭터는 검정 선 + 흰 면뿐이라
    #   중간 회색(115~205)은 전부 의자다.
    r, g, b = rgb[..., 0].astype(int), rgb[..., 1].astype(int), rgb[..., 2].astype(int)
    grey = (abs(r - g) < 16) & (abs(g - b) < 16) & (r > 112) & (r < 208)
    a[(wood | (grey & (al > 8) & ~protect)), 3] = 0
    # 의자를 지운 뒤 남은 작은 부스러기 제거 — 가장 큰 덩어리만 남긴다
    m = a[:, :, 3] > 8
    lab, n = ndimage.label(m)
    if n > 1:
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        keep = int(np.argmax(sizes)) + 1
        drop = m & (lab != keep)
        # 얼굴·머리처럼 떨어져 보이는 조각은 살린다(면적 큰 것 몇 개)
        for i, s in enumerate(sizes, 1):
            if i != keep and s > sizes[keep - 1] * 0.03:
                drop &= (lab != i)
        a[drop, 3] = 0
    return Image.fromarray(a, "RGBA")


def body_height(im):
    """머리끝~발끝. 의자를 지운 뒤라 알파 bbox 가 곧 사람 키다."""
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    return int(ys.max() - ys.min() + 1), (int(xs.min()), int(ys.min()),
                                          int(xs.max()), int(ys.max()))


def main():
    os.makedirs(OUT, exist_ok=True)
    info = []
    for src, dst in PAIRS:
        p = os.path.join(SRC, src + ".png")
        im = strip_chair(p)
        h, box = body_height(im)
        im = im.crop((box[0], box[1], box[2] + 1, box[3] + 1))
        q = os.path.join(OUT, "stickman_%s.png" % dst)
        im.save(q)
        info.append((dst, h, im.size))
        print("%-24s 의자 제거 → 사람 키 %dpx · %s" % (dst, h, im.size))
    # 키 통일 — 둘 중 큰 쪽에 맞추지 말고 **원래 비율**을 유지한다.
    # W24 규격: 졸라맨 761 · 졸라걸 697 → 남녀 키 차이를 그대로 둔다
    print("\n★키 비율 유지 — 졸라맨 %d : 졸라걸 %d = 1 : %.3f"
          % (info[0][1], info[1][1], info[1][1] / info[0][1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
