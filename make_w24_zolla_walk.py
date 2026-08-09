# -*- coding: utf-8 -*-
"""졸라 3인방(졸라맨·졸라걸·스틱맨) **오른편 걷기 8컷 + 좌우반전 8컷** 생성.
   ★사장님 지시(2026-08-05): 졸라 3인방은 Flow 로 만들지 않고 stickman_factory 로 찍어낸다.
     파라메트릭이라 크레딧이 안 들고, 관절 좌표로 그리니 **팔다리가 뒤바뀌지 않는다**
     (Veo 측면 걷기의 고질적 결함이 원리적으로 없다).

   걷기 사이클은 12관절 좌표(60x80 단위)를 8단계로 정의한다. 한 스트라이드 = 8컷.
     0 접지(오른발 앞) → 2 통과 → 4 접지(왼발 앞) → 6 통과 → (순환)
   반대쪽 팔다리가 함께 흔들리도록 팔은 다리와 **엇갈리게** 움직인다(크로스 스윙).

   출력: assets/graphics/poses/w24_<char>_walk_r_0..7.png · _walk_l_0..7.png
   사용: python make_w24_zolla_walk.py [--only zolla_man] [--dry]
"""
import argparse
import os

from PIL import Image

import stickman_factory as SF

OUT = "assets/graphics/poses"

# 캐릭터별 렌더 방식 — 졸라맨=꽉 찬 검은 머리(style zolla) · 졸라걸=render_girl · 스틱맨=기본
CHARS = {
    "zolla_man":  dict(style="zolla", girl=False),
    "zolla_girl": dict(style="zolla", girl=True),
    "stickman":   dict(style=None,    girl=False),
}

# ── 걷기 8단계 — ★**옆모습**으로 오른쪽을 보고 걷는다 (사장님 지시 2026-08-05) ──
# 앞판은 정면을 본 채 다리만 좌우로 벌려서 걷기로 안 보였다. 옆모습에서는
#   ① 얼굴이 오른쪽을 본다(facing="right")
#   ② 다리·팔이 좌우가 아니라 **앞뒤(x축)** 로 스윙한다 — 한쪽이 앞이면 다른 쪽은 뒤
#   ③ 팔은 다리와 엇갈린다(오른다리 앞 → 왼팔 앞)
#   ④ 딛는 다리는 곧게, 흔드는 다리는 무릎을 접는다(발이 땅에서 떨어진다)
#   ⑤ 통과 자세에서 몸이 살짝 뜬다
# 좌표계 60x80 · 골반 (30,41) 기준. x 가 클수록 앞(오른쪽).
CYCLE = [
    # (무릎L, 발L, 무릎R, 발R, 팔꿈치L, 손L, 팔꿈치R, 손R, 몸통올림)
    # 0 접지 — 오른발 앞(착지) · 왼발 뒤(밀어냄) · 왼팔 앞
    ((27.0, 53), (25, 66), (33.0, 52), (37, 66), (32.5, 30), (35, 38), (27.5, 30), (25, 38), 0),
    # 1 왼다리 접혀 올라오기 시작
    ((28.5, 53), (28, 63), (32.0, 52), (35, 66), (32.0, 30), (34, 38), (28.0, 30), (26, 38), 0),
    # 2 통과 — 두 다리 겹침, 왼무릎 최대로 접힘, 몸 살짝 뜸
    ((30.5, 52), (31, 60), (30.5, 52), (31, 66), (30.5, 30), (30, 39), (29.5, 30), (30, 39), 1),
    # 3 왼발이 앞으로 뻗어 나감
    ((32.0, 52), (35, 64), (28.5, 53), (27, 66), (28.5, 30), (26, 38), (31.5, 30), (34, 38), 0),
    # 4 접지 — 왼발 앞(착지) · 오른발 뒤 · 오른팔 앞 (0의 좌우 반대)
    ((33.0, 52), (37, 66), (27.0, 53), (25, 66), (27.5, 30), (25, 38), (32.5, 30), (35, 38), 0),
    # 5
    ((32.0, 52), (35, 66), (28.5, 53), (28, 63), (28.0, 30), (26, 38), (32.0, 30), (34, 38), 0),
    # 6 통과 (오른무릎 접힘)
    ((30.5, 52), (31, 66), (30.5, 52), (31, 60), (29.5, 30), (30, 39), (30.5, 30), (30, 39), 1),
    # 7 오른발이 앞으로 뻗어 나감
    ((28.5, 53), (27, 66), (32.0, 52), (35, 64), (31.5, 30), (34, 38), (28.5, 30), (26, 38), 0),
]


def log(m):
    print(m, flush=True)


def pose_at(i):
    kl, fl, kr, fr, el, hl, er, hr, up = CYCLE[i]
    d = -up          # 통과 자세에서 몸이 살짝 뜬다
    return SF.P(head=(30, 11 + d), chest=(30, 20 + d), body=(30, 30 + d), pelvis=(30, 41 + d),
                kneeLeft=kl, feetLeft=fl, kneeRight=kr, feetRight=fr,
                elbowLeft=el, handLeft=hl, elbowRight=er, handRight=hr)


def render(char, i):
    cfg = CHARS[char]
    # ★facing="right" — 얼굴 특징이 오른쪽으로 쏠리고 옆모습 눈이 그려진다(정면 얼굴이 아니다)
    spec = dict(pts=pose_at(i), expr="neutral", facing="right")
    if cfg["style"]:
        spec["style"] = cfg["style"]
    fn = SF.render_girl if cfg["girl"] else SF.render_pose
    return fn(spec, seed=7 + i)          # seed 를 컷마다 바꿔 손그림 흔들림이 굳지 않게


def main(only, dry):
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for char in ([only] if only else CHARS):
        if char not in CHARS:
            log(f"★모르는 캐릭터: {char}"); return 1
        for i in range(len(CYCLE)):
            im = render(char, i).convert("RGBA")
            r = f"{OUT}/w24_{char}_walk_r_{i}.png"
            l = f"{OUT}/w24_{char}_walk_l_{i}.png"
            if not dry:
                im.save(r)
                im.transpose(Image.FLIP_LEFT_RIGHT).save(l)   # ★왼편 걷기 = 좌우반전
            n += 2
        log(f"  {char:<12} 오른쪽 8컷 + 왼쪽 8컷")
    log(f"\n{'(모의) ' if dry else ''}총 {n}장 → {OUT}/w24_*_walk_[rl]_*.png")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    raise SystemExit(main(a.only, a.dry))
