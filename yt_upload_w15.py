# -*- coding: utf-8 -*-
"""★W15 업로드(자막 API 포함) — 비디오+썸네일+5개국어 자막+지역화+태그+재생목록, 쿼터 자동기록.

사장님 지시(W15, 2026-07-15):
  - 자막을 API로 5개씩 직접 올린다(W14는 UI 수동이었음 → 이번은 API).
  - 한글판: 동영상 언어=한국어 / 영어판: 동영상 언어=영어.
  - 영어판은 ko 슬롯에도 영어 제목을 넣어 한국에서도 영어로 보이게(W13/W14 교훈).
  - 일부공개(unlisted)로 올리고 1시간 후 4K 확인 뒤 공개 전환.
  - AI 고지: containsSyntheticMedia=True.
  - 모든 API 호출을 yt_quota에 기록(쿼터 추적).

사용: python yt_upload_w15.py <ko|en> [--no-subs]
쿼터: insert 1600 + thumb 50 + captions 400×5(2000) + playlist 50 + list 1 ≈ 3,700/편
"""
import os, sys, time, sqlite3
from yt_api import yt, insert_caption, existing_caption_langs, list_playlists, rp
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import yt_quota

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PKG = "hangeul_birth_vowels/w15pkg"

LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
assert LANG in ("ko", "en"), "ko 또는 en"
NO_SUBS = "--no-subs" in sys.argv

VIDEO = f"hangeul_birth_vowels/hangeul_w15_jieun_np_{LANG}.mp4"
THUMB = f"hangeul_birth_vowels/thumb_w15_{LANG}_1280x720.jpg"
TAGS_F = f"{PKG}/w15_tags.txt"
ALL = ("ko", "en", "ja", "zh", "es")
YTCODE = {"ko": "ko", "en": "en", "ja": "ja", "zh": "zh-Hans", "es": "es"}
SUBDIR = f"subs_upload/W15_{'1_한글판' if LANG == 'ko' else '2_영어판'}"
YT5 = {"ko": "한국어", "en": "영어", "ja": "일본어", "zh": "중국어(중국)", "es": "스페인어"}
PLAYLIST_HINT = "한글"   # 한글 배우기 시리즈 재생목록(제목 부분일치)


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
    print(f"=== W15 {LANG.upper()}판 업로드 ===")
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
        # 영어판은 ko 슬롯에도 영어 제목(한국에서도 영어로 보이게)
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
    yt_quota.log("videos.insert", vid, note=f"W15 {LANG}")
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
            srt = os.path.join(SUBDIR, f"{YT5[c]}.srt")
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
        (project,kind,lang,video_id,url,title,visibility,thumbnail_path,local_path,channel,ai_disclosure,category,uploaded_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
        ("hangeul_w15_weather", "lesson", LANG, vid, f"https://www.youtube.com/watch?v={vid}",
         titles[LANG], "unlisted", THUMB, VIDEO, "@drjay-ed", 1, "Education"))
    con.commit(); con.close()
    print("✅ DB 기록 (youtube_uploads)")

    # 쿼터 현황
    print()
    yt_quota._fmt(yt_quota.status())
    return vid


if __name__ == "__main__":
    main()
