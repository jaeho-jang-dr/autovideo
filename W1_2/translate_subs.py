# -*- coding: utf-8 -*-
"""W1-2 자막 5종 — ko / en / ja / zh-Hans / es-419.

★사장님 지시(2026-08-17) "자막 5개 다 만들고."

## 무엇을 번역하고 무엇을 남기나
이 강의의 자막은 **한글 낱말 + 로마자 발음 + 설명** 세 겹이다.
  Careful — the milk is falling! '우유' [u-yu] — sweet white milk.
번역해야 하는 것은 **설명뿐**이다. `'우유'` 와 `[u-yu]` 는 배우는 대상 그 자체라
어느 나라 자막에서도 그대로 남아야 한다([[subtitle-keep-hangeul-in-all-langs]]).

## 왜 원본이 영어판인가
타이밍이 이미 나레이션에 맞춰져 있고, 설명이 한 문장으로 정리돼 있어 번역 지시가
분명해진다. 한국어판은 문장이 길고 어미가 달라 옮기면 줄이 밀린다.

## gemini 가 조용히 실패하는 함정
`GOOGLE_CLOUD_PROJECT` 가 없으면 gemini CLI 는 오류 없이 **원문을 그대로 뱉는다**
([[gemini-cli-project-id-auth]]). 그래서 마지막에 원문과 같은지 반드시 검사한다.

  python W1_2/translate_subs.py
"""
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

EN = "W1_2/w1d2_v3_en.srt"
KO = "W1_2/w1d2_v4_ko.srt"
PKG = "W1_2/subs"
STEM = "w1d2"
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
    numbered = "\n".join("[%d] %s" % (i + 1, t) for i, t in enumerate(texts))
    prompt = (
        "You are translating subtitles for a Korean-language lesson into %s.\n"
        "RULES (critical):\n"
        "1) Keep every Korean chunk inside single quotes '...' EXACTLY unchanged.\n"
        "2) Keep every romanization inside square brackets [...] EXACTLY unchanged.\n"
        "3) Keep bare jamo letters (%s etc.) EXACTLY unchanged.\n"
        "4) Translate ONLY the surrounding explanation into natural %s.\n"
        "5) Output EXACTLY one line per input line, each prefixed with the same [n]. "
        "Exactly %d lines. No headers, no commentary.\n\n"
        % (langname, "ㅏ ㅣ ㅗ ㅜ ㆍ", langname, len(texts))) + numbered
    gem = os.environ.get("GEMINI_CMD", "gemini")
    env = dict(os.environ)
    env.setdefault("GOOGLE_CLOUD_PROJECT", "miryangosweb")   # ★없으면 조용히 원문 반환
    r = subprocess.run('"%s" -m gemini-2.5-flash --yolo' % gem, input=prompt, shell=True,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="ignore", timeout=600, env=env)
    out = r.stdout or ""
    trans = {}
    for m in re.finditer(r"\[(\d+)\]\s*(.+)", out):
        trans[int(m.group(1))] = m.group(2).strip()
    miss = [i + 1 for i in range(len(texts)) if (i + 1) not in trans]
    return [trans.get(i + 1, texts[i]) for i in range(len(texts))], miss


def main():
    os.makedirs(PKG, exist_ok=True)
    blocks = parse(EN)
    texts = [" ".join(b["text"]) for b in blocks]
    print("영어판 %d줄이 원본" % len(blocks))
    shutil.copy(EN, os.path.join(PKG, "%s.en.srt" % STEM))
    if os.path.exists(KO):
        shutil.copy(KO, os.path.join(PKG, "%s.ko.srt" % STEM))
        print("  ko: 한글판 자막 그대로")
    print("  en: 영어판 자막 그대로")

    for code, name in LANGS.items():
        tr, miss = translate(texts, name)
        out = os.path.join(PKG, "%s.%s.srt" % (STEM, code))
        with open(out, "w", encoding="utf-8") as f:
            for b, t in zip(blocks, tr):
                f.write("%s\n%s\n%s\n\n" % (b["idx"], b["time"], t))
        same = sum(1 for a, b in zip(texts, tr) if a == b)
        kr = sum(1 for t in tr if re.search(r"[가-힣ㆍ]", t))
        rom = sum(1 for t in tr if re.search(r"\[[a-z\- ]+\]", t))
        flag = "  ★번역 안 됨(원문 그대로)" if same > len(tr) * 0.8 else ""
        print("  %-8s %d줄 · 한글보존 %d · 발음기호 %d · 누락 %d%s"
              % (code, len(tr), kr, rom, len(miss), flag))
    print("\n자막 5종 → %s" % PKG)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
