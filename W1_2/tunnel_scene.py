# -*- coding: utf-8 -*-
"""터널분수 씬 — **스틱맨이 물 터널을 저 멀리까지 갔다가 돌아온다.**

★사장님 지시(2026-08-14) "이것으로 하고 스틱맨이 터널을 저 멀리까지 갔다가
  돌아오는 것으로 만들어 보자."

## 무대는 **2.5D 엔진**에게 물어본다 (사장님 지시 2026-08-14)
씬이 제 나름의 상수를 들고 있으면 그때뿐이다. 무대는 `W1_2/anchor_tunnel.py` 가
한 번 재서 `assets/anchors/perf_tunnel.json` 에 적어 두었고, 여기서는
`stage2d.Stage("perf_tunnel")` 에게 **키와 밟을 수 있는 땅을 물어보기만** 한다.

  키 = 0.45 × (발y − 321) · 발y 430 에서 49, 발y 715 에서 177
  ※배경 사람들이 작게 그려져 있어 기준 키도 그에 맞췄다. 나레이터 규격(앞줄 400)을
    그대로 쓰면 구경꾼의 두 배가 되어 혼자 거인이 된다.

## 동선 — 캐릭터랑 규칙 (사장님 지적 2026-08-14)
  "달리기 시작 전에 오른편 돌기는 하지 말고 **바로 달려 나가기**.
   멀리서 돌아 달려오기. **도착하면 원근을 세게 쓴다**."

  ① 처음부터 **뒷모습**으로 서 있다가 곧바로 달려 나간다 — 앞에서 도는 동작 없음
  ② 도는 것은 **저 끝에서 한 번뿐**
  ③ 돌아올 때는 카메라 코앞(발y 780)까지 와서 화면을 가득 채운다 — 원근이 세진다

## 컷
DB(`anim_char_poses`)에서 꺼내 쓴다 — 실파일이 있는 것만 나온다.
  run_back_r  44컷  멀어짐(뒷모습)
  run_front_r 44컷  돌아옴(앞모습)
  run_turn_r  64컷  돌아섬

## 배경
`perf_tunnel.mp4` 는 0~2.5초에 아치가 아직 서는 중이다. **터널이 다 선 뒤(2.5초~)만**
잘라 쓰고, 앞으로·거꾸로 오가게 이어 계속 서 있게 만든다.

    python W1_2/tunnel_scene.py            # 렌더
    python W1_2/tunnel_scene.py --check    # 크기만 확인(석 장)
"""
import argparse
import glob
import os
import sqlite3
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageOps

HI_UP = (24, 38)                         # 손을 들어 올리는 컷 구간

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

from stage2d import Stage                                   # noqa: E402  ★2.5D 엔진

DB = os.path.join(ROOT, "channel", "content.db")
BG = "W1_2/bg/perf_tunnel.mp4"
# ★파일 이름을 판마다 바꾼다 — 같은 이름으로 덮으면 브라우저가 예전 것을 물고 있어
#   "고쳤는데 똑같다"가 된다(2026-08-14). 판 번호는 지금 있는 것 다음 번호로.
OUT = None                               # main() 에서 정한다
TMP = "W1_2/_tunnel"
W, H, FPS = 1280, 720, 24

ST = Stage("perf_tunnel")                # 무대는 엔진이 안다
HOR = ST.horizon
K = ST.k
# ★멀리 가는 끝 — 배경에 **서 있는 실루엣과 키가 같아지는 자리**까지.
#   그 사람들은 54~76px 이고, 지금 무대(k=0.62)에서 그 키가 되는 곳이 발y 426 이다.
# ★앞에 서는 끝 — **나레이션 포지션**까지만. 더 밀면 발이 화면 밖으로 나간다.
#   원근은 자리를 밀어내는 게 아니라 **키가 달라지는 것**이다.
FAR, NEAR = 485.0, 700.0
BG_FROM = 60                             # 2.5초 — 터널이 다 선 뒤부터
# ★배경을 몇 배 느리게 흘릴지 (사장님 2026-08-18 "좀 느리게 계속 상영").
#   자른 배경은 132장(5.5초)뿐이라, 3배로 늘리면 16.5초가 정방향으로 흐른다.
BG_SLOW = 3

STRIDE_SEC = 0.30                        # 한 스트라이드 (수문장 씬과 같은 값)
ALPHA, FOCAL = 0.85, 1108.0              # 달리기라 보폭을 조금 크게
BETA = ALPHA * K / FOCAL
CPS = 22.0                               # 스트라이드당 컷 수 (44컷 ≈ 2스트라이드)


def cuts(name):
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT pose_name,file_path FROM anim_char_poses WHERE pose_name LIKE ? "
        "ORDER BY pose_name", (name + "_%",)).fetchall()
    con.close()
    fs = [f for p, f in rows if os.path.exists(f) and p[len(name) + 1:].isdigit()]
    if not fs:
        raise RuntimeError("컷 없음: " + name)
    return [Image.open(f).convert("RGBA") for f in fs]


def path_x(y):
    """터널 한가운데 — 소실점(문)에서 화면 앞 가운데로 살짝 벌어진다."""
    u = (y - HOR) / (NEAR - HOR)
    return 640 + (640 - 640) * u


def stand_h(y):
    return max(6.0, ST.h_at(y, "stickman"))          # ★엔진에게 물어본다


def strides_between(ya, yb):
    return abs(1.0 / (ya - HOR) - 1.0 / (yb - HOR)) / BETA


def y_at(ya, yb, u):
    ia, ib = 1.0 / (ya - HOR), 1.0 / (yb - HOR)
    return HOR + 1.0 / (ia + (ib - ia) * u)


def bg_frames():
    d = os.path.join(TMP, "bg")
    os.makedirs(d, exist_ok=True)
    if len(glob.glob(os.path.join(d, "*.png"))) != 192:
        for f in glob.glob(os.path.join(d, "*.png")):
            os.remove(f)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", BG,
                        os.path.join(d, "f%03d.png")], check=True)
    fs = sorted(glob.glob(os.path.join(d, "*.png")))[BG_FROM:]
    # ★배경은 **정상 방향으로만** 상영한다
    #   (교정앱 r4 #4 · 사장님 2026-08-15 — "필름을 뒤로 돌리지는 말고 배경은
    #    정상적으로 상영하고 캐릭터는 지금처럼 움직이면 된다")
    #   옛 코드는 `fs + fs[::-1]` 로 되감아 물줄기가 거꾸로 빨려 들어갔다.
    # ★교정(사장님 2026-08-18) — "터널분수의 배경은 **뒷걸음 치지 말고 세우지도 말고**
    #   사람이 앞으로 걷기만 **좀 느리게 계속 상영**하고."
    #   마지막 프레임을 물고 있게 했더니 사람들이 그 자리에 굳었다. 이제 각 프레임을
    #   `BG_SLOW` 번씩 물려 **느리게, 앞으로만** 흐르게 한다 — 멈추지도 되감기지도 않는다.
    return [f for f in fs for _ in range(BG_SLOW)]


# ★앞에서는 돌지 않는다 — 처음부터 뒷모습으로 서 있다가 곧바로 달려 나간다.
#   도는 것은 저 끝에서 한 번뿐. 도착은 카메라 코앞까지 와서 원근을 세게 쓴다.
# ★돌아설 때 다른 이미지를 끼우지 않는다 (사장님 2026-08-14
#   "돌아서 나올 때는 다른 이미지는 넣지 말고 바로 돌아서서 나온다").
#   저 끝에서 회전 컷 64장을 끼웠더니 거기서 멈춰 서서 도는 게 되었다.
#   뒷모습에서 앞모습으로 **바로 바뀌며** 곧장 달려 나온다.
# ★교정(r16 #1, 사장님 2026-08-17) — "손을 흔들고 앞으로 보면서 뒤로 달리는 것은
#   하지 말고, **그냥 뒷모습으로 달려 나가는 것**으로 바꾸어 줘."
#   돌아오는 구간(come)은 앞모습 컷을 뒤로 물리며 재생해 '앞을 보며 뒷걸음질'처럼
#   보였고, 끝의 손 인사(hi)도 함께 걷어냈다. 이제 뒷모습으로 저 끝까지 달려
#   나가는 한 동작만 남는다 — 물 터널을 지나 좌판으로 향하는 나레이션과도 맞는다.
# ★교정(한글판 r1 #2, 사장님 2026-08-17) — "여기 스틱맨이 **다시 달려 와야** 하는데
#   안 달려오고, 실루엣 사람들은 **뒤로 걷고** 있다. 이것을 정상적으로 걷게 하고
#   스틱맨도 앞으로 달려 오게 해."
#   · 실루엣이 뒤로 걸은 것은 **합성기가 영상을 앞뒤로 오가게 늘렸기 때문**이다
#     (나레이션이 영상보다 길었다). 정방향으로만 재생하도록 고쳤다.
#   · 돌아오는 구간은 되살린다. 앞서 뺀 것은 '앞을 보며 뒷걸음질' 로 보였기
#     때문인데, 그건 컷을 거꾸로 돌려서였다 — `come` 은 앞모습으로 다가오는
#     정상 재생이라 그대로 두면 된다.
PLAN = [
    # ★교정(사장님 2026-08-18) — "**캐릭터도 세우지 말고** 끝까지 달려 갔다가
    #   돌아 오게." 서 있는 구간(stand_back·far·hold)을 모두 걷어냈다.
    #   저 끝까지 갔다가 곧바로 돌아오는 한 동작만 남는다.
    ("go",   NEAR, FAR,  None),         # 뒷모습으로 저 끝까지
    ("come", FAR,  NEAR, None),         # 앞모습으로 곧바로 돌아온다
]


def compose(bgp, src, y):
    """★발은 **언제나 땅에 붙는다.**

    그림 아래끝이 아니라 **알파의 맨 아랫줄(실제 발바닥)** 을 발y 에 맞춘다.
    컷에 아래 빈 줄이 1px 있고 소수점을 버려서, 그림 높이로 앉히면 발이 1px 떠 있었다
    (검산으로 잡음, 2026-08-14). 키는 위치가 정한다 — `stand_h(y)` 는 엔진 값이다.
    """
    h = stand_h(y)
    k = h / float(src.height)
    im = src.resize((max(1, round(src.width * k)), max(1, round(h))), Image.LANCZOS)
    a = np.asarray(im)[:, :, 3] > 8
    rows = np.nonzero(a.any(1))[0]
    sole = int(rows[-1]) if len(rows) else im.height - 1      # 발바닥 줄
    cv = Image.open(bgp).convert("RGB")
    cv.paste(im, (int(round(path_x(y) - im.width / 2.0)), int(round(y)) - sole), im)
    return cv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    back, front, turn = cuts("run_back_r"), cuts("run_front_r"), cuts("run_turn_r")
    # ★인사(Hi) — 손을 든 컷은 화면 **왼편**으로 올라간다. 오른편으로 들게 뒤집는다.
    hi = [ImageOps.mirror(im) for im in
          [Image.open(p).convert("RGBA")
           for p in sorted(glob.glob("W1_2/motion6_cuts/high_five/*.png"))]]
    bgs = bg_frames()
    print("컷 — 멀어짐 %d · 돌아옴 %d · 돌아섬 %d · 배경 %d장"
          % (len(back), len(front), len(turn), len(bgs)))

    if a.check:
        sh = Image.new("RGB", (W, H * 3 // 2), (10, 10, 10))
        for i, y in enumerate((FAR, 540.0, NEAR)):
            im = compose(bgs[0], front[0], y).resize((W // 2, H // 2), Image.LANCZOS)
            sh.paste(im, ((i % 2) * (W // 2), (i // 2) * (H // 2)))
            ImageDraw.Draw(sh).text(((i % 2) * (W // 2) + 8, (i // 2) * (H // 2) + 6),
                                    "발y %d · 키 %d" % (y, round(stand_h(y))),
                                    fill=(255, 220, 120))
        sh.save("W1_2/_check/tunnel_fit.png")
        print("W1_2/_check/tunnel_fit.png")
        return 0

    segs, t = [], 0.0
    for what, ya, yb, dur in PLAN:
        if dur is None:
            dur = strides_between(ya, yb) * STRIDE_SEC
        segs.append((t, t + dur, what, ya, yb))
        t += dur
    total = t
    for t0, t1, what, ya, yb in segs:
        ns = strides_between(ya, yb) if what in ("go", "come") else 0
        print("  %-10s %5.1f~%5.1f초  발y %4.0f→%4.0f  %4.1f스트라이드"
              % (what, t0, t1, ya, yb, ns))
    print("  합계 %.1f초" % total)

    od = os.path.join(TMP, "out")
    os.makedirs(od, exist_ok=True)
    for f in glob.glob(os.path.join(od, "*.png")):
        os.remove(f)
    n = int(round(total * FPS))
    for i in range(n):
        tt = i / float(FPS)
        t0, t1, what, ya, yb = segs[-1]
        for s in segs:
            if tt < s[1]:
                t0, t1, what, ya, yb = s
                break
        u = 0.0 if t1 <= t0 else min(1.0, max(0.0, (tt - t0) / (t1 - t0)))
        if what in ("go", "come"):
            y = y_at(ya, yb, u)
            st = (tt - t0) / STRIDE_SEC
            seq = back if what == "go" else front
            src = seq[int(st * CPS) % len(seq)]
        elif what == "hi":
            # ★도착하면 바로 서서 **오른편 손**을 들어 인사한다.
            #   손 드는 구간은 24~38컷. 0.5초 안에 다 올리고 그대로 들고 있는다.
            y = ya
            j = HI_UP[0] + int(min(1.0, u / 0.25) * (HI_UP[1] - HI_UP[0]))
            src = hi[min(j, len(hi) - 1)]
        else:
            y = ya
            # ★`far` 는 저 끝에 **뒷모습으로**, `hold` 는 앞모습으로 선다.
            src = back[0] if what in ("stand_back", "far") else front[0]
        compose(bgs[i % len(bgs)], src, y).save(os.path.join(od, "f%03d.png" % i))

    v = 1 + len(glob.glob("W1_2/motion6/tunnel_scene_v*.mp4"))
    out = "W1_2/motion6/tunnel_scene_v%d.mp4" % v
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(od, "f%03d.png"), "-c:v", "libx264",
                    "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    out], check=True)
    print("%s  %d프레임 · %.1f초" % (out, n, n / float(FPS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
