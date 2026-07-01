# -*- coding: utf-8 -*-
"""Assemble act_1..5.md into the full 20-min scenario + production files."""
import re, os

IN = "scratch/nlm/sejong"
OUTDIR = "sejong_film"
os.makedirs(OUTDIR, exist_ok=True)

ACTS = [
    ("1", "어린시절 — 책을 사랑한 소년 충녕", "sejong_child"),
    ("2", "청년 — 학자 대군, 혼인과 가족", "sejong_youth"),
    ("3", "청년왕 — 즉위, 집현전, 백성의 문맹", "sejong_youngking"),
    ("4", "장년 — 훈민정음 창제 (핵심)", "sejong_mid"),
    ("5", "노년 — 보급·승하·영원한 유산", "sejong_old"),
]

def parse(md):
    scenes = []
    blocks = re.split(r"\[장면\s*\d+\]", md)
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        def grab(label, nxt):
            m = re.search(r"\*\s*%s\s*:\s*(.+?)(?=\n\s*\*\s*(?:%s)\s*:|\Z)" % (label, nxt), b, re.S)
            return (m.group(1).strip() if m else "")
        ch = grab("캐릭터", "한국어 나레이션|English narration|VISUAL")
        ko = grab("한국어 나레이션", "English narration|VISUAL")
        en = grab("English narration", "VISUAL")
        vis = grab("VISUAL", "\\Z")
        vis = re.split(r"\n📊|\n---", vis)[0].strip()
        if ko or vis:
            scenes.append({"char": ch, "ko": ko, "en": en, "visual": vis})
    return scenes

all_scenes = []
full = ["# 세종대왕과 한글 — 20분 특별판 시나리오",
        "", "> NotebookLM '세종대왕과 한글' 노트북 130개 딥리서치 소스에서 도출. 한/영 이중언어. 1인칭 세종 시점.",
        "> 캐릭터: 5나이대(어린시절·청년·청년왕·장년·노년) 일관 캐릭터.", ""]
g = 0
act_ranges = []
for num, title, charkey in ACTS:
    md = open(os.path.join(IN, f"act_{num}.md"), encoding="utf-8").read()
    sc = parse(md)
    start = g + 1
    full.append(f"\n## {num}막 · {title}  (캐릭터: {charkey})\n")
    for s in sc:
        g += 1
        s["g"] = g; s["act"] = num; s["charkey"] = charkey
        all_scenes.append(s)
        full.append(f"### 장면 {g}")
        full.append(f"*캐릭터: {s['char']}*\n")
        full.append(f"**KO** {s['ko']}\n")
        full.append(f"**EN** {s['en']}\n")
        full.append(f"**VISUAL** {s['visual']}\n")
    act_ranges.append((num, title, start, g, len(sc)))

open(os.path.join(OUTDIR, "sejong_20min_scenario.md"), "w", encoding="utf-8").write("\n".join(full))

# Flow prompts (global scene -> VISUAL)
with open(os.path.join(OUTDIR, "sejong_prompts.txt"), "w", encoding="utf-8") as f:
    for s in all_scenes:
        f.write(f"{s['g']}. [{s['charkey']}] {s['visual']}\n\n")
# narration
for lang in ("ko", "en"):
    with open(os.path.join(OUTDIR, f"sejong_narration_{lang}.txt"), "w", encoding="utf-8") as f:
        for s in all_scenes:
            f.write(f"[{s['g']}] {s[lang]}\n\n")

print(f"총 장면: {len(all_scenes)}")
for num, title, st, en_, n in act_ranges:
    print(f"  {num}막 {title}: 장면 {st}~{en_} ({n}개)")
est_sec = len(all_scenes) * 32
print(f"추정 길이: ~{est_sec//60}분 {est_sec%60}초 (장면당 ~32초 가정)")
print("출력:", [x for x in os.listdir(OUTDIR) if x.startswith('sejong_2') or x.startswith('sejong_prompts') or x.startswith('sejong_narr')])
