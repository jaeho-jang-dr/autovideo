# -*- coding: utf-8 -*-
"""태권도 씬에 **관중 속 스틱맨**을 세운다.

★사장님 지시(2026-08-18, 교정앱 r21 #1)
  "여기서 스틱맨이 등장하는데, 왼편 긴머리 도복 아가씨 실루엣의 **더 왼쪽**에서
   사람들 중 **아이 크기**만 하게, **우측 3/4** 스틱맨을 찾아서 **정지 이미지로
   이 씬 전체에** 넣어줘."

## 왜 필요한가
나레이션은 "Stickman cheers from among the crowd" 라고 말하는데 화면에 스틱맨이
없었다. 말과 그림이 어긋난 자리다.

## 어디에 세우나
왼편 관중 실루엣을 확대해 재 보니 긴머리 실루엣이 **x≈52 · 발 y≈480 · 키 180px**
이었다. 그 **더 왼쪽**(x 30)에 **아이 크기(키 105px)** 로 세운다 — 관중 키의 약 60%.
정지 이미지이므로 씬 내내 같은 자리에 서서 손을 들고 있는다.

  python W1_2/tkd_add_stickman.py
"""
import glob
import os
import subprocess
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))

SRC = "W1_2/motion6/tkd_show_v7.mp4"
TMP = "W1_2/_tkd"
POSE = "assets/graphics/poses/w12_sm_greeting_wave.png"   # 손을 들어 환호
X, FOOT_Y, H = 30, 480, 158                               # 관중 속 · 사장님 지시로 50% 키움
W, HH, FPS = 1280, 720, 24


def find_pose():
    import render_show as R
    p = R.load_poses()
    for k in ("sm_greeting_wave", "sm_presenting"):
        if k in p:
            return p[k]
    raise SystemExit("포즈 없음")


def main():
    d = os.path.join(TMP, "f")
    os.makedirs(d, exist_ok=True)
    if not glob.glob(d + "/*.png"):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", SRC,
                        "-vf", "scale=%d:%d" % (W, HH), os.path.join(d, "f%04d.png")],
                       check=True)
    fs = sorted(glob.glob(d + "/*.png"))
    pose = Image.open(find_pose()).convert("RGBA")
    k = H / float(pose.height)
    fig = pose.resize((max(1, round(pose.width * k)), H), Image.LANCZOS)
    # 발바닥(알파 맨 아랫줄)을 FOOT_Y 에 맞춘다
    import numpy as np
    a = np.asarray(fig)[:, :, 3] > 8
    rows = np.nonzero(a.any(1))[0]
    sole = int(rows[-1]) if len(rows) else fig.height - 1

    od = os.path.join(TMP, "out")
    os.makedirs(od, exist_ok=True)
    for f in glob.glob(od + "/*.png"):
        os.remove(f)
    for i, fp in enumerate(fs):
        im = Image.open(fp).convert("RGBA")
        im.alpha_composite(fig, (X, FOOT_Y - sole))
        im.convert("RGB").save(os.path.join(od, "f%04d.png" % i))
    v = 8 + len(glob.glob("W1_2/motion6/tkd_show_v*.mp4")) - 7
    out = "W1_2/motion6/tkd_show_v%d.mp4" % v
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
                    "-i", os.path.join(od, "f%04d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                    "-pix_fmt", "yuv420p", out], check=True)
    print("%s  %d프레임 · 스틱맨 x%d 발y%d 키%d" % (out, len(fs), X, FOOT_Y, H))


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
