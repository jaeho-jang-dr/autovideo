# -*- coding: utf-8 -*-
"""W1-2 씬 렌더 — 동선표(`scene_defs.SCENES`)대로 **동작 먼저** 그린다.

★사장님 지시(2026-08-12): "동작 먼저, 나레이션 자막 나중."
  배경 사건에 맞물리는 동작을 중심에 놓고 앞뒤로 이어 붙인다.
  **자르지 말고 확대하지 마라. 원근법을 쓰라.**

· 배경 : 1280×720 원본 그대로(크롭 없음). 동영상은 끝나면 마지막 프레임 유지
· 캐릭터 : 원본 컷을 **축소만**. 좌표·크기·발 y 를 한꺼번에 보간해 원근을 만든다
· 겹침 : **발이 아래일수록 나중에** 그려 앞이 뒤를 덮는다
· 동작 : 원속(8fps). 비트 길이가 컷 길이보다 길면 그 안에서 되풀이한다

    python W1_2/render_scenes.py          # 전부
    python W1_2/render_scenes.py 3        # 앞 3씬만
"""
import glob
import os
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import render_show as R                                  # noqa: E402  자산 로더 재사용
import scene_defs as S                                   # noqa: E402

OUT = "W1_2/_scenes"
FPS = 24

# ★전경 캐릭터가 화면에서 너무 크다 (사장님 지시 2026-08-15 —
#   "앞에서 렌더링 하는 캐릭터의 사이즈를 좀 줄여 **600 사이즈**로 줄여줘",
#    그리고 한 판 더 보신 뒤 "**정면 캐릭터 키 축소** 해줘").
#   동작컷 원본이 717px 기준이므로 그 비율을 고르게 먹인다. 발 y 는 건드리지 않아
#   지면에서 뜨지 않고, 씬마다 잡아 둔 원근 비율도 그대로 유지된다.
#     1차 600/717 = 0.837  → 아직 크다
#     2차 516/717 = 0.720  ← 지금 값. 앞에 선 나레이터가 460 → 331 로 내려온다
CHAR_SCALE = 516.0 / 717.0

# ★정면으로 서서 설명하는 나레이터는 한 번 더 줄인다.
#   달리기·구르기 같은 동작은 커야 잘 보이지만, 제자리에서 말하는 정면 포즈가 크면
#   화면을 가득 채워 답답하다. 사장님이 콕 집어 "정면 캐릭터"라 하신 자리다.
FRONT_POSES = ("sm_presenting", "sm_greeting_wave", "sm_counting_five",
               "sm_arms_out_wide", "sm_holding_mirror", "stickman_w1d2_sit_front")
FRONT_SCALE = 0.88
CUT_FPS = 8.0                     # 기본 원속 (64컷 ÷ 8초)
W, H = 1280, 720

# ★스트라이드 속도 (사장님 확정 2026-08-13)
#   "스트라이드 속도가 너무 느리다. 슬로비디오로 움직인다.
#    걷는 것은 딱 맞아서 좋고, **옆으로 달리기는 두 배**,
#    **앞으로 뒤로 달려 나가고 나오는 것은 세 배** 정도는 되어야 맞는다."
#   ※ 이동 속도가 아니라 **발이 구르는 속도**다 — 컷 재생 fps 를 올린다.
SPEED = {
    "run_front": 3.0, "run_back": 3.0,        # 앞으로·뒤로 달리기 → 3배
    "m6:run_side_r": 2.0, "m6:run_side_l": 2.0,   # 옆으로 달리기 → 2배
    "m6:run_turn_r": 2.0, "m6:run_turn_l": 2.0,
    "m6:run_exit_r": 2.0, "m6:run_exit_l": 2.0,
    "zman_run_side": 2.0, "zman_run_side_l": 2.0,
    "zgirl_run_side": 2.0, "zgirl_run_side_l": 2.0,
    # 걷기는 그대로 1.0 (지금이 딱 맞다)
}


def fps_of(key):
    return CUT_FPS * SPEED.get(key, 1.0)


def h_of(key, h):
    """정면으로 서서 설명하는 포즈는 한 번 더 줄여 얹는다."""
    k = key[5:] if key.startswith("POSE:") else key
    return h * (FRONT_SCALE if k in FRONT_POSES else 1.0)


def lerp(a, b, u):
    return a + (b - a) * u


def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


# ★비트가 길어지면 **동작 계산기**(motion_planner.py)가 계산해 실어 보낸 값이다.
#   (t0,t1,키,x0,x1,h0,h1) 7 — 옛 손글씨 비트
#              +(f0,f1)   9 — 발 y 를 직접 지정 (난간·평상처럼 땅이 아닌 자리)
#              +(fps)    10 — ★발이 안 미끄러지는 재생속도
#              +(i0,i1)  12 — ★그 컷에서 **실제 동작이 일어나는 토막**만 쓴다
def cut_frame(beat, key, t_local, cuts):
    """이 순간 이 비트가 보여 줄 컷 한 장."""
    fs = cuts.get(key)
    if not fs:
        return None
    fps = beat[9] if len(beat) >= 10 else fps_of(key)
    i0, i1 = (beat[10], beat[11]) if len(beat) >= 12 else (0, len(fs))
    i0 = max(0, min(i0, len(fs) - 1))
    i1 = max(i0 + 1, min(i1, len(fs)))
    return fs[i0 + int(t_local * fps) % (i1 - i0)]


def main():
    # 인자 없음 → 전부 / 숫자 → 앞 N씬 / --only 8,9 → 그 씬만
    args = sys.argv[1:]
    only = limit = None
    if args and args[0] in ("--only", "-o"):
        only = {int(x) for x in args[1].split(",")}
    elif args:
        limit = int(args[0])

    cuts, poses = R.load_cuts(), R.load_poses()
    if only:
        scenes = [s for s in S.SCENES if s[0] in only]
        if not scenes:
            print("★그런 씬이 없다:", sorted(only))
            return 1
    else:
        scenes = S.SCENES[:limit] if limit else S.SCENES

    frames_dir = os.path.join(OUT, "_frames")
    os.makedirs(frames_dir, exist_ok=True)
    for f in glob.glob(os.path.join(frames_dir, "*.png")):
        os.remove(f)

    k = 0
    for n, bg, sec, ein, eout, beats, extra in scenes:
        nf = int(sec * FPS)
        bfs = R.bg_frames(bg, nf)
        ev = S.EVENT.get(bg)
        print("  S%-2d %-15s %2d초 · 비트 %d · 곁들이 %d%s"
              % (n, bg, sec, len(beats), len(extra),
                 ("  ★%s %.2fs" % ev) if ev and ev[1] is not None
                 else ("  · %s" % ev[0]) if ev else ""))
        for i in range(nf):
            t = i / float(FPS)
            cv = R.img(bfs[i]).copy()
            if cv.size != (W, H):
                cv = cv.resize((W, H), Image.LANCZOS)

            draw = []                                    # (발 y, 이미지, x, 키)

            # ── 곁들이 ──
            #   (키, x, 키높이)            = 씬 내내 제자리에서 도는 것
            #   (t0,t1,키,x0,x1,h0,h1[,f0,f1]) = ★시간을 갖는 둘째 캐릭터
            for item in extra:
                if len(item) == 3:
                    key, x, h = item
                    fo = None
                else:
                    t0, t1, key, x0, x1, h0, h1 = item[:7]
                    if not (t0 <= t < t1):
                        continue
                    u = smooth((t - t0) / max(1e-6, t1 - t0))
                    x, h = lerp(x0, x1, u), lerp(h0, h1, u)
                    fo = lerp(item[7], item[8], u) if len(item) >= 9 else None
                    t = t                                  # (컷 위상은 아래에서 t0 기준)
                if key.startswith("POSE:"):
                    p = poses.get(key[5:])
                    if not p:
                        continue
                    im = R.img(p)
                else:
                    base_t = t if len(item) == 3 else (t - item[0])
                    fp = cut_frame(item if len(item) > 3 else (0, 0, key), key,
                                   base_t, cuts)
                    if not fp:
                        continue
                    im = R.img(fp)
                draw.append((fo if fo is not None else S.foot_of(h), im, x, h_of(key, h)))

            # ── 주인공 비트 ──
            #   비트는 7개짜리 (t0,t1,키,x0,x1,h0,h1) 또는
            #   ★8·9번째로 **발 y 를 직접 지정**할 수 있다 (f0,f1).
            #   난간·분수처럼 **땅이 아닌 곳에 몸을 두는** 자리에 쓴다.
            #   (사장님 지시 2026-08-13: "난간에 걸터앉은 캐릭터는 높이 조절하느라
            #    전체 크기를 줄였는데, **키는 유지하고** 걸터앉게 한다.")
            for b in beats:
                t0, t1, key, x0, x1, h0, h1 = b[:7]
                if not (t0 <= t < t1):
                    continue
                u = smooth((t - t0) / max(1e-6, t1 - t0))
                x = lerp(x0, x1, u)
                h = lerp(h0, h1, u)
                foot_override = lerp(b[7], b[8], u) if len(b) >= 9 else None
                if key.startswith("POSE:"):
                    p = poses.get(key[5:])
                    if not p:
                        continue
                    im = R.img(p)
                else:
                    fp = cut_frame(b, key, t - t0, cuts)
                    if not fp:
                        print("     ★컷 없음:", key)
                        continue
                    im = R.img(fp)
                draw.append((foot_override if foot_override is not None else S.foot_of(h),
                             im, x, h_of(key, h)))

            # ★원근 z-정렬 — 발이 아래일수록 나중에(앞에) 그린다
            for foot, im, x, h in sorted(draw, key=lambda d: d[0]):
                R.place_xy(cv, im, x, foot, h * CHAR_SCALE)

            cv.convert("RGB").save(os.path.join(frames_dir, "f%05d.png" % k))
            k += 1

    # ★판마다 새 이름으로 낸다 — 같은 이름을 덮으면 브라우저가 옛 판을 문다
    tag = ("s" + "_".join(str(n) for n in sorted(only))) if only else "scenes"
    base = os.path.join(OUT, "w1d2_%s" % tag)
    out, v = base + ".mp4", 2
    while os.path.exists(out):
        out, v = "%s_v%d.mp4" % (base, v), v + 1
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(frames_dir, "f%05d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-pix_fmt", "yuv420p", out], check=True)
    print("\n✅ %s  %d프레임 · %.1f초" % (out, k, k / float(FPS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
