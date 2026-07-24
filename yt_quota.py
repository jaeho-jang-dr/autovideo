# -*- coding: utf-8 -*-
"""★YouTube API 쿼터 추적·조회 (사장님 지시 2026-07-15, content.db에 기록).
   일 10,000유닛 / 리셋 = 한국시간 매일 오후 4시(태평양 자정).

사용:
  python yt_quota.py                      # 오늘(오후4시 리셋 기준) 사용량·잔량 즉답
  python yt_quota.py log <op> <video_id>  # 호출 1건 기록 (자동 비용)
  python yt_quota.py cost                  # 비용표

호출 기록 함수(다른 스크립트에서):
  import yt_quota; yt_quota.log("videos.insert", vid)   # 업로드/자막/썸네일 등 실행 직후 호출
"""
import sqlite3, sys, os
from datetime import datetime, timedelta, timezone

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "channel", "content.db")
KST = timezone(timedelta(hours=9))
DAILY = 10000
COST = {  # 유닛
    "videos.insert": 1600, "captions.insert": 400, "captions.delete": 50,
    "captions.update": 450, "videos.update": 50, "thumbnails.set": 50,
    "playlistItems.insert": 50, "commentThreads.insert": 50,
    "videos.list": 1, "captions.list": 50, "playlists.list": 1, "search.list": 100,
}


def _now():
    # Date.now 계열이 막힌 환경 대비: 시스템 시각을 subprocess로.
    import subprocess
    s = subprocess.run(["python", "-c",
        "import datetime,sys; sys.stdout.write(datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat())"],
        capture_output=True, text=True).stdout.strip()
    return datetime.fromisoformat(s)


def _reset_window(now):
    """오늘 리셋(오후4시 KST) 시각. 지금이 16시 전이면 어제 16시."""
    today16 = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return today16 if now >= today16 else today16 - timedelta(days=1)


def log(operation, video_id=None, note=None, cost=None):
    c = cost if cost is not None else COST.get(operation, 0)
    now = _now()
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO youtube_quota_log (ts, operation, cost, video_id, note) VALUES (?,?,?,?,?)",
                (now.isoformat(), operation, c, video_id, note))
    con.commit(); con.close()
    return c


def status():
    now = _now()
    since = _reset_window(now)
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT operation, cost, ts FROM youtube_quota_log WHERE ts >= ?",
                       (since.isoformat(),)).fetchall()
    con.close()
    used = sum(r[1] for r in rows)
    remain = DAILY - used
    next_reset = since + timedelta(days=1)
    from collections import Counter
    bre = Counter()
    for op, c, ts in rows:
        bre[op] += c
    return dict(now=now, since=since, used=used, remain=remain,
                next_reset=next_reset, calls=len(rows), breakdown=dict(bre))


def _fmt(s):
    print(f"=== YouTube API 쿼터 (한국시간 기준) ===")
    print(f"  현재       : {s['now'].strftime('%m-%d %H:%M')}")
    print(f"  집계 구간  : {s['since'].strftime('%m-%d %H:%M')} ~ 지금 (오후4시 리셋)")
    print(f"  ─────────────────────────────")
    print(f"  사용       : {s['used']:>6} / {DAILY} 유닛  ({s['calls']}회 호출)")
    print(f"  ★남음      : {s['remain']:>6} 유닛")
    print(f"  다음 리셋  : {s['next_reset'].strftime('%m-%d %H:%M')} (한국시간 오후4시)")
    # 남은 걸로 뭘 할 수 있나
    r = s['remain']
    print(f"  ─────────────────────────────")
    print(f"  남은 걸로: 영상업로드 {r//1600}편 / 자막 {r//400}개 / 썸네일·수정 {r//50}회")
    if s['breakdown']:
        print(f"  내역: " + ", ".join(f"{k} {v}" for k, v in sorted(s['breakdown'].items(), key=lambda x:-x[1])))


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "log":
        op = sys.argv[2]; vid = sys.argv[3] if len(sys.argv) > 3 else None
        c = log(op, vid)
        print(f"기록: {op} {c}유닛 (video={vid})")
        _fmt(status())
    elif len(sys.argv) >= 2 and sys.argv[1] == "cost":
        for k, v in sorted(COST.items(), key=lambda x: -x[1]):
            print(f"  {k:<26} {v:>5}")
    else:
        _fmt(status())
