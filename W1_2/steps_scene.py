# -*- coding: utf-8 -*-
"""계단 씬 — **실측 좌표로** 올라가 앉고, 한 칸씩 내려와 달려 나간다.

★사장님 지시(2026-08-13)
  "계단 중간에 있는 큰 돌 넓은 돌판에 앉을 때는 **정면 앉기**로 하고,
   계단을 올라갈 때는 **저 멀리 걸어가기**로 가서 **돌아서서 정면 보고 앉는다**.
   일어나서 계단을 내려올 때는 **정면 걸어오기**를 하면서 좌표를 앞으로 아래로
   **하나 둘 셋 넷 다섯 계단만큼** 이동한 후 **우측으로 돌아서 달려 나간다**."
  "서서 **콩콩콩** 뛰어 내려도 된다. 좌표만 잘 잡아 봐라." / "멋지게 걸어 내려와도 되고."

## 실측 — 계단 디딤판 y (steps_seat.png · 1280×720)
    0칸 682  1칸 640  2칸 607  3칸 591  4칸 569  5칸 544  6칸 525  7칸 509
    8칸 486  9칸 463  10칸 439 ← **넓은 돌 평상**이 이 칸 위에 얹혀 있다
   11칸 423 12칸 404 13칸 381 14칸 360 15칸 341 16칸 323 17칸 306

  · 아래로 갈수록 칸 간격이 **넓어진다**(가까우니까) — 42, 33, 16, 22, 25, 19, 16, 23…
    그래서 한 칸씩 내려올 때 **똑같이 내려오면 안 되고 이 값을 그대로 써야** 한다.
  · 평상 앞에 서는 자리(발) = 10칸 바로 아래 = **463**
  · 앉을 때 엉덩이가 닿는 면 = 평상 윗면 **430**, 발은 앞 칸 **463**

## 원근 — 자리가 정해지면 키가 정해진다
`stage_solve` 가 이 배경에서 푼 값: 지평선 512 · K = 400/(720−512) = 1.923
    키 = 1.923 × (발y − 512)
    발 682 → 327   발 640 → 246   발 591 → 152   발 544 → 62   발 463 → **없어짐**

  ★계단은 **높아진 땅**이라 이 식이 그대로 듣지 않는다(계단을 오르면 멀어지지만
    올라간 만큼 화면에서 다시 내려온다). 그래서 계단 위 자리는 **손으로 잰 키**를 쓴다 —
    아래에서 위로 갈수록 고르게 줄어들도록 잡았다.

    python W1_2/steps_scene.py          # 좌표표를 찍어 본다
    python W1_2/steps_scene.py --render # 그림으로 그려 본다
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

FONT = r"C:\Windows\Fonts\malgun.ttf"
W, H = 1280, 720
OUT = "W1_2/_steps"

# 계단 디딤판 실측 (아래 0칸 → 위 17칸)
TREAD = [682, 640, 607, 591, 569, 544, 525, 509, 486, 463,
         439, 423, 404, 381, 360, 341, 323, 306]
# ★넓은 돌 평상 — 실측(seat_measure.py)
#   윗면 430 · 앞면 아래 463 · **그 앞 칸 486**
#   사장님 지적 2026-08-13: "그 위에 넓은 돌판 평상, **그 앞에 서 있어야지**."
#   → 서는 자리는 평상 앞 칸 **486**(9칸). 앉으면 엉덩이가 430, 발은 앞 칸 486 에 놓인다.
SEAT_TOP = 430                     # 평상 윗면 — 앉았을 때 엉덩이
SEAT_FRONT = 463                   # 평상 앞면 아래끝
STAND_STEP = 8                     # 평상 앞에 서는 칸 (TREAD[8] = 486)
SEAT_FOOT = 486                    # 앉았을 때 발이 놓이는 앞 칸

# ★계단 칸마다의 화면 키 — **무대 공식과 이어 붙인다**
#   무대(stage_solve): 지평선 512 · K = 400/(720−512) = 1.923 → 키 = 1.923×(발y−512)
#     평지 y700 → 362 · 계단 0칸 y682 → 327 · 1칸 y640 → 246
#   계단을 오르면 그 식이 안 듣는다(높아진 땅이라 올라간 만큼 화면에서 도로 내려온다).
#   그래서 **맨 아래 칸은 공식값(327)에 못 박고**, 위로는 평상 앞 칸(8칸)의 190 까지
#   고르게 줄인다. 이렇게 해야 계단을 다 내려와 평지로 나설 때 327→362 로 **커진다** —
#   손으로 400 을 박아 놨더니 평지(362)가 더 작아져 뒤로 물러나 보였다(2026-08-13).
#   ★2026-08-13 갱신 — 엔진(`stage2d`)의 **계단 구역** 값과 맞춘다.
#     앞줄 400 을 그대로 끌고 올라가니 캐릭터가 계단 폭을 넘었다(확인 그림).
#     계단 구역: y306(맨 위)=80 · y682(맨 아래)=240 으로 줄였다.
HORIZON, K = 512.0, 400.0 / (720.0 - 512.0)
BOTTOM_H = 240.0                           # 계단 0칸(y682)
SEAT_H = 150.0                             # 평상 앞 칸(8칸 y486)

# ★계단 없는 평지 — 오른편으로 달려 나갈 땅 (사장님 지시 2026-08-13
#   "다 내려오면 계단 없는 곳 오른편으로 달려 나갈 수 있는 땅 좌표·키 높이도 계산하고")
#   실측 — 계단은 x 210~1075 사이에만 있다. 그 아래·오른쪽은 트인 포장이다.
#   평지 발 y = 700 (계단 맨 아래 칸 682 보다 앞). 그 자리의 키는 무대식으로 푼다:
#   지평선 512 · K = 400/(720−512) = 1.923  →  키 = 1.923 × (700−512) = 362
FLOOR_Y = 700
FLOOR_H = 362
STAIR_X0, STAIR_X1 = 210, 1075     # 계단이 차지하는 가로 범위(실측)


def h_at_step(i):
    """i 칸에 선 스틱맨의 화면 키 — 칸이 올라갈수록 고르게 준다."""
    t = min(1.0, max(0.0, i / float(STAND_STEP)))
    return round(BOTTOM_H + (SEAT_H - BOTTOM_H) * t)


def plan():
    """(t0, t1, 컷키, x0, x1, h0, h1, 발y0, 발y1, 설명[, (컷 i0, i1)])

    ★마지막 칸이 있으면 그 컷에서 **그 토막만** 돌린다. 8초 클립에는 쓸 수 없는
      구간이 섞여 있어서다(정강이가 잘리는 프레임 등).
    """
    cx = 640
    B = []
    t = 0.0

    S = STAND_STEP                                  # 평상 앞 칸 = 8칸(y 486)

    # ★★계단은 **반스트라이드당 한 칸**이다 (사장님 지시 2026-08-13)
    #   "올라가는 것이 걷는 것이 아니고 어색하다. 컷을 자르면서 사이즈를 줄이려니 그런 것
    #    같은데, **걷는 동작을 아주 빠르게 렌더해서 반스트라이드당 계단 하나씩** 올라가게
    #    만들면 된다."
    #   → 옛 판은 5초 동안 위치를 죽 미끄러뜨렸다. 발이 딛는 박자와 계단이 따로 놀아
    #     걷는 것으로 안 보였다. 이제 **반스트라이드마다 위치를 딱 한 칸씩 옮긴다.**
    #   실측 — `walk_exit_back` 4컷이 한 스트라이드 → **반스트라이드 = 2컷**
    HALF = 2                                        # 반스트라이드 컷 수
    STEP_SEC = 0.30                                 # 한 칸(=반스트라이드)에 쓰는 시간

    # ① ★걸어 올라가기 — **반스트라이드마다 한 칸씩, 그 안에서는 크기 고정**
    #    (사장님 지시 2026-08-13)
    #    "사이즈는 계단 한 칸마다 줄이면 되니, **반스트라이드 컷 같은 사이즈**,
    #     그다음 반스트라이드 컷 같은 사이즈로 한 칸 윗계단, 또 그다음 연결 반스트라이드,
    #     이렇게 만들어서 **자연스러운 걸음걸이**로 만들어 줘."
    #    → 크기를 죽 보간하면 걸음마다 몸이 스멀스멀 줄어 어색하다. 반스트라이드
    #      **한 토막 안에서는 키·발 y 를 그대로 두고**, 토막이 바뀔 때 다음 칸 값으로
    #      건너뛴다. 걷는 컷은 토막을 이어 붙여 끊기지 않고 돈다.
    up_fps = HALF / STEP_SEC                        # 한 토막에 2컷 = 6.7fps
    for k in range(S):
        i1 = k + 1                                  # 이 반스트라이드가 딛는 칸
        j = (k % 2) * HALF                          # 컷을 번갈아 이어 붙인다
        B.append((t, t + STEP_SEC, "walk_exit_back", cx, cx,
                  h_at_step(i1), h_at_step(i1), TREAD[i1], TREAD[i1],
                  "%d/%d칸 (y %d · 키 %d 고정)"
                  % (k + 1, S, TREAD[i1], h_at_step(i1)),
                  (j, j + HALF), up_fps, "lin"))
        t += STEP_SEC

    # ② ★돌아서기 대신 **달리기의 첫 정지 프레임 한 장** (사장님 지시)
    #    "돌아서는 옆모습은 그 달리기의 첫 정지 영상으로 대체하고 **바로 앉는다**."
    #    회전 컷을 넣으면 옆모습이 길게 돌아 어색했다. 한 장만 스치듯 지나간다.
    B.append((t, t + 0.25, "m6:run_side_r", cx, cx,
              h_at_step(S), h_at_step(S), TREAD[S], TREAD[S],
              "달리기 첫 컷 한 장 (돌아서기 대체)", (0, 1), 1.0))
    t += 0.25

    # ③④⑤ ★앉기 — `sit_stand_front` 64컷을 **구간으로 나눠** 쓴다.
    #   실측(2026-08-13) — 이 컷은 앉아 있는 동안 정강이 아래가 잘린다. Flow 를 네 번
    #   돌려도(정면·3/4 · Omni·Veo) 같은 자리에서 끊겼다. 대신 **앉는 과정과 일어서는
    #   과정은 다리가 온전**하므로 그 두 토막만 쓰고, 가운데는 앉은 컷 하나를 붙든다.
    #   평상이 정강이를 가리는 자리라 화면에서는 자연스럽게 읽힌다.
    #     0~10  서 있기 · 11~19 앉는 과정(온전) · 24~39 앉아 있기(잘림)
    #     40~47 일어서는 과정(온전) · 48~63 서 있기
    B.append((t, t + 2.0, "sit_stand_front", cx, cx,
              h_at_step(S), h_at_step(S), SEAT_FOOT, SEAT_FOOT,
              "평상에 정면으로 앉는다 (컷 11~19 · 엉덩이 %d · 발 %d)"
              % (SEAT_TOP, SEAT_FOOT), (11, 20)))
    t += 2.0

    B.append((t, t + 4.0, "sit_stand_front", cx, cx,
              h_at_step(S), h_at_step(S), SEAT_FOOT, SEAT_FOOT,
              "앉아서 설명한다 (컷 30 붙듦)", (30, 31)))
    t += 4.0

    B.append((t, t + 2.0, "sit_stand_front", cx, cx,
              h_at_step(S), h_at_step(S), TREAD[S], TREAD[S],
              "일어서서 평상 앞에 선다 (컷 40~47)", (40, 48)))
    t += 2.0

    # ⑥ ★**정면으로 보고** 반스트라이드당 한 칸씩 내려온다 (사장님 지시)
    #    "내려 올 때는 정면으로 보고 반스트라이드당 한 칸씩 내려와서"
    #    `run_front` 44컷이 다섯 스트라이드 → 한 스트라이드 ≈ 8.8컷, **반 ≈ 4컷**.
    #    올라갈 때와 같은 박자(0.30초)로 여덟 칸을 내려온다.
    #    ★올라갈 때와 같은 방식 — **반스트라이드 한 토막 = 한 칸, 그 안에서는 크기 고정**
    DN_HALF = 4                                      # run_front 의 반스트라이드 컷 수
    dn_fps = DN_HALF / STEP_SEC
    for k in range(S):
        i1 = S - k - 1                               # 이 반스트라이드가 딛는 칸
        j = (k % 2) * DN_HALF
        B.append((t, t + STEP_SEC, "run_front", cx, cx,
                  h_at_step(i1), h_at_step(i1), TREAD[i1], TREAD[i1],
                  "%d/%d칸 내려옴 (정면 · y %d · 키 %d 고정)"
                  % (k + 1, S, TREAD[i1], h_at_step(i1)),
                  (j, j + DN_HALF), dn_fps, "lin"))
        t += STEP_SEC

    # ⑦ ★내려오면 **달리기 정지 프레임 한 장**만 끼우고 곧바로 달린다 (사장님 지시)
    #    "다 내려와서 오른편으로 돌 때 그 **달리기의 정지영상만 하나** 연결하고
    #     다음으로 달려 나간다."
    B.append((t, t + 0.25, "m6:run_side_r", cx, cx,
              h_at_step(0), FLOOR_H, TREAD[0], FLOOR_Y,
              "달리기 첫 컷 한 장 (돌기 대체)", (0, 1), 1.0))
    t += 0.25

    # ⑧ ★제자리 없이 곧바로 달려 나간다
    #    (사장님: "달리기는 처음에 제자리이던데 **제자리는 하지 말고** 빠르게 우측으로")
    #    → 옛 판은 x 를 smoothstep 으로 밀어 시작이 느렸다. 이제 **선형**으로 민다.
    #      비트 마지막 칸에 `lin` 을 달아 두면 렌더가 가속 없이 등속으로 움직인다.
    B.append((t, t + 2.4, "m6:run_side_r", cx, 1620,
              FLOOR_H, FLOOR_H, FLOOR_Y, FLOOR_Y,
              "제자리 없이 곧바로 오른쪽으로 달려 나간다 (x %d→1620)" % cx,
              (0, 20), 24.0, "lin"))
    t += 2.4
    return B, t


def main():
    B, total = plan()
    print("계단 씬 — %.1f초 · 비트 %d개\n" % (total, len(B)))
    print("%5s %5s  %-18s %5s %5s  %4s %4s  %s"
          % ("시작", "끝", "컷", "x0", "x1", "키0", "키1", "설명"))
    for b in B:
        t0, t1, key, x0, x1, h0, h1, f0, f1, note = b[:10]
        print("%5.1f %5.1f  %-18s %5d %5d  %4d %4d  %s"
              % (t0, t1, key, x0, x1, h0, h1, note))

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
    bg = Image.open("W1_2/bg/steps_seat.png").convert("RGB").resize((W, H), Image.LANCZOS)
    FPS = 24
    n = 0
    for i in range(int(total * FPS)):
        t = i / float(FPS)
        cv = bg.copy().convert("RGBA")
        for b in B:
            t0, t1, key, x0, x1, h0, h1, f0, f1 = b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7], b[8]
            if not (t0 <= t < t1):
                continue
            raw = (t - t0) / max(1e-6, t1 - t0)
            # ★마지막 칸이 "lin" 이면 **등속**으로 민다 — smoothstep 은 시작이 느려서
            #   달려 나가는 첫머리가 제자리처럼 보였다(사장님 지적 2026-08-13).
            u = raw if (len(b) > 12 and b[12] == "lin") else smooth(raw)
            x, h, fy = lerp(x0, x1, u), lerp(h0, h1, u), lerp(f0, f1, u)
            if key.startswith("POSE:"):
                p = poses.get(key[5:])
                if not p:
                    continue
                im = R.img(p)
            else:
                fs = cuts.get(key)
                if not fs:
                    continue
                # ★비트에 컷 구간이 실려 있으면 그 토막만, 실린 fps 로 돌린다
                i0, i1 = (b[10] if len(b) > 10 else (0, len(fs)))
                fps_cut = b[11] if len(b) > 11 else 8.0
                i0 = max(0, min(i0, len(fs) - 1))
                i1 = max(i0 + 1, min(i1, len(fs)))
                im = R.img(fs[i0 + int((t - t0) * fps_cut) % (i1 - i0)])
            R.place_xy(cv, im, x, fy, h)
        cv.convert("RGB").save(os.path.join(fr, "f%04d.png" % n))
        n += 1
    out = os.path.join(OUT, "steps_scene.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(fr, "f%04d.png"), "-c:v", "libx264",
                    "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out],
                   check=True)
    print("\n✅ %s  %d프레임 · %.1f초" % (out, n, n / float(FPS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
