# -*- coding: utf-8 -*-
"""투명컷 **전수 검사판** — 있는 컷·포즈를 하나씩 눈으로 본다.

★사장님 지시(2026-08-13)
  "투명컷은 하고 나서 내 검사를 받는다."
  "지금 이미 만들어진 투명컷도 하나 하나 다시 검사 받자."

## 무엇을 보여 주는가
투명한 곳은 **체커보드**로 비쳐 보이게 깔아 얹는다. 뚫려야 할 곳이 막혔는지,
막혀야 할 곳이 뚫렸는지 한눈에 보인다. 이름표에 실측값을 같이 찍는다.

  ★막힘 의심 — `punch_gaps` 가 "팔·몸 사이 틈인데 흰색으로 메워져 있다"고 본 것
  ☆발 뜸    — 발 밑에 투명 여백이 남아 있어 땅에서 뜨는 것
  잉크 %    — 컷 안에서 실제로 그림이 차지하는 비율(너무 높으면 배경이 안 뚫린 판)

## 쓰는 법
    python W1_2/inspect_cuts.py                # 검사판 만들고 뷰어 띄우기
    python W1_2/inspect_cuts.py --poses        # 정지 포즈만
    python W1_2/inspect_cuts.py --cuts         # 동작 컷만
    python W1_2/inspect_cuts.py --no-view      # 판만 만들고 뷰어는 안 띄움

뷰어 조작 — 썸네일 클릭/마우스오버 = 오른쪽 큰창 · ←/→ 넘기기 · +/- 크기 · ESC 닫기
"""
import argparse
import glob
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import render_show as R                                    # noqa: E402
import punch_gaps as G                                     # noqa: E402

OUT = "W1_2/_inspect"
FONT = r"C:\Windows\Fonts\malgun.ttf"
CELL = 16                          # 체커 눈금
PER_CUT = 6                        # 동작 컷 하나에서 뽑아 볼 프레임 수
PAD = 30                           # 이름표 자리


def checker(w, h):
    a = np.zeros((h, w, 3), np.uint8)
    yy, xx = np.mgrid[0:h, 0:w]
    odd = ((xx // CELL) + (yy // CELL)) % 2 == 1
    a[..., :] = 255
    a[odd] = (120, 190, 255)
    return Image.fromarray(a, "RGB").convert("RGBA")


def measure(im):
    a = np.asarray(im.convert("RGBA"))
    al = a[..., 3]
    op = al > 8
    if not op.any():
        return None
    rows = np.nonzero(op.any(1))[0]
    return dict(ink=float(op.mean()),
                pad=int(im.height - (rows[-1] + 1)),
                ink_h=int(rows[-1] - rows[0] + 1))


def card(path, tag=""):
    """한 장 → 체커보드에 얹고 이름표를 단 검사 카드."""
    im = Image.open(path).convert("RGBA")
    m = measure(im)
    if not m:
        return None
    gaps, rows = G.find_gaps(im)
    stuck = sum(1 for r in rows if r[5].startswith("★")) if rows else 0

    cv = checker(im.width, im.height + PAD)
    cv.alpha_composite(im, (0, PAD))
    if stuck and gaps is not None:
        # 막혀 있는 틈을 빨갛게 짚어 준다
        a = np.array(cv)
        a[PAD:, :, 0][gaps] = 240
        a[PAD:, :, 1][gaps] = 40
        a[PAD:, :, 2][gaps] = 40
        cv = Image.fromarray(a, "RGBA")

    d = ImageDraw.Draw(cv)
    d.rectangle([0, 0, cv.width, PAD - 1], fill=(24, 26, 32, 255))
    name = os.path.splitext(os.path.basename(path))[0]
    flag = ""
    if stuck:
        flag += " ★막힘%d" % stuck
    if m["pad"] > 8:
        flag += " ☆발뜸%d" % m["pad"]
    txt = "%s%s  잉크%.0f%%  키%d" % (tag or name, flag, m["ink"] * 100, m["ink_h"])
    d.text((6, 5), txt, font=ImageFont.truetype(FONT, 17),
           fill=(255, 90, 90) if flag else (210, 220, 235))
    return cv.convert("RGB"), (name, stuck, m["pad"], m["ink"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--poses", action="store_true")
    ap.add_argument("--cuts", action="store_true")
    ap.add_argument("--no-view", action="store_true")
    ap.add_argument("--thumb", type=int, default=260,
                    help="왼쪽 썸네일 크기(기본 260 — 크게)")
    a = ap.parse_args()
    do_p = a.poses or not a.cuts
    do_c = a.cuts or not a.poses

    os.makedirs(OUT, exist_ok=True)
    for f in glob.glob(os.path.join(OUT, "*.png")):
        os.remove(f)

    bad, n = [], 0
    if do_p:
        # ★`_v1` 은 뚫기 전 **백업 원본**이다 — 검사 대상이 아니다
        poses = {k: v for k, v in R.load_poses().items()
                 if not k.endswith("_v1") and "sheet" not in k}
        print("\n=== 정지 포즈 %d장 ===" % len(poses))
        for k in sorted(poses):
            r = card(poses[k])
            if not r:
                continue
            img, (name, stuck, pad, ink) = r
            img.save(os.path.join(OUT, "p_%s.png" % name))
            n += 1
            if stuck or pad > 8:
                bad.append(("포즈", name, stuck, pad))
                print("  ★ %-34s 막힘%d 발뜸%d" % (name, stuck, pad))

    if do_c:
        cuts = {k: v for k, v in R.load_cuts().items() if not k.endswith("_v1")}
        print("\n=== 동작 컷 %d종 ===" % len(cuts))
        for k in sorted(cuts):
            fs = cuts[k]
            idx = [int(i * (len(fs) - 1) / max(1, PER_CUT - 1)) for i in range(PER_CUT)]
            worst = (0, 0)
            for j, i in enumerate(sorted(set(idx))):
                r = card(fs[i], "%s [%d/%d]" % (k, i, len(fs)))
                if not r:
                    continue
                img, (_, stuck, pad, ink) = r
                img.save(os.path.join(OUT, "c_%s_%02d.png" % (k.replace(":", "-"), j)))
                n += 1
                worst = (max(worst[0], stuck), max(worst[1], pad))
            if worst[0] or worst[1] > 8:
                bad.append(("동작", k, worst[0], worst[1]))
                print("  ★ %-24s 막힘%d 발뜸%d" % (k, worst[0], worst[1]))

    print("\n검사판 %d장 → %s" % (n, OUT))
    if bad:
        print("★손볼 것 %d개:" % len(bad))
        for kind, name, stuck, pad in bad:
            print("   %s %-32s %s%s" % (kind, name,
                  ("팔·몸 틈 막힘 %d곳" % stuck) if stuck else "",
                  ("  발 밑 여백 %dpx" % pad) if pad > 8 else ""))
    else:
        print("막힌 틈·발 뜸 없음")

    if not a.no_view:
        # ★왼쪽 썸네일을 크게 띄운다 (사장님 지시 2026-08-13
        #   "왼편도 가능한 한 크게 보이게, 마우스로 내려 가면서 볼 수 있게")
        subprocess.Popen(["pythonw", "gridviewer.py", "--thumb", str(a.thumb), OUT])
        print("\n뷰어를 띄웠습니다 — 왼쪽 휠로 내리고, 올리면 오른쪽 큰 창에 뜹니다."
              " (+/- 로 썸네일 크기)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
