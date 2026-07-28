# -*- coding: utf-8 -*-
"""W23 가상 렌더(프리비즈) — 걷기·정지 포즈·동작컷을 한 타임라인에 물려 본다 (2026-07-27).

사장님 요구 동선:
  ① 걸어 들어오기 (한 스트라이드 0.75초)
  ② 서면서 돌아서서 말하기 (정지 포즈)
  ③ 말하다 이어서 동작컷(동영상 64컷) 재생
  ④ 동작 끝나면 다시 걸어서 이동/퇴장

좌표 규격: 1280x720 · CHAR_SCALE 0.561 · 발끝 y=678 · 포즈 원본은 몸통중심 x=512 정렬.
걷기컷·정지·동작컷 모두 같은 규격으로 정규화돼 있어 그대로 물린다.

사용:
  python previz_w23_walk.py --bg panda_deck --talk explain --action greet_wave
"""
import argparse
import glob
import os
import re
import shutil
import subprocess

from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
W, H = 1280, 720
SCALE = 0.561
FEET_SRC = 1209
TORSO_SRC = 512                     # 정규화 규격상 몸통중심 x
FPS = 24
TMP = "scratch/_previz"
OUT = "scratch/w23_previz.mp4"


def load(path):
    im = Image.open(path).convert("RGBA")
    return im.resize((round(im.width * SCALE), round(im.height * SCALE)), Image.LANCZOS)


def cut_paths(key):
    ps = []
    for p in glob.glob(f"W23/poses/injun_w23_{key}_*.png"):
        m = re.search(r"_(\d+)\.png$", p)
        if m:
            ps.append((int(m.group(1)), p))
    return [p for _, p in sorted(ps)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bg", default="panda_deck")
    ap.add_argument("--talk", default="explain")
    ap.add_argument("--action", default="greet_wave")
    ap.add_argument("--stride-sec", type=float, default=0.75, help="한 스트라이드 시간")
    ap.add_argument("--stride-px", type=int, default=360, help="한 스트라이드 이동 거리(px)")
    ap.add_argument("--talk-sec", type=float, default=2.5)
    ap.add_argument("--stand-x", type=int, default=437, help="말할 때 서는 x(몸통중심)")
    a = ap.parse_args()

    shutil.rmtree(TMP, ignore_errors=True)
    os.makedirs(TMP, exist_ok=True)

    bg_p = f"assets/graphics/bg/bg_w23_{a.bg}.png"
    bg = Image.open(bg_p).convert("RGB")
    # ★1376x768(1.792) → 1280x720(1.778): 늘리지 말고 가로를 잘라 비율 유지
    s = max(W / bg.width, H / bg.height)
    bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2,
                  (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))

    walk_r = [load(p) for p in cut_paths("walk_r")]
    talk = load(f"W23/poses_still_norm/injun_w23_{a.talk}.png")
    action = [load(p) for p in cut_paths(a.action)]
    if not walk_r or not action:
        raise SystemExit("걷기컷 또는 동작컷 없음")

    feet_cv = round(FEET_SRC * SCALE)
    off_x = round(TORSO_SRC * SCALE)             # 스케일 후 이미지 안에서의 몸통중심 위치

    def put(pose, cx):
        f = bg.copy().convert("RGBA")
        f.alpha_composite(pose, (round(cx) - off_x, feet_cv - pose.height))
        return f.convert("RGB")

    frames = []
    per_stride = max(1, round(a.stride_sec * FPS))          # 0.75s → 18프레임

    def walk_span(x0, x1, ease):
        """★걷기 컷 인덱스를 **이동 거리**에 물린다 — 시간에 물리면 발이 미끄러진다.
        ease='out' 마지막 스트라이드 감속(서면서) · 'in' 첫 스트라이드 가속(출발)."""
        dist = x1 - x0
        n = max(1, round(abs(dist) / a.stride_px * per_stride))
        for i in range(n):
            u = (i + 1) / n
            if ease == "out":                                # 뒤로 갈수록 느려짐
                u = 1 - (1 - u) ** 2
            elif ease == "in":
                u = u ** 2
            x = x0 + dist * u
            ph = abs(x - x0) / a.stride_px * len(walk_r)     # 거리 기반 위상
            frames.append(put(walk_r[int(ph) % len(walk_r)], x))

    # ① 걸어 들어오기 (마지막에 감속)
    walk_span(-120, a.stand_x, "out")
    # ★서는 비트 — 발 모은 컷(0번)을 잠깐 유지해 걷기→정지 전환을 만든다
    for _ in range(4):
        frames.append(put(walk_r[0], a.stand_x))
    # ② 돌아서서 말하기
    for _ in range(round(a.talk_sec * FPS)):
        frames.append(put(talk, a.stand_x))
    # ③ 이어서 동작컷 — 64컷을 8fps 로(원본 8초 속도) → 프레임당 3장 복제
    rep = max(1, FPS // 8)
    for im in action:
        for _ in range(rep):
            frames.append(put(im, a.stand_x))
    # ④ 동작 후 걸어서 퇴장(오른쪽) — 첫 스트라이드 가속
    walk_span(a.stand_x, W + 140, "in")

    for i, f in enumerate(frames):
        f.save(f"{TMP}/{i:05d}.png")
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{TMP}/%05d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", OUT],
                   capture_output=True)
    print(f"✅ {OUT}  {len(frames)}프레임 / {len(frames)/FPS:.1f}초 "
          f"(스트라이드 {a.stride_sec}s·{a.stride_px}px, 걷기 {len(walk_r)}컷, 동작 {len(action)}컷)")


if __name__ == "__main__":
    main()
