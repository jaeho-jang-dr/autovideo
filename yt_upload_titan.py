# -*- coding: utf-8 -*-
"""★titan_science 전체 업로드 (진격의 거인 과학 / 8분 / 4K).
비디오(videos.insert)+썸네일+5개국어 자막(API)+지역화(제목·설명)+태그+재생목록.

yt_upload_w19.py 어댑트. 규칙 동일:
  - 스페인어 es-419(라틴아메리카), 중국어 zh-Hans(본토간체).
  - 일부공개(unlisted)로 올리고 4K 확인 뒤 공개 전환.
  - AI 고지 containsSyntheticMedia=True, 아동용=아니요.
  - 영어판은 ko 지역화 슬롯에도 영어 제목/설명(한국에서도 영어로 보이게).

사용: python yt_upload_titan.py <ko|en> [--no-subs]
"""
import os
import sys
import time

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

import yt_quota
from yt_api import existing_caption_langs, insert_caption, list_playlists, yt

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PKG = "titan_science/pkg"
SUBS = "titan_science/subs"

LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
assert LANG in ("ko", "en"), "ko 또는 en"
NO_SUBS = "--no-subs" in sys.argv

VIDEO = "titan_science/_out/TITAN_%s_4K_final.mp4" % LANG.upper()
THUMB = "titan_science/_thumb/out/titan_%s_A.jpg" % LANG
TAGS_F = f"{PKG}/titan_tags.txt"
ALL = ("ko", "en", "ja", "zh", "es")
YTCODE = {"ko": "ko", "en": "en", "ja": "ja", "zh": "zh-Hans", "es": "es-419"}
SRT = {"ko": f"{SUBS}/TITAN_ko.srt", "en": f"{SUBS}/TITAN_en.srt",
       "ja": f"{SUBS}/TITAN_ja.srt", "zh": f"{SUBS}/TITAN_zh-Hans.srt",
       "es": f"{SUBS}/TITAN_es-419.srt"}
PLAYLIST_HINT = "과학"          # 과학 재생목록(제목 부분일치)


def read(p):
    return open(p, encoding="utf-8").read().strip()


def main():
    for f in [VIDEO, THUMB, TAGS_F] + list(SRT.values()):
        if not os.path.exists(f):
            raise SystemExit("★없음: %s" % f)

    y = yt()
    titles = {c: read(f"{PKG}/{c}_title.txt") for c in ALL}
    descs = {c: read(f"{PKG}/{c}_desc.txt") for c in ALL}
    tags = [t.strip() for t in read(TAGS_F).replace("\n", ",").split(",") if t.strip()]

    size_mb = os.path.getsize(VIDEO) // 1048576
    print("=== titan_science %s판 업로드 ===" % LANG.upper())
    print("  영상: %s (%dMB) / 동영상 언어=%s" % (VIDEO, size_mb, LANG))
    print("  제목: %s" % titles[LANG][:70])
    print("  태그 %d개 / 지역화 %d개 / 자막 %s"
          % (len(tags), len(ALL), "★API 5개" if not NO_SUBS else "스킵"))

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
                # ★영어판은 ko 슬롯에도 영어를 넣는다(한국에서도 영어로 보이게)
                "title": (titles[LANG] if c == "ko" and LANG == "en" else titles[c])[:100],
                "description": (descs[LANG] if c == "ko" and LANG == "en" else descs[c])[:5000],
            }
            for c in ALL
        },
    }

    media = MediaFileUpload(VIDEO, chunksize=8 * 1024 * 1024, resumable=True,
                            mimetype="video/mp4")
    req = y.videos().insert(part="snippet,status,localizations", body=body,
                            media_body=media)
    print("\n[업로드 중]")
    resp, last = None, -1
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            p = int(status.progress() * 100)
            if p >= last + 5:
                print("  %d%%" % p, flush=True)
                last = p
    vid = resp["id"]
    yt_quota.log("videos.insert", vid, note="titan %s" % LANG)
    print("✅ 업로드 완료: https://youtu.be/%s" % vid)

    time.sleep(2)
    y.thumbnails().set(videoId=vid, media_body=MediaFileUpload(THUMB)).execute()
    yt_quota.log("thumbnails.set", vid)
    print("✅ 썸네일 적용: %s" % THUMB)

    sub_res = {}
    if not NO_SUBS:
        print("\n[자막 API 업로드]")
        existing = existing_caption_langs(y, vid)
        yt_quota.log("captions.list", vid)
        for c in ALL:
            code = YTCODE[c]
            try:
                r = insert_caption(y, vid, code, SRT[c], existing, force=True)
                sub_res[code] = r
                if r == "ok":
                    yt_quota.log("captions.insert", vid, note=code)
            except HttpError as e:
                print("  [자막] %s: 실패 %s" % (code, str(e)[:90]))
                sub_res[code] = "err"

    try:
        pls = list_playlists(y)
        yt_quota.log("playlists.list", vid)
        match = [(pid, t) for pid, t, _ in pls if PLAYLIST_HINT in t]
        if match:
            pid, t = match[0]
            y.playlistItems().insert(part="snippet", body={"snippet": {
                "playlistId": pid,
                "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
            yt_quota.log("playlistItems.insert", vid, note=t)
            print("✅ 재생목록 '%s' 추가" % t)
        else:
            print("  [재생목록] '%s' 매칭 없음 — 나중에 따로" % PLAYLIST_HINT)
    except HttpError as e:
        print("  [재생목록] 실패 %s" % str(e)[:90])

    v = y.videos().list(part="snippet,status,localizations", id=vid).execute()["items"][0]
    yt_quota.log("videos.list", vid)
    loc = sorted((v.get("localizations") or {}).keys())
    print("\n=== 검증 ===")
    print("  동영상 언어 : %s" % v["snippet"].get("defaultLanguage"))
    print("  공개 상태   : %s" % v["status"]["privacyStatus"])
    print("  AI 고지     : %s" % v["status"].get("containsSyntheticMedia"))
    print("  지역화 언어 : %s" % loc)
    print("  태그        : %d개" % len(v["snippet"].get("tags", [])))
    print("  자막        : %s" % sub_res)
    print("\nVIDEO_ID=%s" % vid)
    with open("titan_science/pkg/vid_%s.txt" % LANG, "w", encoding="utf-8") as f:
        f.write(vid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
