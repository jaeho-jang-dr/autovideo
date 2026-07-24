# -*- coding: utf-8 -*-
"""W17 3단계: 1시간 후 4K 업스케일 확인 → 확인되면 일부공개(unlisted)를 공개(public)로 전환.
사장님 지시(2026-07-21): "부분공개후 1시간 지나 4k 업스케일 확인한후 다시 공개 한다".

동작:
  - yt-dlp -F 로 각 영상의 사용가능 포맷에서 2160p(4K) 존재 여부 확인(쿼터 0).
  - 4K 있으면 privacyStatus=public 으로 전환(videos.update, status part만).
  - 4K 아직이면 공개하지 않고 상태만 보고(다음 실행에서 재확인).
사용: python yt_publish_w17.py [--force]   (--force: 4K 미확인이어도 강제 공개)
"""
import os, sys, subprocess, sqlite3
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from yt_api import yt
import yt_quota

VID = {"ko": "-Gw2cCugmlc", "en": "8raRKVBvU-k"}
FORCE = "--force" in sys.argv


def has_4k(vid):
    """yt-dlp 포맷 목록에 2160(4K) 있는지. (쿼터 0)"""
    try:
        out = subprocess.run(["yt-dlp", "-F", f"https://www.youtube.com/watch?v={vid}"],
                             capture_output=True, text=True, timeout=90, encoding="utf-8", errors="ignore")
        txt = (out.stdout or "") + (out.stderr or "")
        return ("2160" in txt), txt
    except Exception as e:
        return False, f"[yt-dlp 오류] {e}"


def main():
    y = yt()
    con = sqlite3.connect("channel/content.db")
    for lang, vid in VID.items():
        ok4k, _ = has_4k(vid)
        print(f"[{lang}] {vid} 4K(2160p) 사용가능: {ok4k}")
        if not ok4k and not FORCE:
            print(f"  → 아직 4K 처리중 → 공개 보류(unlisted 유지)")
            continue
        cur = y.videos().list(part="status", id=vid).execute()["items"][0]
        yt_quota.log("videos.list", vid)
        st = cur["status"]
        if st.get("privacyStatus") == "public":
            print(f"  → 이미 public"); continue
        st["privacyStatus"] = "public"
        y.videos().update(part="status", body={"id": vid, "status": st}).execute()
        yt_quota.log("videos.update", vid, note="→public")
        con.execute("UPDATE youtube_uploads SET visibility='public' WHERE video_id=?", (vid,))
        con.commit()
        print(f"  ✅ 공개(public) 전환 완료: https://youtu.be/{vid}")
    con.close()
    print()
    yt_quota._fmt(yt_quota.status())


if __name__ == "__main__":
    main()
