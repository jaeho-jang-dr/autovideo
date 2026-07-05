# -*- coding: utf-8 -*-
"""compile_np.py 4K 마스터(_np_<lang>.mp4)에 자막 번인 1080p 리뷰본 생성.
마스터는 이미 그 언어 오디오 1트랙 + 소프트자막을 가짐 → 소프트자막 버리고 SRT를 하드번인.
출력: <proj>/<srtb>_np_<lang>_burned.mp4  (review_lesson.py가 쓰는 이름).
사용: python burn_np_master.py <proj> <srt_base> <ko|en>
"""
import os, re, sys, subprocess
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
PROJ = sys.argv[1]; SRTB = sys.argv[2]; LANG = sys.argv[3]
MASTER = os.path.join(PROJ, f"{SRTB}_np_{LANG}.mp4")
SRT = os.path.join(PROJ, f"{SRTB}_np.{LANG}.srt")
OUT = os.path.join(PROJ, f"{SRTB}_np_{LANG}_burned.mp4")
SHIFT = 0.3
ROOT = os.getcwd()

def parse(p):
    cues = []
    for blk in open(p, encoding="utf-8").read().strip().split("\n\n"):
        L = blk.strip().split("\n")
        if len(L) < 3: continue
        m = re.match(r"(\d+):(\d+):([\d,\.]+) --> (\d+):(\d+):([\d,\.]+)", L[1])
        if not m: continue
        g = lambda h, mi, se: int(h)*3600 + int(mi)*60 + float(se.replace(",", "."))
        cues.append([g(m[1],m[2],m[3]), g(m[4],m[5],m[6]), "\n".join(L[2:])])
    return cues

def ass_t(t):
    if t < 0: t = 0
    cs = int(round(t*100)); h, cs = divmod(cs, 360000); mi, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h:d}:{mi:02d}:{s:02d}.{cs:02d}"

cues = parse(SRT)
for c in cues: c[0] = max(0.0, c[0]-SHIFT); c[1] = max(0.05, c[1]-SHIFT)
ass_path = os.path.join(ROOT, f"_burnm_np_{LANG}.ass")
head = (
"[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
"[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
"Style: Default,Malgun Gothic,60,&H00FFFFFF,&H000000FF,&H00202020,&H64000000,0,0,0,0,100,100,0,0,1,4,1,2,80,80,135,1\n\n"
"[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
with open(ass_path, "w", encoding="utf-8") as f:
    f.write(head)
    for st, ed, tx in cues:
        t = tx.replace("\n", "\\N").replace("{", "(").replace("}", ")")
        f.write(f"Dialogue: 0,{ass_t(st)},{ass_t(ed)},Default,,0,0,0,,{t}\n")
print(f"[{PROJ}/{LANG}] ASS {len(cues)}큐, master={os.path.basename(MASTER)}", flush=True)
vf = f"scale=1920:1080,ass=_burnm_np_{LANG}.ass"
cmd = [FF, "-y", "-i", MASTER, "-vf", vf, "-map", "0:v:0", "-map", "0:a:0",
       "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-sn", OUT]
r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
try: os.remove(ass_path)
except Exception: pass
def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True).stdout.strip())
    except Exception: return 0
if r.returncode == 0 and os.path.exists(OUT):
    print(f"[{PROJ}/{LANG}] DONE: {OUT} ({dur(OUT):.1f}s, {os.path.getsize(OUT)/1e6:.0f}MB)", flush=True)
else:
    print(f"[{PROJ}/{LANG}] FAILED rc={r.returncode}", flush=True); print((r.stderr or "")[-1500:], flush=True)
