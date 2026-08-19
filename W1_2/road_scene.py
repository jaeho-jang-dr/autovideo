# -*- coding: utf-8 -*-
"""은행나무길 씬 — **달려갔다 서서 휙 돌아 달려온다.**

★사장님 지시(2026-08-13)
  "은행나무길도 그 길을 갈 수 있는 구역으로 만들어서 **달려갔다 달려올 수 있게** 만들자."
  "**달려가기 달려오기의 전환은 잠깐 서 있다가 휙 돌아서 오면 된다.**"
  "나무 높이가 다 같다고 보았을 때 **나무 높이의 차이가 원근의 차이**이니 그것으로 재면 된다."

## 이 배경의 무대 (`assets/anchors/path_leaves.json`)
  · 갈 수 있는 땅 = **사다리꼴 길** — 소실점(y445)으로 좁아진다. 나무 사이 풀밭은 못 간다
  · 지평선 445 · K = 400/(720−445) = 1.454
      발 715 → 키 393   발 600 → 225   발 520 → 109   발 470 → 36
  · 사라지는 크기 20px 에서 시간을 끊는다 — 소실점 코앞은 거리가 무한대로 뻗는다

## 짜임
  ① 앞에서 저 멀리로 **달려간다** (키 393 → 36)
  ② 저 멀리서 **잠깐 선다** (달리기 첫 정지 컷 한 장)
  ③ **휙 돌아선다** (반대 방향 달리기 첫 컷 한 장)
  ④ 이쪽으로 **달려온다** (키 36 → 385)

    python W1_2/road_scene.py            # 좌표표
    python W1_2/road_scene.py --render   # 그림으로
"""
import os
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import stage2d as S                                     # noqa: E402

BG = "path_leaves"
OUT = "W1_2/_road"
W, H = 1280, 720
FPS = 24

# ★사장님 지시(2026-08-13) — 옆으로 달리지 않는다
#   "이렇게 옆으로 달리지 말고, **앞으로 보고 있다가 휙 돌아서 저 멀리 달려갔다가,
#    잠깐 서 있다가 휙 돌아서 다시 앞으로 달려 나와서 나레이션 포지션까지 오는 거지.**"
#   → 길이 화면 안쪽으로 곧게 뻗어 있으니 **뒷모습으로 멀어지고 앞모습으로 다가온다.**
#     옆달리기(run_side)는 화면을 가로지를 때 쓰는 것이고, 이 길에는 안 맞는다.
# ★2026-08-13 갱신 (사장님 지시)
#   "한 장면에 두 씬이니까 **16초 정도**로 만들어 보고 **더 멀리까지** 달려가자.
#    **1초 서 있다가** 다시 달려 오게 하자. **좌우로 지그재그로 한두 번 흔들면서
#    달려 가고, 올 때는 바로** 오자."
NARR = (640, 700)               # 나레이션 자리 — 길 앞, 화면 가운데
FAR = (640, 455)                # 저 멀리 — 더 깊이(옛 472 → 455). 소실점 코앞
GO_SEC, BACK_SEC = 6.4, 6.0     # 달려가고 달려오는 시간
STAND_SEC = 1.2                 # 처음 앞을 보고 서 있는 시간
STOP_SEC, TURN_SEC = 1.0, 0.35  # 저 멀리서 **1초** 서기 · 휙 돌기

# ★갈 때 좌우로 흔드는 지그재그 — (진행률, x 치우침). 길 폭 안에서만 흔든다.
#   길은 소실점으로 좁아지므로 치우침도 **진행할수록 줄인다**(폭에 비례).
ZIGZAG = [(0.00, 0), (0.22, -150), (0.45, 110), (0.68, -60), (0.85, 25), (1.00, 0)]


def plan():
    """(t0, t1, 컷키, x0, x1, h0, h1, 발y0, 발y1, 설명, (컷i0,i1), fps, 'lin')"""
    st = S.Stage(BG)
    B, t = [], 0.0

    h_narr = round(st.h_at(NARR[1]))
    h_far = round(st.h_at(FAR[1]))

    # ① 앞을 보고 서 있다 — 나레이션 자리
    B.append((t, t + STAND_SEC, "POSE:sm_arms_out_wide", NARR[0], NARR[0],
              h_narr, h_narr, NARR[1], NARR[1],
              "앞을 보고 서 있다 (나레이션 자리 · 키 %d)" % h_narr,
              (0, 1), 1.0, "lin"))
    t += STAND_SEC

    # ② 휙 돌아선다 — 뒷모습 달리기 첫 컷 한 장
    B.append((t, t + TURN_SEC, "run_back", NARR[0], NARR[0],
              h_narr, h_narr, NARR[1], NARR[1],
              "휙 돌아선다 (뒷모습)", (0, 1), 1.0, "lin"))
    t += TURN_SEC

    # ③ ★저 멀리로 **뒷모습으로 지그재그** 달려간다 (사장님 지시)
    #    ZIGZAG 마디마다 비트를 끊어 좌우로 흔든다. 치우침은 그 자리의 **길 폭에 비례**해
    #    줄어들므로, 멀어질수록 흔들림도 작아져 길 밖으로 안 나간다.
    for i in range(len(ZIGZAG) - 1):
        (u0, dx0), (u1, dx1) = ZIGZAG[i], ZIGZAG[i + 1]
        seg = GO_SEC * (u1 - u0)
        fy0 = NARR[1] + (FAR[1] - NARR[1]) * u0
        fy1 = NARR[1] + (FAR[1] - NARR[1]) * u1
        # 길 폭에 비례해 치우침을 줄인다 (앞 1.0 → 저 멀리 0.15)
        s0, s1 = 1.0 - 0.85 * u0, 1.0 - 0.85 * u1
        B.append((t, t + seg, "run_back",
                  round(NARR[0] + dx0 * s0), round(NARR[0] + dx1 * s1),
                  round(h_narr + (h_far - h_narr) * u0),
                  round(h_narr + (h_far - h_narr) * u1),
                  round(fy0), round(fy1),
                  "지그재그로 달려간다 %d/%d (x%+d→%+d)"
                  % (i + 1, len(ZIGZAG) - 1, round(dx0 * s0), round(dx1 * s1)),
                  (0, 44), 24.0, "lin"))
        t += seg

    # ④ 저 멀리서 잠깐 선다
    B.append((t, t + STOP_SEC, "run_back", FAR[0], FAR[0],
              h_far, h_far, FAR[1], FAR[1],
              "저 멀리서 잠깐 선다", (0, 1), 1.0, "lin"))
    t += STOP_SEC

    # ⑤ 휙 돌아선다 — 앞모습 달리기 첫 컷 한 장
    B.append((t, t + TURN_SEC, "run_front", FAR[0], FAR[0],
              h_far, h_far, FAR[1], FAR[1],
              "휙 돌아선다 (앞모습)", (0, 1), 1.0, "lin"))
    t += TURN_SEC

    # ⑥ ★앞으로 달려 나와 **나레이션 자리**까지 온다
    B.append((t, t + BACK_SEC, "run_front", FAR[0], NARR[0],
              h_far, h_narr, FAR[1], NARR[1],
              "앞으로 달려 나와 나레이션 자리까지 (앞모습 · 키 %d→%d · 발 %d→%d)"
              % (h_far, h_narr, FAR[1], NARR[1]), (0, 44), 24.0, "lin"))
    t += BACK_SEC
    return st, B, t


def main():
    st, B, total = plan()
    print("은행나무길 씬 — %.1f초 · 비트 %d개" % (total, len(B)))
    print("  지평선 %d · K %.3f · 밟을 수 있는 땅 %.1f%%\n"
          % (st.horizon, st.k, 100.0 * st.walk_mask().mean()))
    print("%5s %5s  %-16s %5s %5s  %4s %4s  %s"
          % ("시작", "끝", "컷", "x0", "x1", "키0", "키1", "설명"))
    for b in B:
        print("%5.1f %5.1f  %-16s %5d %5d  %4d %4d  %s"
              % (b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[9]))

    if "--render" not in sys.argv:
        return 0

    import render_show as R
    from render_scenes import lerp, smooth
    os.makedirs(OUT, exist_ok=True)
    fr = os.path.join(OUT, "_f")
    os.makedirs(fr, exist_ok=True)
    for f in os.listdir(fr):
        os.remove(os.path.join(fr, f))
    cuts, poses = R.load_cuts(), R.load_poses()
    bfs = R.bg_frames(BG, int(total * FPS))
    n = 0
    for i in range(int(total * FPS)):
        t = i / float(FPS)
        cv = R.img(bfs[i]).copy()
        if cv.size != (W, H):
            cv = cv.resize((W, H), Image.LANCZOS)
        for b in B:
            t0, t1, key, x0, x1, h0, h1, f0, f1 = b[:9]
            if not (t0 <= t < t1):
                continue
            raw = (t - t0) / max(1e-6, t1 - t0)
            u = raw if (len(b) > 12 and b[12] == "lin") else smooth(raw)
            x, h, fy = lerp(x0, x1, u), lerp(h0, h1, u), lerp(f0, f1, u)
            if key.startswith("POSE:"):
                p2 = poses.get(key[5:])
                if not p2:
                    continue
                R.place_xy(cv, R.img(p2), x, fy, h)
                continue
            fs = cuts.get(key)
            if not fs:
                continue
            i0, i1 = b[10] if len(b) > 10 else (0, len(fs))
            fps_cut = b[11] if len(b) > 11 else 8.0
            i0 = max(0, min(i0, len(fs) - 1))
            i1 = max(i0 + 1, min(i1, len(fs)))
            R.place_xy(cv, R.img(fs[i0 + int((t - t0) * fps_cut) % (i1 - i0)]),
                       x, fy, h)
        cv.convert("RGB").save(os.path.join(fr, "f%04d.png" % n))
        n += 1
    out = os.path.join(OUT, "road_scene.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(fr, "f%04d.png"), "-c:v", "libx264",
                    "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out],
                   check=True)
    print("\n✅ %s  %d프레임 · %.1f초" % (out, n, n / float(FPS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
