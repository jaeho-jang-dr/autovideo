# -*- coding: utf-8 -*-
"""titan_science 전체 클립을 씬 순서대로 이어 붙인다.

순서 규칙 — 씬 번호 오름차순, 씬 안에서는 **원본 컷 → b → c → d**.
(원본 컷 = 키프레임에서 바로 만든 첫 컷. `_b`/`_c`/`_d` 접미사가 없다.)

    python titan_join_all.py            # 전체 → titan_science/_preview/TITAN_full.mp4
    python titan_join_all.py --scene 8  # 그 씬만 → S08.mp4
"""
import argparse
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
CLIP_DIR = os.path.join(ROOT, "titan_science", "keyframes")
OUT_DIR = os.path.join(ROOT, "titan_science", "_preview")


def clip_order():
    """{씬번호: [키…]} — 씬 안에서 원본 → b → c → d 순."""
    scenes = {}
    for f in os.listdir(CLIP_DIR):
        if not f.endswith(".mp4"):
            continue
        k = f[:-4]
        m = re.match(r"^s(\d\d)_(.+)$", k)
        if not m:
            continue
        n, tail = int(m.group(1)), m.group(2)
        # 원본 컷은 0, 이어받기 컷은 b=1, c=2, d=3
        rank = "bcd".index(tail) + 1 if tail in ("b", "c", "d") else 0
        scenes.setdefault(n, []).append((rank, k))
    return {n: [k for _, k in sorted(v)] for n, v in sorted(scenes.items())}


def join(keys, out_name):
    os.makedirs(OUT_DIR, exist_ok=True)
    lst = os.path.join(OUT_DIR, out_name + ".txt")
    with open(lst, "w", encoding="utf-8") as f:
        for k in keys:
            p = os.path.join(CLIP_DIR, k + ".mp4").replace("\\", "/")
            f.write("file '%s'\n" % p)
    out = os.path.join(OUT_DIR, out_name + ".mp4")
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                        "-i", lst, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                        "-pix_fmt", "yuv420p", "-r", "24", out])
    if r.returncode:
        raise RuntimeError("ffmpeg 실패 rc=%d" % r.returncode)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip()
    return out, float(dur)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", type=int, help="그 씬만 이어 붙인다")
    a = ap.parse_args()

    scenes = clip_order()
    if a.scene:
        keys = scenes.get(a.scene)
        if not keys:
            print("씬 %d 클립 없음" % a.scene)
            return 1
        name = "S%02d" % a.scene
    else:
        keys = [k for n in sorted(scenes) for k in scenes[n]]
        name = "TITAN_full"

    for n in sorted(scenes):
        print("S%02d  %2d컷  %s" % (n, len(scenes[n]), " → ".join(scenes[n])))
    print("-" * 60)

    out, dur = join(keys, name)
    m, s = divmod(dur, 60)
    print("%s  %d클립 · %d분 %.1f초 · %dKB" %
          (out, len(keys), m, s, os.path.getsize(out) // 1024))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
