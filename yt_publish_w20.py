# -*- coding: utf-8 -*-
"""W20 발행: 일부공개(unlisted)를 공개(public)로 전환.
"""
import os, sys, json, sqlite3
os.chdir(os.path.dirname(os.path.abspath(__file__)))
from yt_api import yt
import yt_quota

PKG = "hangeul_birth_vowels/w20pkg"
FORCE = "--force" in sys.argv

def load_ids():
    ids = {}
    for lang in ("ko", "en"):
        p = f"{PKG}/w20_{lang}_manifest.json"
        if os.path.exists(p):
            m = json.load(open(p, encoding="utf-8"))
            if m.get("video_id"):
                ids[lang] = (m["video_id"], p)
    return ids

def main():
    ids = load_ids()
    if not ids:
        raise SystemExit("W20 매니페스트에 video_id 없음")

    y = yt()
    con_path = "channel/content.db"
    con = sqlite3.connect(con_path) if os.path.exists(con_path) else None

    for lang, (vid, manifest_path) in ids.items():
        print(f"[{lang.upper()}] 영상 ID: {vid}")
        
        # YouTube API로 status 조회
        res = y.videos().list(part="status", id=vid).execute()
        items = res.get("items", [])
        if not items:
            print(f"  ❌ YouTube API에서 영상 {vid}를 찾을 수 없습니다.")
            continue
            
        cur_status = items[0]["status"]
        privacy = cur_status.get("privacyStatus")
        print(f"  현재 상태: {privacy}")

        if privacy == "public":
            print(f"  -> 이미 public 상태입니다. (https://youtu.be/{vid})")
            continue

        # public 전환 실행
        cur_status["privacyStatus"] = "public"
        y.videos().update(part="status", body={"id": vid, "status": cur_status}).execute()
        yt_quota.log("videos.update", vid, note="->public")
        
        # Manifest 업데이트
        m_data = json.load(open(manifest_path, encoding="utf-8"))
        m_data["privacyStatus"] = "public"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(m_data, f, ensure_ascii=False, indent=2)

        # DB 업데이트
        if con:
            con.execute("UPDATE youtube_uploads SET visibility='public' WHERE video_id=?", (vid,))
            con.commit()

        print(f"  ✅ [성공] 공개(public) 전환 완료: https://youtu.be/{vid}")

    if con:
        con.close()
    print("\n최종 작업 완료.")

if __name__ == "__main__":
    main()
