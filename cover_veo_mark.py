# -*- coding: utf-8 -*-
"""Veo 반짝임(✦) 워터마크를 채널 로고로 **같은 크기로 덮는다** (2026-07-28).

★Flow/Veo 산출물의 워터마크는 우하단 코너가 아니라 **안쪽**에 있고 반투명이다.
  1280x720 기준 48x48, 중심 (1159, 599). 다른 해상도는 비율로 환산한다.
  (메모리 기록: 1920x1080 기준 중심 (1727, 895) — 같은 상대 위치)
  반투명이라 시간축 분산 스캔에는 안 잡힌다. 어두운 프레임에서 국소 임계값으로 잡아야 한다.

지우는 게 아니라 덮는다 — delogo 보간은 자리가 뭉개져 보이고, 로고를 얹으면
워터마크도 가려지고 채널 표식도 생긴다(사장님 확정 방식).

사용: python cover_veo_mark.py <입력.mp4> [출력.mp4]
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

LOGO = "assets/drjay_ed_logo_circle.png"
# 1280x720 기준 워터마크 상자
WM_CX, WM_CY, WM_SZ = 1159, 599, 48
# ★로고는 워터마크와 같은 크기(48)로 하되, 안티에일리어싱 가장자리까지 덮도록 6px만 여유를 준다.
PAD = 6


def main():
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src.replace(".mp4", "_logo.mp4")
    w, h = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v",
         "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", src],
        capture_output=True, text=True).stdout.strip().split("x")
    w, h = int(w), int(h)
    sx, sy = w / 1280, h / 720
    size = round((WM_SZ + PAD * 2) * sx)
    x = round(WM_CX * sx - size / 2)
    y = round(WM_CY * sy - size / 2)
    print(f"{os.path.basename(src)}  {w}x{h}  로고 {size}px @ ({x},{y})")

    r = subprocess.run(
        ["ffmpeg", "-y", "-i", src, "-i", LOGO,
         "-filter_complex", f"[1:v]scale={size}:{size}[lg];[0:v][lg]overlay={x}:{y}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-c:a", "copy", dst],
        capture_output=True)
    if r.returncode:
        print("★실패:", r.stderr.decode("utf-8", "replace")[-300:])
        sys.exit(1)
    print(f"→ {dst}  {os.path.getsize(dst)/1024/1024:.0f}MB")


if __name__ == "__main__":
    main()
