# -*- coding: utf-8 -*-
"""W19 발행: 4K 업스케일 확인 → 확인되면 일부공개(unlisted)를 공개(public)로 전환.
video_id 는 업로드 때 기록된 매니페스트(w19pkg/w19_{ko,en}_manifest.json)에서 읽는다.

동작:
  - yt-dlp -F 로 각 영상 2160p(4K) 존재 여부 확인(쿼터 0).
  - 4K 있으면 privacyStatus=public (videos.update, status part만).
  - 4K 아직이면 공개 보류(다음 실행 재확인).
사용: python yt_publish_w19.py [--force]
"""
import os, sys, json, subprocess, sqlite3
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from yt_api import yt
import yt_quota

PKG = "hangeul_birth_vowels/w19pkg"
FORCE = "--force" in sys.argv


def load_ids():
    ids = {}
    for lang in ("ko", "en"):
        p = f"{PKG}/w19_{lang}_manifest.json"
        if os.path.exists(p):
            m = json.load(open(p, encoding="utf-8"))
            if m.get("video_id"):
                ids[lang] = m["video_id"]
    return ids


def has_4k(vid):
    try:
        out = subprocess.run(["yt-dlp", "-F", f"https://www.youtube.com/watch?v={vid}"],
                             capture_output=True, text=True, timeout=90, encoding="utf-8", errors="ignore")
        return ("2160" in ((out.stdout or "") + (out.stderr or "")))
    except Exception as e:
        print(f"[yt-dlp 오류] {e}"); return False


def main():
    ids = load_ids()
    if not ids:
        raise SystemExit("매니페스트에 video_id 없음 — 먼저 yt_upload_w19.py 로 업로드하세요.")
    y = yt()
    con = sqlite3.connect("channel/content.db")
    for lang, vid in ids.items():
        ok4k = has_4k(vid)
        print(f"[{lang}] {vid} 4K(2160p): {ok4k}")
        if not ok4k and not FORCE:
            print("  → 아직 4K 처리중 → 공개 보류(unlisted 유지)"); continue
        cur = y.videos().list(part="status", id=vid).execute()["items"][0]
        yt_quota.log("videos.list", vid)
        st = cur["status"]
        if st.get("privacyStatus") == "public":
            print("  → 이미 public"); continue
        st["privacyStatus"] = "public"
        y.videos().update(part="status", body={"id": vid, "status": st}).execute()
        yt_quota.log("videos.update", vid, note="→public")
        con.execute("UPDATE youtube_uploads SET visibility='public' WHERE video_id=?", (vid,))
        con.commit()
        print(f"  ✅ 공개 전환: https://youtu.be/{vid}")
    con.close()
    print()
    yt_quota._fmt(yt_quota.status())


if __name__ == "__main__":
    main()
