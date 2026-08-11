# -*- coding: utf-8 -*-
"""W1-2 스틱맨 자산을 **흰 배경 + 검은 선**으로 만든다.

★사장님 지시(2026-08-11): "배경은 흰색, 캐릭터 선을 검정으로 다시 바꾸어라."
  가이드 `W24R/guides/stickman.png` 와 같은 형식(흰 바탕·검은 잉크).

투명본(`_poses/`)은 합성용으로 그대로 두고, 흰 배경본을 `_poses_white/` 에 따로 만든다.
"""
import glob
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "W1_2", "_poses")
DST = os.path.join(ROOT, "W1_2", "_poses_white")
INK = 26            # 가이드와 같은 검정
BG = 255


def flatten(path):
    """알파를 흰 바탕에 **제대로 합성**한다.

    ★알파만 보고 검정을 칠하면 안 된다 — 카드처럼 색이 있는 소품이 통째로
      새까맣게 된다(2026-08-11 실수). 원래 RGB 를 살려 흰 배경 위에 얹는다.
    """
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im).astype(np.float32)
    rgb, alpha = a[:, :, :3], a[:, :, 3:4] / 255.0
    out = BG * (1 - alpha) + rgb * alpha
    return Image.fromarray(out.astype(np.uint8), "RGB")


def main():
    os.makedirs(DST, exist_ok=True)
    files = sorted(glob.glob(os.path.join(SRC, "stickman_w1d2_*.png")))
    for p in files:
        im = flatten(p)
        q = os.path.join(DST, os.path.basename(p))
        im.save(q)
    print("흰 배경본 %d장 → %s" % (len(files), DST))

    # 검증 — 배경이 진짜 흰색인지, 잉크가 진짜 검정인지
    s = np.asarray(Image.open(os.path.join(DST, os.path.basename(files[0]))))
    print("  배경 화소값 %s · 최소(잉크) %d · 흰색 비율 %.1f%%"
          % (np.bincount(s[..., 0].ravel()).argmax(), s.min(),
             (s[..., 0] == 255).mean() * 100))


if __name__ == "__main__":
    main()
