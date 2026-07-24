# -*- coding: utf-8 -*-
"""★자막 블록에 '영어 원문 + 번역'이 2줄로 중복된 경우, 영어 원문 줄만 제거.
   (제미나이가 원문을 지우지 않고 아래에 번역을 붙인 사고 — 번역/타임스탬프는 정상이라 재번역 불필요)
   ⚠️한글·[로마자]가 든 줄은 절대 지우지 않는다.
사용: python strip_dup_english.py <srt> [<srt> ...]
"""
import re, sys, shutil

LANG = r"[ぁ-んァ-ヶ一-龥]"          # 일본어/중국어 문자
HANGEUL = r"[가-힣ㄱ-ㅎㅏ-ㅣ]"


def is_english_line(t):
    """대상언어 문자·한글이 전혀 없고 영단어가 1개 이상인 줄 = 원문 잔존.
       ★한글이나 대상언어가 든 줄은 정상 자막이므로 절대 건드리지 않는다.
       ★같은 블록에 번역 줄이 따로 있을 때만 호출됨(strip에서 보장)."""
    if re.search(LANG, t) or re.search(HANGEUL, t):
        return False
    return len(re.findall(r"[A-Za-z]{2,}", t)) >= 1


def strip(path):
    src = open(path, encoding="utf-8").read().strip().split("\n\n")
    out, removed = [], 0
    for b in src:
        L = b.split("\n")
        if len(L) < 3 or "-->" not in L[1]:
            out.append(b)
            continue
        head, ts, text = L[0], L[1], L[2:]
        keep = [t for t in text if not is_english_line(t)]
        # 전부 지워지면(=번역 줄이 없음) 원본 유지
        if not [k for k in keep if k.strip()]:
            keep = text
        removed += len(text) - len(keep)
        out.append("\n".join([head, ts] + keep))
    shutil.copy(path, path + ".bak")
    open(path, "w", encoding="utf-8").write("\n\n".join(out) + "\n")
    print(f"{path}: 영어 원문 {removed}줄 제거 (백업 .bak)")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        strip(p)
