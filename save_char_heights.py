# -*- coding: utf-8 -*-
"""캐릭터 **기본 키**를 DB에 박는다 — `char_heights`.

★사장님 지시(2026-08-12): "스틱맨이 700 으로 정했을 때 비율로 졸라맨·졸라걸의 키를
  정해서 캐릭터의 기본 키로 만들고, 그 키대로 데이터베이스에 저장하라."

## 근거
키 비율은 사장님이 **이미 정해 두신 값**이다 — `W24/W24_concept.md` §2
"★이 표가 W24의 **절대 기준**이다. 한 화면에 일곱이 같이 나오므로 키가 어긋나면
 바로 티가 난다." (기준: 인준 180cm = 770px, 나머지는 실제 신장 비율로 환산)
코드에는 `build_w24.py` `SPEC` · `cut_w24_group.py` 에 같은 값이 들어 있다.

## 이번에 바뀌는 것
**스틱맨을 700px 로 내린다.** 스틱맨 규격이 749 이므로 배율은 700/749 = 0.93458.
**전원에 같은 배율**을 먹여 상대 비율을 그대로 유지한다.

    python save_char_heights.py          # 저장
    python save_char_heights.py --show   # 확인만
"""
import argparse
import os
import sqlite3

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

DB = "channel/content.db"

# W24_concept.md §2 — 사장님이 정하신 절대 기준 (키cm, 규격px)
SPEC = [
    ("injun",       "인준",     180, 770),
    ("zolla_man",   "졸라맨",   178, 761),
    ("teacher_jay", "티쳐제이", 175, 749),
    ("stickman",    "스틱맨",   175, 749),
    ("jieun",       "지은",     165, 706),
    ("zolla_girl",  "졸라걸",   163, 697),
    ("madam_jay",   "마담제이", 162, 693),
]

ANCHOR_KEY = "stickman"          # ★스틱맨을
ANCHOR_H = 700                   #   700px 로 잡는다 (사장님 지시 2026-08-12)

DDL = """
CREATE TABLE IF NOT EXISTS char_heights (
    char_key    TEXT PRIMARY KEY,
    korean_name TEXT NOT NULL,
    height_cm   INTEGER,
    spec_px     INTEGER,          -- W24 규격 (인준 770 기준)
    base_h      INTEGER NOT NULL, -- ★기본 키 (스틱맨 700 기준) — 이걸 쓴다
    ratio       REAL,             -- 스틱맨 대비
    source      TEXT,
    updated_at  TEXT DEFAULT (datetime('now','localtime'))
)
"""


def rows():
    anchor_spec = dict((k, s) for k, _, _, s in SPEC)[ANCHOR_KEY]
    scale = ANCHOR_H / float(anchor_spec)
    out = []
    for key, ko, cm, spec in SPEC:
        base = int(round(spec * scale))
        out.append((key, ko, cm, spec, base, round(spec / float(anchor_spec), 4),
                    "W24_concept.md §2 절대기준 × (%d/%d)" % (ANCHOR_H, anchor_spec)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true")
    a = ap.parse_args()

    c = sqlite3.connect(DB)
    c.execute(DDL)
    data = rows()

    if not a.show:
        c.executemany(
            "INSERT INTO char_heights"
            " (char_key,korean_name,height_cm,spec_px,base_h,ratio,source,updated_at)"
            " VALUES (?,?,?,?,?,?,?,datetime('now','localtime'))"
            " ON CONFLICT(char_key) DO UPDATE SET"
            "  korean_name=excluded.korean_name, height_cm=excluded.height_cm,"
            "  spec_px=excluded.spec_px, base_h=excluded.base_h, ratio=excluded.ratio,"
            "  source=excluded.source, updated_at=datetime('now','localtime')", data)
        c.commit()

    print("기준: %s = %dpx  (규격 %d → 배율 %.5f)"
          % (ANCHOR_KEY, ANCHOR_H, dict((k, s) for k, _, _, s in SPEC)[ANCHOR_KEY],
             ANCHOR_H / float(dict((k, s) for k, _, _, s in SPEC)[ANCHOR_KEY])))
    print("%-13s %-9s %4s %7s %8s %8s" % ("char_key", "이름", "cm", "규격px", "기본키px", "스틱맨비"))
    for r in c.execute("select char_key,korean_name,height_cm,spec_px,base_h,ratio"
                       " from char_heights order by base_h desc"):
        print("%-13s %-9s %4s %7s %8s %8.3f" % r)
    print("\n%d행 → %s.char_heights" % (len(data), DB))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
