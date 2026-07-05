# -*- coding: utf-8 -*-
"""언어별 자막 번인 1080p (아웃트로 잘라냄). 사용: python burn_lang.py <ko|en>
- ko: KO오디오(a:0)+한글자막 번인 / en: EN오디오(a:1)+영어자막 번인
- 끝을 나레이션 끝(sum slots)으로 잘라 뒤 아웃트로 제거. 자막 0.3s 앞당김."""
import os, re, sys, json, subprocess

LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
assert LANG in ("ko", "en")
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
CG = os.path.join(ROOT, "child_growth_science")
SRC_SRT = os.path.join(CG, f"child_growth.{LANG}.srt")
DUB = os.path.join(CG, "child_growth_dub.mp4")
OUT = os.path.join(CG, f"child_growth_{LANG}_v4_1080.mp4")
AUDIO_MAP = "0:a:0" if LANG == "ko" else "0:a:1"
SHIFT = 0.3
END = round(sum(json.load(open(os.path.join(CG, "durations_v4.json"), encoding="utf-8")).values()), 2)  # 나레이션 끝 = 아웃트로 앞

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

cues = parse(SRC_SRT)
for c in cues:
    c[0] = max(0.0, c[0]-SHIFT); c[1] = max(0.05, c[1]-SHIFT)

ass_path = os.path.join(ROOT, f"_burn_{LANG}.ass")
head = (
"[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
"[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
"Style: Default,Malgun Gothic,44,&H00FFFFFF,&H000000FF,&H00202020,&H64000000,0,0,0,0,100,100,0,0,1,3,1,2,80,80,54,1\n\n"
"[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
)
with open(ass_path, "w", encoding="utf-8") as f:
    f.write(head)
    for st, ed, tx in cues:
        if st >= END: continue
        t = tx.replace("\n", "\\N").replace("{", "(").replace("}", ")")
        f.write(f"Dialogue: 0,{ass_t(st)},{ass_t(min(ed,END))},Default,,0,0,0,,{t}\n")
print(f"[{LANG}] ASS 생성, END(아웃트로컷)={END}s, 오디오={AUDIO_MAP}", flush=True)

vf = f"scale=1920:1080,ass=_burn_{LANG}.ass"
cmd = ["ffmpeg", "-y", "-t", str(END), "-i", DUB, "-t", str(END), "-vf", vf,
       "-map", "0:v:0", "-map", AUDIO_MAP,
       "-c:v", "libx264", "-preset", "medium", "-crf", "20",
       "-c:a", "aac", "-b:a", "192k", OUT]
print(f"[{LANG}] 번인 인코딩(아웃트로 제거)…", flush=True)
r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
try: os.remove(ass_path)
except Exception: pass
if r.returncode == 0 and os.path.exists(OUT):
    def dur(p):
        try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True).stdout.strip())
        except: return 0
    print(f"[{LANG}] DONE: {OUT} ({dur(OUT):.1f}s, {os.path.getsize(OUT)/1e6:.0f}MB)", flush=True)
else:
    print(f"[{LANG}] FAILED rc={r.returncode}", flush=True); print((r.stderr or "")[-1200:], flush=True)
