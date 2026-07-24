# -*- coding: utf-8 -*-
"""거북목 쇼츠 한글판: 같은 5개 9:16 클립 + 선희 나레이션 + 한글 자막 번인 → 연결."""
import subprocess, os
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
FONT = "C\\:/Windows/Fonts/malgunbd.ttf"
CLIP = "turtle_short_v916"; NARR = "scratch/shorts_v2/narr_ko"
WORK = "scratch/shorts_v2/assemble_ko"; os.makedirs(WORK, exist_ok=True)

# (씬, 목표길이, 자막1, 자막2)
SCENES = [
    (1, 4.0, "지금 스마트폰을", "내려다보고 계신가요?"),
    (2, 5.2, "15도만 숙여도", "목엔 12kg이 실려요"),
    (3, 7.2, "60도로 숙이면 27kg!", "목에 아이를 얹은 셈"),
    (4, 6.3, "자세 리셋 -", "등·뒤통수를 벽에 붙여요"),
    (5, 4.6, "매일 친턱 운동으로", "목을 바르게 펴세요"),
]

def ff(*a):
    subprocess.run(["ffmpeg", "-y", *a], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

parts = []
for n, dur, l1, l2 in SCENES:
    clip = f"{CLIP}/scene_{n}.mp4"; narr = f"{NARR}/s{n}.mp3"
    outp = f"{WORK}/part_{n}.mp4"
    d1 = (f"drawtext=fontfile='{FONT}':text='{l1}':fontcolor=white:fontsize=42:"
          f"borderw=6:bordercolor=black:x=(w-text_w)/2:y=h-292:box=1:boxcolor=black@0.4:boxborderw=14")
    d2 = (f"drawtext=fontfile='{FONT}':text='{l2}':fontcolor=white:fontsize=42:"
          f"borderw=6:bordercolor=black:x=(w-text_w)/2:y=h-238:box=1:boxcolor=black@0.4:boxborderw=14")
    ff("-t", str(dur), "-i", clip, "-i", narr,
       "-filter_complex", f"[0:v]{d1},{d2}[v];[1:a]apad=whole_dur={dur}[a]",
       "-map", "[v]", "-map", "[a]", "-t", str(dur),
       "-c:v", "libx264", "-crf", "19", "-preset", "medium",
       "-c:a", "aac", "-b:a", "192k", "-r", "24", "-ar", "48000", outp)
    parts.append(outp); print(f"part {n} OK ({dur}s)")

lst = f"{WORK}/list.txt"
open(lst, "w", encoding="utf-8").write("\n".join(f"file '{os.path.abspath(p)}'" for p in parts))
final = "scratch/shorts_v2/turtle_short_KO.mp4"
ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", final)
print(f"=== 한글판 완성: {final} ===")
