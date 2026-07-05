# -*- coding: utf-8 -*-
"""마스터 완성 후 마무리: ①4개 언어 검토영상(빠른 mux) ②마스터 4K 업스케일(Lanczos).
사용: python finalize_package.py [reviews|4k|all]"""
import os, subprocess, sys
MAIN="D:/Entertainments/DevEnvironment/autovideo/sejong_film/main"
PKG=os.path.join(MAIN,"pkg"); os.makedirs(PKG,exist_ok=True)
MASTER=os.path.join(MAIN,"sejong_master_video.mp4")
MODE=sys.argv[1] if len(sys.argv)>1 else "all"
assert os.path.exists(MASTER), "마스터 영상 없음 — 렌더 먼저"

def run(c):
    r=subprocess.run(c,capture_output=True,text=True);
    return r.returncode

# ① 검토 영상: 마스터 영상(copy) + 각 언어 오디오 + 소프트자막
if MODE in ("reviews","all"):
    for L in ["en","zh","ja","es"]:
        a=os.path.join(PKG,f"audio_{L}.m4a"); s=os.path.join(PKG,f"sub_{L}.srt")
        out=os.path.join(PKG,f"review_{L}.mp4")
        lang3={"en":"eng","zh":"chi","ja":"jpn","es":"spa"}[L]
        rc=run(["ffmpeg","-y","-v","error","-i",MASTER,"-i",a,"-i",s,
            "-map","0:v","-map","1:a","-map","2","-c:v","copy","-c:a","copy","-c:s","mov_text",
            f"-metadata:s:s:0","language="+lang3,"-shortest",out])
        d=subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",out],capture_output=True,text=True).stdout.strip()
        print(f"review_{L}.mp4  rc={rc}  {d}s")

# ② 마스터 4K 업스케일 (Lanczos, 오디오 유지)
if MODE in ("4k","all"):
    out=os.path.join(PKG,"sejong_master_4k.mp4")
    print("4K 업스케일 시작 (시간 걸림)…")
    rc=run(["ffmpeg","-y","-v","error","-i",MASTER,
        "-vf","scale=3840:2160:flags=lanczos","-c:v","libx264","-crf","18","-preset","slow",
        "-pix_fmt","yuv420p","-c:a","copy",out])
    sz=os.path.getsize(out)/1024/1024 if os.path.exists(out) else 0
    print(f"4K 완료 rc={rc}  {out}  {sz:.0f}MB")
print("FINALIZE_DONE")
