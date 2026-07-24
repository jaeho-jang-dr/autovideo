# -*- coding: utf-8 -*-
"""★YouTube Data API로 영상 업로드 (자막 없이 · 5개국어 제목/설명 · 일부공개)

사장님 지시(2026-07-14):
  - 자막은 사장님이 유튜브 UI로 직접 올리신다 → API로 자막 안 올림(쿼터 4,000 절약)
  - 한글판: 동영상 언어=한국어 + 제목·설명, 추가언어(en/ja/zh/es) 각각 제목·설명
  - 영어판: 동영상 언어=영어 + 제목·설명, 추가언어(ko/ja/zh/es) 각각 제목·설명
  - 자막 5개는 비워 둠. 일부공개(unlisted)까지만.

사용: python yt_upload_api.py <ko|en>
쿼터: videos.insert 1,600 + videos.update(메타) 50 + thumbnails.set 50 ≈ 1,700/편
"""
import os, sys, json, time
from yt_api import yt
from googleapiclient.http import MediaFileUpload

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PKG = "hangeul_birth_vowels/w20pkg"

LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
assert LANG in ("ko", "en")

VIDEO = f"hangeul_birth_vowels/hangeul_w20_injun_np_{LANG}.mp4"
THUMB = f"hangeul_birth_vowels/thumb_w20_{LANG}_1280x720.jpg"
TAGS_F = f"{PKG}/w20_tags.txt"
ALL = ("ko", "en", "ja", "zh", "es")
# 유튜브 지역화 코드 (중국어 간체 = zh-Hans)
YTCODE = {"ko": "ko", "en": "en", "ja": "ja", "zh": "zh-Hans", "es": "es"}


def read(p):
    return open(p, encoding="utf-8").read().strip()


def main():
    for f in (VIDEO, THUMB, TAGS_F):
        if not os.path.exists(f):
            raise SystemExit(f"★없음: {f}")

    y = yt()
    titles = {c: read(f"{PKG}/{c}_title.txt") for c in ALL}
    descs = {c: read(f"{PKG}/{c}_desc.txt") for c in ALL}
    tags = [t.strip() for t in read(TAGS_F).replace("\n", ",").split(",") if t.strip()]

    size_mb = os.path.getsize(VIDEO) // 1048576
    print(f"=== W14 {LANG.upper()}판 업로드 ===")
    print(f"  영상: {VIDEO} ({size_mb}MB)")
    print(f"  동영상 언어(defaultLanguage): {LANG}")
    print(f"  제목: {titles[LANG][:60]}…")
    print(f"  태그 {len(tags)}개 / 지역화 {len(ALL)}개 언어 / 자막: ★비움(사장님 직접 업로드)")

    body = {
        "snippet": {
            "title": titles[LANG][:100],
            "description": descs[LANG][:5000],
            "tags": tags,
            "categoryId": "27",                 # Education
            "defaultLanguage": LANG,            # ★동영상 언어
            "defaultAudioLanguage": LANG,
        },
        "status": {
            "privacyStatus": "unlisted",        # ★일부공개
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,     # ★AI 생성 고지
        },
        # ★영어판은 ko 슬롯에도 영어를 넣어 한국에서도 영어 제목으로 보이게(W13/W14 교훈).
        #   한글판은 ko 슬롯에 한글(정상). = defaultLanguage 언어의 텍스트를 ko 슬롯에.
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
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"  {int(status.progress()*100)}%", flush=True)
    vid = resp["id"]
    print(f"✅ 업로드 완료: https://youtu.be/{vid}")

    # 썸네일
    time.sleep(2)
    y.thumbnails().set(videoId=vid, media_body=MediaFileUpload(THUMB)).execute()
    print(f"✅ 썸네일 적용: {THUMB}")

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
        ("hangeul_w20_emergency", "lesson", LANG, vid, f"https://www.youtube.com/watch?v={vid}",
         titles[LANG], "unlisted", THUMB, VIDEO, "@drjay-ed", 1, "Education"))
    con.commit(); con.close()
    print(f"✅ DB 기록 (youtube_uploads)")
    print(f"\n▶ 자막은 yt_api.py subs 로 API 업로드 예정 (W20)")
    return vid


if __name__ == "__main__":
    main()
