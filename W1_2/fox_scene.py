# -*- coding: utf-8 -*-
"""여우 씬 — 살금살금 다가가다 여우가 나오자 엉덩방아.

★사장님 지시(2026-08-13)
  "이전 장면 여우 나오는 은행잎길 장면 다시 보고 만들어 보자." → "가로 하자.
   **캐릭터 타이밍을 조금 더 빠르게** 하고."

## 배경 사건 실측 (`path_fox.mp4` 192프레임 · 24fps)
    0.0 ~ 1.9초   여우 없음
    ★2.2초        여우가 **귀만 빼꼼** 내민다 (오른쪽 덤불)
    2.9 ~ 5.1초   **완전히 나와** 이쪽을 본다 (덤불 x≈750 · 발 y≈590)
    5.8초 ~       숨는다

## 짜임 — 사건에 캐릭터를 물린다
  ① 왼쪽에서 걸어 들어온다              (0.0 ~ 1.0)
  ② **살금살금** 덤불 쪽으로 다가간다   (1.0 ~ 2.2)  ← 여우가 귀 내미는 순간 도착
  ③ 여우와 마주친다 — 놀란다            (2.2 ~ 2.9)
  ④ **엉덩방아**                        (2.9 ~ 5.1)  ← 여우가 나와 있는 내내
  ⑤ 쭈그려 여우를 살핀다                (5.1 ~ 8.0)

## 무대 (`assets/anchors/path_fox.json`)
  · 갈 수 있는 땅 = 사다리꼴 길 (소실점 y455)
  · 지평선 455 · K = 400/(720−455) = 1.509
  · 덤불 앞 = 발 y 600 → 키 219

    python W1_2/fox_scene.py            # 좌표표
    python W1_2/fox_scene.py --render   # 그림으로
"""
import os
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import stage2d as S                                     # noqa: E402

BG = "path_fox"
OUT = "W1_2/_fox"
W, H = 1280, 720
FPS = 24

# 배경 사건 시각 (실측)
FOX_PEEK = 2.2                  # 귀만 빼꼼
FOX_OUT = 2.9                   # 완전히 나옴
FOX_HIDE = 5.5                  # 숨기 시작

# 자리 — 길 위. 덤불은 오른쪽(x≈750)
ENTER = (280, 690)              # 왼쪽에서 들어오는 자리
BUSH = (640, 600)               # 덤불 앞 (여우와 마주 서는 자리)


def plan():
    st = S.Stage(BG)
    B, t = [], 0.0
    h_in = round(st.h_at(ENTER[1]))
    h_bush = round(st.h_at(BUSH[1]))

    # ① 왼쪽에서 걸어 들어온다 — ★타이밍을 당겼다(1.4초 → 1.0초)
    B.append((t, 1.0, "m6:walk_side_r", ENTER[0], 430,
              h_in, round((h_in + h_bush) / 2), ENTER[1], 645,
              "왼쪽에서 걸어 들어온다 (키 %d)" % h_in, (0, 10), 10.0, "lin"))
    t = 1.0

    # ② 살금살금 — 여우가 **귀 내미는 2.2초에 딱 도착**하게
    B.append((t, FOX_PEEK, "tiptoe", 430, BUSH[0],
              round((h_in + h_bush) / 2), h_bush, 645, BUSH[1],
              "살금살금 덤불 쪽으로 (★%.1f초 여우가 귀를 내민다)" % FOX_PEEK,
              (0, 64), 40.0, "lin"))
    t = FOX_PEEK

    # ★★자세가 달라도 **머리 지름이 같아야 같은 사람**이다 (사장님 지시 2026-08-13)
    #   "같은 위치인데 놀람과 옆으로 주저앉은 캐릭터, 쭈그려 앉은 캐릭터의 크기가
    #    차이가 난다. 정면으로 본 놀람과 쭈그려 앉은 캐릭터의 크기를 키워 봐."
    #   "**옆으로 놀라서 뒤로 넘어져 앉은 캐릭터의 크기만큼** 키워 줘."
    #
    #   실측 — 머리 지름: 엉덩방아 203 · 놀람 204 · 쭈그림 171
    #   잉크 높이로 맞추면 틀린다(쭈그림은 자세가 낮아 잉크가 430 밖에 안 된다).
    #   **엉덩방아(203)를 기준**으로 머리 지름을 맞추면 셋이 같은 사람이 된다.
    HEAD_REF = 203.0                      # 엉덩방아 머리 지름 = 기준
    HEAD = {"stickman_w1d2_surprise": 204.0,
            "stickman_w1d2_crouch_ground_r": 171.0}
    INK = {"stickman_w1d2_surprise": 740.0,
           "stickman_w1d2_crouch_ground_r": 430.0}

    # ★사장님 지시(2026-08-13) — "정면을 보고 놀란 표정, 쪼그려 앉기 **더 키워줘 20%**"
    #   머리로 맞춘 뒤에도 이 둘은 눈으로 보기에 작았다. 20% 더 키운다.
    BOOST = 1.20

    def draw_h(name, stand_h):
        """머리 지름을 기준에 맞춘 뒤, 그 자세의 잉크 높이만큼 그린다."""
        s = HEAD_REF / HEAD[name]         # 머리를 기준에 맞추는 배율
        return round(stand_h * INK[name] / 726.0 * s * BOOST)

    # ③ 마주친다 — 놀란다
    h_sur = draw_h("stickman_w1d2_surprise", h_bush)
    B.append((t, FOX_OUT, "POSE:stickman_w1d2_surprise", BUSH[0], BUSH[0],
              h_sur, h_sur, BUSH[1], BUSH[1],
              "여우와 마주쳐 놀란다 (머리 %d 기준 → 키 %d)" % (HEAD_REF, h_sur),
              (0, 1), 1.0, "lin"))
    t = FOX_OUT

    # ④ ★엉덩방아 — 여우가 나와 있는 내내
    B.append((t, FOX_HIDE, "butt_fall", BUSH[0], BUSH[0] - 40,
              h_bush, h_bush, BUSH[1], BUSH[1],
              "엉덩방아 (★%.1f초 여우가 나와 있다)" % FOX_OUT,
              (0, 64), 26.0, "lin"))
    t = FOX_HIDE

    # ⑤ 쭈그려 살핀다 — 머리 지름을 엉덩방아에 맞춘다(171 → 203 이므로 1.19배 키운다)
    h_cr = draw_h("stickman_w1d2_crouch_ground_r", h_bush)
    B.append((t, 8.0, "POSE:stickman_w1d2_crouch_ground_r", BUSH[0] - 40,
              BUSH[0] - 40, h_cr, h_cr, BUSH[1], BUSH[1],
              "쭈그려 여우를 살핀다 (머리 %d 기준 → 키 %d)" % (HEAD_REF, h_cr),
              (0, 1), 1.0, "lin"))
    return st, B, 8.0


def main():
    st, B, total = plan()
    print("여우 씬 — %.1f초 · 비트 %d개" % (total, len(B)))
    print("  지평선 %d · K %.3f · 밟을 수 있는 땅 %.1f%%\n"
          % (st.horizon, st.k, 100.0 * st.walk_mask().mean()))
    print("%5s %5s  %-30s %5s %5s  %4s %4s  %s"
          % ("시작", "끝", "컷", "x0", "x1", "키0", "키1", "설명"))
    for b in B:
        print("%5.1f %5.1f  %-30s %5d %5d  %4d %4d  %s"
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
    out = os.path.join(OUT, "fox_scene.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(fr, "f%04d.png"), "-c:v", "libx264",
                    "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out],
                   check=True)
    print("\n✅ %s  %d프레임 · %.1f초" % (out, n, n / float(FPS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
