#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
지은·인준 캐릭터 베이스/포즈 레퍼런스 9장을 로컬 SQLite(content.db) assets 테이블에 미러링.

Supabase(supabase/save_characters.py)에 저장한 것과 동일한 레퍼런스를 로컬 카탈로그에도
보관한다. flow_prompt 는 home_vocab 의 프롬프트 파일에서 직접 읽어 원문 그대로 저장한다.

- file_path: 기존 행과 동일하게 home_vocab 기준 bare 파일명
- 멱등: 같은 name_en 행을 지우고 다시 넣는다 (재실행 안전)

사용법:
    python channel/seed_character_assets.py
"""
import os
import sqlite3
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "channel", "content.db")
HV = os.path.join(ROOT, "home_vocab")

# name_en, name_kr, key(=프롬프트 키), file_basename
ASSETS = [
    ("Jieun_Base_Front", "지은_베이스_정면", "jieun_base_front",    "jieun_base_front.png"),
    ("Jieun_Base_Side",  "지은_베이스_측면", "jieun_base_side",     "jieun_base_side.png"),
    ("Jieun_Base_Back",  "지은_베이스_뒷면", "jieun_base_back",     "jieun_base_back.png"),
    ("Jieun_Sit_Front",  "지은_앉음_정면",   "jieun_sitting_front", "jieun_sitting_front.png"),
    ("Jieun_Sit_Side",   "지은_앉음_측면",   "jieun_sitting_side",  "jieun_sitting_side.png"),
    ("Jieun_Sit_Back",   "지은_앉음_뒷면",   "jieun_sitting_back",  "jieun_sitting_back.png"),
    ("Injun_Base_Front", "인준_베이스_정면", "injun_base_front",    "injun_base_front.png"),
    ("Injun_Base_Side",  "인준_베이스_측면", "injun_base_side",     "injun_base_side.png"),
    ("Injun_Base_Back",  "인준_베이스_뒷면", "injun_base_back",     "injun_base_back.png"),
]


def load_prompts():
    """home_vocab 프롬프트 파일에서 key -> flow_prompt 매핑을 만든다."""
    prompts = {}
    # text2img: 'key: prompt'
    for fn in ("jieun_base_prompts.txt", "injun_base_prompts.txt"):
        path = os.path.join(HV, fn)
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            k, v = line.split(":", 1)
            prompts[k.strip()] = v.strip()
    # reference2img jobs: 'outkey | refpath | prompt'
    jobs = os.path.join(HV, "jieun_sitting_jobs.txt")
    if os.path.exists(jobs):
        for line in open(jobs, encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#") or "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                prompts[parts[0]] = parts[2]
    return prompts


def main():
    prompts = load_prompts()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    names = [a[0] for a in ASSETS]
    cur.execute(
        f"DELETE FROM assets WHERE name_en IN ({','.join('?' * len(names))})",
        names,
    )
    removed = cur.rowcount
    rows = []
    for name_en, name_kr, key, base in ASSETS:
        if not os.path.exists(os.path.join(HV, base)):
            print(f"  [WARN] missing file, still registering: {base}")
        rows.append((name_kr, name_en, "character", base, prompts.get(key)))
    cur.executemany(
        "INSERT INTO assets(name_kr,name_en,type,file_path,flow_prompt) "
        "VALUES (?,?,?,?,?)",
        rows,
    )
    conn.commit()
    total = cur.execute("SELECT COUNT(*) FROM assets").fetchone()[0]
    print(f"[OK] removed {removed} stale, inserted {len(rows)} character refs")
    print(f"[OK] assets total -> {total}")
    print("\n등록 내역:")
    for r in cur.execute(
        "SELECT name_kr,name_en,file_path,(flow_prompt IS NOT NULL) "
        "FROM assets WHERE name_en IN (%s) ORDER BY name_en"
        % ",".join("?" * len(names)),
        names,
    ):
        print(f"  {r[0]:14s} {r[1]:18s} {r[2]:24s} prompt={'Y' if r[3] else 'N'}")
    conn.close()


if __name__ == "__main__":
    main()
