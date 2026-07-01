#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""prep_intermediate_poses.py — 실사 캐릭터(지은·인준·닥터제이·마담제이) 투명 컷아웃을
렌더러용 트림 포즈로 복사: assets/characters/cutouts/<char>_<pose>.png → assets/graphics/poses/stickman_<char>_<pose>.png
(렌더러 gesture_seq 가 assets/graphics/poses/stickman_<name>.png 를 찾으므로 이 네이밍 필요)
트림: 알파 bbox + 약간 패딩. 재실행 가능(멱등).
사용: python prep_intermediate_poses.py [char ...]   (기본 jieun dr_jay madam_jay injun)
"""
import os
import sys
import glob

import numpy as np
from PIL import Image

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
CUT = os.path.join(ROOT, "assets", "characters", "cutouts")
POSES = os.path.join(ROOT, "assets", "graphics", "poses")
os.makedirs(POSES, exist_ok=True)


def trim(im, pad=8):
    bb = im.split()[3].getbbox()
    if not bb:
        return im
    x0, y0, x1, y1 = bb
    w, h = im.size
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)))


def main():
    chars = sys.argv[1:] or ["jieun", "dr_jay", "madam_jay", "injun"]
    n = 0
    for ch in chars:
        files = sorted(glob.glob(os.path.join(CUT, f"{ch}_*.png")))
        for f in files:
            pose = os.path.basename(f)[len(ch) + 1:].replace(".png", "")
            im = Image.open(f).convert("RGBA")
            a = np.array(im)[:, :, 3]
            if a.max() == 0:
                continue
            im = trim(im)
            out = os.path.join(POSES, f"stickman_{ch}_{pose}.png")
            im.save(out)
            n += 1
        print(f"  {ch}: {len(files)} poses -> graphics/poses (trimmed) e.g. stickman_{ch}_*")
    print(f"TOTAL {n} renderer poses prepared")


if __name__ == "__main__":
    main()
