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


BODY_MIN_RUN = 60                  # 몸으로 치는 가로 폭(창 한 자루는 이보다 훨씬 가늘다)
SPECK = 0.01                       # 제일 큰 덩어리의 이보다 작으면 티끌 — 지운다


def despeckle(im):
    """★사람의 바깥은 전부 투명 (사장님 지시 2026-08-13).

    Veo 그림에는 종이 질감 얼룩이 섞여 있어, 밝기로만 가르면 배경에 검은 티끌이
    수백 개 남는다(프레임당 100~300개, 전부 100px 미만). 사람은 언제나 한 덩어리
    (창까지 손에 쥐고 있어 붙어 있다)이므로 **제일 큰 덩어리만 남긴다.**
    """
    from scipy import ndimage
    a = np.array(im)
    on = a[:, :, 3] > 8
    lab, n = ndimage.label(on)
    if n <= 1:
        return im, 0
    sizes = ndimage.sum(on, lab, range(1, n + 1))
    keep = np.isin(lab, np.nonzero(sizes >= sizes.max() * SPECK)[0] + 1)
    gone = int((on & ~keep).sum())
    a[:, :, 3][on & ~keep] = 0
    return Image.fromarray(a, "RGBA"), gone


def body_top(a):
    """★든 물건을 빼고 **몸 꼭대기**를 찾는다.

    수문장은 창이 머리 위로 솟아 있어, 그림 전체 높이로 키를 맞추면 창까지
    740 안에 욱여넣어져 몸이 확 작아진다(사장님 기준 — 키는 머리끝~발끝).
    창은 가늘고 몸(갓 챙·어깨)은 넓으니, **가로로 이어진 폭**으로 갈라낸다.
    """
    on = a > 8
    for y in range(on.shape[0]):
        r = on[y]
        if not r.any():
            continue
        d = np.diff(np.concatenate(([0], r.view(np.int8), [0])))
        runs = np.nonzero(d < 0)[0] - np.nonzero(d > 0)[0]
        if runs.max() >= BODY_MIN_RUN:
            return y
    return 0


FACE_RATIO = 1.8                   # 얼굴은 이보다 둥글다
FACE_MIN = 0.004                   # 얼굴은 그림 넓이의 이만큼은 된다


def line_cut(path):
    """★선만 남기고 속은 다 투명 — **얼굴과 창만 흰색** (사장님 규격 2026-08-13)

      "창은 검은 외부 줄, 안은 흰색. 사람은 통으로 — 모자·얼굴·팔·상하의·다리
       연결해서 그 밖은 다 투명. **선 안도 투명.** 얼굴·팔·다리는 검은색."
      "얼굴은 보이고 눈코입.. **얼굴만 흰색, 나머지는 선으로 쌓인 투명.**"

    즉 갓·도포·상하의는 **테두리 선만** 남고 속은 비친다. 흰색으로 남는 것은
    ① 얼굴 동그라미 안 (눈·코·입이 읽혀야 하므로) ② 창 두 줄 사이 — 이 둘뿐이다.
    사람은 선이 끊기지 않고 한 덩어리로 이어져 있어야 한다.

      1. 잉크에서 티끌을 턴다 (제일 큰 덩어리의 1% 미만)
         — Veo 그림엔 종이 질감 얼룩이 섞여 프레임마다 100~300개씩 남는다
      2. **창을 갈라낸다** — 창은 갓보다 위에서 시작하는 유일한 것이라,
         잉크가 갓 꼭대기보다 위에서 시작하는 열이 곧 창이다
      3. 창 두 줄 사이를 메워 흰색으로 남긴다
      4. 몸에서 **맨 위의 둥근 빈 곳**을 얼굴로 보고 흰색으로 남긴다
         (눈·코·입은 잉크라 덮지 않는다 — 2026-08-13 사고)
      5. 그 밖은 전부 알파 0 — 선에 갇힌 주머니도 예외 없다
    """
    from scipy import ndimage
    g = np.asarray(Image.open(path).convert("L")).astype(np.float32)
    ink = g < 170
    if not ink.any():
        return None
    lab, n = ndimage.label(ink)
    sz = ndimage.sum(ink, lab, range(1, n + 1))
    ink = np.isin(lab, np.nonzero(sz >= sz.max() * SPECK)[0] + 1)      # ①
    top = body_top((ink * 255).astype(np.uint8))
    cols = np.nonzero(ink.any(0))[0]
    firsty = np.array([np.nonzero(ink[:, c])[0][0] for c in cols])
    pc = cols[firsty < top - 12]                                       # ②
    band = np.zeros(ink.shape[1], bool)
    if len(pc):
        band[max(0, pc.min() - 2):pc.max() + 3] = True
    pole = ndimage.binary_fill_holes(ink & band[None, :]) & ~ink        # ③

    body = ink & ~band[None, :]
    bl, bn = ndimage.label(body)
    main = body
    if bn:
        bs = ndimage.sum(body, bl, range(1, bn + 1))
        main = bl == (int(np.argmax(bs)) + 1)
    inside = ndimage.binary_fill_holes(main) & ~main
    hl, hn = ndimage.label(inside)
    area = float(main.sum())
    best = None
    for i in range(1, hn + 1):                                          # ④
        h = hl == i
        if h.sum() < area * FACE_MIN:
            continue
        ys, xs = np.nonzero(h)
        w, ht = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        if max(w, ht) / float(max(1, min(w, ht))) >= FACE_RATIO:
            continue
        if best is None or ys.min() < best[0]:
            best = (ys.min(), h)
    face = (best[1] & ~ink) if best is not None else np.zeros_like(inside)

    keep = ink | face | pole                                            # ⑤
    v = np.where(g < 200, g, 255).astype(np.uint8)                      # 질감 얼룩 제거
    a = np.clip(ndimage.gaussian_filter(keep.astype(np.float32), 0.5) * 1.6, 0, 1)
    return Image.fromarray(
        np.dstack([v, v, v, (a * 255).astype(np.uint8)]), "RGBA")


def trim_scale(im, h, body=False):
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    if not len(xs):
        return None
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    # 기준 높이 — 기본은 그림 전체, --body 면 든 물건을 뺀 몸만
    ref = (y1 - body_top(a)) if body else (y1 - y0)
    k = float(h) / max(1, ref)
    im = im.crop((x0, y0, x1, y1))
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))),
                     Image.LANCZOS)


def one(key, body=False, line=False):
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
        cut = line_cut(p) if line else cut_white(Image.open(p))
        if cut is None:
            continue
        im = trim_scale(cut, TARGET_H, body)
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


def make_clip(key, fps=24, bg=(255, 255, 255)):
    """투명컷을 다시 배경 위에 얹어 상영용 mp4 를 만든다(확인용).

    ★fps 는 원본 길이에 맞춘다 — 8초 192프레임에서 3장마다 골라 64컷이므로
      8fps 로 틀어야 원래 속도다. 24fps 면 세 배 빨라 동작을 못 본다.
    ★배경은 초록이 기본에 가깝다 — 흰 배경에 놓으면 **안 뚫린 흰색이 안 보인다**.
    """
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
        cv = Image.new("RGB", (W, H), bg)
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
    ap.add_argument("--body", action="store_true",
                    help="키를 **든 물건을 뺀 몸**으로 잰다(수문장 창 등)")
    ap.add_argument("--line", action="store_true",
                    help="★선만 남기고 속은 투명 — 얼굴과 창만 흰색")
    ap.add_argument("--fps", type=int, default=24, help="상영본 속도(64컷이면 8)")
    ap.add_argument("--green", action="store_true", help="상영본 배경을 초록으로")
    a = ap.parse_args()
    keys = a.keys or [os.path.basename(p)[:-4]
                      for p in sorted(glob.glob(os.path.join(SRC, "*.mp4")))
                      if not p.endswith("_cut.mp4")]
    os.makedirs(OUT, exist_ok=True)
    tot = 0
    for k in keys:
        tot += one(k, a.body, a.line)
        make_clip(k, a.fps, (0, 190, 90) if a.green else (255, 255, 255))
    print("합계 %d컷 → %s" % (tot, OUT))


if __name__ == "__main__":
    main()
