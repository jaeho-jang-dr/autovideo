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
    body = cubic(P["chest"], P["chest"], P["body"], P["pelvis"])
    legL = cubic(P["pelvis"], P["pelvis"], P["kneeLeft"], P["feetLeft"])
    legR = cubic(P["pelvis"], P["pelvis"], P["kneeRight"], P["feetRight"])
    armL = cubic(P["chest"], P["chest"], P["elbowLeft"], P["handLeft"])
    armR = cubic(P["chest"], P["chest"], P["elbowRight"], P["handRight"])

    for path in (body, legL, legR, armL, armR):
        stamp_stroke(draw, path, lw, rng, wobble=wob)
    # neck stub (chest up to head bottom)
    head_c = P["head"]
    neck_top = (head_c[0], head_c[1] + hr)
    stamp_stroke(draw, [P["chest"], neck_top], lw, rng, wobble=0.3)

    if zolla:                                           # 꽉 찬 검은 머리
        draw.ellipse([head_c[0] - hr, head_c[1] - hr, head_c[0] + hr, head_c[1] + hr], fill=INK)
    else:
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

    img = img.resize((CANVAS, CANVAS), Image.LANCZOS)
    return img


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
    "thinking":      dict(pts=P(head=(31, 11), elbowRight=(34, 28), handRight=(31.5, 18.5)),
                          expr="neutral", facing="right", ko="턱에 손, 생각하는 자세", en="Thinking, hand on chin"),
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
