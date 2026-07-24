# -*- coding: utf-8 -*-
"""W12 공개 전환 — ★4K(2160p) 처리 완료를 확인한 뒤에만 public 으로 바꾼다.
사용: python publish_w12_after_4k.py          (즉시 1회 확인 → 되면 공개)
      python publish_w12_after_4k.py --wait   (4K 될 때까지 최대 3시간 폴링 후 공개)
"""
import sys, os, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_api import yt

KO = "pM7eN6Qt6s4"
EN = "VPgmXo5jXtY"
WAIT = "--wait" in sys.argv


def has_4k(vid):
    """유튜브가 4K(2160p) 트랜스코딩을 끝냈는지 — 공개 watch 페이지의 사용 가능 화질로 확인."""
    try:
        out = subprocess.run(
            ["yt-dlp", "-F", f"https://www.youtube.com/watch?v={vid}"],
            capture_output=True, text=True, timeout=90).stdout
        return ("2160" in out), out
    except Exception as e:
        return None, f"(yt-dlp 실패: {e})"


def log(m):
    print(m, flush=True)


def check_all():
    st = {}
    for name, vid in (("KO", KO), ("EN", EN)):
        ok, _ = has_4k(vid)
        st[name] = ok
        log(f"  {name} {vid}: 4K={'✅' if ok else ('❌ 아직' if ok is False else '❓확인불가')}")
    return st


log("=== W12 4K 처리 확인 ===")
st = check_all()

if WAIT:
    deadline = time.time() + 3 * 3600          # 최대 3시간
    while not (st.get("KO") and st.get("EN")) and time.time() < deadline:
        log("  … 10분 후 재확인")
        time.sleep(600)
        st = check_all()

if st.get("KO") and st.get("EN"):
    y = yt()
    log("\n=== 4K 확인됨 → 공개 전환 ===")
    for name, vid in (("KO", KO), ("EN", EN)):
        v = y.videos().list(part="status", id=vid).execute()["items"][0]
        s = v["status"]
        before = s.get("privacyStatus")
        s["privacyStatus"] = "public"
        y.videos().update(part="status", body={"id": vid, "status": s}).execute()
        log(f"  {name} {vid}: {before} → public ✅")
    # DB 갱신
    try:
        import sqlite3
        db = sqlite3.connect("channel/content.db")
        db.execute("UPDATE youtube_uploads SET visibility='public' WHERE video_id IN (?,?)", (KO, EN))
        db.commit(); db.close()
        log("  DB visibility=public 갱신")
    except Exception as e:
        log(f"  DB 갱신 실패(무시): {e}")
    log("\n=== ✅ W12 공개 완료 ===")
else:
    log("\n=== ⏳ 아직 4K 처리 중 — 공개 전환 보류 ===")
    log("    나중에 다시: python publish_w12_after_4k.py")
    raise SystemExit(1)
