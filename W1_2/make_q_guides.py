# -*- coding: utf-8 -*-
"""3/4 대각선 기준 이미지 두 장 — 45도(앞으로) · 135도(뒤로).

★사장님 지시(2026-08-11): "기준 이미지 두 장 더 만들어서 동영상 4개 새로 만들자."

## 왜 필요한가
정면 기준 이미지(guide_front.png)로 4개를 뽑았더니 **넷 다 납작한 옆모습**이 나왔다.
스틱맨은 선 그림이라 각도 단서가 없어서, 글로 "135도"라고 못 박아도 Flow 가
아는 것 중 제일 가까운 옆모습으로 떨어진다. **각도는 참조 이미지가 정한다.**

## 각도를 어떻게 선으로 나타내나
0도=정면, 180도=완전 뒤. 몸이 돌면 어깨·골반의 **가로 폭이 cos 만큼 줄어든다**.
45도·135도 모두 |cos| = 0.707 이므로 좌우 폭을 그만큼 좁힌다.
둘을 가르는 것은 **머리**다.
  - 45도  = 얼굴이 보이되 오른쪽으로 쏠린다 + 코가 오른쪽 윤곽 밖으로 조금
  - 135도 = 얼굴이 없다. **오른쪽 귀 하나 + 코끝만 아주 조금**(사장님 규격)

기존 guide_front / guide_side 와 같은 규격: 1280x720 · 흰 배경 · 키 620px.
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

import stickman_factory as F                                  # noqa: E402

OUT = "W1_2/motion_src"
W, H = 1280, 720
TARGET_H = 620            # 기존 가이드와 같은 키
TOP = 50

ANGLE = {"toward": 45.0, "away": 135.0}    # 0도=정면, 90도=측면, 180도=완전 뒤


def q_pose(kind):
    """★몸 중앙을 지나는 세로축으로 몸통을 통째로 돌린다 (사장님 지시 2026-08-11).

        x' = cx + (x - cx) · cos θ        (화면상 가로 위치)
        z  =    − (x - cx) · sin θ        (깊이 — 클수록 이쪽에 가깝다)

    깊이 부호 확인: θ=90(오른쪽 측면)이면 몸의 오른쪽(u>0)이 화면 뒤로 가야 하므로
    z = −u·sin90 = −u < 0 ✔. 이 부호 덕에 135도에서는 **가까운 쪽이 화면 오른쪽**이
    되고, 그래서 사장님 규격대로 **귀가 오른편에** 보인다.

    ★핵심: **cos45 = +0.707 이지만 cos135 = −0.707 이다.**
      부호가 반대라 135도는 45도의 **좌우가 뒤집힌** 모습이 된다.
      앞서 절댓값만 써서 둘을 똑같이 만들어 구분이 안 됐다(2026-08-11).
      45도는 먼쪽 팔다리가 화면 왼쪽, 135도는 화면 오른쪽에 온다.
    """
    th = math.radians(ANGLE[kind])
    c, s = math.cos(th), math.sin(th)
    cx = 30.0
    pos, depth = {}, {}
    for k, (x, y) in F.base_pts().items():
        u = x - cx
        pos[k] = (cx + u * c, y)
        depth[k] = -u * s
    return pos, depth


def arc(draw, c, r, a0, a1, lw, rng, w=0.85):
    """중심 c, 반지름 r 의 호 — 각도는 도(오른쪽이 0도, 아래가 +)."""
    pts = [(c[0] + r * math.cos(math.radians(t)), c[1] + r * math.sin(math.radians(t)))
           for t in range(int(a0), int(a1) + 1, 6)]
    F.stamp_stroke(draw, pts, lw * w, rng, wobble=0.2)


def head_toward(draw, c, hr, lw, rng):
    """45도 — 얼굴이 오른쪽으로 쏠리고 코가 윤곽 밖으로 뾰족하게 나온다."""
    cx, cy = c
    ey = cy - hr * 0.16
    er = max(2.0 * F.SS, hr * 0.085)
    for dx in (0.06, 0.50):                      # 두 눈이 오른쪽으로 몰린다
        x = cx + hr * dx
        draw.ellipse([x - er, ey - er, x + er, ey + er], fill=F.INK)
    # ★코 — 눈보다 아래, 윤곽 밖으로 뾰족하게. 눈에 겹치면 덩어리로 보인다.
    ny = cy + hr * 0.16
    F.stamp_stroke(draw, [(cx + hr * 0.74, ny - hr * 0.22),
                          (cx + hr * 1.24, ny + hr * 0.02),
                          (cx + hr * 0.80, ny + hr * 0.20)],
                   lw * 0.75, rng, wobble=0.15)
    my = cy + hr * 0.54                          # 입도 코보다 아래로 내린다
    F.stamp_stroke(draw, [(cx + hr * 0.04, my), (cx + hr * 0.60, my)],
                   hr * 0.11, rng, wobble=0.15)


def head_away(draw, c, hr, lw, rng):
    """135도 — 뒤통수. 눈·입 없음. **오른쪽 귀 하나 + 코끝만 아주 조금.**"""
    cx, cy = c
    # 귀 — 머리 오른쪽 윤곽에 붙어 바깥으로 볼록한 반원
    arc(draw, (cx + hr * 0.94, cy - hr * 0.04), hr * 0.30, -105, 105, lw, rng)
    # 코끝 — 귀보다 아래, 윤곽 밖으로 **아주 조금만** 나온 짧은 꺾임
    ny = cy + hr * 0.46
    F.stamp_stroke(draw, [(cx + hr * 0.78, ny - hr * 0.10),
                          (cx + hr * 0.99, ny + hr * 0.02),
                          (cx + hr * 0.80, ny + hr * 0.11)],
                   lw * 0.70, rng, wobble=0.12)


def render(kind, seed=7):
    rng = random.Random(seed)
    img = Image.new("RGBA", (F.CANVAS * F.SS, F.CANVAS * F.SS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    pos, depth = q_pose(kind)
    P = {k: F.to_px(v, F.SS) for k, v in pos.items()}
    lw = 1.55 * F.S * F.SS
    hr = 7.5 * F.S * F.SS
    away = kind == "away"

    F.stamp_stroke(draw, F.cubic(P["chest"], P["chest"], P["body"], P["pelvis"]),
                   lw, rng, wobble=1.3)
    # ★깊이 순서로 그린다 — 먼 것 먼저, 가까운 것 나중.
    #   먼쪽은 선을 조금 가늘게 해서 멀리 있다는 걸 나타낸다.
    #   토막 내서 가리는 흉내를 냈더니 막대 그림에선 부러진 다리로 보였다(2026-08-11).
    limbs = [("pelvis", "kneeLeft", "feetLeft"), ("pelvis", "kneeRight", "feetRight"),
             ("chest", "elbowLeft", "handLeft"), ("chest", "elbowRight", "handRight")]
    for root, joint, tip in sorted(limbs, key=lambda t: depth[t[1]]):
        near = depth[joint] > 0
        F.stamp_stroke(draw, F.cubic(P[root], P[root], P[joint], P[tip]),
                       lw * (1.0 if near else 0.88), rng, wobble=1.3)

    head_c = P["head"]
    F.stamp_stroke(draw, [P["chest"], (head_c[0], head_c[1] + hr)], lw, rng, wobble=0.3)
    F.stamp_ring(draw, head_c, hr, lw, rng)

    # ★발끝 방향이 앞뒤를 가르는 가장 확실한 단서다.
    #   앞으로(45도) = 발가락이 이쪽을 향한다 → 길게, 아래로.
    #   뒤로(135도)  = 뒤꿈치가 이쪽을 향하고 발가락은 화면 안쪽 → 짧게, 위로.
    for foot in (P["feetLeft"], P["feetRight"]):
        if away:
            F.stamp_stroke(draw, [foot, (foot[0] + 6 * F.SS, foot[1] - 4 * F.SS)],
                           lw * 0.9, rng, wobble=0.2)
        else:
            F.stamp_stroke(draw, [foot, (foot[0] + 12 * F.SS, foot[1] + 1 * F.SS)],
                           lw * 0.9, rng, wobble=0.2)

    (head_toward if kind == "toward" else head_away)(draw, head_c, hr, lw, rng)

    img = img.resize((F.CANVAS, F.CANVAS), Image.LANCZOS)

    # 흰 배경 1280x720 정중앙 · 키 620px (기존 가이드와 같은 규격)
    a = img.split()[3].point(lambda v: 255 if v > 8 else 0)
    bb = a.getbbox()
    fig = img.crop(bb)
    s = TARGET_H / fig.height
    fig = fig.resize((max(1, round(fig.width * s)), TARGET_H), Image.LANCZOS)
    cv = Image.new("RGB", (W, H), (255, 255, 255))
    cv.paste(fig, ((W - fig.width) // 2, TOP), fig)
    out = os.path.join(OUT, "guide_q_%s.png" % kind)
    cv.save(out)
    print("  guide_q_%-7s → %s  키 %d · 폭 %d" % (kind, out, TARGET_H, fig.width))
    return out


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for k in ("toward", "away"):
        render(k)
