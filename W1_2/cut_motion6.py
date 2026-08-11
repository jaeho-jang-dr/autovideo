# -*- coding: utf-8 -*-
"""이동 동작 6종 → **64프레임 투명컷** → 상영용 클립.

★사장님 지시(2026-08-11): "그냥 64프레임으로 나누어서 투명컷 해서 걷기 만들어봐."
원본은 흰 배경 선화(8초 192프레임) → 3프레임마다 한 장 = 64컷.
투명컷은 밝기로 가르되 **선으로 둘러싸인 안쪽(얼굴)은 흰색으로 남긴다.**
"""
import argparse
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

SRC = "W1_2/motion6"
OUT = "W1_2/motion6_cuts"
TMP = "W1_2/_m6buf"
N = 64
TARGET_H = 740
INK = 26


def cut_white(im):
    from scipy import ndimage
    g = np.asarray(im.convert("L"), np.float32)
    al = np.clip((225.0 - g) / 55.0, 0, 1)
    bg = al < 0.15
    lab, n = ndimage.label(bg)
    border = set(lab[0].tolist()) | set(lab[-1].tolist()) | \
        set(lab[:, 0].tolist()) | set(lab[:, -1].tolist())
    border.discard(0)
    outside = np.isin(lab, list(border))
    hole = bg & ~outside
    rgb = np.full(g.shape + (3,), INK, np.uint8)
    rgb[hole] = 255
    alpha = np.where(hole, 1.0, al)
    return Image.fromarray(np.dstack([rgb, (alpha * 255).astype(np.uint8)]), "RGBA")


def trim_scale(im, h):
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    if not len(xs):
        return None
    im = im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))
    return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)


def one(key):
    src = os.path.join(SRC, key + ".mp4")
    if not os.path.exists(src):
        print("★없음:", src)
        return 0
    d = os.path.join(TMP, key)
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, "*.png")):
        os.remove(f)
    # 192프레임 → 3프레임마다 한 장 = 64컷
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src,
                    "-vf", "select='not(mod(n\\,3))'", "-vsync", "0",
                    os.path.join(d, "f%03d.png")], check=True)
    fs = sorted(glob.glob(os.path.join(d, "*.png")))[:N]

    od = os.path.join(OUT, key)
    os.makedirs(od, exist_ok=True)
    for f in glob.glob(os.path.join(od, "*.png")):
        os.remove(f)
    kept = 0
    for i, p in enumerate(fs):
        im = trim_scale(cut_white(Image.open(p)), TARGET_H)
        if im is None:
            continue
        im.save(os.path.join(od, "%s_%02d.png" % (key, i)))
        kept += 1

    a = np.asarray(Image.open(os.path.join(od, "%s_00.png" % key)))
    al = a[:, :, 3]
    m = al > 200
    print("  %-12s %2d컷 · 키 %d · 투명 %.1f%% · 잉크 RGB%s"
          % (key, kept, TARGET_H, (al == 0).mean() * 100,
             tuple(a[m][:, :3].mean(0).astype(int))))
    return kept


def make_clip(key, fps=24):
    """투명컷을 다시 흰 배경 위에 얹어 상영용 mp4 를 만든다(확인용)."""
    fs = sorted(glob.glob(os.path.join(OUT, key, "*.png")))
    if not fs:
        return
    W, H = 700, 820
    d = os.path.join(TMP, key + "_play")
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, "*.png")):
        os.remove(f)
    for i, p in enumerate(fs):
        im = Image.open(p).convert("RGBA")
        s = 760 / im.height
        t = im.resize((max(1, round(im.width * s)), 760), Image.LANCZOS)
        cv = Image.new("RGB", (W, H), (255, 255, 255))
        cv.paste(t, ((W - t.width) // 2, 30), t)
        cv.save(os.path.join(d, "f%03d.png" % i))
    out = os.path.join(SRC, key + "_cut.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(fps),
                    "-i", os.path.join(d, "f%03d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", out], check=True)
    print("     상영본 %s  %d프레임 · %dfps · %.1f초"
          % (out, len(fs), fps, len(fs) / fps))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    a = ap.parse_args()
    keys = a.keys or [os.path.basename(p)[:-4]
                      for p in sorted(glob.glob(os.path.join(SRC, "*.mp4")))
                      if not p.endswith("_cut.mp4")]
    os.makedirs(OUT, exist_ok=True)
    tot = 0
    for k in keys:
        tot += one(k)
        make_clip(k)
    print("합계 %d컷 → %s" % (tot, OUT))


if __name__ == "__main__":
    main()
