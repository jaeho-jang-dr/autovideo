# -*- coding: utf-8 -*-
"""★일본어 자막 따옴표 통일 — W13 규격에 맞춘다.
   제미나이가 일본어 번역 시 한글을 일본식 낫표「」로 감싸는 경우가 있는데,
   다른 언어(중국어·스페인어)와 W13은 전부 작은따옴표 '…' 를 쓴다.
     잘못: 「일어나다」[il-eo-na-da] — …
     정상: '일어나다' [il-eo-na-da] — …
   ①「한글」 → '한글'   ②] 뒤 공백 정리   ③ ' 뒤 [발음] 앞 공백 보장
사용: python fix_ja_quotes.py <srt> [<srt> ...]
"""
import re, sys, shutil, os

HAN = r"[가-힣ㄱ-ㅎㅏ-ㅣ]"


def fix(path):
    t = open(path, encoding="utf-8").read()
    orig = t
    # ① 낫표 안에 한글이 든 경우만 작은따옴표로 (일본어 본문의 「」 인용은 건드리지 않음)
    t = re.sub(r"「([^」]*" + HAN + r"[^」]*)」", r"'\1'", t)
    # ② '한글'[발음] → '한글' [발음]  (발음기호 앞 공백 보장)
    t = re.sub(r"('(?:[^']*" + HAN + r"[^']*)')(\[[a-z/ -]+\])", r"\1 \2", t)
    # ③ ] 바로 뒤에 문자가 붙으면 공백 (구두점 제외)
    t = re.sub(r"(\[[a-z/ -]+\])(?=[^\s.,!?)\]、。（）])", r"\1 ", t)
    if t == orig:
        print(f"  {os.path.basename(path)}: 변경 없음")
        return 0
    shutil.copy(path, path + ".bak")
    open(path, "w", encoding="utf-8").write(t)
    n_kt = len(re.findall(r"「", orig)) - len(re.findall(r"「", t))
    print(f"  {os.path.basename(path)}: 낫표→작은따옴표 {n_kt}곳 (백업 .bak)")
    return n_kt


if __name__ == "__main__":
    for p in sys.argv[1:]:
        fix(p)
