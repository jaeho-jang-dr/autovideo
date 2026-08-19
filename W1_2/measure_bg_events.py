# -*- coding: utf-8 -*-
"""배경 동영상에서 **사건이 실제로 몇 초에 · 어디서** 일어나는지 프레임으로 잰다.

★문서 규칙(W1_2_motion.md §2): "배경 클립의 사건 시각이 기준이다. 배경을 먼저 만들고
  그 mp4 에서 사건이 실제로 몇 초에 일어나는지 프레임으로 확인한 뒤 캐릭터 컷을 그
  시각에 맞춘다. 배경이 지시대로 안 나오면 **캐릭터를 배경에 맞춘다**."

프롬프트에 "4.0초에 멈춘다"고 써도 Flow 가 그대로 내주지는 않는다. 그래서 잰다.

## ★2026-08-14 전면 교정 — 옛 방식이 오이·우유를 둘 다 틀렸다
옛 코드는 **프레임 차분(움직임)의 가장 큰 덩어리**를 쫓았다. 그런데 물체가 멈추면
차분이 0 이 되어 추적이 끊긴다. 그래서 '멈춘 자리' 대신 **처음 움직이기 시작한 자리**
를 내놓았다.

    오이   옛 3.79s·(610,509)  → 실측 4.33s·(850,596)   (610,509 는 램프에서 나오는 자리)
    우유팩 옛 5.21s·(958,607)  → 실측 6.58s·(567,593)   (958,607 은 좌판 위 진열 자리)

그래서 두 갈래로 잰다.

  **잔류형** — 오이·우유팩처럼 사건이 끝나고 **화면에 남는** 것
      끝 프레임과 첫 프레임의 차이(잔류 마스크)로 **최종 자리**를 먼저 잡고,
      그 자리 안에서 픽셀이 마지막으로 흔들린 시각을 찾아 **멈춘 시각**으로 삼는다.

  **통과형** — 비둘기·물기둥처럼 지나가 버려 **남지 않는** 것
      잔류가 없으니 움직임 세기 곡선의 **정점**과 그때의 무게중심을 낸다.

자동 검출만 믿지 않는다([[stage-horizon-measure-by-feet]]). `_bgmeas/<키>_check.png`
에 사건 앞뒤 프레임을 붙여 내니 **눈으로 짚어 확인**한 뒤 배선에 넣는다.

    python W1_2/measure_bg_events.py                 # 동영상 배경 전부
    python W1_2/measure_bg_events.py stall_cuke      # 하나만
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
os.chdir(ROOT)

BG = "W1_2/bg"
TMP = "W1_2/_bgmeas"
FPS = 24.0
MW, MH = 640, 360                     # 측정 해상도 (좌표는 1280x720 으로 환산)
# ★환산비는 **뽑아 둔 프레임의 실제 크기**에서 얻는다.
#   옛 캐시(320px)를 640 기준으로 환산해 좌표가 절반이 된 적이 있다(2026-08-14).
SX = SY = 2.0                         # measure() 가 프레임을 읽고 다시 잡는다

# 무엇을 재는 배경인가 — 라벨은 보고용, 목표는 프롬프트에 적어 둔 값
TARGETS = {
    "plaza_arrive":   "분수 줄이 다 솟는다",
    "plaza_gate":     "비둘기 떼가 날아오른다",
    "stall_cuke":     "오이가 굴러와 멈춘다",
    "stall_milk":     "우유팩이 떨어져 멈춘다",
    "fountain_burst": "물기둥이 가장 높다",
    "path_fox":       "여우가 고개를 내민다",
    "path_leaves":    "잎이 손 높이로 내려온다",
    "dusk_lanterns":  "마지막 등이 켜진다",
    "dusk_calm":      "(잔잔 — 사건 없을 수 있다)",
}

RESID_TH = 26.0                       # 잔류로 칠 밝기 차
MOVE_TH = 18.0                        # 움직임으로 칠 프레임간 차
MIN_BLOB = 60                         # 이보다 작은 덩어리는 잡티


def frames(key, force=False):
    d = os.path.join(TMP, key)
    got = sorted(glob.glob(os.path.join(d, "*.png")))
    if got and not force:
        return got
    os.makedirs(d, exist_ok=True)
    for f in got:
        os.remove(f)
    subprocess.run(["ffmpeg", "-y", "-v", "error",
                    "-i", os.path.join(BG, key + ".mp4"),
                    "-vf", "fps=%d,scale=%d:%d" % (int(FPS), MW, MH),
                    "-vsync", "0", os.path.join(d, "f%04d.png")], check=True)
    return sorted(glob.glob(os.path.join(d, "*.png")))


def blobs(mask, k=1):
    """큰 덩어리 k 개를 [(무게중심, 화소수, 마스크)] 로. 없으면 [].

    ★한 사건이 자국을 **두 군데** 남기기도 한다 — 우유팩이 좌판에서 떨어지면
      바닥에 팩이 생기는 동시에 **좌판 위 진열 자리가 빈다**. 큰 것 하나만 고르면
      빈 자리를 사건 자리로 잘못 짚는다(2026-08-14). 그래서 여럿을 내고 눈으로 고른다.
    """
    mask = ndimage.binary_opening(mask, np.ones((3, 3)))
    if not mask.any():
        return []
    lab, n = ndimage.label(mask)
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    out = []
    for j in np.argsort(sizes)[::-1][:k]:
        if sizes[j] < MIN_BLOB:
            break
        m = lab == (j + 1)
        ys, xs = np.nonzero(m)
        out.append(((int(xs.mean() * SX), int(ys.mean() * SY)), int(sizes[j]), m))
    return out


def biggest(mask):
    """가장 큰 덩어리의 (무게중심, 화소수, 마스크). 없으면 (None, 0, None)."""
    b = blobs(mask, 1)
    return b[0] if b else (None, 0, None)


def check_sheet(key, fs, marks):
    """사건 앞뒤 프레임을 한 장에 붙여 낸다 — 눈으로 확인하라고."""
    ims = []
    for t, tag in marks:
        i = max(0, min(len(fs) - 1, int(round(t * FPS))))
        im = Image.open(fs[i]).convert("RGB").resize((320, 180), Image.LANCZOS)
        ims.append((im, "%s %.2fs" % (tag, t)))
    if not ims:
        return None
    sheet = Image.new("RGB", (320 * len(ims), 180), (30, 30, 30))
    for k, (im, _) in enumerate(ims):
        sheet.paste(im, (k * 320, 0))
    p = os.path.join(TMP, key + "_check.png")
    sheet.save(p)
    return p, [t for _, t in ims]


def measure(key, force=False):
    global SX, SY
    fs = frames(key, force)
    if len(fs) < 8:
        print("  ★프레임 부족:", key)
        return None
    a = np.stack([np.asarray(Image.open(p).convert("L"), np.float32) for p in fs])
    SY, SX = 720.0 / a.shape[1], 1280.0 / a.shape[2]      # ★실제 프레임 크기 기준
    nf = len(a)
    dur = nf / FPS
    label = TARGETS.get(key, "?")

    # ── ① 잔류형 — 끝 프레임에 남은 것 ──────────────────────────────
    base = np.median(a[:3], axis=0)             # 첫 3장 중앙값 = 사건 전 화면
    tail = np.median(a[-3:], axis=0)            # 끝 3장 중앙값 = 사건 후 화면
    res = blobs(np.abs(tail - base) > RESID_TH, k=3)

    d = np.abs(np.diff(a, axis=0))              # 프레임간 움직임

    def settle(m):
        """그 자리 둘레가 **마지막으로 흔들린** 프레임 → 그 다음이 정지."""
        roi = ndimage.binary_dilation(m, np.ones((9, 9)))
        e = np.array([float(dd[roi].mean()) for dd in d])
        hot = np.nonzero(e > max(MOVE_TH * 0.35, e.max() * 0.18))[0]
        return (hot[-1] + 1) / FPS if len(hot) else None

    cands = [(c, n, settle(m)) for c, n, m in res]
    cands = [(c, n, t) for c, n, t in cands if t is not None]
    # ★사건 자리는 **더 늦게 잠잠해진 쪽**이다. 우유팩은 좌판이 먼저 비고
    #   바닥 팩이 나중에 멈춘다 — 시각이 늦은 덩어리를 고른다.
    cands.sort(key=lambda r: -r[2])
    c_res, n_res, rest_t = cands[0] if cands else (None, 0, None)
    m_res = res[0][2] if res else None

    # ── ② 통과형 — 움직임 세기 곡선의 정점 ──────────────────────────
    peaks = []
    for i, dd in enumerate(d):
        c, n, _ = biggest(dd > MOVE_TH)
        peaks.append((n, i, c))
    n_pk, i_pk, c_pk = max(peaks, key=lambda r: r[0])
    peak_t = i_pk / FPS

    # 움직임이 있는 구간
    areas = np.array([p[0] for p in peaks], float)
    on = np.nonzero(areas > max(MIN_BLOB, areas.max() * 0.15))[0]
    t0, t1 = (on[0] / FPS, on[-1] / FPS) if len(on) else (0.0, 0.0)

    kind = "잔류형" if (m_res is not None and rest_t) else "통과형"
    when = rest_t if kind == "잔류형" else peak_t
    where = c_res if kind == "잔류형" else c_pk

    print("  %-15s %-22s [%s]" % (key, label, kind))
    print("  %-15s %.2f초 · 움직임 %.2f~%.2fs · 정점 %.2fs(%s)"
          % ("", dur, t0, t1, peak_t, c_pk))
    if kind == "잔류형":
        print("  %-15s ★멈춘 시각 %.2fs · 자리 %s (잔류 %d화소)"
              % ("", rest_t, c_res, n_res))
        for c, n, t in cands[1:]:
            print("  %-15s   (딴 자국 %s · %d화소 · %.2fs 에 잠잠)" % ("", c, n, t))
    else:
        print("  %-15s ★사건 시각 %.2fs · 자리 %s (잔류 없음)"
              % ("", peak_t, c_pk))

    marks = [(0.0, "전"), (max(0.0, when - 1.0), "직전"), (when, "★사건"),
             (min(dur - 1 / FPS, when + 1.0), "직후"), (dur - 1 / FPS, "끝")]
    sheet = check_sheet(key, fs, marks)
    if sheet:
        print("  %-15s 확인용 %s" % ("", sheet[0]))
    return {"key": key, "kind": kind, "when": when, "where": where, "dur": dur}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--force", action="store_true", help="프레임 다시 뽑기")
    a = ap.parse_args()
    keys = a.keys or [k for k in TARGETS
                      if os.path.exists(os.path.join(BG, k + ".mp4"))]
    os.makedirs(TMP, exist_ok=True)
    print("배경 사건 실측 (24fps · 좌표는 1280x720 환산)\n")
    rows = []
    for k in keys:
        r = measure(k, a.force)
        if r:
            rows.append(r)
        print()
    print("=" * 74)
    print("%-16s %-6s %8s  %s" % ("배경", "갈래", "시각", "자리"))
    for r in rows:
        print("%-16s %-6s %7.2fs  %s" % (r["key"], r["kind"], r["when"], r["where"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
