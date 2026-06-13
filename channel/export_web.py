#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
content.db -> web/src/data/content.json 익스포터.

Astro 사이트가 빌드 시점에 읽는 단일 데이터 파일을 생성한다.
content.db(단일 원천)를 수정한 뒤 이 스크립트를 다시 돌리면 사이트가 갱신된다.

사용법:
    python channel/export_web.py
"""
import json
import os
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "content.db")
OUT_PATH = os.path.join(HERE, "..", "web", "src", "data", "content.json")


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    channel = {r["key"]: r["value"]
               for r in cur.execute("SELECT key, value FROM channel_meta")}

    categories = []
    for r in cur.execute(
            "SELECT c.code, c.name_kr, c.name_en, c.medical_lens, c.priority, "
            "(SELECT COUNT(*) FROM episodes e WHERE e.category=c.code) AS count "
            "FROM categories c ORDER BY c.priority, c.code"):
        categories.append(dict(r))

    # 씬(세부 대본)을 에피소드별로 미리 묶어 둔다.
    # 각 에피소드 아래에 seq 순서대로 중첩되며, 한/영 대조 학습 뷰어가 이 데이터를 읽는다.
    scenes_by_episode = {}
    for r in cur.execute(
            "SELECT episode, seq, script_kr, script_en, duration_sec "
            "FROM scenes ORDER BY episode, seq"):
        scenes_by_episode.setdefault(r["episode"], []).append({
            "seq": r["seq"],
            "script_kr": r["script_kr"],
            "script_en": r["script_en"],
            "duration_sec": r["duration_sec"],
        })

    episodes = []
    for r in cur.execute(
            "SELECT code, category, title_kr, title_en, hook_kr, logline_kr, "
            "status, priority, runtime_sec, youtube_kr, youtube_en, publish_date, "
            "reverse_spec, style_profile "
            "FROM episodes ORDER BY priority, code"):
        ep = dict(r)
        ep["scenes"] = scenes_by_episode.get(ep["code"], [])
        episodes.append(ep)

    conn.close()

    total_scenes = sum(len(e["scenes"]) for e in episodes)

    data = {
        "channel": channel,
        "categories": categories,
        "episodes": episodes,
        "counts": {
            "episodes": len(episodes),
            "published": sum(1 for e in episodes if e["status"] == "published"),
            "categories": len(categories),
        },
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(episodes)} episodes, {len(categories)} categories "
          f"-> {os.path.relpath(OUT_PATH, os.path.join(HERE, '..'))}")


if __name__ == "__main__":
    main()
