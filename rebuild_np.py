# -*- coding: utf-8 -*-
"""한글우선·이팩트제거·인트로아웃트로없음 재렌더 + KO/EN 트랙 먹싱.
사용: python rebuild_np.py <proj_dir> <srt_base>
예:  python rebuild_np.py turtle_neck_science turtle_neck_science"""
import subprocess, sys, os, time
PROJ = sys.argv[1]; SRTB = sys.argv[2]
try:
    sys.stdout.reconfigure(encoding="utf-8"); sys.stderr.reconfigure(encoding="utf-8")
except Exception: pass
def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True).stdout.strip())
    except Exception: return 0.0

t0 = time.time()
base = os.path.join(PROJ, f"{SRTB}_np.mp4")
ann = os.path.join(PROJ, "annotations.json")
cmd = ["python", "make_video.py",
       "--scenario", os.path.join(PROJ, "scenario.txt"),
       "--output", base,
       "--no-burn-subs", "--embed-subs",
       "--durations", os.path.join(PROJ, "durations_np.json"),
       "--no-test-fx",
       "--intro", "", "--outro", "", "--outro-card-duration", "0"]
if os.path.exists(ann): cmd += ["--annotations", ann]
print("== [1/2] 재컴파일(이팩트제거·인트로아웃트로없음·한글우선) ==", flush=True)
r = subprocess.run(cmd)
if r.returncode != 0: print("!! COMPILE FAILED", flush=True); sys.exit(1)
print(f"  base {dur(base):.1f}s", flush=True)

print("== [2/2] KO/EN 트랙 + 자막 먹싱 ==", flush=True)
kot = os.path.join(PROJ, "track_ko_np.m4a"); ent = os.path.join(PROJ, "track_en_np.m4a")
out = os.path.join(PROJ, f"{SRTB}_np_dub.mp4")
r = subprocess.run(["ffmpeg","-y","-v","error","-i",base,"-i",kot,"-i",ent,
    "-map","0:v","-map","1:a","-map","2:a","-map","0:s?",
    "-c:v","copy","-c:a","aac","-b:a","192k","-c:s","copy",
    "-metadata:s:a:0","language=kor","-metadata:s:a:0","title=한국어",
    "-metadata:s:a:1","language=eng","-metadata:s:a:1","title=English",
    "-disposition:a:0","default", out])
if r.returncode != 0: print("!! MUX FAILED", flush=True); sys.exit(1)
print(f"  DUB: {out}  {dur(out)/60:.2f}분, {os.path.getsize(out)/1e6:.0f}MB", flush=True)
print(f"== DONE in {(time.time()-t0)/60:.1f}분 ==", flush=True)
