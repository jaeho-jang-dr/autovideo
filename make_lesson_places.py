#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""make_lesson_places.py — 168경을 168강의(24주×7일)에 사전 배정 → web/src/data/korea_lesson_places.json.

규칙: 월요일(day1) = 인기 상위 24경(주차 순). 화~일(day2~7) = 나머지 25~168경을 순서대로.
오더(영상 생성) 시 그 강의의 배정 장소 motif를 배경 프롬프트에 자동 사용(place_bg).
재실행: python make_lesson_places.py
"""
import os
import json
import sqlite3

ROOT = os.path.dirname(os.path.abspath(__file__))
PLACES = json.load(open(os.path.join(ROOT, "web", "src", "data", "korea_places.json"), encoding="utf-8"))
OUT = os.path.join(ROOT, "web", "src", "data", "korea_lesson_places.json")
DB = os.path.join(ROOT, "channel", "content.db")
BY_NO = {p["no"]: p for p in PLACES}


def place_rank_for(week, day):
    if day == 1:
        return week                                   # 월 = 상위 24경(주차순)
    return 24 + (week - 1) * 6 + (day - 1)             # 화~일 = 25~168 순서대로


def lesson_code(week, day):
    # scenes.episode 네이밍과 일치: day1=KO-W01, day2+=KO-W01D2
    return f"KO-W{week:02d}" if day == 1 else f"KO-W{week:02d}D{day}"


def bg_prefix(week, day):
    # 배경 파일 접두: day1=bg_w9, day2+=bg_w1d2 (assets/graphics/bg/<prefix>_sNN.png)
    return f"bg_w{week}" if day == 1 else f"bg_w{week}d{day}"


def write_db(rows, places):
    """168 장소 카탈로그 + 강의-장소 매핑을 content.db에 저장(멱등: 재생성)."""
    con = sqlite3.connect(DB)
    cur = con.cursor()
    # 1) 168경 카탈로그
    cols = ["no", "name_ko", "name_en", "region_ko", "region_en", "category",
            "leisure_ko", "why_ko", "why_en", "motif", "week", "description_en",
            "description_ko", "directions_en", "directions_ko", "map_link",
            "official_link", "image_url", "lesson_week", "lesson_day", "lesson_label"]
    cur.execute("DROP TABLE IF EXISTS korea_places")
    cur.execute("CREATE TABLE korea_places (no INTEGER PRIMARY KEY, "
                + ", ".join(f"{c} TEXT" for c in cols if c != "no") + ")")
    cur.executemany(
        f"INSERT INTO korea_places ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
        [[p.get(c) for c in cols] for p in places])
    # 2) 강의(24주×7일=168) → 장소 배정 매핑
    cur.execute("DROP TABLE IF EXISTS lesson_places")
    cur.execute("""CREATE TABLE lesson_places (
        lesson_code TEXT PRIMARY KEY, week INTEGER, day INTEGER, place_no INTEGER,
        name_ko TEXT, name_en TEXT, region_ko TEXT, motif TEXT, bg_prefix TEXT,
        FOREIGN KEY(place_no) REFERENCES korea_places(no))""")
    cur.executemany(
        """INSERT INTO lesson_places
        (lesson_code, week, day, place_no, name_ko, name_en, region_ko, motif, bg_prefix)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        [(lesson_code(r["week"], r["day"]), r["week"], r["day"], r["place_no"],
          r["name_ko"], r["name_en"], r["region_ko"], r["motif"],
          bg_prefix(r["week"], r["day"])) for r in rows])
    con.commit()
    con.close()


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
    # DB 저장 (korea_places 카탈로그 + lesson_places 매핑)
    write_db(rows, places)
    print(f"{len(rows)} lesson-background assignments -> {os.path.relpath(OUT, ROOT)}; annotated korea_places.json; DB={os.path.relpath(DB, ROOT)}")
    dn = ["", "월", "화", "수", "목", "금", "토", "일"]
    print("week 1:", [f"{dn[r['day']]}={r['place_no']}.{r['name_ko']}" for r in rows if r["week"] == 1])


if __name__ == "__main__":
    main()
