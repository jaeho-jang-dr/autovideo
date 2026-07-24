# -*- coding: utf-8 -*-
"""지은 걷기 스프라이트 시트(8포즈 1줄) → 프레임 분리·정합 → 왼→오른쪽 걷기 mp4.
1) 흰배경 컷아웃 + 바닥선 제거
2) 열 투영으로 8개 인물 자동 분리
3) 머리 x 기준 정합(발끝 y 공통) → frame_0..7.png
4) 배경 위에서 8프레임 순환 재생 + x 왼→오른쪽 이동 → walk_across.mp4
사용: python walk_assemble.py
"""
import os, subprocess
import numpy as np
from PIL import Image

os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
SHEET = "scratch/w19_walk/jieun_walk_sheet.png"
OUT = "scratch/w19_walk"
os.makedirs(OUT, exist_ok=True)


def cutout_white(arr):
    from scipy import ndimage
    rgb = arr[:, :, :3].astype(int)
    lo = rgb.min(axis=2); hi = rgb.max(axis=2)
    white = (lo > 205) & ((hi - lo) < 28)
    lbl, n = ndimage.label(white)
    border = set(lbl[0, :]) | set(lbl[-1, :]) | set(lbl[:, 0]) | set(lbl[:, -1]); border.discard(0)
    bg = np.isin(lbl, list(border))
    arr[bg, 3] = 0
    return arr


im = Image.open(SHEET).convert("RGBA")
arr = np.array(im)
arr = cutout_white(arr)
H, W = arr.shape[:2]

# 바닥선(맨 아래 가로 검은선) 제거: 아래 12% 구간에서 폭 60%+ 걸치는 어두운 가로줄 알파=0
alpha = arr[:, :, 3]
dark = (arr[:, :, :3].max(axis=2) < 90) & (alpha > 0)
for y in range(int(H * 0.86), H):
    if dark[y].mean() > 0.5:      # 가로로 길게 이어진 선 = 바닥선
        arr[y, :, 3] = 0

# 열 투영(상단 80%만 — 발/바닥 영향 배제) — 8명 균등배치 가정, 경계 7곳을 '최소밀도 열'에서 분할
N = 8
colmass = (arr[: int(H * 0.8), :, 3] > 0).sum(axis=0).astype(float)
cuts = [0]
for i in range(1, N):
    c = int(W * i / N)                       # 예상 경계
    win = int(W / N * 0.35)                  # 경계 ±35% 슬롯 내에서 최소밀도 열 탐색
    a, b = max(cuts[-1] + 5, c - win), min(W - 1, c + win)
    x_min = a + int(np.argmin(colmass[a:b])) if b > a else c
    cuts.append(x_min)
cuts.append(W)
runs = [(cuts[i], cuts[i + 1]) for i in range(N)]
print(f"분리 경계: {[r[0] for r in runs]}  (8칸)")

# 각 인물 크롭(전체 높이) — x범위는 런, y범위는 알파>0 전체
frames = []
for (x0, x1) in runs:
    sub = arr[:, x0:x1]
    ys, xs = np.where(sub[:, :, 3] > 0)
    if len(ys) == 0: continue
    crop = sub[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    frames.append(crop)
print(f"프레임 {len(frames)}개 크롭")

# 정합: 공통 캔버스, 발끝 y 하단 정렬, '머리 x'(상단 20% 무게중심) 기준 가로 정렬
CW = max(f.shape[1] for f in frames) + 80
CH = max(f.shape[0] for f in frames) + 20
reg = []
for i, f in enumerate(frames):
    fh, fw = f.shape[:2]
    head = f[: int(fh * 0.22)]
    hy, hx = np.where(head[:, :, 3] > 0)
    head_cx = int(hx.mean()) if len(hx) else fw // 2
    canvas = np.zeros((CH, CW, 4), np.uint8)
    ox = CW // 2 - head_cx           # 머리 x를 캔버스 중앙에
    oy = CH - fh - 6                 # 발끝 하단 정렬
    ox = max(0, min(ox, CW - fw))
    canvas[oy:oy + fh, ox:ox + fw] = f
    Image.fromarray(canvas).save(f"{OUT}/frame_{i}.png")
    reg.append(canvas)
print(f"정합 프레임 {len(reg)}개 → {OUT}/frame_*.png (캔버스 {CW}x{CH})")

# 걷기 mp4: 1280x720 배경 위, 8프레임 순환 + x 왼→오른쪽 이동
BW, BH = 1280, 720
bgp = "assets/graphics/bg/w19_bg_trail.png"
if os.path.exists(bgp):
    bg = Image.open(bgp).convert("RGB").resize((BW, BH))
else:
    bg = Image.new("RGB", (BW, BH), (238, 232, 220))
# 캐릭터 화면높이 ~55%
scale = int(BH * 0.55) / CH
cw2, ch2 = int(CW * scale), int(CH * scale)
regr = [Image.fromarray(f).resize((cw2, ch2)) for f in reg]

FPS = 12
HOLD = 2               # ★2배 느리게: 각 스프라이트 프레임을 2 비디오프레임 유지
SECONDS = 10           # ★이동도 절반 속도(같은 거리, 2배 시간) — 발 미끄러짐 방지
nframes = FPS * SECONDS
tmp = f"{OUT}/_seq"; os.makedirs(tmp, exist_ok=True)
for f in os.listdir(tmp):
    os.remove(os.path.join(tmp, f))
x_start, x_end = -cw2 * 0.4, BW - cw2 * 0.6
foot_y = int(BH * 0.96) - ch2
for k in range(nframes):
    fr = bg.copy()
    t = k / max(1, nframes - 1)
    x = int(x_start + (x_end - x_start) * t)
    ch_img = regr[(k // HOLD) % len(regr)]     # 프레임을 HOLD배 유지 → 사이클 2배 느림
    fr.paste(ch_img, (x, foot_y), ch_img)
    fr.save(f"{tmp}/f{k:04d}.png")

out = f"{OUT}/walk_across.mp4"
subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", f"{tmp}/f%04d.png",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"★ 걷기 영상: {out}")
