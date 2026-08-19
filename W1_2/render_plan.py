# -*- coding: utf-8 -*-
"""W1-2 — `build_scenes` 가 짠 계획을 **비트로 펼쳐 렌더**한다.

규격은 `W1_2/W1_2_RULES.md`. 이 스크립트가 지키는 것:
  §2 원근 90~600 · 크롭·확대 없음
  §3 스트라이드 속도(걷기1 · 옆달리기2 · 앞뒤달리기3)
  §4 원근 z-정렬(발이 아래일수록 앞)
  §5 동작은 끝까지 · 한 화면에 둘·셋 · 있는 자산 전량 소비
  §6 동작이 씬 길이를 정한다
  §7 앞 씬 퇴장과 다음 씬 진입을 문다

    python W1_2/render_plan.py         # 전부
    python W1_2/render_plan.py 3       # 앞 3씬만
"""
import glob
import os
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import render_show as R                                  # noqa: E402
import scene_defs as S                                   # noqa: E402
import build_scenes as B                                 # noqa: E402
from render_scenes import fps_of, lerp, smooth           # noqa: E402

OUT = "W1_2/_plan"
FPS = 24
W, H = 1280, 720

# 동시 캐릭터가 설 자리 (겹치지 않게 벌린다 · §4)
SLOT_X = [230, 1050, 640, 400, 880]
SLOT_H = [300, 260, 430, 200, 340]                       # 층마다 다른 원근


def build_beats(p):
    """계획 한 씬 → (주인공 비트, 곁들이 비트들)"""
    sec = p["sec"]
    ein, eout = p["ein"], p["eout"]
    ev, hook = p["ev"], p["hook"]

    x_home, h_home = 640, 460
    beats, t = [], 0.0

    # ① 진입 — 원근을 살려 들어온다(§2)
    eb = B.enter_beat(ein, 0.0, 3.4, x_home, h_home)
    if eb:
        beats.append(eb)
        t = 3.4

    # ② 사건에 맞물리는 동작(§6) — 사건 시각에 정확히 시작한다
    if ev and ev[1] is not None and hook:      # ★지속형(시각 None)은 사건 맞물림이 없다
        t_ev = max(t + 0.3, ev[1])
        if t_ev > t:
            beats.append((t, t_ev, "POSE:sm_presenting", x_home, x_home, h_home, h_home))
        beats.append((t_ev, t_ev + 8.0, hook[0], x_home, x_home, h_home, h_home))
        t = t_ev + 8.0

    # ③ 퇴장 — 앞 씬과 물린 방향으로(§7)
    xb = B.exit_beat(eout, max(t, sec - 6.0), sec, x_home, h_home)
    if xb:
        if xb[0] > t:
            beats.append((t, xb[0], "POSE:sm_arms_out_wide",
                          x_home, x_home, h_home, h_home))
        beats.append(xb)
    else:
        beats.append((t, sec, "POSE:sm_arms_out_wide",
                      x_home, x_home, h_home, h_home))

    # ④ 곁들이 — 나머지 동작·포즈를 동시에 세운다(§5, 겹치지 않게 §4)
    extra = []
    for j, k in enumerate(p["cuts"]):
        extra.append((k, SLOT_X[j % len(SLOT_X)], SLOT_H[j % len(SLOT_H)]))
    for j, k in enumerate(p["poses"]):
        extra.append(("POSE:" + k, SLOT_X[(j + 3) % len(SLOT_X)],
                      SLOT_H[(j + 2) % len(SLOT_H)]))
    return beats, extra


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    plan = B.main()
    if limit:
        plan = plan[:limit]
    cuts, poses = R.load_cuts(), R.load_poses()

    frames_dir = os.path.join(OUT, "_frames")
    os.makedirs(frames_dir, exist_ok=True)
    for f in glob.glob(os.path.join(frames_dir, "*.png")):
        os.remove(f)

    k = 0
    print("\n=== 렌더 ===")
    for si, p in enumerate(plan, 1):
        beats, extra = build_beats(p)
        nf = int(p["sec"] * FPS)
        bfs = R.bg_frames(p["bg"], nf)
        print("  S%-2d %-15s %2d초 · 비트 %d · 동시 %d"
              % (si, p["bg"], p["sec"], len(beats), len(extra)))
        for i in range(nf):
            t = i / float(FPS)
            cv = R.img(bfs[i]).copy()
            if cv.size != (W, H):
                cv = cv.resize((W, H), Image.LANCZOS)
            draw = []

            for key, x, h in extra:
                if key.startswith("POSE:"):
                    q = poses.get(key[5:])
                    if not q:
                        continue
                    im = R.img(q)
                else:
                    fs = cuts.get(key)
                    if not fs:
                        continue
                    im = R.img(fs[int(t * fps_of(key)) % len(fs)])
                draw.append((S.foot_of(h), im, x, h))

            for b in beats:
                t0, t1, key, x0, x1, h0, h1 = b[:7]
                if not (t0 <= t < t1):
                    continue
                u = smooth((t - t0) / max(1e-6, t1 - t0))
                x, h = lerp(x0, x1, u), lerp(h0, h1, u)
                if key.startswith("POSE:"):
                    q = poses.get(key[5:])
                    if not q:
                        continue
                    im = R.img(q)
                else:
                    fs = cuts.get(key)
                    if not fs:
                        continue
                    im = R.img(fs[int((t - t0) * fps_of(key)) % len(fs)])
                draw.append((S.foot_of(h), im, x, h))

            for foot, im, x, h in sorted(draw, key=lambda d: d[0]):
                R.place_xy(cv, im, x, foot, h)
            cv.convert("RGB").save(os.path.join(frames_dir, "f%05d.png" % k))
            k += 1

    out = os.path.join(OUT, "w1d2_plan.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(frames_dir, "f%05d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", out], check=True)
    print("\n✅ %s  %d프레임 · %.1f초" % (out, k, k / float(FPS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
