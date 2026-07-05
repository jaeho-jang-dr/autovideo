# -*- coding: utf-8 -*-
"""한글 우선 재타이밍 v4: make_video --durations(각 씬=max(KO,EN)+pad) 재컴파일 → KO/EN 자연트랙 먹싱.
결과: child_growth_dub.mp4 (한글 나레이션 안 잘림, 영어는 짧으면 여백)."""
import subprocess, sys, os, time
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
CG = os.path.join(ROOT, "child_growth_science")
try:
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception: pass

def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True).stdout.strip())
    except Exception: return 0.0

t0 = time.time()
print("== [1/2] make_video 재컴파일 (--durations, 한글길이 우선) ==", flush=True)
cmd = ["python", "make_video.py",
       "--scenario", r"child_growth_science\scenario.txt",
       "--output", os.path.join(CG, "child_growth.mp4"),
       "--intro", "", "--outro", "", "--outro-card-duration", "0",  # 인트로/아웃트로 안 씀(사용자 지시)
       "--annotations", r"child_growth_science\annotations.json",
       "--no-burn-subs", "--embed-subs",
       "--durations", os.path.join(CG, "durations_v4.json")]
r = subprocess.run(cmd, cwd=ROOT)
if r.returncode != 0:
    print("!! COMPILE FAILED", flush=True); sys.exit(1)
base = os.path.join(CG, "child_growth.mp4")
print(f"  child_growth.mp4 재컴파일 완료 ({dur(base):.1f}s)", flush=True)

print("== [2/2] KO/EN 자연트랙 + 자막 먹싱 ==", flush=True)
kot = os.path.join(CG, "track_ko_v4.m4a"); ent = os.path.join(CG, "track_en_v4.m4a")
out = os.path.join(CG, "child_growth_dub.mp4")
r = subprocess.run(["ffmpeg","-y","-v","error","-i",base,"-i",kot,"-i",ent,
    "-map","0:v","-map","1:a","-map","2:a","-map","0:s?",
    "-c:v","copy","-c:a","aac","-b:a","192k","-c:s","copy",
    "-metadata:s:a:0","language=kor","-metadata:s:a:0","title=한국어(Dae)",
    "-metadata:s:a:1","language=eng","-metadata:s:a:1","title=English(Alice)",
    "-disposition:a:0","default", out])
if r.returncode != 0:
    print("!! MUX FAILED", flush=True); sys.exit(1)
print(f"  DUB v4: {out}  video={dur(base):.1f}s ko/en=651s  ({dur(out)/60:.2f}분, {os.path.getsize(out)/1e6:.0f}MB)", flush=True)
print(f"== DONE in {(time.time()-t0)/60:.1f}분 ==", flush=True)
