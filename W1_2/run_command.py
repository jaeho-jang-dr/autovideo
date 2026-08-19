# -*- coding: utf-8 -*-
"""말로 시키면 **계획하고 바로 렌더**한다 — 동작 계산기의 실행부.

    python W1_2/run_command.py "저기 계단 중간에 올라가서 한 칸씩 뛰어내려와서 오른편으로 달려 나가라" steps_seat
    python W1_2/run_command.py "우물가에 가서 웅크리고 무엇인가를 주워서 오라" stall_cuke

시킨 말 → `motion_planner` 가 좌표·크기·발 y·컷·배속을 계산 → 그대로 mp4.
계산 근거(몇 미터·몇 보·몇 배속)를 다 찍어 주므로 어디가 틀렸는지 바로 짚을 수 있다.
"""
import glob
import os
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import render_show as R                                    # noqa: E402
import motion_planner as M                                 # noqa: E402
from render_scenes import cut_frame, lerp, smooth          # noqa: E402

OUT = "W1_2/_cmd"
FPS = 24
W, H = 1280, 720


def render(plan, name="cmd"):
    cuts, poses = R.load_cuts(), R.load_poses()
    sec = plan.t
    nf = int(sec * FPS)
    bfs = R.bg_frames(plan.bg, nf)

    frames = os.path.join(OUT, "_frames")
    os.makedirs(frames, exist_ok=True)
    for f in glob.glob(os.path.join(frames, "*.png")):
        os.remove(f)

    missing = set()
    for i in range(nf):
        t = i / float(FPS)
        cv = R.img(bfs[i]).copy()
        if cv.size != (W, H):
            cv = cv.resize((W, H), Image.LANCZOS)
        draw = []
        for b in plan.beats:
            t0, t1, key, x0, x1, h0, h1 = b[:7]
            if not (t0 <= t < t1):
                continue
            u = smooth((t - t0) / max(1e-6, t1 - t0))
            x, h = lerp(x0, x1, u), lerp(h0, h1, u)
            foot = lerp(b[7], b[8], u)
            if key.startswith("POSE:"):
                p = poses.get(key[5:])
                if not p:
                    missing.add(key)
                    continue
                im = R.img(p)
            else:
                fp = cut_frame(b, key, t - t0, cuts)
                if not fp:
                    missing.add(key)
                    continue
                im = R.img(fp)
            draw.append((foot, im, x, h))
        # 원근 z-정렬 — 발이 아래일수록(가까울수록) 나중에 그린다
        for foot, im, x, h in sorted(draw, key=lambda d: d[0]):
            R.place_xy(cv, im, x, foot, h)
        cv.convert("RGB").save(os.path.join(frames, "f%05d.png" % i))

    if missing:
        print("★없는 자산:", ", ".join(sorted(missing)))
    out = os.path.join(OUT, "%s.mp4" % name)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(frames, "f%05d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", out], check=True)
    print("\n✅ %s  %d프레임 · %.1f초" % (out, nf, sec))
    return out


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    text, bg = sys.argv[1], sys.argv[2]
    start = sys.argv[3] if len(sys.argv) > 3 else None
    p = M.Plan(bg)
    if start:
        p.at(start)
    M.parse(text, bg, p)
    p.dump()
    render(p, sys.argv[4] if len(sys.argv) > 4 else "cmd")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
