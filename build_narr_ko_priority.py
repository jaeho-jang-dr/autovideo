# -*- coding: utf-8 -*-
"""edge-tts로 씬별 KO/EN 나레이션 재생성(같은 음성) → 한글우선 슬롯(max(KO,EN)+pad) → durations.json + KO/EN 트랙.
사용: python build_narr_ko_priority.py <proj_dir> <srt_base> <ko_voice: sunhi|injoon>
예:  python build_narr_ko_priority.py turtle_neck_science turtle_neck_science sunhi"""
import os, sys, re, json, subprocess
PROJ = sys.argv[1]; SRTB = sys.argv[2]; KOVOICE = sys.argv[3]
os.environ["EDGE_ACTIVE_VOICE"] = KOVOICE
sys.path.insert(0, os.getcwd())
from tts_manager import save_tts_edge_tts
PAD = 0.35; SPEED = 1.1
KODIR = os.path.join(PROJ, "_ko_edge"); ENDIR = os.path.join(PROJ, "_en_edge")
TMP = os.path.join(PROJ, "_np_tmp")
for d in (KODIR, ENDIR, TMP): os.makedirs(d, exist_ok=True)

def texts(srt):
    out = []
    for blk in open(srt, encoding="utf-8").read().strip().split("\n\n"):
        L = [x for x in blk.strip().split("\n") if x.strip()]
        if len(L) < 3 or "-->" not in L[1]:
            if len(L) >= 2 and "-->" in L[0]:  # 방어
                out.append(" ".join(L[1:]))
            continue
        out.append(" ".join(L[2:]))
    return out
ko = texts(os.path.join(PROJ, f"{SRTB}.ko.srt"))
en = texts(os.path.join(PROJ, f"{SRTB}.en.srt"))
N = min(len(ko), len(en))
print(f"[{PROJ}] {N}큐, KO음성={KOVOICE}", flush=True)

def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True).stdout.strip())
    except Exception: return 0.0

slots = {}
for i in range(N):
    kr = os.path.join(KODIR, f"{i:03d}.mp3"); er = os.path.join(ENDIR, f"{i:03d}.mp3")
    if not os.path.exists(kr) or os.path.getsize(kr) < 800:
        save_tts_edge_tts(ko[i], kr, lang="ko")
    if not os.path.exists(er) or os.path.getsize(er) < 800:
        save_tts_edge_tts(en[i], er, lang="en")
    K = dur(kr) / SPEED; E = dur(er) / SPEED   # 1.1배속 후 유효 길이
    slots[str(i)] = round(max(K, E) + PAD, 3)
    if i % 10 == 0: print(f"  {i}: KO {K:.1f} / EN {E:.1f} -> slot {slots[str(i)]}", flush=True)
json.dump(slots, open(os.path.join(PROJ, "durations_np.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"durations_np.json 저장 — 총 {sum(slots.values()):.1f}s ({sum(slots.values())/60:.2f}분)", flush=True)

def build(rawdir, lang, out):
    parts = []
    for i in range(N):
        raw = os.path.join(rawdir, f"{i:03d}.mp3"); slot = slots[str(i)]
        padded = os.path.join(TMP, f"{lang}_{i:03d}.mp3")
        subprocess.run(["ffmpeg","-y","-v","error","-i",raw,"-af",f"atempo={SPEED},apad,atrim=0:{slot:.3f}",
                        "-ar","44100","-ac","2","-c:a","libmp3lame","-b:a","160k",padded], timeout=60)
        parts.append(padded)
    listf = os.path.join(TMP, f"list_{lang}.txt")
    with open(listf, "w", encoding="utf-8") as f:
        for p in parts: f.write(f"file '{os.path.abspath(p)}'\n")
    subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",listf,"-c:a","aac","-b:a","192k",out], timeout=300)
    print(f"{lang} 트랙: {dur(out):.1f}s -> {out}", flush=True)

build(KODIR, "ko", os.path.join(PROJ, "track_ko_np.m4a"))
build(ENDIR, "en", os.path.join(PROJ, "track_en_np.m4a"))
print("BUILD_NARR_DONE", flush=True)
