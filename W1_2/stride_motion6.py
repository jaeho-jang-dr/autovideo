# -*- coding: utf-8 -*-
"""이동 동작 → **한 스트라이드만** 잘라낸 순환 컷.

★사장님 지시(2026-08-11): "한 스트라이드만 짤라서 해보자. 달리기도 걷기도 마찬가지."

8초 클립 전체(192프레임)를 쓰면 같은 걸음이 서너 번 반복돼 낭비고,
끝을 다시 처음에 이으면 튄다. **한 주기만 뽑아 두면 무한히 돌려도 안 튄다.**

## 주기를 재는 법
프레임 t 와 t+lag 의 실루엣 IoU 를 모든 lag 에 대해 재서 가장 닮은 lag 가 주기다.
- **한 걸음(step)** = 왼발·오른발이 바뀌는 반주기
- **한 스트라이드(stride)** = 같은 발이 다시 앞으로 오는 온주기 = step × 2

다리 폭 자기상관은 달리기에서 흔들려서(상관 0.34) 실루엣 IoU 로 간다.
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
OUT = "W1_2/motion6_stride"
TMP = "W1_2/_m6buf"
# ★스트라이드 안에서 몇 프레임마다 한 컷을 쓸지 (사장님 지시 2026-08-11)
#   걷기 = 세 프레임 중 하나 / 달리기 = **모든 컷**(빠른 동작이라 건너뛰면 튄다)
EVERY = {"walk": 3, "run": 1}
TARGET_H = 740
INK = 26


def every_of(key):
    return EVERY["run"] if key.startswith("run") else EVERY["walk"]


# ── 투명컷 (검증된 방식 그대로) ──────────────────────────────────────────
def cut_white(im):
    from scipy import ndimage
    g = np.asarray(im.convert("L"), np.float32)
    al = np.clip((225.0 - g) / 55.0, 0, 1)
    bg = al < 0.15
    lab, _ = ndimage.label(bg)
    border = set(lab[0].tolist()) | set(lab[-1].tolist()) | \
        set(lab[:, 0].tolist()) | set(lab[:, -1].tolist())
    border.discard(0)
    hole = bg & ~np.isin(lab, list(border))
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


# ── 주기 측정 ────────────────────────────────────────────────────────────
def silhouettes(paths, box=224):
    """실루엣을 발 기준으로 맞춰 정사각 격자에 담는다(위치 변동 제거)."""
    out = []
    for p in paths:
        a = np.asarray(Image.open(p).convert("L")) < 160
        ys, xs = np.nonzero(a)
        if not len(xs):
            out.append(np.zeros((box, box), bool))
            continue
        sub = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        im = Image.fromarray((sub * 255).astype(np.uint8)).resize((box, box), Image.NEAREST)
        out.append(np.asarray(im) > 127)
    return np.array(out)


def iou_at(sil, lag):
    a, b = sil[:-lag], sil[lag:]
    inter = (a & b).sum((1, 2)).astype(float)
    uni = (a | b).sum((1, 2)).astype(float) + 1e-9
    return float((inter / uni).mean())


def iou_seq(sil, lag):
    """프레임별 IoU 수열 — sil[t] 와 sil[t+lag] 를 t 마다 잰다."""
    a, b = sil[:-lag], sil[lag:]
    inter = (a & b).sum((1, 2)).astype(float)
    uni = (a | b).sum((1, 2)).astype(float) + 1e-9
    return inter / uni


def find_step(sil, lo=6, hi=None):
    """한 걸음(반주기) 길이. IoU 가 가장 높은 lag."""
    hi = hi or len(sil) // 3
    scores = [(lag, iou_at(sil, lag)) for lag in range(lo, hi)]
    best = max(scores, key=lambda s: s[1])
    peak = best[1]
    for lag, sc in scores:                    # 배수 lag 도 높으니 첫 봉우리를 쓴다
        if sc >= peak * 0.985:
            return lag, sc, scores
    return best[0], best[1], scores


def find_cycle(sil):
    """★주기와 시작점을 **같이** 찾는다.

    사장님 지적(2026-08-11): "한 스트라이드 바로 전 컷까지 따야 어색하지 않다.
    중복되면 연속할 때 이상한 걸음이 된다."
    → 주기를 어림잡으면 이음매에서 튄다. 한 구간 전체가 다음 구간과 겹치는지를
      재서(sil[t] ↔ sil[t+stride] 를 구간 내내 비교) 가장 잘 맞는 (시작, 주기)를 고른다.
    """
    step, sc, _ = find_step(sil)
    n = len(sil)
    best = None
    for stride in range(max(6, step * 2 - 6), min(step * 2 + 7, n // 2)):
        q = iou_seq(sil, stride)              # 길이 n-stride
        lim = n - 2 * stride
        if lim <= 1:
            continue
        for start in range(1, lim):
            s = float(q[start:start + stride].mean())
            if best is None or s > best[0]:
                best = (s, stride, start)
    if best is None:
        return step * 2, n // 6, sc
    return best[1], best[2], best[0]


def dump_frames(key):
    src = os.path.join(SRC, key + ".mp4")
    d = os.path.join(TMP, key + "_full")
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, "*.png")):
        os.remove(f)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-vsync", "0",
                    os.path.join(d, "f%03d.png")], check=True)
    return sorted(glob.glob(os.path.join(d, "*.png")))


def one(key, every=None, window=None, name=None):
    """window=(a,b) 를 주면 **그 프레임 구간 안에서만** 스트라이드를 찾는다.

    ★나가기 회전 클립은 앞부분이 측면·회전이고 뒤쪽 4초만 뒷모습이다.
      전체에서 주기를 찾으면 측면 걸음이 섞인다 — 구간을 잘라서 찾아야 한다.
    """
    if not os.path.exists(os.path.join(SRC, key + ".mp4")):
        print("★없음:", key)
        return 0
    every = every or every_of(key)
    fs = dump_frames(key)
    off = 0
    if window:
        a, b = window
        off = a
        fs = fs[a:b]
    sil = silhouettes(fs)
    stride, start, sc = find_cycle(sil)

    # ★스트라이드를 등분해 뽑되 **끝 프레임(=시작과 같은 자세)은 뺀다**.
    #   넣으면 이어붙일 때 같은 자세가 두 번 나와 걸음이 절뚝인다.
    ncut = max(4, round(stride / every))
    idx = [start + round(i * stride / ncut) for i in range(ncut)]
    key_out = name or key

    # ★이음매 검사: 마지막 컷 → 첫 컷 이 이웃 컷 사이만큼 자연스러운가
    adj = float(np.mean([iou_at(sil[idx[i]:idx[i + 1] + 1], idx[i + 1] - idx[i])
                         for i in range(ncut - 1)]))
    seam = float(np.mean((sil[idx[-1]] & sil[idx[0]]).sum()) /
                 (np.mean((sil[idx[-1]] | sil[idx[0]]).sum()) + 1e-9))
    mark = "좋음" if seam >= adj - 0.03 else "★튄다"

    print("  %-14s 구간 %d컷 · **스트라이드 %d프레임(%.2f초)** 맞음 %.3f "
          "· %d중1 → **%d컷** · 시작 f%03d · 이음매 %.3f(이웃 %.3f) %s"
          % (key_out, len(fs), stride, stride / 24.0, sc, every, ncut,
             off + start, seam, adj, mark))

    od = os.path.join(OUT, key_out)
    os.makedirs(od, exist_ok=True)
    for f in glob.glob(os.path.join(od, "*.png")):
        os.remove(f)
    for i, j in enumerate(idx):
        im = trim_scale(cut_white(Image.open(fs[j])), TARGET_H)
        if im is not None:
            im.save(os.path.join(od, "%s_%02d.png" % (key_out, i)))
    return stride


def make_loop(key, loops=4, fps=None):
    """★재생 속도는 원본 그대로 — 3중1 로 뽑았으면 8fps, 전 컷이면 24fps."""
    fps = fps or round(24 / every_of(key))
    """한 스트라이드를 여러 번 이어 붙여 순환이 안 튀는지 눈으로 본다."""
    fs = sorted(glob.glob(os.path.join(OUT, key, "*.png")))
    if not fs:
        return
    W, H = 700, 820
    d = os.path.join(TMP, key + "_loop")
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, "*.png")):
        os.remove(f)
    k = 0
    for _ in range(loops):
        for p in fs:
            im = Image.open(p).convert("RGBA")
            t = im.resize((max(1, round(im.width * 760 / im.height)), 760), Image.LANCZOS)
            cv = Image.new("RGB", (W, H), (255, 255, 255))
            cv.paste(t, ((W - t.width) // 2, 30), t)
            cv.save(os.path.join(d, "f%03d.png" % k))
            k += 1
    out = os.path.join(SRC, key + "_stride.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(fps),
                    "-i", os.path.join(d, "f%03d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", out], check=True)
    print("     순환본 %s  %d컷×%d회 · %dfps · 한 바퀴 %.2f초"
          % (out, len(fs), loops, fps, len(fs) / fps))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--every", type=int, default=0)
    a = ap.parse_args()
    keys = a.keys or [os.path.basename(p)[:-4] for p in
                      sorted(glob.glob(os.path.join(SRC, "*.mp4")))
                      if "_cut" not in p and "_stride" not in p]
    os.makedirs(OUT, exist_ok=True)
    for k in keys:
        one(k, a.every or None)
        make_loop(k, fps=round(24 / (a.every or every_of(k))))


if __name__ == "__main__":
    main()
