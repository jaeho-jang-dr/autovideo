# -*- coding: utf-8 -*-
"""지은 옆으로 걷는 동영상 생성 (검증된 Veo 8투명컷 순환 방식).

에셋: assets/graphics/poses/jieun_w19_walk_{r,l}_0..7.png (Veo 걷기영상에서 추출·정합)
방식: 8투명컷을 HOLD 프레임씩 순서대로 순환하며 x좌표를 진행 → 진짜 교차 스트라이드 걷기.
      왼쪽(돌아오기)은 오른쪽 컷 좌우반전. (memory: character-walk-veo-cutout-method)

사용 예:
  python make_jieun_walk.py                         # 오른쪽 걷기, 기본값
  python make_jieun_walk.py --dir left              # 왼쪽(돌아오기)
  python make_jieun_walk.py --dir both              # 오른쪽 + 왼쪽 둘 다
  python make_jieun_walk.py --hold 6 --fps 24       # 더 느리고 부드럽게
  python make_jieun_walk.py --bg FFFFFF --scale 0.62 --out scratch/test.mp4
"""
import os
import glob
import argparse
import subprocess
from PIL import Image

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
POSE = "assets/graphics/poses"
SEQ = "scratch/w19_walk/_seq_make"


def load_cuts(direction):
    """오른쪽/왼쪽 8투명컷 로드. 왼쪽 컷이 없으면 오른쪽 좌우반전으로 생성."""
    rights = sorted(glob.glob(f"{POSE}/jieun_w19_walk_r_*.png"),
                    key=lambda p: int(p.split("_")[-1].split(".")[0]))
    if not rights:
        raise SystemExit("오른쪽 걷기 컷(jieun_w19_walk_r_*.png)이 없습니다. veo_walk_cutout.py 먼저 실행하세요.")
    if direction == "right":
        return [Image.open(p).convert("RGBA") for p in rights]
    # 왼쪽 = 오른쪽 좌우반전 (방향 반전엔 flip이 맞다)
    lefts = sorted(glob.glob(f"{POSE}/jieun_w19_walk_l_*.png"),
                   key=lambda p: int(p.split("_")[-1].split(".")[0]))
    if len(lefts) == len(rights):
        return [Image.open(p).convert("RGBA") for p in lefts]
    return [Image.open(p).convert("RGBA").transpose(Image.FLIP_LEFT_RIGHT) for p in rights]


def make_walk(direction, out_mp4, bg_hex, scale_ratio, fps, hold, bw, bh, stride):
    frs = load_cuts(direction)
    CW, CH = frs[0].size
    bg_rgb = tuple(int(bg_hex[i:i + 2], 16) for i in (0, 2, 4))
    bg = Image.new("RGB", (bw, bh), bg_rgb)

    scale = int(bh * scale_ratio) / CH
    cw2, ch2 = int(CW * scale), int(CH * scale)
    regr = [f.resize((cw2, ch2)) for f in frs]

    cyc = len(regr) * hold
    step = cw2 * stride                       # 한 사이클당 전진 거리
    if direction == "right":
        x0, x1 = -cw2, bw
    else:
        x0, x1 = bw, -cw2
    nframes = max(1, int(abs(x1 - x0) / step * cyc))
    foot_y = int(bh * 0.965) - ch2            # 발끝을 화면 하단 근처에 접지

    os.makedirs(SEQ, exist_ok=True)
    for fn in os.listdir(SEQ):
        os.remove(os.path.join(SEQ, fn))
    for k in range(nframes):
        fr = bg.copy()
        x = int(x0 + (x1 - x0) * (k / max(1, nframes - 1)))
        pose = regr[(k // hold) % len(regr)]
        fr.paste(pose, (x, foot_y), pose)
        fr.save(f"{SEQ}/f{k:04d}.png")

    os.makedirs(os.path.dirname(out_mp4) or ".", exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-framerate", str(fps), "-i", f"{SEQ}/f%04d.png",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_mp4],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    dur = nframes / fps
    print(f"  {direction:5s} → {out_mp4}  ({nframes}프레임 / {dur:.1f}초)")
    return dur


def main():
    ap = argparse.ArgumentParser(description="지은 옆으로 걷는 동영상 생성")
    ap.add_argument("--dir", choices=["right", "left", "both"], default="right",
                    help="걷는 방향 (기본 right)")
    ap.add_argument("--out", default=None, help="출력 mp4 경로 (기본 assets/videos/jieun_walk_<dir>.mp4)")
    ap.add_argument("--bg", default="E0E8F0", help="배경 hex 색 (기본 E0E8F0 연회색블루). 흰색=FFFFFF")
    ap.add_argument("--scale", type=float, default=0.62, help="캐릭터 세로 비율 (0~1, 기본 0.62)")
    ap.add_argument("--fps", type=int, default=12, help="프레임레이트 (기본 12)")
    ap.add_argument("--hold", type=int, default=4, help="컷당 유지 프레임 = 속도(클수록 느림, 기본 4)")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--stride", type=float, default=0.55, help="한 사이클당 전진 보폭(컷너비 배수, 기본 0.55)")
    args = ap.parse_args()

    dirs = ["right", "left"] if args.dir == "both" else [args.dir]
    print("지은 걷기 영상 생성:")
    for d in dirs:
        out = args.out if (args.out and args.dir != "both") else f"assets/videos/jieun_walk_{d}.mp4"
        make_walk(d, out, args.bg.lstrip("#"), args.scale, args.fps, args.hold,
                  args.width, args.height, args.stride)
    print("완료.")


if __name__ == "__main__":
    main()
