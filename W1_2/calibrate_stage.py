# -*- coding: utf-8 -*-
"""배경마다 **원근을 눈으로 보고 정한다** — 동작 계산기의 무대 교정.

★배경은 저마다 자기 원근으로 그려져 있다. 계단 배경의 돌난간(1.0m)에 대어 보면
  기본 무대(90~600)로 세운 캐릭터가 1.2배쯤 크다. 배경 하나에 무대 하나여야 한다.

이 스크립트는 배경 위에 **같은 캐릭터를 여러 깊이로 세운 판**을 만들어 준다.
사장님이 보시고 "이게 맞다" 하시면 그 값을 앵커 파일 `stage` 에 적는다.

    python W1_2/calibrate_stage.py steps_seat
    python W1_2/calibrate_stage.py steps_seat 400 610x320   # 지평선 400, 발610에서 키320

앵커 파일에 적는 꼴:
    "stage": { "horizon": 400, "ref": [610, 320] }
      horizon — 지평선 화면 y (땅의 끝)
      ref     — [발 y, 그 자리에 선 **스틱맨의 화면 키**] 를 하나만 재 주면 된다
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

import render_show as R                                    # noqa: E402
import motion_planner as M                                 # noqa: E402

OUT = "W1_2/_stage"
FONT = r"C:\Windows\Fonts\malgun.ttf"
W, H = 1280, 720
POSE = "sm_arms_out_wide"                                  # 서 있는 기준 포즈


def sheet(bg, stage, note):
    os.makedirs(OUT, exist_ok=True)
    cv = R.img(R.bg_frames(bg, 1)[0]).copy()
    if cv.size != (W, H):
        cv = cv.resize((W, H), Image.LANCZOS)
    poses = R.load_poses()
    im = R.img(poses[POSE])
    A = M.Assets()

    # 화면 바닥부터 지평선까지 고르게 여섯 자리에 같은 사람을 세운다
    ys = []
    lo = stage.foot_at(stage.clamp_h(stage.H_FAR))
    hi = min(H - 8, stage.foot_at(stage.H_NEAR))
    for i in range(6):
        ys.append(lo + (hi - lo) * (i / 5.0))

    d = ImageDraw.Draw(cv)
    xs = [190, 350, 520, 700, 900, 1110]
    for x, y in zip(xs, ys):
        h = stage.clamp_h(stage.h_at(y))
        rh = A.render_h("POSE:" + POSE, h)
        rf = A.render_foot("POSE:" + POSE, y, h)
        R.place_xy(cv, im, x, rf, rh)
        d.line([(x - 70, y), (x + 70, y)], fill=(220, 30, 30), width=2)
        d.text((x - 66, y + 4), "발%d 키%d %.1fm" % (y, h, stage.depth_m(h)),
               font=ImageFont.truetype(FONT, 15), fill=(200, 0, 0))

    d.line([(0, stage.HORIZON), (W, stage.HORIZON)], fill=(0, 90, 220), width=2)
    d.text((10, stage.HORIZON - 22), "지평선 y=%d" % stage.HORIZON,
           font=ImageFont.truetype(FONT, 17), fill=(0, 60, 200))
    d.text((10, 10), note, font=ImageFont.truetype(FONT, 19), fill=(20, 20, 20))

    p = os.path.join(OUT, "%s_stage.png" % bg)
    cv.convert("RGB").save(p)
    print("  →", p)
    return p


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    bg = sys.argv[1]
    if len(sys.argv) >= 4:
        horizon = float(sys.argv[2])
        y, h = sys.argv[3].split("x")
        stage = M.Stage(horizon, (float(y), float(h)))
        note = "손으로 준 무대 — 지평선 %s · 발%s 에서 키%s" % (int(horizon), y, h)
    else:
        stage = M.load_stage(bg)
        cal = "배경 교정본" if stage is not M.STAGE else "기본 무대(90~600)"
        note = "%s — 지평선 %d · K=%.3f" % (cal, stage.HORIZON, stage.K)
    print("[%s] %s" % (bg, note))
    print("  발 y  →  스틱맨 키 · 거리")
    for y in range(int(stage.foot_at(stage.H_FAR)), H, 40):
        print("   %3d  →  %3.0fpx · %.1fm"
              % (y, stage.clamp_h(stage.h_at(y)), stage.depth_m(stage.h_at(y))))
    sheet(bg, stage, note)
    print("\n맞으면 assets/anchors/%s.json 에 이렇게 적는다:" % bg)
    print('  "stage": { "horizon": %d, "ref": [%d, %d] }'
          % (stage.HORIZON, 610, round(stage.h_at(610))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
