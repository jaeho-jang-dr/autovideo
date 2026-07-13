# -*- coding: utf-8 -*-
"""카드 자동 추가 (재생목록 카드). 사용: python card.py <VID> <재생목록명>"""
import sys, time
from playwright.sync_api import sync_playwright
VID = sys.argv[1]; PL = sys.argv[2]
def log(m): print(m, flush=True)
def shot(pg, name):
    try: pg.screenshot(path=f"scratch/yt/{name}.png", timeout=6000)
    except Exception: pass
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(12000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); time.sleep(6)
    # 카드 열기
    opened = False
    for sel in ("#cards-button", "#card-edit-button", "#info-cards-button"):
        try:
            e = pg.locator(sel).first
            if e.count() and e.is_visible(timeout=1200): e.click(); opened = True; break
        except Exception: pass
    if not opened:
        try: pg.get_by_text("카드", exact=True).first.click(); opened = True
        except Exception: pass
    time.sleep(5); shot(pg, f"card_{VID}_1")
    added = False
    # 모달 안(y<500)의 '재생목록' 행 [+] 클릭 (배경 요소 회피)
    try:
        target = None
        for el in pg.get_by_text("재생목록", exact=True).all():
            bb = el.bounding_box()
            if bb and bb["y"] < 500: target = el; break
        if target:
            tb = target.bounding_box(); cy = tb["y"] + tb["height"] / 2
            clicked = False
            btns = pg.locator("ytcp-icon-button, tp-yt-paper-icon-button")
            for i in range(btns.count()):
                bb = btns.nth(i).bounding_box()
                if bb and abs(bb["y"] + bb["height"] / 2 - cy) < 22 and bb["x"] > tb["x"] + tb["width"]:
                    btns.nth(i).click(); clicked = True; log("재생목록+ 클릭(모달y)"); break
            if not clicked:
                pg.mouse.click(tb["x"] + 460, cy); log("재생목록+ 좌표(모달)")
            time.sleep(2.5)
        else: log("모달 재생목록 못찾음")
    except Exception as e: log("재생목록+ 실패 " + str(e)[:40])
    shot(pg, f"card_{VID}_2")
    # '특정 재생목록 선택': 검색 금지(전체 유튜브라 다른 채널 나옴). 상단 내 재생목록 카드 직접 클릭
    try:
        time.sleep(1.5)
        for el in pg.get_by_text(PL, exact=False).all():
            bb = el.bounding_box()
            if bb and bb["y"] < 520:  # 다이얼로그 그리드 상단 (배경/타채널 회피)
                el.click(); added = True; log("내 재생목록 카드 클릭"); time.sleep(2.5); break
        if not added: log("내 재생목록 카드 못찾음")
    except Exception as e: log("선택 실패 " + str(e)[:40])
    shot(pg, f"card_{VID}_3")
    # 저장
    saved = False
    for sel in ("#save-button", "ytcp-button#save-button"):
        try:
            s = pg.locator(sel).first
            if s.is_visible(timeout=1500) and s.is_enabled(): s.click(); saved = True; break
        except Exception: pass
    time.sleep(4)
    log(f"=== {VID}: 카드추가={added} 저장={'OK' if saved else 'NO'} ===")
print("DONE")
