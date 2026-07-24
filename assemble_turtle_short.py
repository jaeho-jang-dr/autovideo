# -*- coding: utf-8 -*-
"""거북목 쇼츠 조립: 5개 9:16 클립 + Emma 나레이션 + 영어 자막 번인 → 연결."""
import subprocess, os, sys
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
FONT = "C\\:/Windows/Fonts/malgunbd.ttf"
CLIP = "turtle_short_v916"
NARR = "scratch/shorts_v2/narr"
WORK = "scratch/shorts_v2/assemble"
os.makedirs(WORK, exist_ok=True)

# (씬번호, 목표길이, 자막 1줄, 자막 2줄)
SCENES = [
    (1, 3.5, "Are you looking down", "at your phone right now?"),
    (2, 6.0, "Tilt your head 15 deg", "and your neck holds 12kg"),
    (3, 6.6, "At 60 deg, 27kg on your neck", "like a child sitting on you!"),
    (4, 6.6, "Reset your posture", "back, heels, head on a wall"),
    (5, 4.6, "Do chin-tucks every day", "to straighten your neck"),
]

def ff(*a):
    subprocess.run(["ffmpeg", "-y", *a], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

parts = []
for n, dur, l1, l2 in SCENES:
    clip = f"{CLIP}/scene_{n}.mp4"
    narr = f"{NARR}/s{n}.mp3"
    outp = f"{WORK}/part_{n}.mp4"
    # 두 줄을 각각 drawtext로 (개행문자 렌더 아티팩트 방지)
    d1 = (f"drawtext=fontfile='{FONT}':text='{l1}':fontcolor=white:fontsize=40:"
          f"borderw=6:bordercolor=black:x=(w-text_w)/2:y=h-290:"
          f"box=1:boxcolor=black@0.4:boxborderw=14")
    d2 = (f"drawtext=fontfile='{FONT}':text='{l2}':fontcolor=white:fontsize=40:"
          f"borderw=6:bordercolor=black:x=(w-text_w)/2:y=h-238:"
          f"box=1:boxcolor=black@0.4:boxborderw=14")
    vf = f"{d1},{d2}"
    # 비디오 dur로 트림 + 자막, 오디오=나레이션 dur까지 패드
    ff("-t", str(dur), "-i", clip, "-i", narr,
       "-filter_complex", f"[0:v]{vf}[v];[1:a]apad=whole_dur={dur}[a]",
       "-map", "[v]", "-map", "[a]", "-t", str(dur),
       "-c:v", "libx264", "-crf", "19", "-preset", "medium",
       "-c:a", "aac", "-b:a", "192k", "-r", "24", "-ar", "48000", outp)
    parts.append(outp)
    print(f"part {n} OK ({dur}s)")

# concat
lst = f"{WORK}/list.txt"
open(lst, "w", encoding="utf-8").write("\n".join(f"file '{os.path.abspath(p)}'" for p in parts))
final = "scratch/shorts_v2/turtle_short_FINAL.mp4"
ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", final)
d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "csv=p=0", final], capture_output=True, text=True).stdout.strip()
print(f"=== 완성: {final} ({d}s) ===")
