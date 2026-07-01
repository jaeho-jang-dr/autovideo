#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
correct_w3_narration.py — W3 나레이션 교정(사용자 피드백):
 1) 자기소개: "한글 선생님 Dr. Jay" → "Jay" (KO/EN)
 2) 조사 받침 규칙: 따옴표 친 낱자는 '소리'(그/크/끄… ㅡ로 끝남=받침 없음)로 들리므로
    그 뒤 조사는 가/는/로 를 쓴다. 'X'이→'X'가, 'X'은→'X'는, 'X'으로→'X'로.
입력: scratch/w3_scenario_v2.json → 출력: scratch/w3_scenario_v3.json
"""
import os
import sys
import json
import re

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "scratch", "w3_scenario_v2.json")
OUT = os.path.join(ROOT, "scratch", "w3_scenario_v3.json")
JAMO = "ㄱㄷㅂㅈㅅㅋㅌㅍㅊㄲㄸㅃㅆㅉ"


def fix_jay_ko(s):
    s = s.replace("우리 모두의 한글 선생님 Dr. Jay", "Jay")
    s = s.replace("한글 선생님 Dr. Jay", "Jay")
    s = s.replace("Dr. Jay", "Jay")
    return s


def fix_jay_en(s):
    s = s.replace("Dr. Jay, your Korean language teacher", "Jay")
    s = s.replace("your Korean language teacher, Dr. Jay", "Jay")
    s = s.replace("Dr. Jay", "Jay")
    return s


def fix_particles(s):
    """따옴표 낱자 뒤 조사: 'X'이 →'X'가, 'X'은 →'X'는, 'X'으로→'X'로 (소리는 받침 없음)."""
    for j in JAMO:
        # 'X'으로 (가장 김 먼저)
        s = s.replace(f"'{j}'으로", f"'{j}'로")
        # 'X'이 + (공백/문장부호) → 'X'가  (복사 '이에요/이야/이고' 같은 copula 오치환 방지: 뒤에 공백/구두점만)
        s = re.sub(rf"'{j}'이(?=[\s,.!?])", f"'{j}'가", s)
        # 'X'은 + (공백/문장부호) → 'X'는
        s = re.sub(rf"'{j}'은(?=[\s,.!?])", f"'{j}'는", s)
    return s


def main():
    data = json.load(open(SRC, encoding="utf-8"))
    n_jay, n_part = 0, 0
    for sc in data["scenes"]:
        ko0 = sc["script_kr"]
        ko = fix_jay_ko(ko0)
        ko = fix_particles(ko)
        if ko != ko0:
            if ("Dr. Jay" in ko0 or "한글 선생님" in ko0):
                n_jay += 1
        # 조사 변경 개수 카운트(대략)
        n_part += sum(1 for j in JAMO for _ in re.finditer(rf"'{j}'(가|는|로)(?=[\s,.!?])", ko)) \
            - sum(1 for j in JAMO for _ in re.finditer(rf"'{j}'(가|는|로)(?=[\s,.!?])", fix_jay_ko(ko0)))
        sc["script_kr"] = ko
        sc["script_en"] = fix_jay_en(sc["script_en"])
        sc["cap_ko"] = fix_jay_ko(sc["cap_ko"])
        sc["cap_en"] = fix_jay_en(sc["cap_en"])
    json.dump(data, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"saved {OUT}")
    print(f"Jay 수정 씬: {n_jay}, 조사 교정(누적 추정): {n_part}")
    # 검수용: 따옴표 낱자+조사 컨텍스트 출력
    print("\n--- 조사 교정 결과 확인 (낱자+조사) ---")
    for sc in data["scenes"]:
        for m in re.finditer(r"'[ㄱ-ㅎ]'[가는로이은]| Jay|Jay입니다", sc["script_kr"]):
            pass
        hits = re.findall(r"'[ㄱ-ㅎ]'[가는로]", sc["script_kr"])
        if hits:
            print(f"S{sc['seq']:>2}: {' '.join(hits)}")


if __name__ == "__main__":
    main()
