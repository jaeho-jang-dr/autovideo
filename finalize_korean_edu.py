#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""korean_education 최종 마무리: 재렌더 → 영어 나레이션 → 해례본 썸네일 → 드라이브 업로드."""
import os
import sys
import shutil
import subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
KE = os.path.join(ROOT, "korean_education")
OUT = os.path.join(KE, "korean_education.mp4")
DRIVE = r"G:\내 드라이브\AutoVideo\korean_education"


def run(cmd, log):
    with open(log, "w", encoding="utf-8") as f:
        return subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode


print("[1/4] 전체 재렌더 (90씬, 크롭없음+로고, 자막 한/영)...", flush=True)
rc = run(["python", "make_video.py",
          "--scenario", "korean_education/scenario.txt", "--output", OUT,
          "--profile", "assets/profiles/minimal_ink.json",
          "--intro", "assets/intro.mp4", "--outro", "assets/outro.mp4",
          "--outro-card", "assets/outro_template.png",
          "--no-burn-subs", "--embed-subs"],
         os.path.join(KE, "_compile_final.log"))
if rc != 0 or not os.path.exists(OUT):
    print(f"[ERR] 렌더 실패 rc={rc}", flush=True)
    sys.exit(1)
print("[1/4] 렌더 완료", flush=True)

print("[2/4] 영어 나레이션 추가...", flush=True)
shutil.rmtree(os.path.join(KE, "_en_tts"), ignore_errors=True)
rc = run(["python", "add_en_narration.py", OUT], os.path.join(KE, "_en_narr_final.log"))
print(f"[2/4] 나레이션 종료 rc={rc}", flush=True)

print("[3/4] 훈민정음 해례본 썸네일 재적용...", flush=True)
try:
    from PIL import Image
    from make_video import generate_thumbnail
    bg = os.path.join(KE, "_thumb_bg_haerye.png")
    if os.path.exists(bg):
        try: os.remove(bg)
        except Exception: pass
        
    if not os.path.exists(bg):
        canvas = Image.new("RGBA", (1280, 720), (255, 255, 255, 255))
        scroll_img_path = os.path.join(ROOT, "assets/graphics/obj_haerye_scroll.png")
        if os.path.exists(scroll_img_path):
            scroll = Image.open(scroll_img_path).convert("RGBA")
            # Scale up to cover the entire 1280x720 screen
            scale = max(1280.0 / scroll.width, 720.0 / scroll.height)
            w = int(scroll.width * scale)
            h = int(scroll.height * scale)
            scroll = scroll.resize((w, h), Image.Resampling.LANCZOS)
            
            # Apply 50% opacity (alpha)
            r, g, b, a = scroll.split()
            a = a.point(lambda p: int(p * 0.5))
            scroll = Image.merge("RGBA", (r, g, b, a))
            
            # Center and paste onto the white canvas
            offset_x = (1280 - w) // 2
            offset_y = (720 - h) // 2
            canvas.alpha_composite(scroll, (offset_x, offset_y))
        canvas.convert("RGB").save(bg)
        
    generate_thumbnail(bg, "한글 자음 모음 소리내기", "훈민정음",
                       os.path.join(KE, "scene_0_thumbnail_korean.png"))

    print("[3/4] 썸네일 완료", flush=True)
except Exception as e:
    print(f"[3/4] 썸네일 실패: {e}", flush=True)

print("[4/4] 구글 드라이브 업로드...", flush=True)
os.makedirs(DRIVE, exist_ok=True)
base = os.path.splitext(OUT)[0]
files = [OUT, base + ".ko.srt", base + ".en.srt", base + ".en.m4a",
         os.path.join(KE, "scene_0_thumbnail_korean.png")]
for f in files:
    if os.path.exists(f):
        d = os.path.join(DRIVE, os.path.basename(f))
        shutil.copy2(f, d)
        ok = os.path.getsize(f) == os.path.getsize(d)
        print(f"  {'OK' if ok else 'MISMATCH'} {os.path.basename(f)} ({os.path.getsize(d)} bytes)", flush=True)
    else:
        print(f"  MISSING {os.path.basename(f)}", flush=True)
print("[DONE] korean_education 최종 완료", flush=True)
