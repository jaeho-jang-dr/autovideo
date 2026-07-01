#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""place_bg.py — 한국 명소(140곳)를 파스텔 배경 Flow 프롬프트로 변환.

방법(사용자 지정):
  장소명 입력 → (140 리스트의 motif 사용 / 없으면 웹에서 아이코닉·레저 사진 참고)
  → 누가 봐도 그 장소인 + 즐거운 레저/모임 모티프 → 파스텔 storybook 렌더 + 스크립트 사물.

사용:
  from place_bg import place_prompt
  place_prompt("한강", ["picnic mat", "ramen cup"])
  python place_bg.py 한강 "오리,우유"            # CLI 테스트
"""
import os
import sys
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
PLACES = json.load(open(os.path.join(ROOT, "web", "src", "data", "korea_places.json"), encoding="utf-8"))

PASTEL = ("soft pastel storybook illustration, thick friendly outlines, flat colors, "
          "gentle warm pastel palette, no text, no people, "
          "leave the left third and lower area open for a character, 16:9")


def find_place(name):
    n = (name or "").strip()
    nl = n.lower()
    for p in PLACES:
        if n and (n in p["name_ko"] or p["name_ko"] in n or nl in p["name_en"].lower()):
            return p
    return None


def place_prompt(name, objects=None):
    """장소명(+스크립트 사물) → Flow 파스텔 배경 프롬프트.
    objects: 그 씬에 등장할 사물(영문 권장) 리스트 — '내용에 나오는 사물 등장' 요구 반영."""
    p = find_place(name)
    motif = p["motif"] if p else name
    leisure = f", lively but cozy leisure scene ({p['leisure_ko']})" if p else ""
    obj = (", with " + ", ".join(objects)) if objects else ""
    return f"{motif}{leisure}{obj}, {PASTEL}"


def main():
    if len(sys.argv) < 2:
        print("usage: python place_bg.py <place> [obj1,obj2]")
        return
    name = sys.argv[1]
    objs = [o.strip() for o in sys.argv[2].split(",")] if len(sys.argv) > 2 else None
    p = find_place(name)
    print("matched:", (p["name_ko"] + " / " + p["name_en"]) if p else "(not in 140 — use web reference)")
    print("prompt:", place_prompt(name, objs))


if __name__ == "__main__":
    main()
