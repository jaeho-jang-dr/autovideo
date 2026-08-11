#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
stickman_factory.py — 파라메트릭 스틱맨 포즈 생성기 (손그림 잉크 스타일).

SVG 에디터(stickman_svg_editor)의 12관절 모델을 Python/PIL 로 재현한다.
 - 포즈 = 12개 관절점(60x80 좌표계) + headRadius + lineWidth + 표정 + facing.
 - 사지 = 큐빅 베지어 `M start C start, mid, end` (에디터와 동일) 를 두꺼운 둥근
   잉크 스트로크(미세한 손그림 흔들림)로 스탬프 렌더.
 - 머리 = 빈 원(ring) + 표정(눈/입).
 - 출력 = 투명 배경 1024x1024 PNG (2x 슈퍼샘플 후 다운스케일).

레퍼런스: assets/graphics/stickman_standing.png 의 크림배경 검은 라인아트 스타일.
재사용: drjay-ed 24주 한글 커리큘럼 전체의 공용 스틱맨 라이브러리.
"""
import os
import sys
import math
import random

from PIL import Image, ImageDraw, ImageFilter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---- render constants -------------------------------------------------------
CANVAS = 1024
SS = 2                      # supersample factor
INK = (28, 28, 28, 255)     # near-black ink
S = 11.5                    # units(60x80) -> px scale
OX = (CANVAS - 60 * S) / 2  # ~167
OY = (CANVAS - 80 * S) / 2  # ~52

OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "graphics", "poses")


def to_px(p, scale=1.0):
    """unit (x,y) -> supersampled pixel coords."""
    return ((p[0] * S + OX) * scale, (p[1] * S + OY) * scale)


# ---- geometry ---------------------------------------------------------------
def cubic(p0, c1, c2, p3, n=64):
    """Cubic bezier sample (matches editor: M p0 C p0,mid,end => c1=p0, c2=mid)."""
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = (mt**3) * p0[0] + 3 * (mt**2) * t * c1[0] + 3 * mt * (t**2) * c2[0] + (t**3) * p3[0]
        y = (mt**3) * p0[1] + 3 * (mt**2) * t * c1[1] + 3 * mt * (t**2) * c2[1] + (t**3) * p3[1]
        pts.append((x, y))
    return pts


def stamp_stroke(draw, pts, width_px, rng, wobble=1.3, taper=False, fill=INK):
    """Stamp overlapping ink dots along a polyline for a round, organic stroke."""
    # densify
    dense = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        steps = max(1, int(seg / 1.5))
        for s in range(steps):
            t = s / steps
            dense.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    dense.append(pts[-1])
    n = len(dense)
    phase = rng.uniform(0, math.tau)
    freq = rng.uniform(1.4, 2.4)
    for i, (x, y) in enumerate(dense):
        u = i / max(1, n - 1)
        # perpendicular wobble (low-freq sine) for hand-drawn feel
        if i < n - 1:
            dx, dy = dense[i + 1][0] - x, dense[i + 1][1] - y
        else:
            dx, dy = x - dense[i - 1][0], y - dense[i - 1][1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        off = wobble * SS * math.sin(freq * math.tau * u + phase)
        cx, cy = x + nx * off, y + ny * off
        w = width_px
        if taper:
            w = width_px * (0.55 + 0.45 * math.sin(math.pi * u))  # thin at ends
        w *= rng.uniform(0.93, 1.07)
        r = w / 2
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)


def stamp_ring(draw, center, radius_px, width_px, rng, wobble=0.8):
    """Open circle head, drawn as an organic ring."""
    n = 120
    phase = rng.uniform(0, math.tau)
    for i in range(n + 1):
        a = i / n * math.tau
        rr = radius_px + wobble * SS * math.sin(3 * a + phase)
        x = center[0] + rr * math.cos(a)
        y = center[1] + rr * math.sin(a)
        r = width_px / 2 * rng.uniform(0.94, 1.06)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=INK)


# ---- face -------------------------------------------------------------------
def draw_face(draw, head_c, head_r_px, expr, facing, rng, col=INK):
    cx, cy = head_c
    # facing offset: shift features toward facing side
    fx = {"front": 0.0, "left": -0.32, "right": 0.32}.get(facing, 0.0)
    eye_dx = head_r_px * 0.34
    eye_y = cy - head_r_px * 0.12
    cxf = cx + head_r_px * fx
    eye_r = max(2.0 * SS, head_r_px * 0.085)

    def dot(x, y, r):
        draw.ellipse([x - r, y - r, x + r, y + r], fill=col)

    def arc_mouth(yc, w, h, smile):
        # smile>0 => U-shape happy (middle lower); smile<0 => frown (middle higher)
        seg = []
        for i in range(13):
            t = i / 12
            x = cxf - w + 2 * w * t
            y = yc + smile * h * math.sin(math.pi * t)
            seg.append((x, y))
        stamp_stroke(draw, seg, head_r_px * 0.13, rng, wobble=0.2, fill=col)

    if facing == "front":
        eyes = [(cxf - eye_dx, eye_y), (cxf + eye_dx, eye_y)]
    else:
        # side profile: two close eyes toward facing direction
        s = 1 if facing == "right" else -1
        eyes = [(cxf + s * eye_dx * 0.15, eye_y), (cxf + s * eye_dx * 0.62, eye_y)]

    if expr in ("tired", "sleepy"):
        for (ex, ey) in eyes:  # half-closed = short horizontal dashes
            seg = [(ex - eye_r * 1.4, ey), (ex + eye_r * 1.4, ey)]
            stamp_stroke(draw, seg, head_r_px * 0.11, rng, wobble=0.15, fill=col)
    else:
        for (ex, ey) in eyes:
            dot(ex, ey, eye_r)

    my = cy + head_r_px * 0.42
    mw = head_r_px * 0.30
    if expr == "happy":
        arc_mouth(my, mw, head_r_px * 0.32, +1)
    elif expr == "sad":
        arc_mouth(my + head_r_px * 0.08, mw, head_r_px * 0.30, -1)
    elif expr in ("talk", "surprised"):
        r = head_r_px * 0.16
        draw.ellipse([cxf - r, my - r, cxf + r, my + r], outline=col, width=int(head_r_px * 0.12))
    elif expr == "tired":
        arc_mouth(my + head_r_px * 0.05, mw * 0.8, head_r_px * 0.18, -1)
    elif expr.startswith("mouth_"):
        # ★모음 입 모양 (W1-2 어휘 강의용) — 개구도·입술 모양을 그대로 그린다.
        #   교재 기준: ㅏ=최대 세로 · ㅣ=옆으로 최대 · ㅗ=원형 · ㅜ=작고 뾰족 · ㅕ=중간
        #   (w, h) = 입의 가로/세로 반지름, head_r 대비 비율
        SHAPE = {
            "mouth_a":   (0.20, 0.36),   # 아 — 턱을 크게 떨어뜨림 (세로 최대)
            "mouth_i":   (0.40, 0.15),   # 이 — 옆으로 활짝. ★납작해도 '열린 입'으로 보이게 높이를 준다
            "mouth_o":   (0.25, 0.25),   # 오 — 동그란 원순
            "mouth_u":   (0.15, 0.17),   # 우 — 더 작고 오므림 (테 하나만, 굵게)
            "mouth_yeo": (0.19, 0.27),   # 여 — ㅣ→ㅓ 중간
        }
        w, h = SHAPE.get(expr, (0.22, 0.22))
        rw, rh = head_r_px * w, head_r_px * h
        lwm = head_r_px * (0.15 if expr == "mouth_u" else 0.11)   # 우는 굵게 = 오므린 느낌
        draw.ellipse([cxf - rw, my - rh, cxf + rw, my + rh], outline=col, width=int(lwm))
    else:  # neutral
        seg = [(cxf - mw * 0.7, my), (cxf + mw * 0.7, my)]
        stamp_stroke(draw, seg, head_r_px * 0.12, rng, wobble=0.15, fill=col)


# ---- pose rendering ---------------------------------------------------------
def render_pose(pose, seed=7):
    rng = random.Random(seed)
    img = Image.new("RGBA", (CANVAS * SS, CANVAS * SS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    P = {k: to_px(v, SS) for k, v in pose["pts"].items()}
    zolla = pose.get("style") == "zolla"                # 클래식 졸라맨: 꽉 찬 머리 + 얇고 곧은 사지
    lw = pose.get("lw", 1.15 if zolla else 1.55) * S * SS
    hr = pose.get("hr", 7.0 if zolla else 7.5) * S * SS
    wob = 0.5 if zolla else 1.3

    # limbs (cubic: start C start, mid, end) — draw legs/body first, arms on top
    # ★크게 꺾인 관절은 곡선으로 그리면 모서리를 잘라먹어 국수처럼 늘어진다.
    #   앉기·쪼그리기 같은 상호작용 포즈에서 무릎이 실제 다리에서 벗어나 보였다(2026-08-11).
    #   그래서 **꺾임이 크면 두 개의 직선**(관절을 실제로 지나가게)으로 그린다.
    def limb(root, joint, tip, bend_limit=125.0):
        v1 = (joint[0] - root[0], joint[1] - root[1])
        v2 = (tip[0] - joint[0], tip[1] - joint[1])
        n1 = math.hypot(*v1) or 1.0
        n2 = math.hypot(*v2) or 1.0
        cosang = (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)
        ang = math.degrees(math.acos(max(-1.0, min(1.0, cosang))))
        if ang > 180.0 - bend_limit:              # 방향이 크게 꺾였다
            return [[root, joint], [joint, tip]]  # 두 직선 — 관절을 정확히 지난다
        return [cubic(root, root, joint, tip)]

    body = cubic(P["chest"], P["chest"], P["body"], P["pelvis"])
    legL = limb(P["pelvis"], P["kneeLeft"], P["feetLeft"])
    legR = limb(P["pelvis"], P["kneeRight"], P["feetRight"])
    armL = limb(P["chest"], P["elbowLeft"], P["handLeft"])
    armR = limb(P["chest"], P["elbowRight"], P["handRight"])

    for path in [body] + legL + legR + armL + armR:
        stamp_stroke(draw, path, lw, rng, wobble=wob)
    # neck stub (chest up to head bottom)
    head_c = P["head"]
    neck_top = (head_c[0], head_c[1] + hr)
    stamp_stroke(draw, [P["chest"], neck_top], lw, rng, wobble=0.3)

    if pose.get("bun"):                                 # 머리묶음 먼저(머리 뒤에) — 졸라'걸' 정체성
        facing = pose.get("facing", "front")
        off = {"front": 0.0, "right": -0.5, "left": 0.5}.get(facing, 0.0)
        br = hr * 0.62
        bx = head_c[0] + off * hr * 1.05
        by = head_c[1] - hr * 0.72
        bcol = pose.get("bun_color", INK)
        draw.ellipse([bx - br, by - br, bx + br, by + br], fill=bcol)
        draw.ellipse([bx - br, by - br, bx + br, by + br], outline=INK, width=int(lw * 0.7))
    if zolla:                                           # 꽉 찬 검은 머리(졸라맨)
        draw.ellipse([head_c[0] - hr, head_c[1] - hr, head_c[0] + hr, head_c[1] + hr], fill=INK)
    else:                                               # 외곽선 머리 + (옵션) 흰 얼굴 채우기(졸라걸)
        hf = pose.get("head_fill")
        if hf:
            draw.ellipse([head_c[0] - hr, head_c[1] - hr, head_c[0] + hr, head_c[1] + hr], fill=hf)
        stamp_ring(draw, head_c, hr, lw, rng)
    # feet ticks
    for foot, knee in [(P["feetLeft"], P["kneeLeft"]), (P["feetRight"], P["kneeRight"])]:
        ang = math.atan2(foot[1] - knee[1], foot[0] - knee[0])
        fx = foot[0] + math.cos(ang) * 0 + (1 if foot[0] >= P["pelvis"][0] else -1) * 9 * SS
        stamp_stroke(draw, [foot, (fx, foot[1] + 1 * SS)], lw * 0.9, rng, wobble=0.2)

    draw_face(draw, head_c, hr, pose.get("expr", "neutral"), pose.get("facing", "front"), rng,
              col=(250, 250, 248, 255) if zolla else INK)
    if pose.get("pencil"):
        draw_pencil(draw, P, lw, rng, pose["pencil"])
    if pose.get("card"):
        draw_card(draw, P, lw, rng, pose["card"])

    img = img.resize((CANVAS, CANVAS), Image.LANCZOS)
    if pose.get("glow"):
        img = add_line_glow(img, pose.get("glow"))
    return img


# ---- ★라인 발광(네온) — 스틱맨이 심심해 보이지 않게 (사장님 지시 2026-07-28) ----
GLOW_PRESET = {
    # 이름: (RGB, 바깥 번짐 반경, 안쪽 코어 반경, 세기)
    "cyan":   ((120, 230, 255), 26, 8, 1.00),
    "warm":   ((255, 208, 120), 26, 8, 0.95),
    "mint":   ((140, 255, 200), 24, 7, 0.95),
    "violet": ((190, 150, 255), 26, 8, 1.00),
    "white":  ((255, 255, 255), 22, 7, 0.85),
}


def add_line_glow(img, spec="cyan"):
    """선 주위에 빛을 입힌다. 알파를 두 번(넓게/좁게) 흐려 **바깥 번짐 + 안쪽 코어**를 겹치고,
    원본 잉크선을 맨 위에 다시 얹어 형태는 그대로 유지한다.
    spec = 프리셋 이름 또는 (r,g,b) 또는 {"color":(r,g,b),"blur":26,"core":8,"gain":1.0}"""
    if isinstance(spec, str):
        rgb, blur, core, gain = GLOW_PRESET.get(spec, GLOW_PRESET["cyan"])
    elif isinstance(spec, dict):
        rgb = tuple(spec.get("color", (120, 230, 255)))
        blur, core, gain = spec.get("blur", 26), spec.get("core", 8), spec.get("gain", 1.0)
    else:
        rgb, blur, core, gain = tuple(spec), 26, 8, 1.0

    a = img.split()[-1]
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for radius, weight in ((blur, 0.55 * gain), (core, 0.85 * gain)):
        halo = a.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: int(min(255, v * weight)))
        layer = Image.new("RGBA", img.size, rgb + (0,))
        layer.putalpha(halo)
        out = Image.alpha_composite(out, layer)
    return Image.alpha_composite(out, img)          # 원본 선을 맨 위에 — 형태 보존


# ---- 졸라걸(주황머리) 통통 손그림 렌더 — 외곽선 튜브 팔다리 + 손·발 ----------
GIRL_SKIN = (252, 250, 247, 255)   # 흰 얼굴/몸통 속
GIRL_HAIR = (232, 126, 58, 255)    # 주황 머리

def render_girl(pose, seed=7):
    """render_pose와 같은 관절 좌표를 쓰되, 원본 졸라걸 룩(외곽선 튜브 팔다리+손발+주황머리묶음)."""
    rng = random.Random(seed)
    img = Image.new("RGBA", (CANVAS * SS, CANVAS * SS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    P = {k: to_px(v, SS) for k, v in pose["pts"].items()}
    facing = pose.get("facing", "front")
    LWO = 2.15 * S * SS            # 튜브 외곽 두께(검은 외곽선)
    LWI = 1.05 * S * SS            # 튜브 속(흰)
    hr = pose.get("hr", 7.2) * S * SS

    body = cubic(P["chest"], P["chest"], P["body"], P["pelvis"])
    legL = cubic(P["pelvis"], P["pelvis"], P["kneeLeft"], P["feetLeft"])
    legR = cubic(P["pelvis"], P["pelvis"], P["kneeRight"], P["feetRight"])
    armL = cubic(P["chest"], P["chest"], P["elbowLeft"], P["handLeft"])
    armR = cubic(P["chest"], P["chest"], P["elbowRight"], P["handRight"])
    limbs = [body, legL, legR, armL, armR]

    def poly(path, w, col):
        xy = [(p[0], p[1]) for p in path]
        draw.line(xy, fill=col, width=int(w), joint="curve")
        r = w / 2
        for p in (xy[0], xy[-1]):
            draw.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=col)

    for path in limbs:                       # 1) 검은 외곽선 전부
        poly(path, LWO, INK)
    for path in limbs:                       # 2) 흰 속 전부(튜브 완성)
        poly(path, LWI, GIRL_SKIN)

    # 손(벙어리장갑) / 발(신발)
    for hand in (P["handLeft"], P["handRight"]):
        hrd = 2.3 * S * SS
        draw.ellipse([hand[0]-hrd, hand[1]-hrd, hand[0]+hrd, hand[1]+hrd], fill=GIRL_SKIN, outline=INK, width=int(LWO*0.35))
    for foot, knee in [(P["feetLeft"], P["kneeLeft"]), (P["feetRight"], P["kneeRight"])]:
        d = 1 if foot[0] >= P["pelvis"][0] else -1
        fw, fh = 3.6 * S * SS, 2.0 * S * SS
        cx = foot[0] + d * fw * 0.4
        draw.ellipse([cx-fw, foot[1]-fh*0.4, cx+fw, foot[1]+fh], fill=GIRL_SKIN, outline=INK, width=int(LWO*0.35))

    # 머리묶음(주황) → 머리(흰+외곽선) → 얼굴
    head_c = P["head"]
    off = {"front": 0.0, "right": -0.5, "left": 0.5}.get(facing, 0.0)
    br = hr * 0.66
    bx = head_c[0] + off * hr * 1.05
    by = head_c[1] - hr * 0.70
    draw.ellipse([bx-br, by-br, bx+br, by+br], fill=GIRL_HAIR, outline=INK, width=int(LWO*0.4))
    draw.ellipse([head_c[0]-hr, head_c[1]-hr, head_c[0]+hr, head_c[1]+hr], fill=GIRL_SKIN, outline=INK, width=int(LWO*0.55))
    draw_face(draw, head_c, hr, pose.get("expr", "neutral"), facing, rng, col=INK)
    if pose.get("pencil"):
        draw_pencil(draw, P, LWI, rng, pose["pencil"])

    return img.resize((CANVAS, CANVAS), Image.LANCZOS)


# ---- pose library -----------------------------------------------------------
def base_pts():
    return {
        "head": (30, 11), "chest": (30, 20), "body": (30, 30), "pelvis": (30, 41),
        "elbowLeft": (25, 29), "handLeft": (23, 39),
        "elbowRight": (35, 29), "handRight": (37, 39),
        "kneeLeft": (27.5, 52), "feetLeft": (26, 66),
        "kneeRight": (32.5, 52), "feetRight": (34, 66),
    }


def P(**over):
    pts = base_pts()
    pts.update(over)
    return pts


# ---- colored pencil (held in hand) ------------------------------------------
PENCIL_COLOR = (228, 96, 58, 255)    # 빨강-주황 컬러 연필
PENCIL_WOOD = (226, 198, 152, 255)


def draw_pencil(draw, P, lw, rng, spec):
    """캐릭터 손에 든 컬러 연필 — elbow→hand 방향으로 뻗어 나간다."""
    side = spec.get("hand", "right")
    hand = P["handRight"] if side == "right" else P["handLeft"]
    elbow = P["elbowRight"] if side == "right" else P["elbowLeft"]
    dx, dy = hand[0] - elbow[0], hand[1] - elbow[1]
    L = math.hypot(dx, dy) or 1.0
    ux, uy = dx / L, dy / L
    length = spec.get("len", 13) * S * SS
    base = (hand[0] - ux * 1.4 * S * SS, hand[1] - uy * 1.4 * S * SS)
    tip = (hand[0] + ux * length, hand[1] + uy * length)

    def lerp(a, b, t):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

    p80, p92 = lerp(base, tip, 0.80), lerp(base, tip, 0.92)
    pw = lw * 0.95
    stamp_stroke(draw, [base, tip], pw + 3 * SS, rng, wobble=0.08)                  # ink outline
    stamp_stroke(draw, [base, p80], pw, rng, wobble=0.08, fill=PENCIL_COLOR)        # colored body
    stamp_stroke(draw, [p80, p92], pw * 0.82, rng, wobble=0.05, fill=PENCIL_WOOD)   # wood cone
    stamp_stroke(draw, [p92, tip], pw * 0.5, rng, wobble=0.04, taper=True)          # graphite point


# ---- 삽화 카드 (손에 든 사각 카드) ------------------------------------------
# ★W1-2 어휘 강의의 핵심 소품 — 그림을 글자 옆에 붙이는 '삽화 매칭' 활동에 쓴다.
CARD_FILL = (252, 250, 244, 255)     # 크림색 카드 바탕


def draw_card(draw, P, lw, rng, spec):
    """두 손 사이에 든 정사각 카드. spec:
       {"w":12, "h":12, "fan":1, "tilt":0}  — fan>1 이면 부채처럼 여러 장."""
    hl, hr_ = P["handLeft"], P["handRight"]
    cx = (hl[0] + hr_[0]) / 2
    cy = (hl[1] + hr_[1]) / 2
    w = spec.get("w", 12) * S * SS / 2
    h = spec.get("h", 12) * S * SS / 2
    fan = int(spec.get("fan", 1))
    spread = float(spec.get("spread", 1.5))     # ★부채 벌림 — 1.5=기본, 크게 줄수록 활짝
    tilt = float(spec.get("tilt", 0.0))         # ★바깥장 기울기(라디안)
    outline_w = int(lw * 0.75)

    # 부채는 뒤장부터 그려 앞장이 위로 오게 한다
    for i in range(fan - 1, -1, -1):
        t = 0 if fan == 1 else (i / (fan - 1) - 0.5)      # -0.5 … +0.5
        ox = t * w * spread
        oy = -abs(t) * h * 0.35 * min(1.0, spread / 1.5)
        if tilt and t:
            # 바깥장을 바깥으로 기울인다 — 회전한 사각형을 폴리곤으로 그린다
            ang = tilt * (t * 2)
            ca, sa = math.cos(ang), math.sin(ang)
            pts = []
            for dx, dy in ((-w, -h), (w, -h), (w, h), (-w, h)):
                pts.append((cx + ox + dx * ca - dy * sa, cy + oy + dx * sa + dy * ca))
            draw.polygon(pts, fill=CARD_FILL, outline=INK)
            for k in range(4):
                stamp_stroke(draw, [pts[k], pts[(k + 1) % 4]], outline_w, rng, wobble=0.1)
            continue
        box = [cx - w + ox, cy - h + oy, cx + w + ox, cy + h + oy]
        draw.rectangle(box, fill=CARD_FILL, outline=INK, width=outline_w)

    # 앞장 안쪽에 그림 자리 표시(빈 액자) — 실제 삽화는 합성에서 얹는다
    inset = w * 0.22
    draw.rectangle([cx - w + inset, cy - h + inset, cx + w - inset, cy + h - inset],
                   outline=INK, width=max(1, int(outline_w * 0.55)))

    # ★손이 카드 뒤로 숨지 않게 — 카드 양옆에 손끝을 다시 얹는다(들고 있는 게 보여야 한다)
    for hx, hy in ((cx - w, cy), (cx + w, cy)):
        stamp_stroke(draw, [(hx - w * 0.16, hy - h * 0.18), (hx + w * 0.16, hy + h * 0.18)],
                     lw * 0.95, rng, wobble=0.15)


# ---- full pose registry -----------------------------------------------------
# Each: pts, expr, facing, and bilingual description (for content.db assets).
POSES = {
    # --- Week 3: 졸라맨(꽉 찬 검은 머리+흰 표정) 다이나믹 설명 포즈 ---
    "z_wave":     dict(style="zolla", pts=P(elbowRight=(37, 15), handRight=(41, 5)), expr="happy",
                       ko="졸라맨 손 흔들며 인사", en="Zolla waving hello"),
    "z_point_r":  dict(style="zolla", pts=P(elbowRight=(38, 20), handRight=(48, 17)), expr="happy",
                       ko="졸라맨 오른쪽 힘차게 가리키며 설명", en="Zolla pointing right"),
    "z_point_l":  dict(style="zolla", pts=P(elbowLeft=(22, 20), handLeft=(12, 17)), expr="happy",
                       ko="졸라맨 왼쪽 가리키며 설명", en="Zolla pointing left"),
    "z_present":  dict(style="zolla", pts=P(elbowLeft=(24, 26), handLeft=(17, 31), elbowRight=(36, 26), handRight=(43, 31)),
                       expr="happy", ko="졸라맨 두 팔 벌려 발표", en="Zolla presenting, arms open"),
    "z_explain":  dict(style="zolla", pts=P(elbowRight=(35, 16), handRight=(38, 7), elbowLeft=(26, 28), handLeft=(28, 36)),
                       expr="talk", ko="졸라맨 한 손 들어 강조하며 말함", en="Zolla explaining, hand up"),
    "z_tissue":   dict(style="zolla", pts=P(head=(30, 11), elbowRight=(34, 17), handRight=(32.5, 12)),
                       expr="talk", ko="졸라맨 손을 입 앞에 (휴지 실험)", en="Zolla hand at mouth (tissue test)"),
    "z_think":    dict(style="zolla", pts=P(head=(31, 11), elbowRight=(34, 28), handRight=(31.5, 18.5)),
                       expr="neutral", facing="right", ko="졸라맨 턱에 손, 생각/듣기", en="Zolla thinking/listening"),
    "z_cheer":    dict(style="zolla", pts=P(elbowLeft=(26, 13), handLeft=(23, 4), elbowRight=(34, 13), handRight=(37, 4)),
                       expr="happy", ko="졸라맨 두 팔 들고 환호", en="Zolla cheering"),
    "z_thumb":    dict(style="zolla", pts=P(elbowRight=(35, 24), handRight=(38, 17)), expr="happy",
                       ko="졸라맨 엄지 척", en="Zolla thumbs up"),
    "z_strong":   dict(style="zolla", pts=P(head=(30, 12), chest=(30, 21), elbowLeft=(25, 27), handLeft=(27.5, 23),
                                            elbowRight=(35, 27), handRight=(32.5, 23)),
                       expr="talk", ko="졸라맨 주먹 불끈, 힘주기(된소리)", en="Zolla tensing fists (tense sound)"),
    "z_lean":     dict(style="zolla", pts=P(head=(28, 12), chest=(29, 21), body=(30, 30),
                                            elbowLeft=(23, 24), handLeft=(16, 26), elbowRight=(35, 28), handRight=(33, 36)),
                       expr="happy", ko="졸라맨 몸 기울여 설명", en="Zolla leaning to explain"),
    "z_clap":     dict(style="zolla", pts=P(elbowLeft=(26, 27), handLeft=(29.5, 30), elbowRight=(34, 27), handRight=(30.5, 30)),
                       expr="happy", ko="졸라맨 박수", en="Zolla clapping"),
    "z_sit_think": dict(style="zolla", pts=P(head=(31, 13), chest=(30, 22), body=(29.5, 31), pelvis=(28, 42),
                                             kneeLeft=(33, 43), feetLeft=(34, 56), kneeRight=(34, 42), feetRight=(35, 55),
                                             elbowLeft=(31, 30), handLeft=(34, 40), elbowRight=(33, 28), handRight=(31, 20)),
                        expr="neutral", facing="right", ko="졸라맨 앉아서 턱 괴고 생각", en="Zolla sitting, thinking"),
    "z_jump":     dict(style="zolla", pts=P(head=(30, 12), chest=(30, 21), body=(30, 30), pelvis=(30, 40),
                                            elbowLeft=(25, 13), handLeft=(21, 4), elbowRight=(35, 13), handRight=(39, 4),
                                            kneeLeft=(26, 48), feetLeft=(24, 56), kneeRight=(34, 48), feetRight=(36, 56)),
                       expr="happy", ko="졸라맨 번쩍 점프(신남)", en="Zolla jumping up"),
    # --- 졸라맨 W6+ 신규(왼손 가리키기 전용 + 왼쪽 앉기 + 남성 시그니처) ---
    "z_point_l2": dict(style="zolla", pts=P(elbowLeft=(24, 22), handLeft=(15, 27)), expr="happy",
                       ko="졸라맨 왼손으로 (콘텐츠쪽) 가리키며 설명", en="Zolla pointing with left hand"),
    "z_point_l_up": dict(style="zolla", pts=P(elbowLeft=(24, 20), handLeft=(16, 14)), expr="happy",
                       ko="졸라맨 왼손 비스듬히 위로 가리키기", en="Zolla left hand pointing up-left"),
    "z_sit_left": dict(style="zolla", pts=P(head=(29, 13), chest=(30, 22), body=(30.5, 31), pelvis=(32, 42),
                                            kneeLeft=(27, 43), feetLeft=(26, 56), kneeRight=(26, 42), feetRight=(25, 55),
                                            elbowLeft=(29, 30), handLeft=(26, 40), elbowRight=(29, 28), handRight=(31, 20)),
                        expr="neutral", facing="left", ko="졸라맨 왼쪽으로 비스듬히 앉아 생각/설명", en="Zolla sitting, angled left"),
    "z_flex":     dict(style="zolla", pts=P(head=(30, 12), chest=(30, 21), elbowLeft=(22, 21), handLeft=(25, 14),
                                            elbowRight=(38, 21), handRight=(35, 14)),
                       expr="happy", ko="졸라맨 알통 자랑(힘!) — 남성 시그니처", en="Zolla flexing biceps (male signature)"),
    "z_hero":     dict(style="zolla", pts=P(head=(30, 12), chest=(30, 21), elbowLeft=(23, 28), handLeft=(26.5, 40),
                                            elbowRight=(37, 28), handRight=(33.5, 40)),
                       expr="happy", ko="졸라맨 허리에 손, 당당한 히어로 포즈", en="Zolla hands on hips, hero stance"),
    # --- Week 2: 컬러 연필을 든 캐릭터 ---
    "pencil_point":   dict(pts=P(elbowRight=(37, 21), handRight=(46, 20)), expr="happy",
                           pencil={"len": 13}, ko="컬러 연필로 오른쪽을 가리키며 설명", en="Pointing with a colored pencil"),
    "pencil_wave":    dict(pts=P(elbowRight=(37, 15), handRight=(41, 6)), expr="happy",
                           pencil={"len": 13}, ko="컬러 연필 들고 인사", en="Waving with a colored pencil"),
    "pencil_present": dict(pts=P(elbowLeft=(24, 26), handLeft=(18, 32), elbowRight=(36, 24), handRight=(43, 27)),
                           expr="happy", pencil={"len": 13}, ko="컬러 연필 들고 두 팔 벌려 설명", en="Presenting with a colored pencil"),
    "pencil_write":   dict(pts=P(head=(31, 12), chest=(31, 21), body=(31, 30), pelvis=(30, 41),
                                 elbowRight=(35, 30), handRight=(40, 40), elbowLeft=(28, 30), handLeft=(26, 38)),
                           expr="neutral", facing="right", pencil={"len": 11}, ko="컬러 연필로 글씨 쓰는 자세", en="Writing with a colored pencil"),
    # --- general / daily-activity (reusable across the 24-week curriculum) ---
    "standing":      dict(pts=P(), expr="neutral", ko="가만히 서 있는 기본 자세", en="Standing neutral"),
    "standing_happy":dict(pts=P(), expr="happy", ko="웃으며 서 있는 자세", en="Standing, smiling"),
    "greeting_wave": dict(pts=P(elbowRight=(37, 15), handRight=(41, 6)), expr="happy",
                          ko="손 흔들며 인사", en="Waving hello"),
    "arms_open":     dict(pts=P(elbowLeft=(24, 26), handLeft=(18, 32), elbowRight=(36, 26), handRight=(42, 32)),
                          expr="happy", ko="두 팔 벌려 설명/환영", en="Arms open, explaining"),
    "cheer":         dict(pts=P(elbowLeft=(26, 13), handLeft=(23, 4), elbowRight=(34, 13), handRight=(37, 4)),
                          expr="happy", ko="두 팔 들고 환호", en="Cheering, both arms up"),
    "clap":          dict(pts=P(elbowLeft=(26, 27), handLeft=(29.5, 30), elbowRight=(34, 27), handRight=(30.5, 30)),
                          expr="happy", ko="박수", en="Clapping"),
    "pointing_right":dict(pts=P(elbowRight=(37, 21), handRight=(46, 20)), expr="happy",
                          ko="오른쪽을 가리키며 설명", en="Pointing right (presenting)"),
    "pointing_left": dict(pts=P(elbowLeft=(23, 21), handLeft=(14, 20)), expr="happy",
                          ko="왼쪽을 가리키며 설명", en="Pointing left (presenting)"),
    "pointing_up":   dict(pts=P(elbowRight=(34, 14), handRight=(36, 4)), expr="neutral",
                          ko="위(하늘)를 가리킴", en="Pointing up (heaven)"),
    "pointing_down": dict(pts=P(elbowRight=(35, 33), handRight=(38, 45)), expr="neutral",
                          ko="아래(땅)를 가리킴", en="Pointing down (earth)"),
    "thinking":      dict(pts=P(head=(31, 11), elbowRight=(38, 27), handRight=(33, 18)),
                          expr="neutral", facing="right", ko="턱에 손(팔꿈치 바깥), 양팔 보이는 생각 자세", en="Thinking, hand on chin (both arms visible)"),
    "shrug":         dict(pts=P(elbowLeft=(24, 25), handLeft=(20, 26.5), elbowRight=(36, 25), handRight=(40, 26.5)),
                          expr="surprised", ko="어깨 으쓱, 갸우뚱(모름)", en="Shrug, confused"),
    "thumbs_up":     dict(pts=P(elbowRight=(35, 24), handRight=(38, 17.5)), expr="happy",
                          ko="엄지 척", en="Thumbs up"),
    "hands_on_hips": dict(pts=P(elbowLeft=(23, 28), handLeft=(26.5, 40), elbowRight=(37, 28), handRight=(33.5, 40)),
                          expr="happy", ko="허리에 손, 당당한 자세", en="Hands on hips, confident"),
    "raising_hand":  dict(pts=P(elbowRight=(33, 12), handRight=(33, 2.5)), expr="happy",
                          ko="손 번쩍 들기(질문/참여)", en="Raising hand"),
    "walking":       dict(pts=P(kneeLeft=(26, 52), feetLeft=(22, 65), kneeRight=(34, 52), feetRight=(38, 65),
                                elbowLeft=(26, 30), handLeft=(28, 38), elbowRight=(34, 29), handRight=(32, 37)),
                          expr="neutral", ko="걷는 자세", en="Walking"),
    "running":       dict(pts=P(head=(33, 12), chest=(32, 21), body=(31, 30), pelvis=(29, 40),
                                kneeLeft=(33, 49), feetLeft=(41, 55), kneeRight=(25, 50), feetRight=(20, 61),
                                elbowLeft=(36, 26), handLeft=(40, 23), elbowRight=(27, 30), handRight=(24, 36)),
                          expr="happy", facing="right", ko="달리는 자세", en="Running"),
    "jumping":       dict(pts=P(head=(30, 12), chest=(30, 21), body=(30, 30), pelvis=(30, 40),
                                elbowLeft=(25, 13), handLeft=(21, 5), elbowRight=(35, 13), handRight=(39, 5),
                                kneeLeft=(26, 48), feetLeft=(24, 56), kneeRight=(34, 48), feetRight=(36, 56)),
                          expr="happy", ko="점프(신남)", en="Jumping with joy"),
    "sitting":       dict(pts=P(head=(31, 13), chest=(30, 22), body=(29.5, 31), pelvis=(28, 42),
                                kneeLeft=(33, 43), feetLeft=(34, 56), kneeRight=(34, 42), feetRight=(35, 55),
                                elbowLeft=(31, 30), handLeft=(34, 40), elbowRight=(33, 30), handRight=(36, 40)),
                          expr="neutral", facing="right", ko="의자에 앉은 자세(옆모습)", en="Sitting on a chair (side)"),
    "tired_slump":   dict(pts=P(head=(30, 17), chest=(30, 24), body=(30, 32), pelvis=(30, 42),
                                elbowLeft=(26, 31), handLeft=(28, 37), elbowRight=(34, 31), handRight=(32, 37)),
                          expr="tired", ko="책상에 엎드린 듯 지친 자세", en="Tired, slumped at desk"),
    "holding_phone": dict(pts=P(head=(30, 12), elbowLeft=(27.5, 26), handLeft=(30, 28),
                                elbowRight=(32.5, 26), handRight=(31, 28)), expr="happy",
                          ko="휴대폰을 들고 보는 자세", en="Holding/looking at phone"),
    "presenting":    dict(pts=P(head=(31, 11), elbowRight=(36, 21), handRight=(45, 18)), expr="happy",
                          facing="right", ko="칠판/화면 앞에서 발표", en="Presenting at a board"),
    "writing":       dict(pts=P(head=(31, 12), chest=(31, 21), body=(31, 30), pelvis=(30, 41),
                                elbowRight=(35, 30), handRight=(40, 40), elbowLeft=(28, 30), handLeft=(26, 38)),
                          expr="neutral", facing="right", ko="책상에서 글씨 쓰는 자세", en="Writing at a desk"),
    "reading":       dict(pts=P(head=(30, 13), elbowLeft=(27, 27), handLeft=(29, 31),
                                elbowRight=(33, 27), handRight=(31, 31)), expr="neutral",
                          ko="책을 들고 읽는 자세", en="Reading a book"),
    "bowing":        dict(pts=P(head=(26, 22), chest=(28, 26), body=(29, 33), pelvis=(30, 41),
                                elbowLeft=(26, 31), handLeft=(24, 38), elbowRight=(31, 31), handRight=(31, 38)),
                          expr="happy", facing="right", ko="고개 숙여 인사(절)", en="Bowing politely"),
    "listening":     dict(pts=P(elbowRight=(35, 18), handRight=(34, 11.5)), expr="happy",
                          ko="귀에 손, 듣는 자세(헤드폰)", en="Listening, hand to ear"),

    # ── W1-2 「모음으로 만드는 첫 단어」 전용 8포즈 ────────────────────────────
    # ★몸은 base 그대로 두고 **얼굴(입 모양)만** 바꾼다 — 5종이 한 사람으로 보여야 한다.
    "w1d2_mouth_a":   dict(pts=P(), expr="mouth_a",
                           ko="입 모양 '아' — 턱을 세로로 최대 개방",
                           en="Mouth shape 'a' — jaw dropped wide"),
    "w1d2_mouth_i":   dict(pts=P(), expr="mouth_i",
                           ko="입 모양 '이' — 입술을 옆으로 활짝",
                           en="Mouth shape 'i' — lips pulled wide"),
    "w1d2_mouth_o":   dict(pts=P(), expr="mouth_o",
                           ko="입 모양 '오' — 입술을 동그랗게",
                           en="Mouth shape 'o' — lips rounded"),
    "w1d2_mouth_u":   dict(pts=P(), expr="mouth_u",
                           ko="입 모양 '우' — 입술을 작게 앞으로",
                           en="Mouth shape 'u' — lips small and forward"),
    "w1d2_mouth_yeo": dict(pts=P(), expr="mouth_yeo",
                           ko="입 모양 '여' — ㅣ에서 ㅓ로 넘어가는 중간",
                           en="Mouth shape 'yeo' — mid glide from i to eo"),
    # ★카드는 **두 손을 가슴 높이로 모아** 그 사이에 든다
    # ★카드는 **머리를 가리지 않게** 가슴 아래(y≈28)에서 든다. 머리 아래끝이 y≈18.5 다.
    "w1d2_card_hold": dict(pts=P(elbowLeft=(24.5, 27), handLeft=(23.0, 28),
                                 elbowRight=(35.5, 27), handRight=(37.0, 28)),
                           expr="happy", card=dict(w=14, h=13, fan=1),
                           ko="삽화 카드를 가슴 앞에 들어 보임",
                           en="Holding an illustration card in front of the chest"),
    "w1d2_card_fan":  dict(pts=P(elbowLeft=(24, 27), handLeft=(22.0, 28),
                                 elbowRight=(36, 27), handRight=(38.0, 28)),
                           expr="happy", card=dict(w=12, h=11, fan=3),
                           ko="삽화 카드 세 장을 부채처럼 펼쳐 보임",
                           en="Fanning out three illustration cards"),
    # ── 상호작용 포즈 — 배경의 어느 부분에 가서 쓴다 (인터랙트랑) ──────────────
    # ★엉덩이(pelvis)가 앵커에 오도록 배치한다. 무릎을 앞으로 접고 발은 바닥에.
    # ★사장님 지시(2026-08-11)
    #   ① **고관절 90도 · 무릎 90도** — 허벅지 수평, 정강이 수직
    #   ② **정면에서 45도 튼 3/4 뷰**가 제일 보기 좋다 — 얼굴도 보이고 다리 접힘도 보인다
    #   3/4 라서 허벅지는 앞으로 나오며 **짧아 보이게**(원근 단축) 그린다: 11 → 약 7단위
    #   ③ **화면 중앙을 향해 튼다** — 왼편에 있으면 오른쪽으로, 오른편에 있으면 왼쪽으로.
    #      그래서 좌우 두 벌을 둔다(`_r` = 오른쪽을 향해 튼 것, 왼편에 놓을 때 쓴다).
    "w1d2_sit_bench_r": dict(pts=P(head=(28.5, 13), chest=(28.5, 22), body=(28.7, 31),
                                   pelvis=(29, 41),
                                   kneeLeft=(35.5, 42), feetLeft=(35.5, 56),
                                   kneeRight=(33, 43), feetRight=(33, 57),
                                   elbowLeft=(25.5, 30), handLeft=(27, 39.5),
                                   elbowRight=(32, 30), handRight=(33, 39.5)),
                             expr="happy", facing="right",
                             ko="벤치에 걸터앉기 — 오른쪽으로 45도 튼 3/4 뷰(왼편 배치용)",
                             en="Perched on a bench, turned right 45°, for left-side placement"),
    "w1d2_sit_bench_l": dict(pts=P(head=(31.5, 13), chest=(31.5, 22), body=(31.3, 31),
                                   pelvis=(31, 41),
                                   kneeLeft=(27, 43), feetLeft=(27, 57),
                                   kneeRight=(24.5, 42), feetRight=(24.5, 56),
                                   elbowLeft=(28, 30), handLeft=(27, 39.5),
                                   elbowRight=(34.5, 30), handRight=(33, 39.5)),
                             expr="happy", facing="left",
                             ko="벤치에 걸터앉기 — 왼쪽으로 45도 튼 3/4 뷰(오른편 배치용)",
                             en="Perched on a bench, turned left 45°, for right-side placement"),
    # ★난간 잡기 — **손(handRight)** 이 앵커에 온다. 팔은 앞으로 뻗고 몸은 3/4.
    "w1d2_grab_rail_r": dict(pts=P(head=(28, 11.5), chest=(28, 20), body=(28.5, 30),
                                   pelvis=(29, 41),
                                   elbowRight=(34, 25), handRight=(40, 27),
                                   elbowLeft=(25, 29), handLeft=(24, 39),
                                   kneeLeft=(27, 52), feetLeft=(26, 66),
                                   kneeRight=(31.5, 52), feetRight=(33, 66)),
                             expr="happy", facing="right",
                             ko="난간을 오른손으로 잡는 자세(오른쪽을 향해)",
                             en="Grabbing a railing with the right hand, facing right"),
    "w1d2_grab_rail_l": dict(pts=P(head=(32, 11.5), chest=(32, 20), body=(31.5, 30),
                                   pelvis=(31, 41),
                                   elbowLeft=(26, 25), handLeft=(20, 27),
                                   elbowRight=(35, 29), handRight=(36, 39),
                                   kneeLeft=(28.5, 52), feetLeft=(27, 66),
                                   kneeRight=(33, 52), feetRight=(34, 66)),
                             expr="happy", facing="left",
                             ko="난간을 왼손으로 잡는 자세(왼쪽을 향해)",
                             en="Grabbing a railing with the left hand, facing left"),
    # ★땅 짚고 살피기 — 쪼그려 앉아 한 손은 땅(handRight), 다른 손은 무릎.
    #   고관절·무릎을 깊게 접는다. 손이 앵커에 온다.
    # ★쪼그려 앉기 — 엉덩이가 **발뒤꿈치 가까이**(y58) 내려가고 무릎이 **크게 올라온다**(y46).
    #   허벅지는 뒤로 접히고 정강이는 앞으로 세워진다. 발은 바닥(y66) 그대로.
    #   상체는 앞으로 살짝 숙이고, 오른손이 **바닥(y66)** 을 짚는다 — 여기가 앵커.
    # ★쪼그려 앉기 — **길이를 지켜서 접는다**(서기: 허벅지 11 · 정강이 14 · 몸통 21).
    #   발은 바닥 y66 → 정강이를 앞으로 세워 무릎 y53 → 허벅지를 뒤로 접어 엉덩이 y59.
    #   무릎이 엉덩이보다 **위**에 오는 것이 쪼그림의 핵심. 상체는 앞으로 살짝 숙인다.
    #   오른손이 **바닥 y66** 을 짚는다 — 여기가 앵커.
    # ★사장님 지시(2026-08-11): **엉덩이가 땅에 닿는다.**
    #   엉덩이 y66(바닥) · 무릎을 세워 앞으로 · 발은 바닥. 다리를 벌려 겹치지 않게 한다.
    "w1d2_crouch_ground_r": dict(pts=P(head=(28, 37), chest=(28.5, 46), body=(29, 56),
                                       pelvis=(29.5, 66),
                                       kneeLeft=(37, 55), feetLeft=(36, 66),
                                       kneeRight=(33.5, 58), feetRight=(33, 66),
                                       elbowRight=(34, 55), handRight=(39, 66),
                                       elbowLeft=(26, 52), handLeft=(31, 60)),
                                 expr="happy", facing="right",
                                 ko="땅에 주저앉아(엉덩이가 바닥) 오른손으로 바닥을 짚고 살피는 자세",
                                 en="Sitting on the ground, right hand touching the ground"),
    # ★난간에 **바짝 붙어 등을 기대고** 두 팔을 난간 위에 올린다(2026-08-11 재작업).
    #   ①몸통을 뒤로 살짝 눕혀 등이 난간에 닿는 느낌 ②두 팔을 다 난간 위로 벌려 올린다
    #   ③다리는 앞으로 내밀어 발이 몸보다 앞에 — 기댄 사람의 무게중심
    "w1d2_lean_rail_r": dict(pts=P(head=(27, 12), chest=(28, 21), body=(29.5, 30),
                                   pelvis=(31, 40),
                                   elbowRight=(33, 22), handRight=(38, 19.5),
                                   elbowLeft=(24, 23), handLeft=(20, 20.5),
                                   kneeLeft=(30, 52), feetLeft=(28, 66),
                                   kneeRight=(34, 51), feetRight=(36, 66)),
                             expr="happy", facing="right",
                             ko="난간에 등을 기대고 두 팔을 난간 위에 올린 자세",
                             en="Leaning back against a railing, both arms resting on it"),
    # ★벤치 **뒤에 서서 두 팔을 등받이에 올린다.** 몸 아랫부분은 벤치에 가려진다.
    "w1d2_stand_behind_bench": dict(pts=P(head=(30, 11), chest=(30, 20), body=(30, 30),
                                          pelvis=(30, 41),
                                          elbowLeft=(25, 24), handLeft=(21, 26),
                                          elbowRight=(35, 24), handRight=(39, 26),
                                          kneeLeft=(28, 52), feetLeft=(27, 66),
                                          kneeRight=(32, 52), feetRight=(33, 66)),
                                    expr="happy",
                                    ko="벤치 뒤에 서서 두 팔을 등받이에 올린 자세",
                                    en="Standing behind a bench, both arms resting on the backrest"),
    "w1d2_surprise":  dict(pts=P(head=(30, 10.6),
                                 elbowLeft=(25, 26), handLeft=(22, 19),
                                 elbowRight=(35, 26), handRight=(38, 19)),
                           expr="mouth_o",
                           ko="두 손을 들고 놀란 자세 — '오!'",
                           en="Hands up in surprise — 'oh!'"),
    # --- video-specific: Birth of Hangeul & Simple Vowels ---
    "sejong":        dict(pts=P(head=(30, 11), elbowLeft=(26, 28), handLeft=(29.5, 34),
                                elbowRight=(34, 28), handRight=(30.5, 34)), expr="neutral",
                          ko="세종대왕(두 손 모은 위엄) — 왕관/곤룡포는 소품", en="King Sejong, hands clasped (regal)"),
    "mouth_demo":    dict(pts=P(head=(30, 11), elbowRight=(34, 18), handRight=(31.5, 14)), expr="talk",
                          ko="자기 입을 가리키며 발음 시범", en="Pointing to own mouth (pronunciation)"),
    "holding_mirror":dict(pts=P(head=(30, 11), elbowRight=(36, 19), handRight=(42, 14.5)), expr="happy",
                          ko="거울을 들고 입모양 점검", en="Holding a mirror to face"),
    "point_self":    dict(pts=P(elbowRight=(34, 24), handRight=(31, 22.5)), expr="happy",
                          ko="자기 가슴을 가리킴(바로 나!)", en="Pointing at self"),
}


def build_all(outdir, names=None):
    os.makedirs(outdir, exist_ok=True)
    manifest = []
    for name, pose in POSES.items():
        if names and name not in names:
            continue
        im = render_pose(pose, seed=(abs(hash(name)) % 1000) + 1)
        fn = f"stickman_{name}.png"
        im.save(os.path.join(outdir, fn))
        manifest.append({
            "name": name, "file": f"assets/graphics/poses/{fn}",
            "expr": pose.get("expr", "neutral"), "facing": pose.get("facing", "front"),
            "ko": pose["ko"], "en": pose["en"],
        })
        print("saved", fn)
    import json
    with open(os.path.join(outdir, "_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"\n{len(manifest)} poses -> {outdir}/_manifest.json")
    return manifest


if __name__ == "__main__":
    sel = sys.argv[1:] or None
    build_all(OUTDIR, names=sel)
