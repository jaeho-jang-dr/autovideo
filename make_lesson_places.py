#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_lesson_places.py — 168경을 168강의(24주×7일)에 사전 배정 → web/src/data/korea_lesson_places.json.

규칙: 월요일(day1) = 인기 상위 24경(주차 순). 화~일(day2~7) = 나머지 25~168경을 순서대로.
오더(영상 생성) 시 그 강의의 배정 장소 motif를 배경 프롬프트에 자동 사용(place_bg).
재실행: python make_lesson_places.py
"""
import os
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
PLACES = json.load(open(os.path.join(ROOT, "web", "src", "data", "korea_places.json"), encoding="utf-8"))
OUT = os.path.join(ROOT, "web", "src", "data", "korea_lesson_places.json")
BY_NO = {p["no"]: p for p in PLACES}


def place_rank_for(week, day):
    if day == 1:
        return week                                   # 월 = 상위 24경(주차순)
    return 24 + (week - 1) * 6 + (day - 1)             # 화~일 = 25~168 순서대로


def main():
    rows = []
    for wk in range(1, 25):
        for d in range(1, 8):
            rank = place_rank_for(wk, d)
            p = BY_NO.get(rank, {})
            rows.append({
                "week": wk, "day": d, "place_no": rank,
                "name_ko": p.get("name_ko", ""), "name_en": p.get("name_en", ""),
                "region_ko": p.get("region_ko", ""), "motif": p.get("motif", ""),
            })
    json.dump(rows, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # 역매핑: 각 명소(korea_places.json)에 배정된 강의(주차-강 번호) 주석 추가 → 명소 페이지 표시용
    place_lesson = {r["place_no"]: (r["week"], r["day"]) for r in rows}
    pp = os.path.join(ROOT, "web", "src", "data", "korea_places.json")
    places = json.load(open(pp, encoding="utf-8"))
    for p in places:
        wd = place_lesson.get(p["no"])
        if wd:
            p["lesson_week"], p["lesson_day"] = wd[0], wd[1]
            p["lesson_label"] = f"{wd[0]}-{wd[1]}"     # 요일 개념 대신 강의번호
        else:
            p["lesson_week"] = p["lesson_day"] = None
            p["lesson_label"] = ""
    json.dump(places, open(pp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(rows)} lesson-background assignments -> {os.path.relpath(OUT, ROOT)}; annotated korea_places.json")
    dn = ["", "월", "화", "수", "목", "금", "토", "일"]
    print("week 1:", [f"{dn[r['day']]}={r['place_no']}.{r['name_ko']}" for r in rows if r["week"] == 1])


if __name__ == "__main__":
    main()
