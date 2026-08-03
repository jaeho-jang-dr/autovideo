# -*- coding: utf-8 -*-
"""W24 플래시몹 군무 — 스틱맨 3인 32박 안무 생성 + 음악 합성 (2026-07-28).

곡: Never Coming Down (The Soundlings) · **148 BPM** · 1박 0.405s · 32박 12.97s
안무: 8박 × 4절, **2박마다 키포즈 1개** = 16 키포즈.
      A 인사(W1) · B 숫자(W8) · C 가리키기·통화(W13·W18) · D 하이파이브·환호(W23)

캐릭터: 졸라맨(cyan) · 졸라걸(warm) · 스틱맨(violet) — 라인 발광으로 구분.
사용: python make_w24_dance.py
"""
import math
import os
import subprocess

from PIL import Image

import stickman_factory as S

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
OUT = "W24/dance"
os.makedirs(OUT, exist_ok=True)
BPM = 148
BEAT = 60.0 / BPM
FPS = 24
MP3 = "W24/Never Coming Down - The Soundlings.mp3"
W, H = 1280, 720

B = {"head": [30, 11], "chest": [30, 20], "body": [30, 30], "pelvis": [30, 41],
     "elbowLeft": [25, 29], "handLeft": [23, 39], "elbowRight": [35, 29], "handRight": [37, 39],
     "kneeLeft": [27.5, 52], "feetLeft": [26, 66], "kneeRight": [32.5, 52], "feetRight": [34, 66]}


def P(**kw):
    """기본 자세에서 지정 관절만 바꾼 포즈 좌표."""
    d = {k: list(v) for k, v in B.items()}
    d.update({k: list(v) for k, v in kw.items()})
    return d


# ── 16 키포즈 (2박마다 하나) ──────────────────────────────────────────────────
KEY = [
    # A절 — 인사 (W1)
    ("A1 오른손 흔들기", P(elbowRight=[37, 15], handRight=[41, 5])),
    ("A2 왼손 흔들기",   P(elbowLeft=[23, 15], handLeft=[19, 5])),
    ("A3 두 손 모아 앞으로", P(elbowLeft=[26, 27], handLeft=[29, 33], elbowRight=[34, 27], handRight=[31, 33])),
    ("A4 제자리 뛰기",   P(kneeLeft=[27.5, 50], feetLeft=[26, 62], kneeRight=[32.5, 50], feetRight=[34, 62],
                        head=[30, 9], chest=[30, 18], body=[30, 28], pelvis=[30, 39])),
    # B절 — 숫자 (W8)
    ("B1 하나 찍기", P(elbowRight=[36, 24], handRight=[40, 20])),
    ("B2 둘 찍기",   P(elbowRight=[37, 22], handRight=[42, 17])),
    ("B3 셋 찍기",   P(elbowRight=[38, 20], handRight=[44, 14])),
    ("B4 손뼉",      P(elbowLeft=[27, 25], handLeft=[30, 24], elbowRight=[33, 25], handRight=[30, 24])),
    # C절 — 가리키기·통화 (W13·W18)
    ("C1 오른팔 사선", P(elbowRight=[38, 18], handRight=[46, 8])),
    ("C2 왼팔 사선",   P(elbowLeft=[22, 18], handLeft=[14, 8])),
    ("C3 통화 좌",     P(elbowRight=[36, 18], handRight=[33, 12], head=[29, 11])),
    ("C4 통화 우",     P(elbowRight=[36, 18], handRight=[33, 12], head=[31, 11])),
    # D절 — 하이파이브·환호 (W23)
    ("D1 하이파이브 우", P(elbowRight=[38, 16], handRight=[45, 10])),
    ("D2 하이파이브 좌", P(elbowLeft=[22, 16], handLeft=[15, 10])),
    ("D3 두 팔 활짝",   P(elbowLeft=[22, 20], handLeft=[16, 12], elbowRight=[38, 20], handRight=[44, 12])),
    ("D4 점프 만세",    P(elbowLeft=[24, 14], handLeft=[21, 4], elbowRight=[36, 14], handRight=[39, 4],
                        head=[30, 8], chest=[30, 17], body=[30, 27], pelvis=[30, 38],
                        kneeLeft=[27.5, 48], feetLeft=[26, 59], kneeRight=[32.5, 48], feetRight=[34, 59])),
]

CHARS = [
    ("zolla_man",  {"style": "zolla", "glow": "cyan",   "expr": "happy"}),
    ("zolla_girl", {"style": "zolla", "glow": "warm",   "expr": "happy", "bun": True,
                    "bun_color": (232, 126, 58, 255)}),
    ("stickman",   {"glow": "violet", "expr": "happy"}),
]


def render_all():
    made = {}
    for name, style in CHARS:
        d = f"{OUT}/{name}"
        os.makedirs(d, exist_ok=True)
        frames = []
        for i, (label, pts) in enumerate(KEY):
            pose = dict(style); pose["pts"] = pts
            im = S.render_pose(pose, seed=7 + i)
            p = f"{d}/{i:02d}.png"
            im.save(p); frames.append(p)
        made[name] = frames
        print(f"  {name}: {len(frames)}포즈")
    return made


def compose(made):
    """세 캐릭터를 나란히 세우고 32박(=16포즈×2박)을 24fps 프레임으로 편다."""
    per_pose = BEAT * 2                        # 2박 = 0.811s
    n_frames = round(per_pose * FPS)           # 포즈당 프레임 수 ≈ 19
    tmp = f"{OUT}/_seq"
    os.makedirs(tmp, exist_ok=True)
    xs = [330, 640, 950]
    idx = 0
    for rep in range(2):                       # 32박 × 2회
        for k in range(len(KEY)):
            base = Image.new("RGB", (W, H), (12, 12, 20))
            for (name, _), cx in zip(CHARS, xs):
                im = Image.open(made[name][k]).convert("RGBA")
                s = 620 / im.height
                im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
                base.paste(im, (cx - im.width // 2, H - im.height - 40), im)
            for _ in range(n_frames):
                base.save(f"{tmp}/{idx:05d}.png"); idx += 1
    print(f"  프레임 {idx}장 ({idx/FPS:.1f}초)")

    out = f"{OUT}/w24_dance_test.mp4"
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{tmp}/%05d.png",
                    "-i", MP3, "-t", f"{idx/FPS:.2f}",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", out], capture_output=True)
    return out


if __name__ == "__main__":
    print(f"=== W24 군무 · {BPM} BPM · 2박당 1포즈({BEAT*2:.3f}s) · 32박 {32*BEAT:.2f}s ===")
    made = render_all()
    out = compose(made)
    print(f"✅ {out}  ({os.path.getsize(out)//1024}KB)")
