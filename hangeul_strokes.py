#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
hangeul_strokes.py — 단모음 8개를 **정획순(올바른 필순)**으로 한 획씩 써 나가는 잉크 렌더러.

한글 교육 영상의 핵심: 글자도, 획순도 틀리면 안 된다.
획순 원칙(보편): ① 위에서 아래로, ② 왼쪽에서 오른쪽으로, ③ 기둥(세로)이 오른쪽인 모음(ㅓ/ㅔ)은
곁줄기(가로 짧은획)를 먼저 쓰고 기둥을 나중에 쓴다. 아래는 그 원칙을 각 모음에 적용한 표준 필순.

각 stroke = (점들, 화살표 방향 설명). 220×220 정사각 박스 좌표(중심 110, y는 아래로 증가).
stickman_factory 의 잉크 스탬프를 공유해 선 스타일을 통일한다.

검증: python hangeul_strokes.py           # 8개 모음 정획순 단계별 시트
"""
import os
import sys
import math
import random

from PIL import Image
from PIL import ImageDraw
from stickman_factory import stamp_stroke, SS

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
BOX = 220                 # design box (matches letter PNG framing)
LW = 15                   # stroke width in box units

# 단모음 정획순. 각 모음: [(stroke 점들, 방향설명), ...]  순서 = 쓰는 순서.
STROKES = {
    "ㅣ": [([(110, 28), (110, 206)], "세로 위→아래")],
    "ㅡ": [([(30, 130), (190, 130)], "가로 왼→오")],
    "ㅏ": [([(108, 30), (108, 204)], "①세로 위→아래"),
           ([(108, 117), (180, 117)], "②곁줄기 왼→오")],
    "ㅓ": [([(40, 117), (112, 117)], "①곁줄기 왼→오"),
           ([(112, 30), (112, 204)], "②세로 위→아래")],
    "ㅗ": [([(110, 36), (110, 120)], "①짧은세로 위→아래"),
           ([(34, 168), (186, 168)], "②가로 왼→오")],
    "ㅜ": [([(34, 96), (186, 96)], "①가로 왼→오"),
           ([(110, 96), (110, 184)], "②짧은세로 위→아래")],
    "ㅐ": [([(86, 30), (86, 204)], "①세로 위→아래(ㅏ)"),
           ([(86, 117), (140, 117)], "②곁줄기 왼→오(ㅏ)"),
           ([(162, 30), (162, 204)], "③세로 위→아래(ㅣ)")],
    "ㅔ": [([(70, 117), (114, 117)], "①곁줄기 왼→오(ㅓ)"),
           ([(114, 30), (114, 204)], "②세로 위→아래(ㅓ)"),
           ([(166, 30), (166, 204)], "③세로 위→아래(ㅣ)")],
}


def _partial(stroke, frac):
    """polyline 의 앞 frac(0..1) 만큼 잘라서 반환 (획이 그려지는 중)."""
    if frac >= 1.0:
        return stroke
    if frac <= 0.0:
        return [stroke[0]]
    # arclength 기준 (단모음 획은 2점 직선이라 단순 보간)
    total = sum(math.hypot(stroke[i + 1][0] - stroke[i][0], stroke[i + 1][1] - stroke[i][1])
                for i in range(len(stroke) - 1))
    target = total * frac
    out = [stroke[0]]
    acc = 0.0
    for i in range(len(stroke) - 1):
        a, b = stroke[i], stroke[i + 1]
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        if acc + seg >= target:
            t = (target - acc) / seg if seg else 1.0
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            return out
        out.append(b)
        acc += seg
    return out


def render_vowel(vowel, size_px, progress=1.0, seed=0):
    """vowel 을 정획순으로 progress(0..1)까지 그린 투명 PNG(RGBA, size_px²) 반환."""
    if vowel not in STROKES:
        raise KeyError(f"no stroke data for {vowel!r}")
    strokes = STROKES[vowel]
    rng = random.Random(seed or (abs(hash(vowel)) % 1000 + 1))
    f = size_px / BOX
    img = Image.new("RGBA", (size_px * SS, size_px * SS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    lw = LW * f * SS
    n = len(strokes)
    done = progress * n
    for i, (pts, _desc) in enumerate(strokes):
        local = max(0.0, min(1.0, done - i))
        if local <= 0.0:
            continue
        seg = _partial(pts, local)
        scaled = [(x * f * SS, y * f * SS) for (x, y) in seg]
        if len(scaled) == 1:
            scaled = [scaled[0], (scaled[0][0] + 0.1, scaled[0][1] + 0.1)]
        stamp_stroke(draw, scaled, lw, rng, wobble=0.45)
    return img.resize((size_px, size_px), Image.LANCZOS)


def _sheet():
    """정획순 단계별 검증 시트 (각 모음: 단계마다 한 획씩 추가)."""
    cream = (245, 245, 240, 255)
    cell, maxsteps = 150, 3
    rows = list(STROKES.keys())
    sheet = Image.new("RGBA", (cell * (maxsteps + 1), cell * len(rows)), cream)
    from PIL import ImageFont
    f = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 22)
    d = ImageDraw.Draw(sheet)
    for r, v in enumerate(rows):
        ns = len(STROKES[v])
        for step in range(1, maxsteps + 1):
            if step <= ns:
                prog = step / ns
                im = render_vowel(v, cell - 24, progress=prog)
                sheet.alpha_composite(im, (step * cell + 12, r * cell + 12))
        d.text((12, r * cell + cell // 2 - 14), f"{v}\n{ns}획", fill=(40, 40, 40), font=f)
    out = os.path.join(ROOT, "scratch", "_stroke_order.png")
    sheet.convert("RGB").save(out)
    print("stroke-order sheet ->", out)


if __name__ == "__main__":
    _sheet()
