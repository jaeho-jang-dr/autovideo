# -*- coding: utf-8 -*-
"""W21 5개국 자막: en.srt 타이밍 + ja/zh/es 번역(gemini). '한글'·[발음]은 그대로, 설명만 번역.
   ko/en은 그대로 복사. → hangeul_birth_vowels/w21pkg/hangeul_w21_madam_np.{code}.srt"""
import re, os, subprocess, shutil
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
BASE = "hangeul_birth_vowels"
EN = f"{BASE}/hangeul_w21_madam_np.en.srt"
KO = f"{BASE}/hangeul_w21_madam_np.ko.srt"
PKG = f"{BASE}/w21pkg"
os.makedirs(PKG, exist_ok=True)
LANGS = {"ja": "Japanese", "zh": "Simplified Chinese (mainland)", "es": "Latin American Spanish"}


def parse(path):
    blocks, cur = [], None
    for ln in open(path, encoding="utf-8"):
        s = ln.rstrip("\n")
        if re.match(r"^\d+$", s):
            cur = {"idx": s, "time": None, "text": []}
        elif "-->" in s:
            if cur: cur["time"] = s
        elif s.strip() == "":
            if cur: blocks.append(cur); cur = None
        else:
            if cur: cur["text"].append(s)
    if cur: blocks.append(cur)
    return blocks


def translate(texts, langname):
    numbered = "\n".join(f"[{i+1}] {t}" for i, t in enumerate(texts))
    prompt = (
        f"You are translating subtitles for a Korean-language lesson into {langname}.\n"
        f"RULES (critical):\n"
        f"1) Keep every Korean chunk inside single quotes '...' EXACTLY unchanged.\n"
        f"2) Keep every romanization inside square brackets [...] EXACTLY unchanged.\n"
        f"3) Translate ONLY the surrounding explanation/meaning into natural {langname}.\n"
        f"4) Output EXACTLY one line per input line, each prefixed with the same [n]. "
        f"Exactly {len(texts)} lines. No headers, no extra commentary.\n\n" + numbered)
    gem = os.environ.get("GEMINI_CMD", "gemini")
    r = subprocess.run(f'"{gem}" -m gemini-2.5-flash --yolo', input=prompt, shell=True,
                       capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=420)
    out = r.stdout or ""
    trans = {}
    for m in re.finditer(r"\[(\d+)\]\s*(.+)", out):
        trans[int(m.group(1))] = m.group(2).strip()
    miss = [i + 1 for i in range(len(texts)) if (i + 1) not in trans]
    return [trans.get(i + 1, texts[i]) for i in range(len(texts))], miss


blocks = parse(EN)
texts = [" ".join(b["text"]) for b in blocks]
print(f"블록 {len(blocks)}개")
# ko/en 복사
shutil.copy(KO, f"{PKG}/hangeul_w21_madam_np.ko.srt")
shutil.copy(EN, f"{PKG}/hangeul_w21_madam_np.en.srt")
for code, name in LANGS.items():
    tr, miss = translate(texts, name)
    with open(f"{PKG}/hangeul_w21_madam_np.{code}.srt", "w", encoding="utf-8") as f:
        for b, t in zip(blocks, tr):
            f.write(f"{b['idx']}\n{b['time']}\n{t}\n\n")
    kr = sum(1 for t in tr if re.search(r"[가-힣]", t))
    print(f"  {code}: {len(tr)}줄 · 한글보존 {kr}줄 · 누락 {len(miss)}{miss[:5]}")
print("자막 5종 완료 →", PKG)
