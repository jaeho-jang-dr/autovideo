# -*- coding: utf-8 -*-
"""Parse the NotebookLM scenario JSON (value.answer) into usable production files:
   - sejong_scenario.md      (full readable scenario)
   - sejong_prompts.txt      (10 VISUAL prompts for Google Flow, numbered)
   - sejong_narration_ko.txt / _en.txt (per-scene narration for rendering)
"""
import json, re, os

SRC = "scratch/nlm/sejong_scenario_raw.txt"
OUT = "scratch/nlm/sejong"
os.makedirs(OUT, exist_ok=True)

answer = json.load(open(SRC, encoding="utf-8"))["value"]["answer"]

# Split into scenes on [장면N]
parts = re.split(r"\[장면\s*(\d+)\]", answer)
# parts = ['', '1', '<body1>', '2', '<body2>', ...]
scenes = []
for i in range(1, len(parts), 2):
    num = int(parts[i]); body = parts[i + 1]
    def grab(label, nxt):
        m = re.search(r"\*\*%s\*\*\s*(.+?)(?=\n\s*\*\s*\*\*(?:%s)|\Z)" % (label, nxt), body, re.S)
        return (m.group(1).strip() if m else "").strip()
    ko = grab("한국어 나레이션", "English Narration|VISUAL")
    en = grab("English Narration", "VISUAL")
    vis = grab("VISUAL", "$^")
    # clean trailing separators / footer question
    vis = re.split(r"\n---|\n📊", vis)[0].strip()
    en = re.split(r"\n---", en)[0].strip()
    ko = re.split(r"\n---", ko)[0].strip()
    scenes.append({"n": num, "ko": ko, "en": en, "visual": vis})

scenes = [s for s in scenes if s["n"] <= 10][:10]
print("parsed scenes:", len(scenes))

# 1) full scenario markdown
with open(os.path.join(OUT, "sejong_scenario.md"), "w", encoding="utf-8") as f:
    f.write("# 세종대왕과 한글 — 영상 시나리오 (NotebookLM 73 소스 근거)\n\n")
    f.write("> NotebookLM '세종대왕과 한글' 노트북 딥리서치 소스에서 도출. 한/영 이중언어.\n\n")
    for s in scenes:
        f.write("## 장면 %d\n\n" % s["n"])
        f.write("**KO 나레이션**\n%s\n\n" % s["ko"])
        f.write("**EN narration**\n%s\n\n" % s["en"])
        f.write("**VISUAL (Flow)**\n%s\n\n---\n\n" % s["visual"])

# 2) Flow prompts (one VISUAL per scene)
with open(os.path.join(OUT, "sejong_prompts.txt"), "w", encoding="utf-8") as f:
    for s in scenes:
        f.write("%d. %s\n\n" % (s["n"], s["visual"]))

# 3) narration per language
for lang in ("ko", "en"):
    with open(os.path.join(OUT, "sejong_narration_%s.txt" % lang), "w", encoding="utf-8") as f:
        for s in scenes:
            f.write("[%d] %s\n\n" % (s["n"], s[lang]))

print("wrote:", os.listdir(OUT))
for s in scenes:
    print("  scene %d: ko=%dch en=%dch vis=%dch" % (s["n"], len(s["ko"]), len(s["en"]), len(s["visual"])))
