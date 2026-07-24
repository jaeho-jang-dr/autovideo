# -*- coding: utf-8 -*-
"""동영상 정보 카드를 내부 API로 설정(edit_video). endscreenEdit 미포함=최종화면 안 건드림.
사용: python yt_infocard.py <VID> <field> <tvid1> <ms1> "<teaser1>" "<msg1>" [<tvid2> <ms2> "<teaser2>" "<msg2>"] ...
  field: 시도할 동영상카드 필드명(videoInfoCard / simpleVideoInfoCard 등)"""
import time, sys, json, hashlib
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
FIELD = sys.argv[2]
rest = sys.argv[3:]
CARDS_IN = [(rest[i], int(rest[i+1]), rest[i+2], rest[i+3]) for i in range(0, len(rest), 4)]
KEY = "AIzaSyBUPetSUmoZL-OhlxA7wSac5XinrygCqMo"
ORIGIN = "https://studio.youtube.com"
ENDPOINT = f"{ORIGIN}/youtubei/v1/video_editor/edit_video?alt=json&key={KEY}"

def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii","ignore").decode(), flush=True)

ctx_obj = json.load(open("scratch/yt/ctx.json", encoding="utf-8"))

def inner_key_for(field):
    f = field.lower()
    if "playlist" in f: return "fullPlaylistId"
    if "video" in f: return "fullVideoId"   # 리서치: playlistInfoCard.fullPlaylistId 대칭
    return "id"

cards = []
for i, (tvid, ms, teaser, msg) in enumerate(CARDS_IN):
    cards.append({
        "videoId": VID,
        "teaserStartMs": ms,
        FIELD: {inner_key_for(FIELD): tvid},
        "infoCardEntityId": f"card{i}_{ms}",
        "customMessage": msg,
        "teaserText": teaser,
    })
payload = {"context": ctx_obj, "externalVideoId": VID, "infoCardEdit": {"infoCards": cards}}

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    cookies = ctx.cookies("https://studio.youtube.com")
    sapisid = None
    for nm in ("SAPISID", "__Secure-3PAPISID"):
        for c in cookies:
            if c["name"] == nm: sapisid = c["value"]; break
        if sapisid: break
    ts = int(time.time())
    digest = hashlib.sha1(f"{ts} {sapisid} {ORIGIN}".encode()).hexdigest()
    auth = f"SAPISIDHASH {ts}_{digest}"
    log(f"SAPISID {'있음' if sapisid else '없음'}, auth 생성")

    pgs = [p for p in ctx.pages if "studio.youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page()
    # studio 오리진 보장
    if "studio.youtube.com" not in pg.url:
        pg.goto(f"{ORIGIN}/video/{VID}/edit", wait_until="domcontentloaded"); time.sleep(3)

    res = pg.evaluate("""async ([url, body, auth]) => {
        try {
            const r = await fetch(url, {method:'POST', headers:{'authorization':auth,'content-type':'application/json','x-origin':'https://studio.youtube.com','x-goog-authuser':'0'}, credentials:'include', body: JSON.stringify(body)});
            const t = await r.text();
            return {status:r.status, body:t};
        } catch(e) { return {status:-1, body:String(e)}; }
    }""", [ENDPOINT, payload, auth])

    log(f"HTTP {res['status']}")
    bd = res["body"]
    try:
        j = json.loads(bd)
        log("응답 keys: " + str(list(j.keys())))
        if "error" in j:
            log("ERROR: " + json.dumps(j["error"], ensure_ascii=False)[:600])
        else:
            log("성공 추정. 응답(앞 800): " + bd[:800])
    except Exception:
        log("응답(앞 600): " + bd[:600])
    ctx.close()
print("DONE")
