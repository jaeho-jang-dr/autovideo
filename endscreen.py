# -*- coding: utf-8 -*-
"""최종화면 자동 추가 ('동영상 1개, 구독 1개' 템플릿 → 시청자맞춤+구독 → 저장). 사용: python endscreen.py <VID>"""
import sys, time
from playwright.sync_api import sync_playwright
VID = sys.argv[1]
def log(m): print(m, flush=True)
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(12000)
    posts = []
    pg.on("request", lambda r: posts.append(r.url) if "youtubei" in r.url else None)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); time.sleep(6)
    # 엔딩 화면 열기
    opened = False
    for sel in ("#endscreens-button", "#endscreen-edit-button"):
        try:
            e = pg.locator(sel).first
            if e.count() and e.is_visible(timeout=1200): e.click(); opened = True; break
        except Exception: pass
    if not opened:
        try: pg.get_by_text("엔딩 화면", exact=True).first.click(); opened = True
        except Exception: pass
    time.sleep(5)
    # 템플릿 '동영상 1개, 구독 1개' 카드 클릭
    tpl = False
    try:
        lbl = pg.get_by_text("동영상 1개, 구독 1개", exact=False).first
        card = lbl.locator("xpath=ancestor::*[@role='button' or contains(@class,'template')][1]")
        if card.count(): card.first.click(); tpl = True
        else: lbl.click(); tpl = True
    except Exception as e: log("템플릿 실패 " + str(e)[:40])
    time.sleep(3)
    # 저장 — ★JS 클릭(actionability 우회) + edit_video POST 검증
    time.sleep(2)
    cands = []
    for loc in (pg.locator("#save-button"), pg.locator("ytcp-button#save-button"),
                pg.get_by_role("button", name="저장"), pg.get_by_text("저장", exact=True)):
        for i in range(loc.count()):
            try:
                bb = loc.nth(i).bounding_box(); en = loc.nth(i).is_enabled()
                if bb and en: cands.append((loc.nth(i), bb))
            except Exception: pass
    cands.sort(key=lambda t: -t[1]["x"])
    log(f"저장후보(활성) {len(cands)}개 x={[round(b['x']) for _,b in cands]}")
    for el, bb in cands:
        try:
            el.evaluate("e => e.click()"); log(f"  JS저장클릭 @{round(bb['x'])},{round(bb['y'])}")
            time.sleep(3)
            if any("edit_video" in p for p in posts): break
        except Exception as e: log("  JS클릭실패 " + str(e)[:24])
    time.sleep(6)
    ev = any("edit_video" in p for p in posts)
    log(f"=== {VID}: 템플릿={tpl} 저장={'OK(edit_video)' if ev else 'MISS'} ===")
print("DONE")
