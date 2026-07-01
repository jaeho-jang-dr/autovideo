#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
register_poses.py — stickman_factory 가 생성한 포즈 라이브러리를 content.db 에 등록.

assets/graphics/poses/_manifest.json 을 읽어 `assets` 테이블에 upsert 한다.
 - type='character', file_path='assets/graphics/poses/stickman_<name>.png'
 - 멱등: 기존 stickman 포즈 행(file_path LIKE '%/poses/stickman_%')을 먼저 삭제 후 재삽입.
포즈를 다시 뽑은 뒤 `python register_poses.py` 만 재실행하면 DB가 동기화된다.
"""
import os
import sys
import json
import sqlite3

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ROOT, "channel", "content.db")
MAN = os.path.join(ROOT, "assets", "graphics", "poses", "_manifest.json")
METHOD = "stickman_factory.py (parametric 12-joint, hand-drawn ink, cream-bg line art)"


def main():
    manifest = json.load(open(MAN, encoding="utf-8"))
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cols = {r[1] for r in cur.execute("pragma table_info(assets)")}
    has_created = "created_at" in cols

    cur.execute("DELETE FROM assets WHERE file_path LIKE 'assets/graphics/poses/stickman_%'")
    removed = cur.rowcount

    n = 0
    for e in manifest:
        name_en = f"stickman_{e['name']}"
        name_kr = e["ko"]
        flow = f"{METHOD} | expr={e['expr']} facing={e['facing']} | {e['en']}"
        if has_created:
            cur.execute(
                "INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt, created_at) "
                "VALUES (?,?,?,?,?, datetime('now'))",
                (name_kr, name_en, "character", e["file"], flow),
            )
        else:
            cur.execute(
                "INSERT INTO assets (name_kr, name_en, type, file_path, flow_prompt) VALUES (?,?,?,?,?)",
                (name_kr, name_en, "character", e["file"], flow),
            )
        n += 1

    con.commit()
    print(f"removed {removed} old stickman rows, inserted {n} poses")
    # verify
    rows = cur.execute(
        "SELECT name_en, name_kr, file_path FROM assets "
        "WHERE file_path LIKE 'assets/graphics/poses/stickman_%' ORDER BY name_en"
    ).fetchall()
    miss = [fp for _, _, fp in rows if not os.path.exists(os.path.join(ROOT, fp))]
    print(f"registered {len(rows)} rows; missing files: {len(miss)}")
    for fp in miss:
        print("  MISSING:", fp)
    con.close()


if __name__ == "__main__":
    main()
