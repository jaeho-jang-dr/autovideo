# -*- coding: utf-8 -*-
"""교정된 _ko_dae 클립들로 KO 트랙 재조립 + 더빙본 재먹싱(영상·EN·자막 그대로)."""
import os, re, subprocess
CG = "D:/Entertainments/DevEnvironment/autovideo/child_growth_science"
KODIR = os.path.join(CG, "_ko_dae"); TMP = os.path.join(CG, "_dub_tmp"); os.makedirs(TMP, exist_ok=True)
VIDEO = os.path.join(CG, "child_growth.mp4")
def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True).stdout.strip())
    except: return 0.0
def parse(p):
    out=[]
    for blk in open(p,encoding="utf-8").read().strip().split("\n\n"):
        L=blk.strip().split("\n")
        if len(L)>=3 and re.match(r"\d+:\d+",L[1]): out.append(1)
    return len(out)
N=parse(os.path.join(CG,"child_growth.ko.srt"))
VDUR=dur(VIDEO)
# concat 순서
listf=os.path.join(TMP,"list_ko_fix.txt")
with open(listf,"w",encoding="utf-8") as f:
    for i in range(N):
        p=os.path.join(KODIR,f"{i:03d}.mp3")
        f.write(f"file '{p}'\n")
kot=os.path.join(CG,"track_ko.m4a")
subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",listf,"-af",f"apad,atrim=0:{VDUR:.3f}","-c:a","aac","-b:a","192k",kot],timeout=180)
print(f"KO 트랙 재조립: {dur(kot):.1f}s (영상 {VDUR:.1f}s)")
ent=os.path.join(CG,"track_en.m4a")
out=os.path.join(CG,"child_growth_dub.mp4")
subprocess.run(["ffmpeg","-y","-v","error","-i",VIDEO,"-i",kot,"-i",ent,
    "-map","0:v","-map","1:a","-map","2:a","-map","0:s?",
    "-c:v","copy","-c:a","aac","-b:a","192k","-c:s","copy",
    "-metadata:s:a:0","language=kor","-metadata:s:a:0","title=한국어(Dae)",
    "-metadata:s:a:1","language=eng","-metadata:s:a:1","title=English(Alice)",
    "-disposition:a:0","default", out],timeout=600)
print("REMUX DONE:",out,f"{dur(out)/60:.2f}분")
