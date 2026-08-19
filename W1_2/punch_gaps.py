# -*- coding: utf-8 -*-
"""몸 **사이의 틈**을 전부 뚫는다 — 투명컷 교정.

★사장님 확정 규칙(2026-08-13)
  "**얼굴을 빼고** 팔 사이, 팔과 몸 사이, 다리와 다리 사이, 다리와 몸 사이
   **모두 다 투명하게** 컷 하라."
  "투명컷은 하고 나서 **내 검사를 받는다**."

## 왜 막혔나
`cut_oneshot.cut()` 은 선이 둘러싼 안쪽을 **불투명 흰색**으로 채운다. 얼굴이 흰
동그라미라 그래야 하기 때문이다. 그런데 팔을 몸에 붙이고 선 자세는 팔·옆구리·
어깨가 만드는 틈도 선으로 둘러싸이므로, 얼굴과 똑같이 흰색으로 메워져 버린다.

## 가르는 법 — **틈이냐 몸이냐**는 폭으로 갈린다
넓이·가로세로비로는 안 갈린다(실측: 겨드랑이 틈 2.15 · 종아리 속 4.8 —
길쭉한 쪽이 오히려 **몸**이다). 갈라 주는 것은 **가장 굵은 데의 폭**이다.
조각 안에 넣을 수 있는 가장 큰 원의 지름을 재서 키로 나눈다.

| 조각 | 폭(키 대비) | 어떻게 하나 |
|---|---|---|
| 얼굴 동그라미 | — | **둔다** (맨 위의 둥근 조각 하나뿐) |
| 종아리·팔뚝 **속** | 3~4% (선 사이라 좁다) | **둔다** — 이건 몸이다 |
| 다리와 다리 사이 | 6~9% | ★**뚫는다** |
| 팔과 몸 사이 | 10~13% | ★**뚫는다** |
| 손에 든 카드·거울 | 넓고 꽉 참(0.80↑)이며 둥글넓적 | **둔다** — 몸이 아니라 물건 |

    python W1_2/punch_gaps.py                     # 검사만 (안 고침)
    python W1_2/punch_gaps.py --preview <폴더>    # 뚫을 자리를 빨갛게 칠해 보여 준다
    python W1_2/punch_gaps.py --fix               # 실제로 뚫는다(원본은 _v1 로 보관)
    python W1_2/punch_gaps.py --cuts --fix        # ★동작 컷 64프레임까지 전부
    python W1_2/punch_gaps.py zman_shoulder_recv --fix
"""
import argparse
import glob
import os
import shutil
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

POSE_DIRS = ["W1_2/pose_cuts", "W1_2/_poses"]
CUT_DIRS = ["W1_2/motion6_cuts", "W1_2/motion6_stride"]
M6_DIR = "assets/graphics/poses"   # m6_walk_side_r_00.png … 낱장 이동컷 라이브러리
MIN_PX = 40                        # 이보다 작은 건 안티에일리어싱 티끌
WIDE = 0.055                       # ★키 대비 이 폭을 넘으면 '틈'(몸이 아니다)
FILL_MAX = 0.80                    # 이보다 꽉 차고 둥글넓적하면 손에 든 물건
OBJ_RATIO = 2.2                    # 물건은 이보다 둥글넓적하다
FACE_RATIO = 1.7                   # 얼굴은 이보다 둥글다


def girth(mask):
    """조각 안에 넣을 수 있는 **가장 큰 원의 지름** — 가장 굵은 데의 폭."""
    return 2.0 * float(ndimage.distance_transform_edt(mask).max())


def find_gaps(im, wide=WIDE):
    """(틈 마스크, 조각 목록) — 조각 = (넓이, 가로, 세로, 폭%, 채움율, 판정).

    ★사장님 규칙 — **얼굴만 흰색으로 두고, 몸과 몸 사이는 전부 투명**.
      팔뚝·종아리 **속**은 몸이므로 남긴다. 그 둘은 **폭**으로 갈린다.
    """
    a = np.array(im.convert("RGBA"))
    alpha = a[:, :, 3]
    rgb = a[:, :, :3]
    ink = (alpha > 100) & (rgb.max(2) < 170)              # 검은 선만 잉크
    if not ink.any():
        return None, []

    lab, n = ndimage.label(ink)
    sizes = ndimage.sum(ink, lab, range(1, n + 1))
    main = lab == (int(np.argmax(sizes)) + 1)             # 몸통 선 한 덩어리
    # ★**아직 메워져 있는** 안쪽만 본다. 이미 뚫어 둔 곳은 선에 둘러싸여 있어도
    #   투명하므로 다시 세면 안 된다(안 그러면 뚫고도 "막힘"으로 잡힌다).
    inside = (ndimage.binary_fill_holes(main) & ~main & (alpha > 100))

    ys0, xs0 = np.nonzero(main)
    body_h = float(ys0.max() - ys0.min() + 1)

    hl, hn = ndimage.label(inside)
    cand = []
    for i in range(1, hn + 1):
        h = hl == i
        area = int(h.sum())
        if area < MIN_PX:
            continue
        ys, xs = np.nonzero(h)
        w = int(xs.max() - xs.min() + 1)
        ht = int(ys.max() - ys.min() + 1)
        cand.append(dict(i=i, m=h, area=area, w=w, h=ht, top=int(ys.min()),
                         ratio=max(w, ht) / float(max(1, min(w, ht))),
                         fill=area / float(w * ht),
                         gir=girth(h) / body_h))

    # ★얼굴 먼저 집어낸다 — **맨 위에 있는 둥근 조각**. 이것만 흰색으로 남는다.
    round_ones = [c for c in cand
                  if c["ratio"] < FACE_RATIO and c["gir"] > 0.06]
    face = min(round_ones, key=lambda c: c["top"])["i"] if round_ones else None

    gaps = np.zeros_like(inside)
    rows = []
    for c in cand:
        if c["i"] == face:
            why = "얼굴(둔다)"
        elif c["gir"] < wide:
            why = "좁다 — 팔뚝·종아리 속(몸이다·둔다)"
        elif c["fill"] >= FILL_MAX and c["ratio"] < OBJ_RATIO:
            why = "꽉 참 — 손에 든 카드·거울(둔다)"
        else:
            why = "★몸 사이 틈"
            gaps |= c["m"]
        rows.append((c["area"], c["w"], c["h"], c["gir"] * 100, c["fill"], why))
    rows.sort(reverse=True)
    return gaps, rows


def preview(path, gaps, out_dir):
    """뚫을 자리를 **빨갛게 칠해** 보여 준다 — 눈으로 보고 정한다."""
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    a[:, :, 0][gaps] = 240
    a[:, :, 1][gaps] = 40
    a[:, :, 2][gaps] = 40
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, os.path.basename(path))
    Image.fromarray(a, "RGBA").convert("RGB").save(p)
    return p


def _punch_file(path, gaps, backup=False):
    """틈을 알파 0 으로. 선까지 갉지 않도록 잉크 쪽으로 1px 물러난다."""
    im = Image.open(path).convert("RGBA")
    a = np.array(im)
    if backup:
        bak = os.path.splitext(path)[0] + "_v1.png"
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
    safe = gaps & ~ndimage.binary_dilation(
        (a[:, :, 3] > 100) & (a[:, :, :3].max(2) < 170), iterations=1)
    a[:, :, 3][safe] = 0
    Image.fromarray(a, "RGBA").save(path)


def punch(path, fix=False, wide=WIDE, prev_dir=None):
    im = Image.open(path).convert("RGBA")
    gaps, rows = find_gaps(im, wide)
    if gaps is None or not rows:
        return 0
    ng = sum(1 for r in rows if r[5].startswith("★"))
    name = os.path.splitext(os.path.basename(path))[0]
    print("  %-34s 안쪽 조각 %d개" % (name, len(rows)), end="")
    print(("  → ★틈 %d개" % ng) if ng else "  → 뚫을 것 없음")
    for area, w, h, ratio, fill, why in rows[:5]:
        print("      %6dpx %4dx%-4d 폭%5.1f%% 채움%.2f  %s"
              % (area, w, h, ratio, fill, why))
    if ng and prev_dir:
        print("      미리보기 →", preview(path, gaps, prev_dir))
    if not ng or not fix:
        return ng

    bak = os.path.join(os.path.dirname(path), name + "_v1.png")
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    a = np.array(im)
    # 틈은 알파 0. 선까지 갉지 않도록 잉크 쪽으로 1px 물러난다.
    safe = gaps & ~ndimage.binary_dilation(
        (a[:, :, 3] > 100) & (a[:, :, :3].max(2) < 170), iterations=1)
    a[:, :, 3][safe] = 0
    Image.fromarray(a, "RGBA").save(path)
    print("      저장 (원본 → %s)" % os.path.basename(bak))
    return ng


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--wide", type=float, default=WIDE,
                    help="키 대비 이 폭을 넘는 조각만 틈으로 본다 (기본 0.055)")
    ap.add_argument("--preview", default=None, help="뚫을 자리를 빨갛게 칠해 저장할 폴더")
    ap.add_argument("--cuts", action="store_true", help="동작 컷(64프레임)만")
    ap.add_argument("--all-cuts", dest="all_cuts", action="store_true",
                    help="정지 포즈 + 동작 컷 전부")
    a = ap.parse_args()

    # ── 정지 포즈 ──
    paths = []
    for d in POSE_DIRS:
        for p in sorted(glob.glob(os.path.join(d, "*.png"))):
            n = os.path.splitext(os.path.basename(p))[0]
            if n.endswith("_v1") or "sheet" in n:      # 검증용 시트는 자산이 아니다
                continue
            if a.names and n not in a.names:
                continue
            paths.append(p)

    tot = 0
    if not a.cuts:
        print("정지 포즈 %d장%s\n"
              % (len(paths), " · ★실제로 뚫는다" if a.fix else " (검사만)"))
        for p in paths:
            tot += punch(p, a.fix, a.wide, a.preview)

    # ── ★동작 컷 (64프레임 스트라이드 컷 포함) ──
    #   사장님 지시: "스트라이드 컷 전체 64프레임 투명컷은 컷랑이 전담해야 한다."
    #   프레임마다 자세가 다르므로 **프레임 하나하나** 판별해 뚫는다.
    if a.cuts or a.all_cuts:
        dirs = []
        for base in CUT_DIRS:
            for d in sorted(glob.glob(os.path.join(base, "*"))):
                if os.path.isdir(d):
                    k = os.path.basename(d)
                    if a.names and k not in a.names:
                        continue
                    dirs.append(d)
        print("\n동작 컷 %d종%s\n"
              % (len(dirs), " · ★실제로 뚫는다" if a.fix else " (검사만)"))
        for d in dirs:
            if d.endswith("_v1"):
                continue
            fs = sorted(glob.glob(os.path.join(d, "*.png")))
            # ★되돌릴 수 있게 폴더째 한 번 백업 한다 (64프레임을 한꺼번에 건드리므로)
            if a.fix:
                bak = d + "_v1"
                if not os.path.isdir(bak):
                    shutil.copytree(d, bak)
            n = 0
            for p in fs:
                gaps, rows = find_gaps(Image.open(p).convert("RGBA"), a.wide)
                ng = sum(1 for r in rows if r[5].startswith("★")) if rows else 0
                if not ng:
                    continue
                n += ng
                if a.fix:
                    _punch_file(p, gaps)
            tot += n
            print("  %-24s %2d프레임 · 틈 %3d개%s"
                  % (os.path.basename(d), len(fs), n, " → 뚫음" if (n and a.fix) else ""))

        # ★m6 이동컷 라이브러리는 **폴더가 아니라 낱장**으로 흩어져 있다
        #   (assets/graphics/poses/m6_walk_side_r_00.png …). 여기도 같이 뚫는다.
        keys = {}
        for p in sorted(glob.glob(os.path.join(M6_DIR, "m6_*.png"))):
            b = os.path.basename(p)[3:-4]
            if b[-3:-2] == "_" and b[-2:].isdigit():
                keys.setdefault(b[:-3], []).append(p)
        for k in sorted(keys):
            if a.names and k not in a.names:
                continue
            fs = keys[k]
            if a.fix:
                bak = os.path.join(M6_DIR, "_v1", k)
                if not os.path.isdir(bak):
                    os.makedirs(bak, exist_ok=True)
                    for p in fs:
                        shutil.copy2(p, bak)
            n = 0
            for p in fs:
                gaps, rows = find_gaps(Image.open(p).convert("RGBA"), a.wide)
                ng = sum(1 for r in rows if r[5].startswith("★")) if rows else 0
                if not ng:
                    continue
                n += ng
                if a.fix:
                    _punch_file(p, gaps)
            tot += n
            print("  m6:%-21s %2d프레임 · 틈 %3d개%s"
                  % (k, len(fs), n, " → 뚫음" if (n and a.fix) else ""))

    print("\n틈 %d개%s" % (tot, " 뚫었다" if a.fix else " 찾았다 — 뚫으려면 --fix"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
