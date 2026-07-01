# -*- coding: utf-8 -*-
"""48씬 개요를 표 파일(MD/CSV)로 저장 + 컨택트시트 보관본 복사.
출력:
  sejong_film/main/keyframes_overview.md   (사람이 보는 표 + 시트 참조)
  sejong_film/main/scenes48.csv            (엑셀/시트용)
  sejong_film/main/keyframes_contactsheet.png  (48장 한장 보관본)
"""
import os, json, csv, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MAIN = os.path.join(ROOT, "sejong_film", "main")
shots = json.load(open(os.path.join(ROOT, "scratch", "shots48.json"), encoding="utf-8"))

ACTS = [
    (1, 6,  "1막 · 어린 시절 (충녕대군)"),
    (7, 14, "2막 · 청년 / 즉위 전"),
    (15, 23, "3막 · 즉위 · 젊은 왕"),
    (24, 41, "4막 · 훈민정음 창제"),
    (42, 48, "5막 · 노년 · 유산"),
]
LEN = {"S": "짧음(S)", "M": "보통(M)", "L": "김(L)"}

def act_of(n):
    for a, b, t in ACTS:
        if a <= n <= b:
            return t
    return ""

# ---------- CSV ----------
csv_path = os.path.join(MAIN, "scenes48.csv")
with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["씬", "막", "모드", "인물", "길이", "전환", "비주얼", "KO 나레이션(요약)"])
    for s in shots:
        ko = (s.get("ko") or "").replace("\n", " ")
        w.writerow([f"S{s['n']:02d}", act_of(s["n"]), s["mode"], s.get("char", "-"),
                    s.get("len", ""), s.get("trans", ""), s.get("vis", ""), ko])

# ---------- Markdown ----------
md = []
md.append("# 세종대왕과 한글 · 본편 48씬 개요\n")
md.append("> 하이브리드(🎬실사 / ✏️애니) 본편 구성표. 키프레임 48장 = `sejong_film/main/keyframes/S01.png ~ S48.png`.\n")
md.append("> 48장 한눈에 보기: `keyframes_contactsheet.png`\n")
md.append("\n![48 keyframes](keyframes_contactsheet.png)\n")

cur_act = None
for s in shots:
    a = act_of(s["n"])
    if a != cur_act:
        cur_act = a
        md.append(f"\n## {a}\n")
        md.append("| 씬 | 모드 | 인물 | 길이 | 전환 | 비주얼 |")
        md.append("|----|------|------|------|------|--------|")
    mode_icon = "🎬실사" if s["mode"] == "실사" else "✏️애니"
    vis = (s.get("vis") or "").replace("|", "/")
    md.append(f"| **S{s['n']:02d}** | {mode_icon} | {s.get('char','-')} | {LEN.get(s.get('len',''), s.get('len',''))} | {s.get('trans','')} | {vis} |")

n_real = sum(1 for s in shots if s["mode"] == "실사")
n_anim = sum(1 for s in shots if s["mode"] == "애니")
md.append(f"\n---\n\n**합계**: 총 48씬 · 🎬실사 {n_real} · ✏️애니 {n_anim}\n")

md_path = os.path.join(MAIN, "keyframes_overview.md")
open(md_path, "w", encoding="utf-8").write("\n".join(md))

# ---------- 컨택트시트 보관본 복사 ----------
src = os.path.join(ROOT, "scratch", "kf_all48.png")
dst = os.path.join(MAIN, "keyframes_contactsheet.png")
if os.path.exists(src):
    shutil.copyfile(src, dst)

print("WROTE:")
print(" ", md_path)
print(" ", csv_path)
print(" ", dst if os.path.exists(dst) else "(no contact sheet src)")
print(f"실사 {n_real} / 애니 {n_anim} / 총 {len(shots)}")
