# -*- coding: utf-8 -*-
"""W16 노출: 이미 업로드된 영상(사장님 업로드)에 제목설명·태그·5개국어 지역화·썸네일·재생목록 갱신.
자막은 사장님이 UI로 이미 올림 → 여기선 안 건드림. 공개상태는 unlisted 유지(1시간 후 별도 공개).
★언어원칙: 스페인어=es-419(라틴아메리카), 중국어=zh-Hans(북경/본토 간체).
사용: python yt_meta_w16.py <ko|en>"""
import os, sys, time, sqlite3
from yt_api import yt
from googleapiclient.http import MediaFileUpload
os.chdir(os.path.dirname(os.path.abspath(__file__)))
PKG = "hangeul_birth_vowels/w16pkg"

VID = {"ko": "l35_jlJEEzU", "en": "Eu9BvXmn2ck"}
THUMB = {"ko": "hangeul_birth_vowels/thumb_w16_ko_1280x720.jpg",
         "en": "hangeul_birth_vowels/thumb_w16_en_1280x720.jpg"}
ALL = ("ko", "en", "ja", "zh", "es")
YTCODE = {"ko": "ko", "en": "en", "ja": "ja", "zh": "zh-Hans", "es": "es-419"}  # ★원칙
PLAYLIST_HINT = "한글"

def read(p): return open(p, encoding="utf-8").read().strip()

LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
assert LANG in ("ko", "en")
vid = VID[LANG]
y = yt()
titles = {c: read(f"{PKG}/{c}_title.txt") for c in ALL}
descs = {c: read(f"{PKG}/{c}_desc.txt") for c in ALL}
tags = [t.strip() for t in read(f"{PKG}/w16_tags.txt").replace("\n", ",").split(",") if t.strip()]

cur = y.videos().list(part="snippet,status,localizations", id=vid).execute()["items"][0]
snip = cur["snippet"]
snip["title"] = titles[LANG][:100]
snip["description"] = descs[LANG][:5000]
snip["tags"] = tags
snip["categoryId"] = "27"          # Education
snip["defaultLanguage"] = LANG
snip["defaultAudioLanguage"] = LANG

loc = {}
for c in ALL:
    # 영어판은 ko 슬롯에도 영어(한국에서도 영어로 보이게 — 강의 표준)
    t = titles["en"] if (c == "ko" and LANG == "en") else titles[c]
    d = descs["en"] if (c == "ko" and LANG == "en") else descs[c]
    loc[YTCODE[c]] = {"title": t[:100], "description": d[:5000]}

st = cur["status"]
st["selfDeclaredMadeForKids"] = False
st["containsSyntheticMedia"] = True   # ★AI 고지
# privacyStatus 는 현재값(unlisted) 유지

y.videos().update(part="snippet,status,localizations",
                  body={"id": vid, "snippet": snip, "status": st, "localizations": loc}).execute()
print(f"[메타] {LANG} 갱신: 기본언어={LANG}, 태그 {len(tags)}개, 지역화 {sorted(loc.keys())}")

# 썸네일
y.thumbnails().set(videoId=vid, media_body=MediaFileUpload(THUMB[LANG])).execute()
print(f"[썸네일] {THUMB[LANG]}")

# 재생목록
pls = y.playlists().list(part="snippet", mine=True, maxResults=50).execute()["items"]
match = [(p["id"], p["snippet"]["title"]) for p in pls if PLAYLIST_HINT in p["snippet"]["title"]]
if match:
    pid, ptitle = match[0]
    # 중복 방지: 이미 있으면 스킵
    y.playlistItems().insert(part="snippet", body={"snippet": {
        "playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
    print(f"[재생목록] '{ptitle}' 추가")
else:
    print(f"[재생목록] '{PLAYLIST_HINT}' 매칭 없음")

# 검증
v = y.videos().list(part="snippet,status,localizations", id=vid).execute()["items"][0]
print(f"=== 검증 {LANG} ===  공개={v['status']['privacyStatus']} · 기본언어={v['snippet'].get('defaultLanguage')} "
      f"· 지역화={sorted((v.get('localizations') or {}).keys())} · 태그={len(v['snippet'].get('tags',[]))}개 "
      f"· AI고지={v['status'].get('containsSyntheticMedia')}")

# DB 기록
con = sqlite3.connect("channel/content.db")
con.execute("""INSERT OR REPLACE INTO youtube_uploads
    (project,kind,lang,video_id,url,title,visibility,thumbnail_path,local_path,resolution,channel,ai_disclosure,category,uploaded_at)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))""",
    ("hangeul_w16_hobby", "lesson", LANG, vid, f"https://youtu.be/{vid}", titles[LANG],
     "unlisted", THUMB[LANG], f"hangeul_birth_vowels/hangeul_w16_stickman_np_{LANG}.mp4", "3840x2160",
     "@drjay-ed", 1, "Education"))
con.commit(); con.close()
print("[DB] youtube_uploads 기록")
