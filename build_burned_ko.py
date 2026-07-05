# -*- coding: utf-8 -*-
"""한글 자막 번인 버전: SRT 0.5s 앞당김 → ASS(스타일 내장)로 1080p 영상에 KO자막 번인.
출력: child_growth_science/child_growth_ko_burned_1080.mp4 (KO 나레이션 유지)."""
import os, re, subprocess, shutil

ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
CG = os.path.join(ROOT, "child_growth_science")
SRC_SRT = os.path.join(CG, "child_growth.ko.srt")
SHIFT = 0.3   # v4: 타이밍이 이미 정확(한글 안 잘림) → 자막 살짝만 앞당김(읽기 여유)
DUB = os.path.join(CG, "child_growth_dub.mp4")
OUT = os.path.join(CG, "child_growth_ko_burned_1080.mp4")

def parse(p):
    cues = []
    for blk in open(p, encoding="utf-8").read().strip().split("\n\n"):
        L = blk.strip().split("\n")
        if len(L) < 3: continue
        m = re.match(r"(\d+):(\d+):([\d,\.]+) --> (\d+):(\d+):([\d,\.]+)", L[1])
        if not m: continue
        g = lambda h, mi, se: int(h)*3600 + int(mi)*60 + float(se.replace(",", "."))
        cues.append([g(m[1], m[2], m[3]), g(m[4], m[5], m[6]), "\n".join(L[2:])])
    return cues

def srt_t(t):
    if t < 0: t = 0
    ms = int(round(t*1000)); h, ms = divmod(ms, 3600000); mi, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{mi:02d}:{s:02d},{ms:03d}"
def ass_t(t):
    if t < 0: t = 0
    cs = int(round(t*100)); h, cs = divmod(cs, 360000); mi, cs = divmod(cs, 6000); s, cs = divmod(cs, 100)
    return f"{h:d}:{mi:02d}:{s:02d}.{cs:02d}"

cues = parse(SRC_SRT)
for c in cues:
    c[0] = max(0.0, c[0] - SHIFT); c[1] = max(0.05, c[1] - SHIFT)

# 앞당긴 SRT + VTT(리뷰앱용)
shifted = os.path.join(CG, "child_growth_shift.ko.srt")
with open(shifted, "w", encoding="utf-8") as f:
    for i, (st, ed, tx) in enumerate(cues, 1):
        f.write(f"{i}\n{srt_t(st)} --> {srt_t(ed)}\n{tx}\n\n")
vtt = os.path.join(CG, "child_growth_v3.ko.vtt")
txt = re.sub(r"(\d\d:\d\d:\d\d),(\d\d\d)", r"\1.\2", open(shifted, encoding="utf-8").read())
open(vtt, "w", encoding="utf-8").write("WEBVTT\n\n" + txt)
print(f"앞당긴 SRT/VTT 저장 ({SHIFT}s)", flush=True)

# ASS 생성 (Malgun Gothic, 흰글자+어두운 외곽선, 하단중앙)
ass_path = os.path.join(ROOT, "_burn_ko.ass")
head = (
"[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 0\nScaledBorderAndShadow: yes\n\n"
"[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
"Style: Default,Malgun Gothic,46,&H00FFFFFF,&H000000FF,&H00202020,&H64000000,0,0,0,0,100,100,0,0,1,3,1,2,60,60,54,1\n\n"
"[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
)
with open(ass_path, "w", encoding="utf-8") as f:
    f.write(head)
    for st, ed, tx in cues:
        t = tx.replace("\n", "\\N").replace("{", "(").replace("}", ")")
        f.write(f"Dialogue: 0,{ass_t(st)},{ass_t(ed)},Default,,0,0,0,,{t}\n")
print("ASS 생성 완료", flush=True)

vf = "scale=1920:1080,ass=_burn_ko.ass"
cmd = ["ffmpeg", "-y", "-i", DUB, "-vf", vf,
       "-map", "0:v:0", "-map", "0:a:0",
       "-c:v", "libx264", "-preset", "medium", "-crf", "20",
       "-c:a", "aac", "-b:a", "192k", "-metadata:s:a:0", "language=kor", OUT]
print("번인 인코딩 시작(1080p)…", flush=True)
r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
try: os.remove(ass_path)
except Exception: pass
if r.returncode == 0 and os.path.exists(OUT):
    print(f"DONE: {OUT} ({os.path.getsize(OUT)/1e6:.0f}MB)", flush=True)
else:
    print("FFMPEG FAILED rc=" + str(r.returncode), flush=True)
    print((r.stderr or "")[-1500:], flush=True)
