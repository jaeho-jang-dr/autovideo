#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
hangeul_write.py — 자음 + 음절(초·중·종성 조합) 정획순 파라메트릭 드로잉.

획순 규칙(사장님 지시 2026-07-05):
  · 위 → 아래, 왼 → 오, 왼편 먼저.
  · 이응(ㅇ)은 **반시계 방향**으로 그린다.
  · **기본 자음 먼저, 가획(추가 획)은 나중에** 긋는다 (ㅋ=ㄱ+획, ㅌ=ㄷ+획, ㅊ=ㅈ+획, ㅎ=ㅇ+획).

좌표계 = 220×220 박스(중심 110, y 아래로 증가). 모음은 hangeul_strokes.STROKES 재사용.
render_char(jamo, ...)      단자모(자음/모음) 정획순 드로잉.
render_syllable(syl, ...)   완성 음절(강/책/윽 …)을 초→중→종성 순서로 정획순 드로잉.
검증: python hangeul_write.py    # 자음 + W4 음절 획순 시트
"""
import os, sys, math, random
from PIL import Image, ImageDraw
from stickman_factory import stamp_stroke, SS
from hangeul_strokes import STROKES as V_STROKES, _partial

try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass

ROOT = os.path.dirname(os.path.abspath(__file__))
BOX = 220
LW = 15

# ㅇ 반시계 원(위 12시에서 시작 → 반시계). 다각형 근사.
def _circle_ccw(cx, cy, r, n=28):
    pts = []
    for i in range(n + 1):
        a = math.pi / 2 + (2 * math.pi) * (i / n)   # 12시 시작, +각도=반시계(y아래 좌표계)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

# 자음 정획순. 각 자음: [(폴리라인 점들, 방향설명), ...]  (기본 먼저, 가획 나중)
C_STROKES = {
    "ㄱ": [([(46, 56), (176, 56), (150, 196)], "가로 왼→오 꺾어 아래")],
    "ㄴ": [([(64, 48), (64, 190), (192, 190)], "세로 위→아래, 가로 왼→오")],
    "ㄷ": [([(54, 52), (186, 52)], "①위 가로 왼→오"),
           ([(58, 54), (58, 192), (188, 192)], "②세로 위→아래+아래 가로")],
    # ★ㄹ 바로잡음(사장님 지적 2026-08-14 "ㄹ을 정확하게 다시 써").
    #   ㄹ 은 내리긋는 자리가 **위는 오른쪽, 아래는 왼쪽**으로 번갈아 간다.
    #   전에는 ②에서 오른쪽으로 또 내려긋고 ③이 y=148 에서 시작해,
    #   가운데 가로(y=96)와 왼 세로가 **끊겨 떠 있었다**.
    "ㄹ": [([(54, 46), (170, 46), (158, 96)], "①위 ㄱ(오른쪽으로 내림)"),
           ([(54, 96), (176, 96)], "②가운데 가로 왼→오"),
           ([(58, 96), (58, 196), (186, 196)], "③아래 ㄴ(왼쪽으로 내림)")],
    "ㅁ": [([(58, 46), (58, 194)], "①왼 세로 위→아래"),
           ([(58, 46), (186, 46), (186, 194)], "②위 가로+오른 세로"),
           ([(58, 194), (186, 194)], "③아래 가로 왼→오")],
    "ㅂ": [([(56, 44), (56, 194)], "①왼 세로"),
           ([(184, 44), (184, 194)], "②오른 세로"),
           ([(56, 122), (184, 122)], "③가운데 가로"),
           ([(56, 194), (184, 194)], "④아래 가로")],
    "ㅇ": [(_circle_ccw(110, 118, 82), "반시계 원(위 12시 시작)")],
    "ㅅ": [([(112, 44), (52, 198)], "①왼 삐침"),
           ([(120, 92), (186, 198)], "②오른 삐침")],
    "ㅈ": [([(50, 54), (186, 54)], "①위 가로 왼→오"),
           ([(112, 54), (54, 196)], "②왼 삐침"),
           ([(120, 96), (186, 196)], "③오른 삐침")],
    "ㅊ": [([(82, 30), (150, 30)], "①위 짧은획 먼저(위→아래로 내려오며)"),
           ([(50, 74), (186, 74)], "②ㅈ 위 가로"),
           ([(112, 74), (54, 202)], "③ㅈ 왼 삐침"),
           ([(120, 112), (186, 202)], "④ㅈ 오른 삐침")],
    "ㅋ": [([(46, 54), (176, 54), (150, 196)], "①ㄱ"),
           ([(74, 122), (176, 122)], "②가획: 가운데 가로(나중)")],
    "ㅌ": [([(54, 50), (186, 50)], "①ㄷ 위 가로"),
           ([(58, 52), (58, 194), (188, 194)], "②ㄷ 세로+아래 가로"),
           ([(58, 122), (186, 122)], "③가획: 가운데 가로(나중)")],
    "ㅍ": [([(44, 58), (192, 58)], "①위 가로"),
           ([(74, 58), (74, 186)], "②왼 세로"),
           ([(162, 58), (162, 186)], "③오른 세로"),
           ([(44, 186), (192, 186)], "④아래 가로")],
    "ㅎ": [([(84, 30), (150, 30)], "①위 짧은획"),
           ([(50, 64), (186, 64)], "②가로"),
           (_circle_ccw(110, 150, 52), "③ㅇ 반시계(가획 나중)")],
    "ㄲ": [([(36, 58), (110, 58), (94, 190)], "①왼 ㄱ"),
           ([(120, 58), (192, 58), (176, 190)], "②오른 ㄱ")],
}

# 쌍자음(ㄸㅃㅆㅉ) = 기본 자음을 왼/오 반쪽에 나란히(왼 먼저). 프로그램 생성.
def _half(base, left):
    off, sc = (4, 0.47) if left else (118, 0.47)
    return [([(off + x * sc, y) for (x, y) in pts], d + ("(왼)" if left else "(오)"))
            for (pts, d) in C_STROKES[base]]
for _dbl, _b in [("ㄸ", "ㄷ"), ("ㅃ", "ㅂ"), ("ㅆ", "ㅅ"), ("ㅉ", "ㅈ")]:
    C_STROKES[_dbl] = _half(_b, True) + _half(_b, False)

# 이중모음(이오티드) — 기본 모음 + 곁줄기/짧은세로 추가. (세로계 곁줄기는 위→아래 순)
V2_STROKES = {
    "ㅑ": [([(108, 30), (108, 204)], "세로"),
           ([(108, 84), (182, 84)], "위 곁줄기"),
           ([(108, 150), (182, 150)], "아래 곁줄기")],
    "ㅕ": [([(38, 84), (112, 84)], "위 곁줄기"),
           ([(38, 150), (112, 150)], "아래 곁줄기"),
           ([(112, 30), (112, 204)], "세로")],
    "ㅛ": [([(78, 34), (78, 118)], "왼 짧은세로"),
           ([(142, 34), (142, 118)], "오른 짧은세로"),
           ([(32, 150), (188, 150)], "가로")],
    "ㅠ": [([(32, 92), (188, 92)], "가로"),
           ([(78, 92), (78, 176)], "왼 짧은세로"),
           ([(142, 92), (142, 176)], "오른 짧은세로")],
    "ㅒ": [([(84, 30), (84, 204)], "세로"),
           ([(84, 84), (140, 84)], "위 곁줄기"),
           ([(84, 150), (140, 150)], "아래 곁줄기"),
           ([(164, 30), (164, 204)], "ㅣ 세로")],
    "ㅖ": [([(66, 84), (114, 84)], "위 곁줄기"),
           ([(66, 150), (114, 150)], "아래 곁줄기"),
           ([(114, 30), (114, 204)], "세로"),
           ([(166, 30), (166, 204)], "ㅣ 세로")],
}
JUNG_ALL = list("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅛㅜㅠㅡㅣ")   # 조립 가능한 단/이중(iotized) 모음

VERT = set("ㅏㅐㅑㅒㅓㅔㅕㅖㅣ")      # 세로 모음 → 초성 왼 / 중성 오른
HORZ = set("ㅗㅛㅜㅠㅡ")             # 가로 모음 → 초성 위 / 중성 아래

CHO = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")
JUNG = list("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ")
JONG = list(" ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ")


def strokes_of(jamo):
    if jamo in C_STROKES: return C_STROKES[jamo]
    if jamo in V_STROKES: return V_STROKES[jamo]
    if jamo in V2_STROKES: return V2_STROKES[jamo]
    return None


def _fit(pts, box_region):
    """220박스 좌표 → 대상 영역(x0,y0,w,h)으로 선형 매핑."""
    x0, y0, w, h = box_region
    return [(x0 + x / BOX * w, y0 + y / BOX * h) for (x, y) in pts]


def _syllable_layout(cho, jung, jong):
    """자모별 (jamo, 220박스영역(x0,y0,w,h)) 리스트를 초→중→종 순서로."""
    seq = []
    has_j = jong != " " and jong != ""
    if jung in HORZ:            # 가로모음: 초성 위, 중성 아래(넓게), 종성 맨아래
        if has_j:
            seq.append((cho,  (46, 8, 128, 96)))
            seq.append((jung, (16, 104, 188, 58)))
            seq.append((jong, (46, 158, 128, 58)))
        else:
            seq.append((cho,  (52, 14, 116, 118)))
            seq.append((jung, (16, 132, 188, 74)))
    else:                       # 세로모음: 초성 왼, 중성 오른, 종성 아래
        if has_j:
            seq.append((cho,  (14, 10, 104, 128)))
            seq.append((jung, (120, 6, 92, 150)))
            seq.append((jong, (30, 150, 150, 66)))
        else:
            seq.append((cho,  (20, 22, 106, 176)))
            seq.append((jung, (120, 14, 92, 192)))
    return seq


def decompose(syl):
    if not syl or len(syl) != 1:
        return None
    o = ord(syl) - 0xAC00
    if o < 0 or o > 11171:
        return None
    cho = CHO[o // 588]; jung = JUNG[(o % 588) // 28]; jong = JONG[o % 28]
    return cho, jung, jong


def _draw_seq(draw, seq, f, prog):
    """seq=[(jamo, region), ...]. 전체 획을 prog(0..1)까지 초→중→종 순서로 그림."""
    # 전체 획 리스트(자모별 획들을 영역에 맞춰 변환)
    all_strokes = []
    for jamo, region in seq:
        st = strokes_of(jamo)
        if not st:
            continue
        for pts, _desc in st:
            all_strokes.append(_fit(pts, region))
    n = len(all_strokes)
    if n == 0:
        return
    done = prog * n
    rng = random.Random(1)
    for i, pts in enumerate(all_strokes):
        local = max(0.0, min(1.0, done - i))
        if local <= 0.0:
            continue
        seg = _partial(pts, local)
        scaled = [(x * f * SS, y * f * SS) for (x, y) in seg]
        if len(scaled) == 1:
            scaled = [scaled[0], (scaled[0][0] + 0.1, scaled[0][1] + 0.1)]
        stamp_stroke(draw, scaled, LW * f * SS * 0.82, rng, wobble=0.4)


def render_char(jamo, size_px, progress=1.0, seed=0):
    """단자모(자음/모음) 정획순 드로잉."""
    f = size_px / BOX
    img = Image.new("RGBA", (size_px * SS, size_px * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _draw_seq(d, [(jamo, (0, 0, BOX, BOX))], f, progress)
    return img.resize((size_px, size_px), Image.LANCZOS)


def render_syllable(syl, size_px, progress=1.0, seed=0):
    """완성 음절/단어를 초→중→종성 순서로 정획순 드로잉. 여러 음절이면 가로로 나란히."""
    chars = list(syl)
    n = len(chars)
    if n <= 1:
        f = size_px / BOX
        img = Image.new("RGBA", (size_px * SS, size_px * SS), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        dec = decompose(syl) if syl else None
        if dec is None:
            _draw_seq(d, [(syl, (0, 0, BOX, BOX))], f, progress)
        else:
            _draw_seq(d, _syllable_layout(*dec), f, progress)
        return img.resize((size_px, size_px), Image.LANCZOS)
    # 다음절 단어: 폭 = n음절, 각 음절 순서대로 progress 배분
    W_px = size_px * n
    img = Image.new("RGBA", (W_px * SS, size_px * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = size_px / BOX
    done = progress * n
    for i, ch in enumerate(chars):
        local = max(0.0, min(1.0, done - i))
        if local <= 0.0:
            break
        dec = decompose(ch)
        seq = _syllable_layout(*dec) if dec else [(ch, (0, 0, BOX, BOX))]
        # i번째 음절 영역으로 x 오프셋
        seq2 = [(j, (x0 + i * BOX, y0, w, h)) for (j, (x0, y0, w, h)) in seq]
        _draw_seq(d, seq2, f, local)
    return img.resize((W_px, size_px), Image.LANCZOS)


def can_write(s):
    """이 엔진으로 획순 드로잉 가능한지(모든 구성 자모의 획 정의 보유). 다음절 단어 지원."""
    if len(s) != 1:
        return all(can_write(c) for c in s)
    dec = decompose(s)
    if dec is None:
        return strokes_of(s) is not None
    return all((j == " ") or (strokes_of(j) is not None) for j in dec)


# ---------------- 검증 시트 ----------------
def _sheet():
    from PIL import ImageFont
    cream = (245, 245, 240, 255)
    cons = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")
    vows = list("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅛㅜㅠㅡㅣ")
    words = ["강", "책", "산", "옷", "물", "곰", "밥", "부엌", "꽃", "앞",
             "윽", "은", "읃", "을", "음", "읍", "응"]
    cell, steps = 148, 5
    rows = cons + vows + words
    sheet = Image.new("RGBA", (cell * (steps + 1), cell * len(rows)), cream)
    f = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 40)
    fs = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 20)
    d = ImageDraw.Draw(sheet)
    for r, ch in enumerate(rows):
        # 0열: 폰트 정답 글자(대조용)
        d.text((cell // 2 - 22, r * cell + cell // 2 - 30), ch, fill=(150, 150, 150), font=f)
        d.text((10, r * cell + 8), ("ok" if can_write(ch) else "NO"), fill=(30, 120, 30) if can_write(ch) else (200, 0, 0), font=fs)
        for s in range(1, steps + 1):
            prog = s / steps
            im = render_syllable(ch, cell - 24, progress=prog)
            sheet.alpha_composite(im, ((s) * cell + 12, r * cell + 12))
    out = os.path.join(ROOT, "scratch", "_hangeul_write_sheet.png")
    sheet.convert("RGB").save(out)
    print("write sheet ->", out, f"({len(rows)} rows)")


if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "scratch"), exist_ok=True)
    _sheet()
