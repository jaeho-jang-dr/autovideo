# -*- coding: utf-8 -*-
"""한글 우선 재타이밍: 각 씬 길이 = max(KO자연, EN자연)+PAD → durations.json + KO/EN 트랙(무절단, 짧은쪽 여백).
raw 클립(_ko_dae/_en_alice의 NNN_raw.mp3)을 자연 속도로 슬롯에 넣고 남으면 무음 패딩."""
import os, re, json, subprocess

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
CG = os.path.join(ROOT, "child_growth_science")
KOD = os.path.join(CG, "_ko_dae"); END = os.path.join(CG, "_en_alice")
TMP = os.path.join(CG, "_v4_tmp"); os.makedirs(TMP, exist_ok=True)
N = 91
PAD = 0.35

def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True).stdout.strip())
    except Exception: return 0.0

# 1) 슬롯 계산 = max(KO, EN) + PAD
slots = {}
for i in range(N):
    K = dur(os.path.join(KOD, f"{i:03d}_raw.mp3"))
    E = dur(os.path.join(END, f"{i:03d}_raw.mp3"))
    slots[str(i)] = round(max(K, E) + PAD, 3)
json.dump(slots, open(os.path.join(CG, "durations_v4.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
total = sum(slots.values())
print(f"durations_v4.json 저장 — 나레이션 총 {total:.1f}s ({total/60:.2f}분), 씬 {N}개", flush=True)

# 2) 트랙 빌드: raw를 슬롯에 자연속도로 넣고 무음 패딩(atrim으로 정확히 슬롯 길이)
def build(rawdir, lang, out):
    parts = []
    for i in range(N):
        raw = os.path.join(rawdir, f"{i:03d}_raw.mp3")
        slot = slots[str(i)]
        padded = os.path.join(TMP, f"{lang}_{i:03d}.mp3")
        subprocess.run(["ffmpeg","-y","-v","error","-i",raw,"-af",f"apad,atrim=0:{slot:.3f}",
                        "-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","160k",padded], timeout=60)
        parts.append(padded)
    listf = os.path.join(TMP, f"list_{lang}.txt")
    with open(listf, "w", encoding="utf-8") as f:
        for p in parts: f.write(f"file '{p}'\n")
    subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",listf,
                    "-c:a","aac","-b:a","192k",out], timeout=300)
    print(f"{lang} 트랙: {dur(out):.1f}s -> {out}", flush=True)

build(KOD, "ko", os.path.join(CG, "track_ko_v4.m4a"))
build(END, "en", os.path.join(CG, "track_en_v4.m4a"))
print("BUILD_TRACKS_DONE", flush=True)
