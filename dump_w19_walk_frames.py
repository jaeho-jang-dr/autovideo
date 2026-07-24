# -*- coding: utf-8 -*-
"""W19 지은 걷기영상 → 약 5초 구간 전 프레임(24fps) 컷아웃 + 번호부여 → 뷰어로 표시.
   사용자가 한 스트라이드(왼발앞→오른발앞) 구간 번호를 고르면, 그 사이를 8등분해 최종 8컷 생성.
사용: python dump_w19_walk_frames.py
"""
import os, glob, subprocess
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
VID = "W19_package/Woman_walks_right_side_profile_202607221409.mp4"
SS, DUR, FPS = 0.4, 5.0, 24            # 0.4s부터 5초 = 약 120프레임
SEQ = "scratch/w19_walk/seq5"          # 원본 프레임(최종컷 재추출용)
OUT = "scratch/w19_walk/frames_numbered"  # 번호매긴 프리뷰
for d in (SEQ, OUT):
    os.makedirs(d, exist_ok=True)
    for f in glob.glob(f"{d}/*.png"):
        os.remove(f)

# 동일 규격(다른 포즈와 키 통일용)
CANVAS_W, CANVAS_H, FEET_Y, TARGET_BODY = 1024, 1280, 1210, 770

# 1) 원본 프레임 시퀀스 추출(네이티브 프레임 유지)
subprocess.run(["ffmpeg", "-y", "-ss", str(SS), "-t", str(DUR), "-i", VID,
                "-vsync", "0", "-start_number", "0", f"{SEQ}/%04d.png"],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
frames = sorted(glob.glob(f"{SEQ}/*.png"))
print(f"추출 프레임 {len(frames)}개 (t={SS}s부터 {DUR}s, {FPS}fps)")


def cutout_largest(arr):
    arr = arr.copy()
    rgb = arr[:, :, :3].astype(int)
    lo = rgb.min(axis=2); hi = rgb.max(axis=2)
    white = (lo > 200) & ((hi - lo) < 30)
    lbl, _ = ndimage.label(white)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1])
    border.discard(0)
    arr[np.isin(lbl, list(border)), 3] = 0
    a = arr[:, :, 3] > 0
    l2, n = ndimage.label(a)
    if n > 1:
        sizes = ndimage.sum(np.ones_like(l2), l2, range(1, n + 1))
        arr[l2 != int(np.argmax(sizes)) + 1, 3] = 0
    ys, xs = np.where(arr[:, :, 3] > 0)
    if len(ys) == 0:
        return None
    return arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def body_metrics(crop):
    alpha = crop[:, :, 3] > 0
    w = alpha.sum(axis=1).astype(float); H = len(w)
    torso = np.median(w[int(H * 0.42):int(H * 0.72)]) or w.max()
    thr = max(0.5 * torso, 0.12 * w.max())
    head_top = 0
    for y in range(H):
        if w[y] >= thr and np.mean(w[y:y + 22] >= thr * 0.6) > 0.6:
            head_top = y; break
    span = (H - 1) - head_top
    band = alpha[int(H * 0.42):int(H * 0.72)]
    bx = np.where(band.any(axis=0))[0]
    cx = int(bx.mean()) if len(bx) else crop.shape[1] // 2
    return span, cx


try:
    font = ImageFont.truetype("C:/Windows/Fonts/malgunbd.ttf", 60)
    fsm = ImageFont.truetype("C:/Windows/Fonts/malgun.ttf", 26)
except Exception:
    font = ImageFont.load_default(); fsm = font

# 2) 프레임마다 컷아웃 → 동일 키로 정규화(비율유지) → 번호 오버레이 → 프리뷰 저장
PW, scale_v = 440, 440 / CANVAS_W
PH = int(CANVAS_H * scale_v)
for i, fp in enumerate(frames):
    crop = cutout_largest(np.array(Image.open(fp).convert("RGBA")))
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (255, 255, 255, 255))
    if crop is not None:
        span, cx = body_metrics(crop)
        s = TARGET_BODY / span
        nw, nh = max(1, round(crop.shape[1] * s)), max(1, round(crop.shape[0] * s))
        im = Image.fromarray(crop).resize((nw, nh), Image.LANCZOS)
        canvas.paste(im, (CANVAS_W // 2 - round(cx * s), FEET_Y - nh), im)
    prev = canvas.convert("RGB").resize((PW, PH), Image.LANCZOS)
    d = ImageDraw.Draw(prev)
    # 발끝 기준선(빨강) — 스트라이드 비교용
    d.line([(0, int(FEET_Y * scale_v)), (PW, int(FEET_Y * scale_v))], fill=(255, 120, 120), width=1)
    # 큰 번호(좌상단, 노란 박스)
    d.rectangle([6, 6, 116, 78], fill=(255, 214, 0))
    d.text((16, 4), f"{i:02d}", fill=(0, 0, 0), font=font)
    d.text((124, 26), f"t={SS + i / FPS:.3f}s", fill=(60, 60, 60), font=fsm)
    prev.save(f"{OUT}/f{i:03d}.png")

print(f"번호매긴 프리뷰 {len(frames)}개 → {OUT}/f000.png ~ f{len(frames)-1:03d}.png")
print("뷰어로 확인 후, 스트라이드 시작~끝 번호를 알려주세요 (예: 20~48). 그 사이를 8등분해 최종 8컷 생성합니다.")
