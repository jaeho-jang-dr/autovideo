# -*- coding: utf-8 -*-
"""달려서 뒤로 멀어지며 오른쪽 구석으로 사라지기 (사장님 지시 2026-08-11)

  왼편 앞쪽 설명 자리에 서서 말하다가 → 오른편으로 달려가고
  → 몸을 돌려 → 뒷모습으로 달리며 **오른쪽 뒤 구석으로 사라진다.**

★핵심 — 멀어지는 구간에서 세 가지가 **동시에** 일어난다.
   ① 달리는 동작(뒷모습 컷 32~63 순환)
   ② 발 y 가 지평선 쪽으로 올라간다 → **원근 규칙이 키를 정한다**
   ③ x 가 오른쪽으로 이동한다
  손으로 배율을 정하지 않는다. 발 y 만 움직이고 키는 perspective_height 가 낸다.

★발 y 곡선은 **지수(등비)** 다. 지평선까지 남은 거리가 매 초 같은 비율로 줄어든다
  → 처음엔 쑥 작아지고 뒤로 갈수록 천천히 — 실제로 멀어지는 것처럼 보인다.

★그리기 순서 — 먼 것부터. 발 y 가 벤치 바닥선(630)보다 위로 올라가면
  벤치·석조 난간 **뒤**이므로 그 물체들로 다시 덮는다(occlude).
"""
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
import interactrang as I                                    # noqa: E402

BG_KEY = "gwanghwamun_bench"
BG = "W1_2/bg/gwanghwamun_bench.png"
OUT = "W1_2/clips/run_away_exit.mp4"
TMP = "W1_2/_runbuf"
CHK = "W1_2/_check"
CUTS = "W1_2/motion6_cuts/run_exit/run_exit_%02d.png"

FPS = 24                    # 출력 프레임레이트
CUT_HZ = 12                 # 컷 교체 속도(초당) — 원본 8컷/초의 1.5배(달리는 느낌)
MOUTH_HOLD = 4              # 입모양 유지 프레임(24fps → 초당 6번 바뀜)

# ── 컷 구간 (사장님 지시대로) ────────────────────────────────────────────
SIDE = (0, 16)              # 00~15 측면 90도 오른쪽 달리기 (00 은 선 자세)
TURN = (16, 32)             # 16~31 90→180 회전
BACK = (32, 64)             # 32~63 뒷모습 제자리 달리기 ← 멀어질 때 이것만 순환

# ── 구간 길이(프레임, 24fps) ────────────────────────────────────────────
N_A = 42                    # 0.000~1.750  설명(정지)
N_B = 24                    # 1.750~2.750  측면 달리기
N_C = 32                    # 2.750~4.083  회전 (16컷 × 2프레임 = 1:1 재생)
N_D = 94                    # 4.083~8.000  뒷모습 달리며 멀어짐

# ── 경로 ────────────────────────────────────────────────────────────────
X_STAND = 330               # 왼편 앞쪽 설명 자리
Y_FRONT = 700               # 앞쪽 바닥(발 y) — 여기서 제일 크다
X_RUN_END = 900             # 측면 달리기 끝
X_TURN_END = 960            # 회전 끝(=멀어지기 시작점)
X_GONE = 1440               # 오른쪽 화면 밖
Y_FAR = 520                 # 지평선(480) 가까이 — 여기서 제일 작다(키 101px)

MOUTH = ["mouth_a", "mouth_o", "mouth_a", "mouth_i",
         "mouth_yeo", "mouth_u", "mouth_o", "mouth_i"]

OCC_BOX = (700, 380, 1376, 625)     # 벤치 + 석조 난간(가릴 물체)

# ★석조 난간은 **색으로 못 잡는다** — 밝은 쪽 면(228,218,209)이 포장 바닥색과 같아서
#   무채색 판정을 빠져나간다(실측 2026-08-11). 그래서 윤곽선을 실측해 도형으로 박는다.
RAIL_SHAPES = [
    (1220, 364, 1287, 574),                                  # 큰 사각기둥
    (1315, 428, 1373, 452),                                  # 오른쪽 기둥 머리
    (1320, 450, 1368, 572),                                  # 기둥 몸
    (1314, 568, 1374, 600),                                  # 기둥 받침
]
RAIL_BEAM = [(1243, 395), (1376, 385), (1376, 429), (1243, 430)]     # 가로 들보

HORIZON = I.load_anchors(BG_KEY)["perspective"]["horizon_y"]


def trim(im):
    a = np.asarray(im.convert("RGBA"))[:, :, 3]
    ys, xs = np.nonzero(a > 8)
    return im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))


def occ_test(sub):
    """가릴 물체 판정 — 벤치 나무 + 석조 난간(무채색 회색) + 짙은 윤곽선."""
    r, g, b = sub[..., 0], sub[..., 1], sub[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    wood = I.wood_mask(sub)
    stone = (mx - mn <= 24) & (mx <= 222) & (mx >= 110)     # 난간 화강석
    dark = mx <= 130                                        # 윤곽선·그늘
    return wood | stone | dark


def fit(im, h):
    """★비율 유지로만 키운다/줄인다."""
    h = max(1, int(round(h)))
    w = max(1, int(round(im.width * h / im.height)))
    return im.resize((w, h), Image.LANCZOS)


def head_cx(im):
    """머리 중심 x (원본 픽셀).

    ★컷마다 bbox 폭이 208~442 로 들쭉날쭉하다(다리를 벌리면 넓어진다).
      bbox 한가운데를 기준으로 놓으면 머리가 프레임마다 ±30px 좌우로 흔들린다.
      **몸의 기준은 머리** 이므로 머리 중심을 경로에 맞춘다.
    """
    a = np.asarray(im.convert("RGBA"))[:, :, 3] > 8
    band = a[:max(1, int(a.shape[0] * 0.13))]
    xs = np.nonzero(band.any(axis=0))[0]
    return (float(xs.min()) + float(xs.max())) / 2.0 if len(xs) else im.width / 2.0


def path(i):
    """프레임 i → (컷 이미지 키, 컷 인덱스, x, 발y)."""
    if i < N_A:                                             # A 설명
        k = (i // MOUTH_HOLD) % len(MOUTH)
        return ("pose", MOUTH[k], X_STAND, Y_FRONT)

    i -= N_A
    if i < N_B:                                             # B 측면 달리기
        u = i / float(N_B)
        c = SIDE[0] + int(i * CUT_HZ / FPS) % (SIDE[1] - SIDE[0])
        x = X_STAND + (X_RUN_END - X_STAND) * (u ** 1.3)    # 서 있다 출발 → 가속
        return ("cut", c, x, Y_FRONT)

    i -= N_B
    if i < N_C:                                             # C 회전
        u = i / float(N_C)
        c = min(TURN[1] - 1, TURN[0] + int(i * CUT_HZ / FPS))
        x = X_RUN_END + (X_TURN_END - X_RUN_END) * u
        return ("cut", c, x, Y_FRONT)

    i -= N_C                                                # D 멀어짐
    u = i / float(N_D - 1)
    c = BACK[0] + int(i * CUT_HZ / FPS) % (BACK[1] - BACK[0])
    x = X_TURN_END + (X_GONE - X_TURN_END) * u              # ② 오른쪽으로
    hy0 = Y_FRONT - HORIZON
    hy1 = Y_FAR - HORIZON
    fy = HORIZON + hy0 * (hy1 / hy0) ** u                   # ③ 등비로 물러남
    return ("cut", c, x, fy)


def main():
    d = I.load_anchors(BG_KEY)
    p = d["perspective"]
    bg = Image.open(BG).convert("RGBA")

    cuts = {}
    for n in range(64):
        cuts[n] = trim(Image.open(CUTS % n).convert("RGBA"))
    poses = {m: trim(Image.open("W1_2/_poses/stickman_w1d2_%s.png" % m).convert("RGBA"))
             for m in set(MOUTH)}

    os.makedirs(CHK, exist_ok=True)
    mask = I.make_occ_mask(BG, OCC_BOX, os.path.join(CHK, "bench_rail_mask.png"), occ_test)
    mi = Image.open(mask).convert("L")
    dr = ImageDraw.Draw(mi)
    for r in RAIL_SHAPES:
        dr.rectangle(r, fill=255)
    dr.polygon(RAIL_BEAM, fill=255)
    mi.save(mask)

    n = N_A + N_B + N_C + N_D
    plan = [path(i) for i in range(n)]

    # ── 렌더 전 숫자 검증 ────────────────────────────────────────────────
    print("프레임 %d개 · %.2f초 @%dfps" % (n, n / FPS, FPS))
    print("%6s %6s %7s %7s %8s %6s %s" % ("t(s)", "컷", "x", "발y", "키px", "폭px", "구간"))
    hs, xs = [], []
    for i, (kind, key, x, fy) in enumerate(plan):
        h = I.perspective_height(fy, p["horizon_y"], p["ref_foot_y"], p["ref_h"])
        hs.append(h)
        xs.append(x)
        if i % 12 == 0 or i == n - 1:
            src = poses[key] if kind == "pose" else cuts[key]
            w = src.width * h / src.height
            seg = ("A설명" if i < N_A else "B측면달리기" if i < N_A + N_B
                   else "C회전" if i < N_A + N_B + N_C else "D멀어짐")
            print("%6.2f %6s %7.1f %7.1f %8.1f %6.1f %s"
                  % (i / FPS, str(key), x, fy, h, w, seg))

    d0 = N_A + N_B + N_C
    bad_h = [i for i in range(d0 + 1, n) if hs[i] > hs[i - 1] + 1e-6]
    bad_x = [i for i in range(1, n) if xs[i] < xs[i - 1] - 1e-6]
    print("[검증] D구간 키 단조감소: %s" % ("OK" if not bad_h else "실패 %s" % bad_h[:5]))
    print("[검증] 전체 x 단조증가 : %s" % ("OK" if not bad_x else "실패 %s" % bad_x[:5]))
    print("[검증] 컷 인덱스 범위  : D=%d~%d (32~63 이내: %s)"
          % (min(k for t, k, _, _ in plan[d0:]), max(k for t, k, _, _ in plan[d0:]),
             all(32 <= k <= 63 for t, k, _, _ in plan[d0:])))

    # ── 합성 ─────────────────────────────────────────────────────────────
    os.makedirs(TMP, exist_ok=True)
    for f in glob.glob(os.path.join(TMP, "*.png")):
        os.remove(f)

    for i, (kind, key, x, fy) in enumerate(plan):
        h = I.perspective_height(fy, p["horizon_y"], p["ref_foot_y"], p["ref_h"])
        src = poses[key] if kind == "pose" else cuts[key]
        im = fit(src, h)
        comp = bg.copy()
        hx = head_cx(src) * im.height / src.height        # ★머리 중심을 경로에 맞춘다
        pos = (int(round(x - hx)), int(round(fy - im.height)))
        comp.alpha_composite(im, pos)
        if fy < p["ref_foot_y"]:            # 벤치·난간보다 뒤 → 가려진다
            comp = I.occlude(bg, comp, mask)
        comp.convert("RGB").save(os.path.join(TMP, "f%04d.png" % i))
        if i in (0, N_A, N_A + N_B, d0, d0 + 20, d0 + 56, d0 + 96, n - 1):
            comp.convert("RGB").save(os.path.join(CHK, "run_away_%03d.png" % i))

    os.makedirs("W1_2/clips", exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(TMP, "f%04d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", OUT], check=True)
    print("OK %s  %dKB · %d프레임 · %.2f초"
          % (OUT, os.path.getsize(OUT) // 1024, n, n / FPS))


if __name__ == "__main__":
    main()
