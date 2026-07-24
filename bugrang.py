# -*- coding: utf-8 -*-
"""버그랑(BugRang) — 감독(Claude)의 실수·버그를 날짜·시각과 함께 DB에 기록하고,
하루 1회 미리포트분을 모아 Anthropic /bug 제출용 리포트로 뽑는다.

사용:
  python bugrang.py add --title "..." --what "..." [--category ...] [--impact ...] [--cause ...] [--prevent ...] [--severity high]
  python bugrang.py list [--all]          # 미리포트(기본) 또는 전체
  python bugrang.py report [--mark]       # 미리포트분을 /bug용 마크다운으로 출력, --mark면 reported 처리
  python bugrang.py stats
DB: bugrang.db (프로젝트 루트). 시각은 KST(Asia/Seoul) 기준 ISO 문자열.
"""
import sqlite3, os, sys, argparse
from datetime import datetime, timezone, timedelta

os.chdir(os.path.dirname(os.path.abspath(__file__)))
DB = "bugrang.db"
KST = timezone(timedelta(hours=9))

def conn():
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS bug_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts_kst TEXT NOT NULL,
        date_kst TEXT NOT NULL,
        severity TEXT DEFAULT 'medium',
        category TEXT DEFAULT '',
        title TEXT NOT NULL,
        what_happened TEXT NOT NULL,
        impact TEXT DEFAULT '',
        root_cause TEXT DEFAULT '',
        prevention TEXT DEFAULT '',
        reported INTEGER DEFAULT 0,
        reported_at TEXT
    )""")
    # 날짜시간 + 내용만 담는 단순 시간순 로그(사장님 요청)
    c.execute("""CREATE TABLE IF NOT EXISTS event_log(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts_kst TEXT NOT NULL,
        date_kst TEXT NOT NULL,
        content TEXT NOT NULL
    )""")
    c.commit()
    return c

def add_event(c, content):
    t = now_kst()
    c.execute("INSERT INTO event_log(ts_kst,date_kst,content) VALUES(?,?,?)",
              (t.isoformat(timespec="seconds"), t.strftime("%Y-%m-%d"), content))
    c.commit()
    return t

def now_kst():
    return datetime.now(KST)

def cmd_add(a):
    c = conn(); t = now_kst()
    c.execute("""INSERT INTO bug_log(ts_kst,date_kst,severity,category,title,what_happened,impact,root_cause,prevention)
                 VALUES(?,?,?,?,?,?,?,?,?)""",
              (t.isoformat(timespec="seconds"), t.strftime("%Y-%m-%d"),
               a.severity, a.category, a.title, a.what, a.impact, a.cause, a.prevent))
    c.commit()
    bid = c.execute('SELECT last_insert_rowid()').fetchone()[0]
    add_event(c, f"[버그#{bid}/{a.severity}] {a.title} — {a.what}")  # 시간순 로그에도 남김
    print(f"[버그랑] 기록됨 #{bid}  ({t.strftime('%Y-%m-%d %H:%M:%S KST')})  {a.title}")

def cmd_log(a):
    c = conn(); t = add_event(c, a.content)
    print(f"[버그랑] 이벤트 기록 ({t.strftime('%Y-%m-%d %H:%M:%S KST')}): {a.content}")

def cmd_journal(a):
    c = conn()
    rows = c.execute("SELECT id,ts_kst,content FROM event_log ORDER BY id").fetchall()
    if not rows:
        print("(이벤트 없음)"); return
    for r in rows:
        print(f"#{r[0]:>3} [{r[1]}] {r[2]}")
    print(f"\n총 {len(rows)}건")

def cmd_list(a):
    c = conn()
    q = "SELECT id,ts_kst,severity,category,title,reported FROM bug_log"
    if not a.all: q += " WHERE reported=0"
    q += " ORDER BY id"
    rows = c.execute(q).fetchall()
    if not rows:
        print("(기록 없음)"); return
    for r in rows:
        mark = "✅보고됨" if r[5] else "🕒대기"
        print(f"#{r[0]:>3} [{r[1]}] {mark} <{r[2]}/{r[3]}> {r[4]}")
    print(f"\n총 {len(rows)}건")

def cmd_report(a):
    c = conn()
    rows = c.execute("""SELECT id,ts_kst,severity,category,title,what_happened,impact,root_cause,prevention
                        FROM bug_log WHERE reported=0 ORDER BY id""").fetchall()
    if not rows:
        print("# 버그랑 일일 리포트\n\n오늘 새로 보고할 실수 없음. 👍"); return
    d = now_kst().strftime("%Y-%m-%d")
    out = [f"# 버그랑(BugRang) 일일 리포트 — {d} KST",
           f"# autovideo 프로젝트 · Claude Code(감독) 자기보고 · {len(rows)}건\n"]
    for i,r in enumerate(rows,1):
        out += [f"## {i}. [{r[2].upper()}] {r[4]}",
                f"- **일시**: {r[1]}",
                f"- **분류**: {r[3]}",
                f"- **무슨 일**: {r[5]}",
                f"- **영향**: {r[6]}",
                f"- **원인**: {r[7]}",
                f"- **재발방지**: {r[8]}\n"]
    print("\n".join(out))
    if a.mark:
        ts = now_kst().isoformat(timespec="seconds")
        c.execute("UPDATE bug_log SET reported=1, reported_at=? WHERE reported=0", (ts,))
        c.commit()
        sys.stderr.write(f"\n[버그랑] {len(rows)}건 reported 처리 ({ts})\n")

def cmd_stats(a):
    c = conn()
    tot = c.execute("SELECT COUNT(*) FROM bug_log").fetchone()[0]
    pend = c.execute("SELECT COUNT(*) FROM bug_log WHERE reported=0").fetchone()[0]
    print(f"버그랑 통계: 총 {tot}건 · 미보고 {pend}건")
    for sev,n in c.execute("SELECT severity,COUNT(*) FROM bug_log GROUP BY severity"):
        print(f"  {sev}: {n}")

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    ad = sub.add_parser("add")
    ad.add_argument("--title", required=True); ad.add_argument("--what", required=True)
    ad.add_argument("--category", default=""); ad.add_argument("--impact", default="")
    ad.add_argument("--cause", default=""); ad.add_argument("--prevent", default="")
    ad.add_argument("--severity", default="medium")
    ad.set_defaults(func=cmd_add)
    ls = sub.add_parser("list"); ls.add_argument("--all", action="store_true"); ls.set_defaults(func=cmd_list)
    rp = sub.add_parser("report"); rp.add_argument("--mark", action="store_true"); rp.set_defaults(func=cmd_report)
    st = sub.add_parser("stats"); st.set_defaults(func=cmd_stats)
    lg = sub.add_parser("log"); lg.add_argument("--content", required=True); lg.set_defaults(func=cmd_log)
    jn = sub.add_parser("journal"); jn.set_defaults(func=cmd_journal)
    a = p.parse_args(); a.func(a)

if __name__ == "__main__":
    main()
