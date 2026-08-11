# -*- coding: utf-8 -*-
"""titan_science 자막 번역 — en.srt 타이밍 그대로 ja / zh-Hans / es-419.

translate_srt_w24.py 를 그대로 따왔다(한글 보존 규칙은 이 영상엔 없어서 뺐다).
★gemini CLI 는 GOOGLE_CLOUD_PROJECT 가 없으면 조용히 실패하고 **원문을 그대로 뱉는다**.
  그래서 마지막에 en 과 바이트가 같은지 반드시 검사한다.
"""
import os
import re
import shutil
import subprocess

os.chdir(os.path.dirname(os.path.abspath(__file__)))
SUB = "titan_science/subs"
EN = f"{SUB}/TITAN_en.srt"
KO = f"{SUB}/TITAN_ko.srt"
LANGS = {"ja": "Japanese",
         "zh-Hans": "Simplified Chinese (mainland)",
         "es-419": "Latin American Spanish"}


def parse(path):
    blocks, cur = [], None
    for ln in open(path, encoding="utf-8"):
        s = ln.rstrip("\n")
        if re.match(r"^\d+$", s):
            cur = {"idx": s, "time": None, "text": []}
        elif "-->" in s:
            if cur:
                cur["time"] = s
        elif s.strip() == "":
            if cur:
                blocks.append(cur)
                cur = None
        else:
            if cur:
                cur["text"].append(s)
    if cur:
        blocks.append(cur)
    return blocks


def translate(texts, langname):
    numbered = "\n".join(f"[{i+1}] {t}" for i, t in enumerate(texts))
    prompt = (
        f"You are translating subtitles for a popular-science cartoon video about "
        f"why a giant humanoid creature could not work under real physics "
        f"(square-cube law, heat dissipation, bone strength) into {langname}.\n"
        f"RULES (critical):\n"
        f"1) Natural, conversational {langname} that a 15-30 year old viewer enjoys.\n"
        f"2) Keep numbers and units exactly (50m, 48 tons, 1638, 190 tons).\n"
        f"3) Keep each line short enough to read as a subtitle.\n"
        f"4) Output EXACTLY one line per input line, each prefixed with the same [n]. "
        f"Exactly {len(texts)} lines. No headers, no extra commentary.\n\n" + numbered)
    gem = os.environ.get("GEMINI_CMD", "gemini")
    env = dict(os.environ)
    env.setdefault("GOOGLE_CLOUD_PROJECT", "miryangosweb")      # ★없으면 인증이 깨진다
    r = subprocess.run(f'"{gem}" -m gemini-2.5-flash --yolo', input=prompt, shell=True,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="ignore", timeout=600, env=env)
    out = r.stdout or ""
    trans = {}
    for m in re.finditer(r"\[(\d+)\]\s*(.+)", out):
        trans[int(m.group(1))] = m.group(2).strip()
    miss = [i + 1 for i in range(len(texts)) if (i + 1) not in trans]
    return [trans.get(i + 1, texts[i]) for i in range(len(texts))], miss


def main():
    blocks = parse(EN)
    texts = [" ".join(b["text"]) for b in blocks]
    print("블록 %d개" % len(blocks))
    en_size = os.path.getsize(EN)
    for code, name in LANGS.items():
        tr, miss = translate(texts, name)
        p = f"{SUB}/TITAN_{code}.srt"
        with open(p, "w", encoding="utf-8") as f:
            for b, t in zip(blocks, tr):
                f.write("%s\n%s\n%s\n\n" % (b["idx"], b["time"], t))
        same = os.path.getsize(p) == en_size
        print("  %-7s %3d줄 · 누락 %d %s %s"
              % (code, len(tr), len(miss), miss[:5],
                 "★en과 크기 동일 — 번역 통째 실패 의심" if same else ""))
    print("자막 5종 →", SUB)
    for f in sorted(os.listdir(SUB)):
        if f.endswith(".srt"):
            print("   %-22s %6d B" % (f, os.path.getsize(os.path.join(SUB, f))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
