# -*- coding: utf-8 -*-
"""W9 5개국어 자막 생성. 원본 srt(ko=KO영상 타임라인, en=EN영상 타임라인)에서 텍스트만 뽑아
Gemini로 번역(한국어 따옴표 단어는 그대로 유지) → 원본 타임스탬프로 rebuild. 타임스탬프 훼손 0.
출력: hangeul_birth_vowels/w9pkg/<vid>_<lang>.srt  (vid=ko|en 영상, lang=ko/en/ja/zh/es)
사용: python w9_subs_gen.py
"""
import os, re, subprocess, sys
BASE = "hangeul_birth_vowels"; OUT = os.path.join(BASE, "w9pkg"); os.makedirs(OUT, exist_ok=True)
GEMINI = "gemini"
LANG_NAME = {"en": "English", "ja": "Japanese", "zh": "Simplified Chinese", "es": "Spanish", "ko": "Korean"}
# 각 영상별: 원본 srt + 그 영상에 넣을 자막 언어들
JOBS = {
    "ko": {"src": f"{BASE}/hangeul_w9v2_stickman_np.ko.srt", "langs": ["en", "ja", "zh", "es"]},
    "en": {"src": f"{BASE}/hangeul_w9v2_stickman_np.en.srt", "langs": ["ko", "ja", "zh", "es"]},
}

def parse(path):
    blocks, order = {}, []
    raw = open(path, encoding="utf-8").read().replace("\r\n", "\n").strip()
    for chunk in re.split(r"\n\s*\n", raw):
        lines = chunk.split("\n")
        if len(lines) < 2 or not lines[0].strip().isdigit():
            continue
        idx = lines[0].strip(); ts = lines[1].strip(); text = " ".join(lines[2:]).strip()
        blocks[idx] = (ts, text); order.append(idx)
    return blocks, order

def translate(texts, lang):
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
    prompt = (f"Translate each numbered line into natural {LANG_NAME[lang]} for a Korean-language lesson subtitle. "
              f"KEEP any Korean word/phrase in single quotes '…' EXACTLY as-is (do not translate what's inside the quotes). "
              f"Translate only the surrounding explanation. Output ONLY the same numbered lines (same count, same numbers), nothing else.")
    p = subprocess.run([GEMINI, "-m", "gemini-2.5-flash", "--yolo", prompt],
                       input=numbered, capture_output=True, text=True, encoding="utf-8", timeout=240)
    out = p.stdout or ""
    res = {}
    for line in out.split("\n"):
        m = re.match(r"\s*(\d+)[.)]\s*(.*)", line)
        if m:
            res[int(m.group(1))] = m.group(2).strip()
    return res

total = 0
for vid, job in JOBS.items():
    blocks, order = parse(job["src"])
    texts = [blocks[i][1] for i in order]
    for lang in job["langs"]:
        tr = translate(texts, lang)
        outp = os.path.join(OUT, f"{vid}_{lang}.srt")
        parts = []
        for n, idx in enumerate(order, 1):
            ts = blocks[idx][0]
            txt = tr.get(n, blocks[idx][1])  # 누락 시 원문 폴백
            parts.append(f"{n}\n{ts}\n{txt}")
        open(outp, "w", encoding="utf-8").write("\n\n".join(parts) + "\n")
        ok = sum(1 for n in range(1, len(order)+1) if n in tr)
        print(f"{vid}_{lang}.srt: {len(order)}블록 (번역성공 {ok})", flush=True)
        total += 1
print(f"=== {total}개 자막 생성 완료 → {OUT} ===")
