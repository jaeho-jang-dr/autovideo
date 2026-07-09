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
    # 저장
    saved = False
    for sel in ("#save-button", "ytcp-button#save-button"):
        try:
            s = pg.locator(sel).first
            if s.is_visible(timeout=2000) and s.is_enabled(): s.click(); saved = True; break
        except Exception: pass
    time.sleep(4)
    log(f"=== {VID}: 템플릿={tpl} 저장={'OK' if saved else 'NO(이미있음/변경없음)'} ===")
print("DONE")
