# -*- coding: utf-8 -*-
"""★W23 YouTube Data API 업로드 — 본편 + 썸네일 + 5개국어 제목/설명 + 태그 (일부공개)
   자막은 업로드 직후 `python yt_api.py subs <VID> <manifest>` 로 5개국어를 API로 올린다
   (사장님 지시 2026-07-27: 자막도 API로).

사용: python yt_upload_api_w23.py <ko|en>
쿼터: videos.insert 1,600 + thumbnails.set 50 ≈ 1,650/편 (자막은 captions.insert 400 × 5)
   ★video_id를 매니페스트에 기록한다 — yt_publish_w23.py(공개 전환)가 이 값을 읽는다.
   (yt_upload_api_w22.py 계승)"""
import os, sys, json, time
from yt_api import yt
from googleapiclient.http import MediaFileUpload
import yt_quota

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PKG = "hangeul_birth_vowels/w23pkg"

LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
assert LANG in ("ko", "en")

VIDEO = f"hangeul_birth_vowels/hangeul_w23_injun_np_{LANG}.mp4"
THUMB = f"hangeul_birth_vowels/thumb_w23_{LANG}_1280x720.jpg"
TAGS_F = f"{PKG}/w23_tags.txt"
MANIFEST = f"{PKG}/w23_{LANG}_manifest.json"
ALL = ("ko", "en", "ja", "zh", "es")
YTCODE = {"ko": "ko", "en": "en", "ja": "ja", "zh": "zh-Hans", "es": "es"}   # 중국어 간체 = zh-Hans


def read(p):
    return open(p, encoding="utf-8").read().strip()


def main():
    for f in (VIDEO, THUMB, TAGS_F, MANIFEST):
        if not os.path.exists(f):
            raise SystemExit(f"★없음: {f}")

    y = yt()
    titles = {c: read(f"{PKG}/{c}_title.txt") for c in ALL}
    descs = {c: read(f"{PKG}/{c}_desc.txt") for c in ALL}
    tags = [t.strip() for t in read(TAGS_F).replace("\n", ",").split(",") if t.strip()]

    size_mb = os.path.getsize(VIDEO) // 1048576
    print(f"=== W23 {LANG.upper()}판 업로드 ===")
    print(f"  영상: {VIDEO} ({size_mb}MB)")
    print(f"  동영상 언어(defaultLanguage): {LANG}")
    print(f"  제목: {titles[LANG][:60]}…")
    print(f"  태그 {len(tags)}개 / 지역화 {len(ALL)}개 언어")

    body = {
        "snippet": {
            "title": titles[LANG][:100],
            "description": descs[LANG][:5000],
            "tags": tags,
            "categoryId": "27",                 # Education
            "defaultLanguage": LANG,
            "defaultAudioLanguage": LANG,
        },
        "status": {
            "privacyStatus": "unlisted",        # ★일부공개 — 4K 처리 후 공개 전환
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,     # ★AI 생성 고지
        },
        # ★영어판은 ko 슬롯에도 영어를 넣어 한국에서도 영어 제목으로 보이게(W13/W14 교훈).
        "localizations": {
            YTCODE[c]: {
                "title": (titles[LANG] if c == "ko" and LANG == "en" else titles[c])[:100],
                "description": (descs[LANG] if c == "ko" and LANG == "en" else descs[c])[:5000],
            }
            for c in ALL
        },
    }

    media = MediaFileUpload(VIDEO, chunksize=8 * 1024 * 1024, resumable=True, mimetype="video/mp4")
    req = y.videos().insert(part="snippet,status,localizations", body=body, media_body=media)

    print("\n[업로드 중]")
    resp = None
    last = -1
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            p = int(status.progress() * 100)
            if p >= last + 10:
                print(f"  {p}%", flush=True); last = p
    vid = resp["id"]
    yt_quota.log("videos.insert", vid, note=f"W23 {LANG}")
    print(f"✅ 업로드 완료: https://youtu.be/{vid}")

    # 썸네일
    time.sleep(2)
    y.thumbnails().set(videoId=vid, media_body=MediaFileUpload(THUMB)).execute()
    yt_quota.log("thumbnails.set", vid)
    print(f"✅ 썸네일 적용: {THUMB}")

    # ★매니페스트에 video_id 기록 (자막 업로드·공개 전환이 이 값을 읽는다)
    mf = json.load(open(MANIFEST, encoding="utf-8"))
    mf["video_id"] = vid
    mf["url"] = f"https://www.youtube.com/watch?v={vid}"
    json.dump(mf, open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✅ 매니페스트 기록: {MANIFEST}")

    # 검증
    v = y.videos().list(part="snippet,status,localizations", id=vid).execute()["items"][0]
    loc = sorted((v.get("localizations") or {}).keys())
    print("\n=== 검증 ===")
    print(f"  동영상 언어 : {v['snippet'].get('defaultLanguage')}")
    print(f"  공개 상태   : {v['status']['privacyStatus']}")
    print(f"  지역화 언어 : {loc}")
    print(f"  태그        : {len(v['snippet'].get('tags', []))}개")
    print(f"  AI 고지     : {v['status'].get('containsSyntheticMedia')}")

    # DB 기록
    import sqlite3
    con = sqlite3.connect("channel/content.db")
    con.execute("""INSERT INTO youtube_uploads
        (project,kind,lang,video_id,url,title,visibility,thumbnail_path,local_path,channel,ai_disclosure,category,uploaded_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
        ("hangeul_w23_meetup", "lesson", LANG, vid, f"https://www.youtube.com/watch?v={vid}",
         titles[LANG], "unlisted", THUMB, VIDEO, "@drjay-ed", 1, "Education"))
    con.commit(); con.close()
    print("✅ DB 기록 (youtube_uploads)")
    print(f"\n▶ 다음: python yt_api.py subs {vid} {MANIFEST}")
    return vid


if __name__ == "__main__":
    main()
