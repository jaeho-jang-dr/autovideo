# -*- coding: utf-8 -*-
"""titan 설명문 ja / zh / es 번역 — en_desc 를 원본으로 삼는다."""
import os
import subprocess

os.chdir(os.path.dirname(os.path.abspath(__file__)))
P = "titan_science/pkg"
SRC = open(f"{P}/en_desc.txt", encoding="utf-8").read().strip()
LANGS = {"ja": "Japanese",
         "zh": "Simplified Chinese (mainland China)",
         "es": "Latin American Spanish"}


def tx(name):
    prompt = (
        f"Translate this YouTube video description into natural, engaging {name}.\n"
        f"RULES:\n"
        f"1) Keep the layout exactly — paragraph breaks, the bullet list with '·', "
        f"the '──────────' divider, the two '*' notice lines, and the URL on its own line.\n"
        f"2) Keep numbers and units exactly (60 m, 1638, 48 tons, 190 tons).\n"
        f"3) Keep the subtitle language names line as-is: 한국어 · English · 日本語 · 中文 · Español\n"
        f"4) Keep https://drjayed.com unchanged.\n"
        f"5) Output ONLY the translated description. No preamble, no code fences.\n\n"
        + SRC)
    env = dict(os.environ)
    env.setdefault("GOOGLE_CLOUD_PROJECT", "miryangosweb")
    r = subprocess.run('"gemini" -m gemini-2.5-flash --yolo', input=prompt, shell=True,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="ignore", timeout=600, env=env)
    out = (r.stdout or "").strip()
    # gemini CLI 머리말 제거
    lines = [ln for ln in out.splitlines()
             if not ln.startswith(("YOLO mode", "Server '", "Loaded cached"))]
    return "\n".join(lines).strip()


for code, name in LANGS.items():
    t = tx(name)
    p = f"{P}/{code}_desc.txt"
    open(p, "w", encoding="utf-8").write(t + "\n")
    same = t.strip() == SRC.strip()
    print("  %-3s %5d자 %s" % (code, len(t), "★영문 그대로 — 번역 실패" if same else ""))
print("설명 5종 →", P)
