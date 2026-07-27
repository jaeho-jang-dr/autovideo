# -*- coding: utf-8 -*-
"""1시간 대기(4K 처리) 후 W21 두 판을 공개 전환 + DB 갱신."""
import time, subprocess, sqlite3, sys
VIDS = ["yyeIBiEIp6E", "TKjiVsG8MuI"]
print("4K 처리 대기 시작 (60분)...", flush=True)
time.sleep(3600)
for vid in VIDS:
    r = subprocess.run([sys.executable, "yt_api.py", "public", vid], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    print(f"[public] {vid}:", (r.stdout or r.stderr).strip()[-200:], flush=True)
con = sqlite3.connect("channel/content.db")
for vid in VIDS:
    con.execute("UPDATE youtube_uploads SET visibility='public' WHERE video_id=?", (vid,))
con.commit(); con.close()
print("### PUBLIC_DONE ### W21 KO/EN 공개 + DB 갱신", flush=True)
