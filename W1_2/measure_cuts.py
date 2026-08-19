# -*- coding: utf-8 -*-
"""동작 컷을 **실측**해 `W1_2/cut_metrics.json` 으로 굽는다 — 동작 계산기의 재료.

★왜 필요한가
  `place_xy()` 는 **이미지 아래끝**을 발 y 에 맞춘다. 그런데 컷마다 발 밑에
  투명 여백이 다르게 남아 있어, 같은 발 y 를 줘도 어떤 컷은 뜨고 어떤 컷은 박힌다
  (사장님 지적 2026-08-13 "뒤로 달려 나갈 때에도 발이 바닥에서 떨어지면 안 된다").

★무엇을 재는가 (프레임마다 재서 컷 단위로 모은다)
  ink_top/ink_bot  잉크(알파>8) 위·아래끝            → 발 밑 여백 = img_h - ink_bot
  ink_h            발-머리 bbox 높이                  → **자세따라 변한다(변해도 된다)**
  head_d           머리 지름                          → ★축척의 기준(자세 무관)
  cx               잉크 무게중심 x                    → 러닝머신 컷인지(제자리) 판별
  travel           한 바퀴 도는 동안 cx 가 움직인 폭  → 0 이면 제자리 컷

    python W1_2/measure_cuts.py
"""
import glob
import json
import os
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import render_show as R                                    # noqa: E402

OUT = "W1_2/cut_metrics.json"


def head_diameter(a):
    """맨 위 잉크 덩어리의 가로폭 = 머리 지름.

    ★자세가 바뀌어도 머리 크기는 안 변한다 — 그래서 이것이 축척의 기준이다
      (사장님 지시: "머리의 아래위 길이를 재서 전체 크기를 측정하라").
      가로폭으로 재는 이유는 머리카락이 위로 뻗어 세로가 들쭉날쭉해서다.
    """
    rows = np.where(a.any(axis=1))[0]
    if not len(rows):
        return 0
    top = rows[0]
    # 머리 꼭대기에서 아래로 훑으며 가장 넓어지는 지점 = 머리 최대 지름
    best = 0
    for y in range(top, min(top + 90, a.shape[0])):
        xs = np.where(a[y])[0]
        if not len(xs):
            continue
        w = xs[-1] - xs[0] + 1
        if w > best * 1.6 and best:                        # 어깨로 내려간 것
            break
        best = max(best, w)
    return int(best)


def foot_spread(a, rows):
    """발 부분(잉크 아래 12%)의 **가로 폭** = 그 프레임의 두 발 벌린 정도.

    한 바퀴 도는 동안의 **최대 폭이 보폭(stride)** 이다 — 컷 픽셀 단위.
    이 값이 있어야 "이 컷을 몇 배속으로 돌려야 발이 안 미끄러지는가" 를 계산할 수 있다.
    """
    top, bot = rows[0], rows[-1]
    y0 = int(bot - (bot - top) * 0.12)
    band = a[y0:bot + 1]
    if not band.any():
        return 0
    cols = np.where(band.any(axis=0))[0]
    return int(cols[-1] - cols[0] + 1)


def measure_frame(p):
    im = Image.open(p).convert("RGBA")
    a = np.asarray(im.split()[-1]) > 8
    if not a.any():
        return None
    rows = np.where(a.any(axis=1))[0]
    cols = np.where(a.any(axis=0))[0]
    ys, xs = np.nonzero(a)
    return dict(img_w=im.width, img_h=im.height,
                ink_top=int(rows[0]), ink_bot=int(rows[-1]) + 1,
                ink_l=int(cols[0]), ink_r=int(cols[-1]) + 1,
                ink_h=int(rows[-1] - rows[0] + 1),
                ink_w=int(cols[-1] - cols[0] + 1),
                head_d=head_diameter(a),
                feet_w=foot_spread(a, rows),
                cx=float(xs.mean()))


def main():
    cuts = R.load_cuts()
    poses = R.load_poses()
    out = {"cuts": {}, "poses": {}}

    print("=== 동작 컷 %d종 ===" % len(cuts))
    for k in sorted(cuts):
        fs = cuts[k]
        ms = [m for m in (measure_frame(p) for p in fs) if m]
        if not ms:
            continue
        ink_h = [m["ink_h"] for m in ms]
        pad = [m["img_h"] - m["ink_bot"] for m in ms]
        head = [m["head_d"] for m in ms if m["head_d"] > 0]
        cxs = [m["cx"] for m in ms]
        feet = [m["feet_w"] for m in ms]
        rec = dict(
            n=len(fs),
            img_w=ms[0]["img_w"], img_h=ms[0]["img_h"],
            ink_h_med=int(np.median(ink_h)), ink_h_max=int(max(ink_h)),
            ink_h_min=int(min(ink_h)),
            foot_pad_med=int(np.median(pad)), foot_pad_max=int(max(pad)),
            head_d_med=int(np.median(head)) if head else 0,
            travel=int(max(cxs) - min(cxs)),
            stride_px=int(max(feet)),                      # ★한 보의 보폭(컷 픽셀)
            # ★축척의 기준 — 원샷 동작은 **첫 프레임(서 있는 상태)**, 이동 컷은 중앙값.
            #   자세가 변해도 이 기준으로 잰 축척은 컷 내내 고정이다.
            ink_h_first=ms[0]["ink_h"],
            # ★프레임별 값 — 이걸로 **실제 동작이 일어나는 구간**을 찾아낸다.
            #   8초짜리 Veo 컷은 앞뒤로 그냥 서 있는 시간이 길다. 그 구간을 잘라내야
            #   "동작을 반쯤 하다 만다"는 소리를 안 듣는다.
            ink_top_list=[m["ink_top"] for m in ms],
            ink_bot_list=[m["ink_bot"] for m in ms],
            ink_h_list=[m["ink_h"] for m in ms],
            cx_list=[round(m["cx"], 1) for m in ms],
        )
        out["cuts"][k] = rec
        print("  %-22s %2d컷 %4dx%-4d 잉크%3d~%-3d 발밑%3d 보폭%4d 이동%4d"
              % (k, rec["n"], rec["img_w"], rec["img_h"], rec["ink_h_min"],
                 rec["ink_h_max"], rec["foot_pad_med"], rec["stride_px"],
                 rec["travel"]))

    print("\n=== 정지 포즈 %d장 ===" % len(poses))
    for k in sorted(poses):
        m = measure_frame(poses[k])
        if not m:
            continue
        out["poses"][k] = dict(img_w=m["img_w"], img_h=m["img_h"],
                               ink_h=m["ink_h"], ink_w=m["ink_w"],
                               ink_top=m["ink_top"], ink_bot=m["ink_bot"],
                               ink_l=m["ink_l"], ink_r=m["ink_r"],
                               head_d=m["head_d"],
                               foot_pad=m["img_h"] - m["ink_bot"])
        flag = "  ★발밑여백" if m["img_h"] - m["ink_bot"] > 8 else ""
        print("  %-34s %4dx%-4d 잉크%4d 발밑여백%3d%s"
              % (k, m["img_w"], m["img_h"], m["ink_h"],
                 m["img_h"] - m["ink_bot"], flag))

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("\n✅ %s — 동작 %d · 포즈 %d"
          % (OUT, len(out["cuts"]), len(out["poses"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
