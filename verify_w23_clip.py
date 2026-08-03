# -*- coding: utf-8 -*-
"""W23 동작 클립 ↔ 가이드 동일성 확인 (사장님 지시 2026-07-27: 동영상 하나하나마다 확인 절차).

하는 일
  1. 생성된 클립에서 프레임을 고르게 뽑는다(기본 8장).
  2. 가이드 이미지를 맨 앞에 두고 한 폴더에 모아 **gridviewer**로 띄운다
     (왼쪽 썸네일 → 마우스 올리면 오른쪽 큰창).
  3. 보조 수치: 옷·머리·피부 **주요 색 팔레트 거리**와 **몸높이·어깨폭 비율**을 가이드와 비교해
     "같은 사람인지" 를 숫자로도 보여준다. 최종 판단은 사장님 눈이다.

사용:
  python verify_w23_clip.py --key greet_wave [--frames 8] [--no-view]
  python verify_w23_clip.py --clip W23/clips/injun_w23_greet_wave.mp4 --guide W23/guides/injun_w23_guide_front.png
"""
import argparse
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
from cutrang import cutout_char, body_metrics          # 검증된 컷아웃·치수 재사용


def palette(img_rgba, k=6):
    """캐릭터 픽셀만 모아 대표색 k개(빈도순)."""
    a = np.array(img_rgba)
    if a.shape[2] == 4:
        m = a[:, :, 3] > 0
        px = a[m][:, :3]
    else:
        px = a.reshape(-1, 3)
    if len(px) == 0:
        return []
    q = (px // 32 * 32).astype(int)
    keys, counts = np.unique(q, axis=0, return_counts=True)
    order = np.argsort(-counts)[:k]
    tot = counts.sum()
    return [(tuple(int(v) for v in keys[i]), counts[i] / tot) for i in order]


def pal_dist(p1, p2):
    """두 팔레트의 가중 색거리(0=동일). 0.10 이하면 사실상 같은 배색."""
    if not p1 or not p2:
        return 1.0
    d = 0.0
    for c1, w1 in p1:
        best = min(np.linalg.norm(np.array(c1) - np.array(c2)) for c2, _ in p2)
        d += w1 * best / 441.7
    return round(d, 4)


def shape_of(rgba):
    crop = cutout_char(np.array(rgba)) if np.array(rgba).shape[2] == 4 else None
    if crop is None:
        a = np.array(rgba.convert("RGBA"))
        crop = cutout_char(a)
    if crop is None:
        return None
    span, cx = body_metrics(crop)
    h, w = crop.shape[:2]
    return dict(body=span, w=w, h=h, ratio=round(w / max(1, h), 3))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key")
    ap.add_argument("--clip")
    ap.add_argument("--guide")
    ap.add_argument("--frames", type=int, default=8)
    ap.add_argument("--no-view", action="store_true")
    a = ap.parse_args()

    clip = a.clip or f"W23/clips/injun_w23_{a.key}.mp4"
    guide = a.guide
    if not guide:
        import re
        src = open("gen_w23_assets.py", encoding="utf-8").read()
        m = re.search(rf'\("{a.key}",\s*(GUIDE_\w+)', src)
        gmap = {"GUIDE_FRONT": "W23/guides/injun_w23_guide_front.png",
                "GUIDE_3Q": "W23/guides/injun_w23_guide_3q.png",
                "GUIDE_SIDE": "W23/guides/injun_w23_guide_side.png"}
        guide = gmap.get(m.group(1) if m else "GUIDE_FRONT", gmap["GUIDE_FRONT"])
    if not os.path.exists(clip):
        raise SystemExit(f"클립 없음: {clip}")

    out = f"scratch/w23_verify/{a.key or os.path.basename(clip).split('.')[0]}"
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        os.remove(os.path.join(out, f))

    # 가이드를 0번으로
    shutil.copyfile(guide, f"{out}/00_가이드_{os.path.basename(guide)}")

    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", clip], capture_output=True, text=True).stdout.strip() or 8)
    times = [dur * i / (a.frames - 1) * 0.98 for i in range(a.frames)]
    gimg = Image.open(guide).convert("RGBA")
    gpal, gshape = palette(gimg), shape_of(gimg)

    print(f"클립 {clip}  길이 {dur:.2f}s")
    print(f"가이드 {guide}")
    print(f"  가이드 대표색: {[c for c, _ in gpal[:4]]}")
    print(f"  가이드 몸높이 {gshape['body']}px · 가로세로비 {gshape['ratio']}\n")
    print(f"{'프레임':>6} {'시각':>7}  {'색거리':>7}  {'몸높이':>7}  {'가로세로비':>9}  판정")
    rows = []
    for i, t in enumerate(times):
        p = f"{out}/{i+1:02d}_t{t:04.1f}s.png"
        subprocess.run(["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", clip, "-frames:v", "1", p],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not os.path.exists(p):
            continue
        im = Image.open(p).convert("RGBA")
        sp, sh = palette(im), shape_of(im)
        d = pal_dist(gpal, sp)
        body = sh["body"] if sh else 0
        ratio = sh["ratio"] if sh else 0
        ok = "OK" if d <= 0.12 else ("주의" if d <= 0.2 else "★다름")
        print(f"{i+1:6d} {t:6.2f}s  {d:7.3f}  {body:7d}  {ratio:9.3f}  {ok}")
        rows.append(d)
    if rows:
        avg = sum(rows) / len(rows)
        print(f"\n평균 색거리 {avg:.3f} → " +
              ("가이드와 사실상 동일한 배색" if avg <= 0.12 else
               "약간 어긋남 — 눈으로 확인 필요" if avg <= 0.2 else "★다른 캐릭터일 가능성 — 재생성 권고"))
    print(f"\n대조 이미지 {len(rows)+1}장 → {out}")
    if not a.no_view:
        subprocess.Popen(["pythonw", "gridviewer.py", out], cwd=ROOT)
        print("gridviewer 로 띄웠다(왼쪽 썸네일 → 마우스 올리면 오른쪽 큰창).")


if __name__ == "__main__":
    main()
