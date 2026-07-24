# -*- coding: utf-8 -*-
"""쇼츠 4개 번인 없이 재조립: 9:16 클립 + Azure 나레이션만 (자막 번인 제거).
자막은 5개국어 소프트 SRT로만 제공 → 화면에 박히는 글자 0."""
import subprocess, os
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")

# (out, CLIP, NARR, [씬별 목표길이])  ← 기존 assemble 스크립트의 dur과 동일
JOBS = [
    ("scratch/shorts_v2/turtle_short_FINAL.mp4", "turtle_short_v916", "scratch/shorts_v2/narr",    [3.5, 6.0, 6.6, 6.6, 4.6]),
    ("scratch/shorts_v2/turtle_short_KO.mp4",    "turtle_short_v916", "scratch/shorts_v2/narr_ko", [4.0, 5.2, 7.2, 6.3, 4.6]),
    ("scratch/shorts_v2/workout_short_EN.mp4",   "workout_injury_916","scratch/wi/narr_en",        [5.0, 4.0, 4.5, 4.0, 5.0]),
    ("scratch/shorts_v2/workout_short_KO.mp4",   "workout_injury_916","scratch/wi/narr_ko",        [5.6, 5.2, 4.8, 4.6, 5.8]),
]

def ff(*a):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *a], check=True)

for final, CLIP, NARR, durs in JOBS:
    WORK = final.replace(".mp4", "_cleanparts")
    os.makedirs(WORK, exist_ok=True)
    parts = []
    for i, dur in enumerate(durs, 1):
        clip = f"{CLIP}/scene_{i}.mp4"; narr = f"{NARR}/s{i}.mp3"
        outp = f"{WORK}/part_{i}.mp4"
        # 번인(drawtext) 없음 — 비디오 그대로 통과, 오디오는 씬 길이까지 패드
        ff("-t", str(dur), "-i", clip, "-i", narr,
           "-filter_complex", f"[1:a]apad=whole_dur={dur}[a]",
           "-map", "0:v", "-map", "[a]", "-t", str(dur),
           "-c:v", "libx264", "-crf", "19", "-preset", "medium",
           "-c:a", "aac", "-b:a", "192k", "-r", "24", "-ar", "48000", outp)
        parts.append(outp)
    lst = f"{WORK}/list.txt"
    open(lst, "w", encoding="utf-8").write("\n".join(f"file '{os.path.abspath(p)}'" for p in parts))
    ff("-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", final)
    d = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",final],
                       capture_output=True, text=True).stdout.strip()
    print(f"clean 완성: {final} ({d}s)", flush=True)
print("ASSEMBLE_CLEAN_DONE")
