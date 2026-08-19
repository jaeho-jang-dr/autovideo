# -*- coding: utf-8 -*-
"""★W1-2 전체 업로드 (스틱맨/광화문광장/모음만으로 만든 낱말 15개).
비디오(videos.insert)+썸네일+5개국어 자막(API)+지역화(제목·설명)+태그+재생목록, 쿼터 자동기록.

yt_upload_w19.py 어댑트. 규칙 동일:
  - 스페인어 es-419(라틴아메리카), 중국어 zh-Hans(본토간체).
  - 일부공개(unlisted)로 올리고 4K 확인 뒤 공개 전환(yt_publish_w19.py).
  - AI 고지 containsSyntheticMedia=True, 아동용=아니요.
  - 영어판은 ko 지역화 슬롯에도 영어 제목/설명(한국에서도 영어로 보이게).

사용: python W1_2/yt_upload_w1d2.py <ko|en> [--no-subs]
쿼터: insert 1600 + thumb 50 + captions 400x5(2000) + playlist 50 + list 1 ≈ 3,700/편
"""
import os, sys, time, sqlite3
# ★이 스크립트는 W1_2/ 안에 있으므로 루트를 경로에 넣어야 yt_api 를 찾는다
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from yt_api import yt, insert_caption, existing_caption_langs, list_playlists
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import yt_quota

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
PKG = "W1_2/w1d2pkg"

LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
assert LANG in ("ko", "en"), "ko 또는 en"
NO_SUBS = "--no-subs" in sys.argv

VIDEO = f"W1_2/w1d2_4k_{LANG}.mp4"                 # ★4K 본편
THUMB = f"W1_2/w1d2_thumb_{LANG}.jpg"
TAGS_F = f"{PKG}/w1d2_tags_{LANG}.txt"
ALL = ("ko", "en", "ja", "zh", "es")
YTCODE = {"ko": "ko", "en": "en", "ja": "ja", "zh": "zh-Hans", "es": "es-419"}  # ★es-419/zh-Hans
SUBDIR = "W1_2/subs"                              # ★자막은 한 폴더에 코드명으로 있다
YT5 = {"ko": "한국어", "en": "영어", "ja": "일본어", "zh": "중국어(중국)", "es": "스페인어"}
PLAYLIST_HINT = "한국어 쉽게"   # 재생목록 "한국어 쉽게 배우기"(제목 부분일치)


def read(p):
    return open(p, encoding="utf-8").read().strip()


def main():
    for f in (VIDEO, THUMB, TAGS_F):
        if not os.path.exists(f):
            raise SystemExit(f"★없음: {f}")

    y = yt()
    # ★ja/zh/es 제목·설명은 따로 만들지 않았다 — 영어판 것을 쓴다
    #   (자막은 5개국어로 다 올라간다. 다국어 제목은 노출 단계에서 보완)
    titles = {c: read(f"{PKG}/{c}_title.txt") if os.path.exists(f"{PKG}/{c}_title.txt")
              else read(f"{PKG}/en_title.txt") for c in ALL}
    descs = {c: read(f"{PKG}/{c}_desc.txt") if os.path.exists(f"{PKG}/{c}_desc.txt")
             else read(f"{PKG}/en_desc.txt") for c in ALL}
    tags = [t.strip() for t in read(TAGS_F).replace("\n", ",").split(",") if t.strip()]

    size_mb = os.path.getsize(VIDEO) // 1048576
    print(f"=== W1-2 {LANG.upper()}판 업로드 ===")
    print(f"  영상: {VIDEO} ({size_mb}MB) / 동영상 언어={LANG}")
    print(f"  제목: {titles[LANG][:60]}…")
    print(f"  태그 {len(tags)}개 / 지역화 {len(ALL)}개 / 자막: {'★API 업로드 5개' if not NO_SUBS else '스킵'}")

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
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,     # ★AI 고지
        },
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
            print(f"  {int(status.progress() * 100)}%", flush=True)
    vid = resp["id"]
    yt_quota.log("videos.insert", vid, note=f"W1-2 {LANG}")
    print(f"✅ 업로드 완료: https://youtu.be/{vid}")

    # 썸네일
    time.sleep(2)
    y.thumbnails().set(videoId=vid, media_body=MediaFileUpload(THUMB)).execute()
    yt_quota.log("thumbnails.set", vid)
    print(f"✅ 썸네일 적용: {THUMB}")

    # 자막 5개 (API)
    sub_res = {}
    if not NO_SUBS:
        print("\n[자막 API 업로드]")
        existing = existing_caption_langs(y, vid)
        yt_quota.log("captions.list", vid)
        for c in ALL:
            srt = os.path.join(SUBDIR, f"w1d2.{YTCODE[c]}.srt")
            code = YTCODE[c]
            try:
                r = insert_caption(y, vid, code, srt, existing, force=True)
                sub_res[code] = r
                if r == "ok":
                    yt_quota.log("captions.insert", vid, note=code)
            except HttpError as e:
                print(f"  [자막] {code}: 실패 {e}")
                sub_res[code] = "err"

    # 재생목록 추가
    try:
        pls = list_playlists(y)
        yt_quota.log("playlists.list", vid)
        match = [(pid, t) for pid, t, _ in pls if PLAYLIST_HINT in t]
        if match:
            pid, t = match[0]
            y.playlistItems().insert(part="snippet", body={"snippet": {
                "playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
            yt_quota.log("playlistItems.insert", vid, note=t)
            print(f"✅ 재생목록 '{t}' 추가")
        else:
            print(f"  [재생목록] '{PLAYLIST_HINT}' 매칭 없음 — 스킵")
    except HttpError as e:
        print(f"  [재생목록] 실패 {e}")

    # 검증
    v = y.videos().list(part="snippet,status,localizations", id=vid).execute()["items"][0]
    yt_quota.log("videos.list", vid)
    loc = sorted((v.get("localizations") or {}).keys())
    print("\n=== 검증 ===")
    print(f"  동영상 언어 : {v['snippet'].get('defaultLanguage')}")
    print(f"  공개 상태   : {v['status']['privacyStatus']}")
    print(f"  지역화 언어 : {loc}")
    print(f"  태그        : {len(v['snippet'].get('tags', []))}개")
    print(f"  AI 고지     : {v['status'].get('containsSyntheticMedia')}")
    print(f"  자막 결과   : {sub_res}")

    # DB 기록
    con = sqlite3.connect("channel/content.db")
    con.execute("""INSERT INTO youtube_uploads
        (project,kind,lang,video_id,url,title,visibility,thumbnail_path,local_path,resolution,channel,ai_disclosure,category,uploaded_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
        ("hangeul_w19_opinion", "lesson", LANG, vid, f"https://www.youtube.com/watch?v={vid}",
         titles[LANG], "unlisted", THUMB, VIDEO, "3840x2160", "@drjay-ed", 1, "Education"))
    con.commit(); con.close()
    print("✅ DB 기록 (youtube_uploads)")

    # 매니페스트에 video_id 기록(노출 단계에서 사용)
    import json
    mpath = f"{PKG}/w19_{LANG}_manifest.json"
    try:
        m = json.load(open(mpath, encoding="utf-8")) if os.path.exists(mpath) else {}
    except Exception:
        m = {}
    m["video_id"] = vid
    m["url"] = f"https://youtu.be/{vid}"
    json.dump(m, open(mpath, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✅ 매니페스트 video_id 기록: {mpath}")

    print()
    yt_quota._fmt(yt_quota.status())
    return vid


if __name__ == "__main__":
    main()
