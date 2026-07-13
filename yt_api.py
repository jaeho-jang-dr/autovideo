# -*- coding: utf-8 -*-
"""yt_api.py — YouTube Data API v3로 다국어 노출 처리(신형 Studio UI 우회, 견고).
ADC 인증 사용: gcloud auth application-default login --scopes=...youtube.force-ssl 필요.

서브커맨드:
  test                                  현재 인증 채널 확인(mine)
  captions <VID>                        해당 영상의 기존 자막 트랙 나열
  localize <VID> <manifest.json>        자막(captions.insert) + 다국어 제목설명(localizations) + 태그 + 기본언어 일괄
  subs <VID> <manifest.json>            자막만
  meta <VID> <manifest.json>            제목설명+태그+기본언어만
  tags <VID> <tags.txt>                 태그만
  public <VID>                          공개 전환(privacyStatus=public)
  playlists                             내 재생목록 목록
  playlist_add <VID> "<제목일부>"        재생목록에 영상 추가(제목 부분일치)
옵션: --force (기존 자막 트랙 있으면 삭제 후 재업로드)
"""
import sys, os, json, io
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
ROOT = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.path.join(ROOT, "yt_token.json")

# 유튜브 언어행 한국어명 → BCP-47 코드
ROW2CODE = {"한국어": "ko", "영어": "en", "일본어": "ja", "중국어": "zh-Hans", "스페인어": "es"}
# 자막 표시용 이름
CODE2NAME = {"ko": "한국어", "en": "English", "ja": "日本語", "zh-Hans": "中文", "es": "Español"}


def yt():
    creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            open(TOKEN, "w", encoding="utf-8").write(creds.to_json())
        else:
            raise SystemExit("토큰 무효 — python yt_auth.py 재실행 필요")
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def code_of(row):
    key = row.split("(")[0].strip()
    return ROW2CODE.get(key)


def rp(p):
    """manifest의 상대경로를 repo 루트 기준 절대경로로."""
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def existing_caption_langs(y, vid):
    """업로드된(수동) 자막 트랙만. 자동자막(ASR)은 우리 자막을 막지 않도록 제외."""
    r = y.captions().list(part="snippet", videoId=vid).execute()
    out = {}
    for it in r.get("items", []):
        s = it["snippet"]
        if (s.get("trackKind") or "").lower() == "asr":
            continue
        out[s["language"]] = it["id"]
    return out


def insert_caption(y, vid, code, srt_path, existing, force=False):
    if code in existing:
        if force:
            y.captions().delete(id=existing[code]).execute()
            print(f"  [자막] {code}: 기존 삭제")
        else:
            print(f"  [자막] {code}: 이미 있음 → 스킵(--force로 재업로드)")
            return "exists"
    if not os.path.exists(srt_path):
        print(f"  [자막] {code}: SRT 없음 {srt_path}")
        return "no_file"
    body = {"snippet": {"videoId": vid, "language": code, "name": "", "isDraft": False}}
    media = MediaFileUpload(srt_path, mimetype="application/octet-stream", resumable=False)
    y.captions().insert(part="snippet", body=body, media_body=media).execute()
    print(f"  [자막] {code}: 업로드 OK ({os.path.basename(srt_path)})")
    return "ok"


def do_subs(y, vid, man, force=False):
    existing = existing_caption_langs(y, vid)
    print(f"기존 자막 언어: {sorted(existing)}")
    res = {}
    for L in man["langs"]:
        if "sub" not in L.get("do", ["sub"]) or not L.get("srt"):
            continue
        code = code_of(L["row"])
        if not code:
            print(f"  [자막] 코드매핑 실패: {L['row']}"); continue
        try:
            res[code] = insert_caption(y, vid, code, rp(L["srt"]), existing, force)
        except HttpError as e:
            print(f"  [자막] {code}: 실패 {e}"); res[code] = "err"
    return res


def do_meta(y, vid, man):
    # 현재 snippet/localizations 읽어서 병합 갱신
    v = y.videos().list(part="snippet,localizations", id=vid).execute()["items"][0]
    snip = v["snippet"]
    loc = v.get("localizations", {}) or {}
    # 기본 언어 = manifest 첫 행(add=false)의 코드
    default_code = None
    for L in man["langs"]:
        if not L.get("add"):
            default_code = code_of(L["row"]); break
    if default_code:
        snip["defaultLanguage"] = default_code
    # 태그
    if man.get("tags_file") and os.path.exists(rp(man["tags_file"])):
        raw = open(rp(man["tags_file"]), encoding="utf-8").read().strip()
        tags = [t.strip() for t in raw.replace("\n", ",").split(",") if t.strip()]
        snip["tags"] = tags
        print(f"  [태그] {len(tags)}개 세팅")
    # 다국어 제목설명
    added = []
    for L in man["langs"]:
        if "meta" not in L.get("do", []) or not (L.get("title") and L.get("desc")):
            continue
        code = code_of(L["row"])
        if not code:
            continue
        title = open(rp(L["title"]), encoding="utf-8").read().strip()
        desc = open(rp(L["desc"]), encoding="utf-8").read().strip()
        loc[code] = {"title": title[:100], "description": desc[:5000]}
        added.append(code)
    body = {"id": vid, "snippet": snip, "localizations": loc}
    y.videos().update(part="snippet,localizations", body=body).execute()
    print(f"  [제목설명] 기본언어={snip.get('defaultLanguage')} / 로컬라이제이션 추가={added}")
    return {"default": snip.get("defaultLanguage"), "locales": added, "tags": len(snip.get("tags", []))}


def do_tags(y, vid, tags_file):
    v = y.videos().list(part="snippet", id=vid).execute()["items"][0]
    snip = v["snippet"]
    raw = open(rp(tags_file), encoding="utf-8").read().strip()
    tags = [t.strip() for t in raw.replace("\n", ",").split(",") if t.strip()]
    snip["tags"] = tags
    y.videos().update(part="snippet", body={"id": vid, "snippet": snip}).execute()
    total = sum(len(t) + 2 for t in tags)
    print(f"  [태그] {len(tags)}개 (~{total}자) 세팅 OK")


def do_public(y, vid):
    v = y.videos().list(part="status", id=vid).execute()["items"][0]
    st = v["status"]
    before = st.get("privacyStatus")
    st["privacyStatus"] = "public"
    y.videos().update(part="status", body={"id": vid, "status": st}).execute()
    print(f"  [공개] {before} → public OK")


def list_playlists(y):
    pls = []
    req = y.playlists().list(part="snippet,contentDetails", mine=True, maxResults=50)
    while req:
        r = req.execute()
        for it in r.get("items", []):
            pls.append((it["id"], it["snippet"]["title"], it["contentDetails"].get("itemCount")))
        req = y.playlists().list_next(req, r)
    return pls


def playlist_add(y, vid, title_sub):
    pls = list_playlists(y)
    match = [(pid, t) for pid, t, _ in pls if title_sub in t]
    if not match:
        print(f"  [재생목록] '{title_sub}' 매칭 없음. 현재 목록:")
        for pid, t, n in pls:
            print(f"     - {t} ({n}) {pid}")
        return
    pid, t = match[0]
    y.playlistItems().insert(part="snippet", body={"snippet": {
        "playlistId": pid, "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()
    print(f"  [재생목록] '{t}'에 추가 OK")


def post_comment(y, vid, text_file):
    text = open(rp(text_file), encoding="utf-8").read().strip()
    r = y.commentThreads().insert(part="snippet", body={"snippet": {
        "videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}}).execute()
    cid = r["snippet"]["topLevelComment"]["id"]
    print(f"  [댓글] 게시 OK id={cid}")
    return cid


def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    cmd = sys.argv[1]
    force = "--force" in sys.argv
    y = yt()
    if cmd == "test":
        r = y.channels().list(part="snippet,contentDetails", mine=True).execute()
        for it in r.get("items", []):
            print("채널:", it["snippet"]["title"], "/ id:", it["id"])
    elif cmd == "captions":
        for c, cid in existing_caption_langs(y, sys.argv[2]).items():
            print(f"  {c}  {cid}")
    elif cmd == "subs":
        do_subs(y, sys.argv[2], json.load(open(rp(sys.argv[3]), encoding="utf-8")), force)
    elif cmd == "meta":
        do_meta(y, sys.argv[2], json.load(open(rp(sys.argv[3]), encoding="utf-8")))
    elif cmd == "tags":
        do_tags(y, sys.argv[2], sys.argv[3])
    elif cmd == "localize":
        man = json.load(open(rp(sys.argv[3]), encoding="utf-8"))
        print("=== 자막 ==="); s = do_subs(y, sys.argv[2], man, force)
        print("=== 제목설명/태그/기본언어 ==="); m = do_meta(y, sys.argv[2], man)
        print("=== 요약 ===", json.dumps({"subs": s, "meta": m}, ensure_ascii=False))
    elif cmd == "public":
        do_public(y, sys.argv[2])
    elif cmd == "comment":
        post_comment(y, sys.argv[2], sys.argv[3])
    elif cmd == "playlists":
        for pid, t, n in list_playlists(y):
            print(f"  {t}  ({n})  {pid}")
    elif cmd == "playlist_add":
        playlist_add(y, sys.argv[2], sys.argv[3])
    else:
        print("알수없는 커맨드:", cmd); print(__doc__)


if __name__ == "__main__":
    main()
