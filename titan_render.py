# -*- coding: utf-8 -*-
"""titan_science 합성 렌더 — 워터마크 로고 덮개 + 나레이션.

★레이어 순서: 배경(클립) → **워터마크 덮개** → 자막(소프트 srt, 번인 금지)
★워터마크 실측(2026-08-10, 12클립 48프레임 누적): 48x48, 중심 (1160, 600)
  → 로고를 **딱 그 크기(48px)** 로 얹는다.

    python titan_render.py --lang ko
    python titan_render.py --lang en
"""
import argparse
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
CLIP_DIR = os.path.join(ROOT, "titan_science", "keyframes")
AUD_DIR = os.path.join(ROOT, "titan_science", "audio")
OUT_DIR = os.path.join(ROOT, "titan_science", "_out")
WORK = os.path.join(ROOT, "titan_science", "_wm")
LOGO = os.path.join(ROOT, "assets", "drjay_ed_logo_circle.png")
FULL = os.path.join(ROOT, "titan_science", "_preview", "TITAN_full.mp4")

# ★실측값 — scan_wm.py 로 뽑았다
WM_D = 48
WM_X, WM_Y = 1136, 576          # 좌상단 (중심 1160,600 − 24)


def dur(path):
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    return float(d) if d else 0.0


def scene_starts():
    """씬 시작 시각(초) — 클립을 씬 순서대로 이어 붙인 기준."""
    import collections
    per = collections.defaultdict(float)
    for f in os.listdir(CLIP_DIR):
        m = re.match(r"^s(\d\d)_.+\.mp4$", f)
        if m:
            per[int(m.group(1))] += dur(os.path.join(CLIP_DIR, f))
    starts, t = {}, 0.0
    for n in sorted(per):
        starts[n] = t
        t += per[n]
    return starts, dict(sorted(per.items()))


def logo_png():
    """로고를 워터마크와 같은 크기로 줄여 둔다."""
    out = os.path.join(WORK, "logo_%d.png" % WM_D)
    os.makedirs(WORK, exist_ok=True)
    if not os.path.exists(out):
        from PIL import Image
        Image.open(LOGO).convert("RGBA").resize((WM_D, WM_D), Image.LANCZOS).save(out)
    return out


def build_audio(lang, starts, lens):
    """씬별 나레이션을 제 시각에 놓아 한 트랙으로 만든다.
    영상보다 긴 씬은 atempo 로 살짝 당겨 그 씬 안에 넣는다."""
    ins, filters, labels = [], [], []
    for i, n in enumerate(sorted(starts)):
        mp3 = os.path.join(AUD_DIR, "s%02d_%s.mp3" % (n, lang))
        if not os.path.exists(mp3):
            continue
        d, room = dur(mp3), lens[n]
        ins += ["-i", mp3]
        f = "[%d:a]" % len(labels)
        if d > room:                       # ★초과분만 당긴다
            f += "atempo=%.4f," % min(2.0, d / (room - 0.15))
        f += "adelay=%d|%d[a%d]" % (int(starts[n] * 1000), int(starts[n] * 1000), i)
        filters.append(f)
        labels.append("[a%d]" % i)
    out = os.path.join(WORK, "narr_%s.m4a" % lang)
    fc = ";".join(filters) + ";" + "".join(labels) + \
        "amix=inputs=%d:normalize=0[out]" % len(labels)
    subprocess.run(["ffmpeg", "-y", "-v", "error"] + ins +
                   ["-filter_complex", fc, "-map", "[out]",
                    "-c:a", "aac", "-b:a", "192k", out], check=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", choices=["ko", "en"], required=True)
    a = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    starts, lens = scene_starts()
    logo = logo_png()
    narr = build_audio(a.lang, starts, lens)
    out = os.path.join(OUT_DIR, "TITAN_%s.mp4" % a.lang.upper())

    print("영상 %.1f초 · 나레이션 %.1f초 · 로고 %dpx @ (%d,%d)"
          % (dur(FULL), dur(narr), WM_D, WM_X, WM_Y))
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-stats",
        "-i", FULL, "-i", logo, "-i", narr,
        "-filter_complex", "[0:v][1:v]overlay=%d:%d[v]" % (WM_X, WM_Y),
        "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
    print("%s  %.1f초 · %dMB" % (out, dur(out), os.path.getsize(out) // 1024 // 1024))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
