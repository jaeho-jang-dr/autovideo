# -*- coding: utf-8 -*-
"""★한글 자막의 '발음 예문'에도 로마자를 붙인다 (사장님 지시 2026-07-28).

`add_pron_to_srt.py` 는 **따옴표 안의 단어·짧은 표현**만 처리하고 4어절 이상 문장은
가독성 때문에 건너뛴다. 그런데 한글판 자막은 학습용이라 **따라 하는 예문에도**
발음기호가 있어야 한다("한글 단어와 짧은 문장에는 로마자 발음기호를 넣어 공부하게 한다").

대상 = DB 발음 클립으로 만든 예문(= 학습자가 실제로 따라 하는 문장)만. 나레이션 설명 문장은
건드리지 않는다(자막이 지저분해진다).

사용: python add_pron_sentences.py <입력.srt> <출력.srt>
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from add_pron_to_srt import romanize          # noqa: E402  실제발음 규칙 그대로 재사용
from gen_w23_db_voice import SENTENCES        # noqa: E402  DB 발음 클립 예문 = 학습 대상

ROM_TAIL = re.compile(r"\[[a-z][a-z\- ]*\]")


def main():
    src, dst = sys.argv[1], sys.argv[2]
    # 긴 문장부터 치환해야 짧은 문장이 먼저 먹고 들어가지 않는다
    targets = sorted(set(SENTENCES), key=len, reverse=True)
    hit = 0
    out = []
    for line in open(src, encoding="utf-8"):
        s = line.rstrip("\n")
        if re.match(r"^\d+$", s) or " --> " in s or not s.strip():
            out.append(s); continue
        for sent in targets:
            if sent not in s:
                continue
            i = s.find(sent) + len(sent)
            if ROM_TAIL.match(s[i:].lstrip()[:40] or ""):     # 이미 붙어 있으면 건너뜀
                continue
            rom = romanize(sent.rstrip("?!."))
            if not rom:
                continue
            s = s[:i] + f" [{rom}]" + s[i:]
            hit += 1
            break                                              # 한 줄에 하나만
        out.append(s)
    open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print(f"발음 예문 로마자 추가: {hit}곳 → {dst}")


if __name__ == "__main__":
    main()
