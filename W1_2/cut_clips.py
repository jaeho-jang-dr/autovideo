# -*- coding: utf-8 -*-
"""W1-2 동영상 3개 → 64프레임 투명컷 → 스틸 클립.

한글랑 규격: 동영상 → **프레임 64개** 추출 → 투명컷 → 키 통일 → 배경 위에 얹기.
원본은 흰 배경 선화라 밝기 하나로 가른다(정지 포즈와 같은 방식).
"""
import glob
import os
import subprocess

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIPS = os.path.join(ROOT, "W1_2", "clips")
OUT = os.path.join(ROOT, "W1_2", "cuts")
TMP = os.path.join(ROOT, "W1_2", "_cutbuf")
N = 64
TARGET_H = 740          # 정지 포즈·걷기와 같은 키
INK = 26


def cut_white(im):
    """흰 배경 → 투명. ★단, **선으로 둘러싸인 안쪽(얼굴·카드)은 흰색으로 채운다.**

    흰색을 전부 지우면 머리 안쪽과 카드 안쪽까지 뚫려 배경이 비친다.
    규격은 '얼굴은 흰 바탕에 눈·입'이다. 그래서 바깥 배경과 이어지지 않는
    막힌 흰 영역은 불투명 흰색으로 되돌린다.
    """
    from scipy import ndimage

    g = np.asarray(im.convert("L"), np.float32)
    al = np.clip((225.0 - g) / 55.0, 0, 1)          # 잉크=1, 배경=0

    # 바깥 배경 = 테두리에서 이어지는 '거의 흰' 영역
    bg = al < 0.15
    lab, n = ndimage.label(bg)
    border = set(lab[0].tolist()) | set(lab[-1].tolist()) | \
        set(lab[:, 0].tolist()) | set(lab[:, -1].tolist())
    border.discard(0)
    outside = np.isin(lab, list(border))
    inside_hole = bg & ~outside                     # 막힌 흰 영역 = 얼굴 안·카드 안

    rgb = np.full(g.shape + (3,), INK, np.uint8)
    rgb[inside_hole] = 255                          # 안쪽은 흰색
    alpha = np.where(inside_hole, 1.0, al)          # 안쪽도 불투명
    return Image.fromarray(
        np.dstack([rgb, (alpha * 255).astype(np.uint8)]), "RGBA")


def trim_scale(im, h_target):
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    if not len(xs):
        return None
    im = im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    w, h = im.size
    return im.resize((max(1, round(w * h_target / h)), h_target), Image.LANCZOS)


def one(key):
    src = os.path.join(CLIPS, key + ".mp4")
    if not os.path.exists(src):
        print("★없음:", src)
        return 0
    d = os.path.join(TMP, key)
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, "*.png")):
        os.remove(f)
    # 8초 192프레임 → 64컷 = 3프레임마다 한 장
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                    "-vf", "select='not(mod(n\\,3))'", "-vsync", "0",
                    os.path.join(d, "f%03d.png")], check=True)
    fs = sorted(glob.glob(os.path.join(d, "*.png")))[:N]
    od = os.path.join(OUT, key)
    os.makedirs(od, exist_ok=True)
    for f in glob.glob(os.path.join(od, "*.png")):
        os.remove(f)
    for i, p in enumerate(fs):
        im = trim_scale(cut_white(Image.open(p)), TARGET_H)
        im.save(os.path.join(od, "%s_%02d.png" % (key, i)))
    # 검증
    a = np.asarray(Image.open(os.path.join(od, "%s_00.png" % key)))[:, :, 3]
    mid = ((a > 0) & (a < 255)).mean() * 100
    print("  %-13s %2d컷 · 키 %d · 반투명경계 %.2f%%" % (key, len(fs), TARGET_H, mid))
    return len(fs)


def main():
    os.makedirs(OUT, exist_ok=True)
    tot = 0
    for k in ("mouth_cycle", "card_lift", "card_fan"):
        tot += one(k)
    print("합계 %d컷 → %s" % (tot, OUT))


if __name__ == "__main__":
    main()
