# -*- coding: utf-8 -*-
"""운동손상 쇼츠 조립(영어/한글): 5개 9:16 클립 + 나레이션 + 자막 번인 → 연결."""
import subprocess, os, sys
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
FONT = "C\\:/Windows/Fonts/malgunbd.ttf"
CLIP = "workout_injury_916"
lang = sys.argv[1] if len(sys.argv) > 1 else "en"   # en / ko
NARR = f"scratch/wi/narr_{lang}"
WORK = f"scratch/wi/assemble_{lang}"; os.makedirs(WORK, exist_ok=True)

# (씬, 목표길이, 자막1, 자막2)
if lang == "en":
    SCENES = [
        (1, 5.0, "69% of gym injuries come from", "ego lifting too heavy"),
        (2, 4.0, "The shoulder gets hurt the most", "watch for impingement"),
        (3, 4.5, "Rounding your back on deadlifts", "crushes your lumbar discs"),
        (4, 4.0, "Knees caving inward", "tear your meniscus"),
        (5, 5.0, "Injured? Use RICE and rest", "recovery is where you grow"),
    ]
    final = "scratch/shorts_v2/workout_short_EN.mp4"
else:
    SCENES = [
        (1, 5.6, "헬스 부상의 69%는", "무리한 고중량 욕심 때문"),
        (2, 5.2, "가장 많이 다치는 어깨", "충돌증후군을 조심"),
        (3, 4.8, "데드리프트에 허리가 말리면", "요추 디스크가 눌려요"),
        (4, 4.6, "무릎이 안으로 모이면", "반월상 연골이 찢어져요"),
        (5, 5.8, "다쳤다면 RICE와 휴식", "회복이 곧 성장이에요"),
    ]
    final = "scratch/shorts_v2/workout_short_KO.mp4"

def ff(*a):
    subprocess.run(["ffmpeg", "-y", *a], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

parts = []
for n, dur, l1, l2 in SCENES:
    clip = f"{CLIP}/scene_{n}.mp4"; narr = f"{NARR}/s{n}.mp3"
    outp = f"{WORK}/part_{n}.mp4"
    d1 = (f"drawtext=fontfile='{FONT}':text='{l1}':fontcolor=white:fontsize=40:"
          f"borderw=6:bordercolor=black:x=(w-text_w)/2:y=h-292:box=1:boxcolor=black@0.45:boxborderw=14")
    d2 = (f"drawtext=fontfile='{FONT}':text='{l2}':fontcolor=white:fontsize=40:"
          f"borderw=6:bordercolor=black:x=(w-text_w)/2:y=h-238:box=1:boxcolor=black@0.45:boxborderw=14")
    ff("-t", str(dur), "-i", clip, "-i", narr,
       "-filter_complex", f"[0:v]{d1},{d2}[v];[1:a]apad=whole_dur={dur}[a]",
       "-map", "[v]", "-map", "[a]", "-t", str(dur),
       "-c:v", "libx264", "-crf", "19", "-preset", "medium",
       "-c:a", "aac", "-b:a", "192k", "-r", "24", "-ar", "48000", outp)
    parts.append(outp); print(f"part {n} OK ({dur}s)")

lst = f"{WORK}/list.txt"
open(lst, "w", encoding="utf-8").write("\n".join(f"file '{os.path.abspath(p)}'" for p in parts))
ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", final)
d = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",final],
                   capture_output=True, text=True).stdout.strip()
print(f"=== {lang} 완성: {final} ({d}s) ===")
