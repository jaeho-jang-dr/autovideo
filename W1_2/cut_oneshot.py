# -*- coding: utf-8 -*-
"""**한 번만 하는 동작** 전용 64컷 투명컷 — 자세별 키를 보존한다.

★`cut_motion6.py` 는 손대지 않는다. 그쪽은 걷기·달리기(키가 안 변하는 순환 동작)로
  검증된 경로다. 이 스크립트는 **키가 변하는 1회 동작**(앉기·쭈그리기·구르기·백플립)용이다.

## 왜 따로 만드나 — 2026-08-12 실측된 두 결함

**① 프레임마다 키를 740 으로 맞추면 자세가 뭉개진다.**
`cut_motion6.trim_scale(im, 740)` 은 프레임마다 제 bbox 로 잘라 **각각** 740px 로 늘린다.
걷기는 키가 안 변하니 무해하지만, 앉으면 앉은 몸이 선 키만큼 부풀어 오른다
(`sit_stand` 실측). 자세별 키 기준(서기100·구부림80·의자60·웅크림50)이 무너진다.
→ **클립당 배율 하나**를 기준 프레임에서 구해 전 프레임에 똑같이 먹인다.
  그러면 앉으면 작아지고 구르면 납작해진다.

**② 배경이 순백이 아닌 클립이 있다.**
`forward_roll`·`pick_up` 은 코너 최소 216/217 로 임계값 225 아래였다. 배경이 인물로
새어들어 컷 폭이 1288~1701px 까지 벌어졌다(정상 204~352px).
→ 임계값을 **클립마다 코너에서 실측**해 잡는다.

**③ Flow 워터마크(✦)가 섞인다.**
→ 가장 큰 덩어리와 **그 안쪽에 든 것**(눈·입)만 남기고 나머지 부스러기는 버린다.

    python W1_2/cut_oneshot.py sit_stand pick_up ...
    python W1_2/cut_oneshot.py --color zgirl_high_five      # 색 보존(졸라)
"""
import argparse
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

import stride_motion6 as S                          # noqa: E402  주기 측정만 빌려 쓴다
import motion6_defs as M                            # noqa: E402  기준 이미지 경로

SRC = "W1_2/motion6"
OUT = "W1_2/motion6_cuts"
TMP = "W1_2/_m6buf"
N = 64
TARGET_H = 740          # ★기준 프레임의 **서 있는** 키. 다른 자세는 여기에 비례해 작아진다
INK = 26
REF_FRAME = 0           # 기준 프레임 = 첫 컷(대개 서 있는 자세)


def bg_threshold(paths):
    """배경 임계값을 **코너에서 실측**한다. 순백이 아닌 클립이 있다."""
    lo = 255
    for p in paths[::8]:
        g = np.asarray(Image.open(p).convert("L"))
        c = np.concatenate([g[:80, :80].ravel(), g[:80, -80:].ravel(),
                            g[-80:, :80].ravel(), g[-80:, -80:].ravel()])
        lo = min(lo, int(c.min()))
    # 배경 최저값보다 12 어두운 지점부터 인물로 본다
    return max(150, lo - 12)


def cut(im, thr, keep_color):
    """투명컷. 윤곽이 둘러싼 안쪽은 흰색으로, 부스러기는 버린다."""
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    g = np.asarray(im.convert("L"), np.float32)
    alpha = np.clip((thr - g) / 55.0, 0, 1)

    solid = alpha > 0.45
    lab, n = ndimage.label(solid)
    if n == 0:
        return None
    sizes = ndimage.sum(solid, lab, range(1, n + 1))
    main = lab == (int(np.argmax(sizes)) + 1)
    body = ndimage.binary_fill_holes(main)          # 몸 + 머리 안쪽까지 꽉 찬 덩어리
    keep = solid & body                             # ★부스러기(워터마크) 탈락, 눈·입은 생존

    hole = body & ~keep                             # 선이 둘러싼 안쪽(얼굴 바탕 등)
    if keep_color:
        rgb = a.astype(np.uint8)                    # ★원래 색을 살린다(졸라걸 주황 머리)
    else:
        rgb = np.full(g.shape + (3,), INK, np.uint8)
    rgb[hole] = 255
    al = np.where(hole, 1.0, np.where(keep, alpha, 0.0))
    return Image.fromarray(np.dstack([rgb, (al * 255).astype(np.uint8)]), "RGBA")


def bbox(im):
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    if not len(xs):
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def head_span(im):
    """★머리의 **위아래 길이**를 잰다 (사장님 지시 2026-08-12).

    "사람이 자세에 따라 커졌다 작아졌다 하면 안 된다. 머리의 아래위 길이를 재서
     전체 크기를 측정하라. 자세는 달라져도 캐릭터의 크기는 유지하라."

    몸통 키는 자세마다 변하니 크기 기준이 될 수 없다. **머리는 어떤 자세에서도,
    거꾸로 뒤집혀도 같은 원**이다. 그래서 머리를 재서 그걸 고정한다.

    찾는 법 — 윤곽선이 둘러싼 안쪽 영역들 중 **가장 동그란 것**이 머리 안쪽이다.
    (팔과 몸통이 만드는 삼각형도 둘러싸이지만 길쭉하고 채움이 성글다.
     원은 채움 0.785·종횡비 1.0, 삼각형은 채움 0.5·종횡비 낮음)
    반환값은 머리 **바깥 지름**(안쪽 높이 + 선 두께 양쪽).
    """
    a = np.array(im.convert("RGBA"))
    alpha = a[:, :, 3]
    # ★알파로 가르면 안 된다 — cut() 이 머리 안쪽을 **불투명 흰색**으로 채워 놔서
    #   알파 기준으로는 구멍이 이미 메워져 있다. **어두운 선**만 잉크로 본다.
    ink = (alpha > 100) & (a[:, :, :3].max(2) < 170)
    lab, n = ndimage.label(ink)
    if n == 0:
        return None
    sizes = ndimage.sum(ink, lab, range(1, n + 1))
    main = lab == (int(np.argmax(sizes)) + 1)
    interior = ndimage.binary_fill_holes(main) & ~main
    if not interior.any():
        return None

    fy = np.nonzero(ink.any(1))[0]
    fig_h = float(fy.max() - fy.min() + 1) if len(fy) else 1.0

    li, ni = ndimage.label(interior)
    cands = []
    for i in range(1, ni + 1):
        m = li == i
        ys, xs = np.nonzero(m)
        h = int(ys.max() - ys.min() + 1)
        area = int(m.sum())
        if area < 150:
            continue
        cands.append((area, int(ys.min()), h))       # (면적, 맨위 y, 높이)
    if not cands:
        return None
    # ★고르는 법 — **전체 키에 견준 띠**로 거르고, 남은 것 중 맨 위를 고른다.
    #   오늘 세 번 다른 것을 머리로 잘못 잡았다(2026-08-12) —
    #     ①손 고리 25px (졸라맨 달리기, 배율 5배 튐)
    #     ②든 카드   (zman_card_hold, 키 666 vs 775)
    #     ③팔·머리·어깨가 만든 큰 고리 657px (sm_greeting_wave, 키 160)
    #   ★문턱을 '가장 큰 후보의 25%' 로 잡으면 ③의 거대한 고리가 문턱을 밀어 올려
    #     **진짜 머리가 먼저 탈락**한다. 그래서 문턱을 **전체 키 기준**으로 둔다.
    #   머리는 사람 키의 대략 1/5~1/3 이다.
    #   ★순서가 중요하다 — **큰 고리를 먼저 버리고 그 다음에 문턱을 잰다.**
    #     문턱을 먼저 재면 거대한 고리가 문턱을 밀어 올려 진짜 머리가 탈락한다.
    ok = [c for c in cands if c[2] <= 0.34 * fig_h] or cands      # ①큰 고리 버리기
    floor = 0.25 * max(c[0] for c in ok)                          # ②남은 것으로 문턱
    ok = [c for c in ok if c[0] >= floor]                         # ③잔챙이 버리기
    best = min(ok, key=lambda c: c[1])                            # ④맨 위 = 머리
    # ★선 두께를 더하지 않는다. 몸 전체에서 잰 두께는 **졸라맨의 꽉 찬 검은 머리카락**을
    #   가장 두꺼운 덩어리로 잡아 88px 까지 부푼다(스틱맨은 14px) — 졸라맨 측면 머리가
    #   275px 로 튄 원인이었다. 절대값은 필요 없고 **프레임 사이 일관성**만 있으면 되므로
    #   머리 안쪽 높이를 그대로 기준으로 쓴다.
    return float(best[2])


# ★캐릭터별 기준 이미지 — **다 같이 서서 키를 같은 비율로 정렬한 상태**가 이 그림들이다.
#   여기서 잰 머리 높이가 그 캐릭터의 영구 기준값이 된다(사장님 지시 2026-08-12).
CHAR_GUIDES = {
    "stick": ["W1_2/motion_src/guide_front.png", "W1_2/motion_src/guide_side.png"],
    "zman": ["W1_2/motion_src/guide_zman_front.png", "W1_2/motion_src/guide_zman_side.png"],
    "zgirl": ["W1_2/motion_src/guide_zgirl_front.png", "W1_2/motion_src/guide_zgirl_side.png"],
}
_HEAD_CACHE = {}


def char_of(key):
    return "zman" if key.startswith("zman") else ("zgirl" if key.startswith("zgirl") else "stick")


def char_head(key, keep_color=False):
    """★그 캐릭터의 **머리 높이 기준값** — 미리 재서 박아 두는 값.

    "머리의 아래위 높이를 미리 측정해 놓으면, 앉혀도 비율로 앉혀서 전체 사이즈를
     줄이지 않을 것이다." (사장님 2026-08-12)

    기준 이미지의 인물을 **서기 키 740** 으로 놓았을 때의 머리 높이다. 정면·측면 두 장을
    평균 내 한 값으로 굳힌다(둘이 4% 어긋난다). 같은 캐릭터의 모든 클립·모든 자세가
    이 값 하나를 공유하므로 **앉아도 굴러도 사람 크기가 그대로**다.
    원근(깊이)만이 크기를 바꾼다.
    """
    ch = char_of(key)
    if ch in _HEAD_CACHE:
        return _HEAD_CACHE[ch]
    vals = []
    for g in CHAR_GUIDES[ch]:
        if not os.path.exists(g):
            continue
        c = cut(Image.open(g), 225, keep_color)
        b = bbox(c) if c is not None else None
        h = head_span(c) if c is not None else None
        if b and h:
            vals.append(h * (TARGET_H / float(b[3] - b[1])))
    val = float(np.mean(vals)) if vals else None
    _HEAD_CACHE[ch] = val
    return val


def save_reversed(key):
    """★좌우 반전본을 **실파일**로 저장한다 — `<key>_l/`.

    사장님 지시(2026-08-12): "리버스도 만든다, 저장한다."
    렌더에서 flip 플래그로 뒤집으면 이중 반전 사고가 난다(W23 walk_l 사고).
    라이브러리 규칙대로 **왼쪽 방향은 실제로 뒤집은 파일**을 두고 flip=0 으로 쓴다
    ([[stickman-move-cut-library]]).
    """
    src = os.path.join(OUT, key)
    dst = os.path.join(OUT, key + "_l")
    fs = sorted(glob.glob(os.path.join(src, "*.png")))
    if not fs:
        return 0
    os.makedirs(dst, exist_ok=True)
    for f in glob.glob(os.path.join(dst, "*.png")):
        os.remove(f)
    for p in fs:
        im = Image.open(p).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT)
        im.save(os.path.join(dst, os.path.basename(p).replace(key, key + "_l", 1)))
    print("  %-16s %2d컷 · 좌우 반전본 → %s" % (key + "_l", len(fs), dst))
    return len(fs)


def one(key, keep_color=False, stride=False, window=None, every=1):
    src = os.path.join(SRC, key + ".mp4")
    if not os.path.exists(src):
        print("  ★없음:", src)
        return 0
    d = os.path.join(TMP, key + "_os")
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, "*.png")):
        os.remove(f)
    # ★순환 동작은 주기를 재야 하니 **전 프레임**을, 1회 동작은 3프레임마다 뽑는다
    vf = [] if stride else ["-vf", "select='not(mod(n\\,3))'"]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src] + vf +
                   ["-vsync", "0", os.path.join(d, "f%03d.png")], check=True)
    allf = sorted(glob.glob(os.path.join(d, "*.png")))
    fs = allf if stride else allf[:N]
    thr = bg_threshold(fs)

    # ★크기 기준 = **머리 지름**(사장님 지시 2026-08-12).
    #   "전체 캐릭터의 키는 내가 이미 정해 줬다. 그 기준에 맞추어서 나열하고,
    #    원근을 이용할 때는 그 원근에 따라 달라진다."
    #   → 목표 머리 지름은 **캐릭터의 기준 이미지**에서 한 번만 구한다(클립마다 재지 않는다).
    #     그래야 모든 클립·모든 동작이 **같은 크기의 같은 사람**으로 나온다.
    target_head = char_head(key, keep_color)
    if not target_head:
        print("  ★기준 이미지에서 머리를 못 찾았다:", key)
        return 0

    if stride:
        seg = fs[window[0]:window[1]] if window else fs
        sil = S.silhouettes(seg)
        per, start, sc = S.find_cycle(sil)
        # ★끝 프레임(=시작과 같은 자세)은 뺀다 — 넣으면 이어붙일 때 절뚝인다
        cyc = seg[start:start + per]
        # ★스트라이드 안에서 몇 프레임마다 한 컷을 쓸지 (사장님 지시 2026-08-12:
        #   "한 스트라이드 정해서 3개 중 하나 잡아서 투명컷")
        fs = cyc[::every]
        print("  %-16s 스트라이드 %d프레임(%.2f초) 맞음 %.3f · 시작 f%03d · %d중1 → %d컷"
              % (key, per, per / 24.0, sc, (window[0] if window else 0) + start,
                 every, len(fs)))

    cuts = [cut(Image.open(p), thr, keep_color) for p in fs]
    boxes = [bbox(c) if c is not None else None for c in cuts]
    heads = [head_span(c) if c is not None else None for c in cuts]

    # ★머리 검출이 튀는 프레임(가려짐·붙음)은 버리고 중앙값으로 되돌린다
    good = [h for h in heads if h]
    med = float(np.median(good)) if good else ref_head
    heads = [h if (h and 0.85 * med <= h <= 1.15 * med) else med for h in heads]

    od = os.path.join(OUT, key)
    os.makedirs(od, exist_ok=True)
    for f in glob.glob(os.path.join(od, "*.png")):
        os.remove(f)

    kept, hs, ws = 0, [], []
    for i, (c, b, hd) in enumerate(zip(cuts, boxes, heads)):
        if c is None or b is None:
            continue
        s = target_head / float(hd)                 # ★프레임마다 **머리**를 맞춘다
        c = c.crop(b)
        w = max(1, round(c.width * s))
        h = max(1, round(c.height * s))
        c.resize((w, h), Image.LANCZOS).save(os.path.join(od, "%s_%02d.png" % (key, i)))
        kept += 1
        hs.append(h)
        ws.append(w)

    print("  %-16s %2d컷 · 임계 %d · 머리 %.0fpx 고정 → 몸키 %d~%d (서기 %d 기준 %d~%d%%) · 폭 %d~%d%s"
          % (key, kept, thr, target_head, min(hs), max(hs), TARGET_H,
             round(min(hs) * 100 / TARGET_H), round(max(hs) * 100 / TARGET_H),
             min(ws), max(ws), " · 색보존" if keep_color else ""))
    return kept


def make_clip(key, fps=24):
    """확인용 상영본 — 발끝을 바닥에 맞춰 얹어 자세별 키가 눈에 보이게 한다."""
    fs = sorted(glob.glob(os.path.join(OUT, key, "*.png")))
    if not fs:
        return
    W, H, FLOOR = 760, 860, 800
    d = os.path.join(TMP, key + "_osplay")
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(os.path.join(d, "*.png")):
        os.remove(f)
    for i, p in enumerate(fs):
        im = Image.open(p).convert("RGBA")
        cv = Image.new("RGB", (W, H), (255, 255, 255))
        cv.paste(im, ((W - im.width) // 2, FLOOR - im.height), im)
        cv.save(os.path.join(d, "f%03d.png" % i))
    out = os.path.join(SRC, key + "_os.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(fps),
                    "-i", os.path.join(d, "f%03d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", out], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="+")
    ap.add_argument("--color", action="store_true", help="원래 색을 살린다(졸라)")
    ap.add_argument("--stride", action="store_true", help="순환 동작 — 한 스트라이드만")
    ap.add_argument("--window", help="a:b — 그 프레임 구간에서만 주기를 찾는다")
    ap.add_argument("--every", type=int, default=1, help="스트라이드 안에서 N프레임마다 한 컷")
    ap.add_argument("--reverse", action="store_true", help="좌우 반전본도 <key>_l 로 저장")
    a = ap.parse_args()
    win = tuple(int(x) for x in a.window.split(":")) if a.window else None
    os.makedirs(OUT, exist_ok=True)
    tot = 0
    for k in a.keys:
        tot += one(k, a.color, a.stride, win, a.every)
        make_clip(k)
        if a.reverse:
            tot += save_reversed(k)
            make_clip(k + "_l")
    print("합계 %d컷 → %s" % (tot, OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
