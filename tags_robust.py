# -*- coding: utf-8 -*-
"""태그 설정 견고판 — /edit 열고 '자세히 보기' 펼쳐 태그칸 비우고 클립보드 붙여넣기 + 저장.
사용: python tags_robust.py <VIDEO_ID> <tags_txt_file>"""
import sys, os, time, re
from playwright.sync_api import sync_playwright
try:
    import pyperclip; HASCLIP = True
except Exception: HASCLIP = False
VID = sys.argv[1]; TAGS = open(sys.argv[2], encoding="utf-8").read().strip()
def log(m): print(m, flush=True)
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(15000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); time.sleep(7)
    # '자세히 보기' 펼치기
    for sel in ("ytcp-button#toggle-button", "#toggle-button", "ytcp-button:has-text('자세히 보기')"):
        try:
            btn = pg.locator(sel).first
            if btn.is_visible(timeout=2000): btn.click(); log("자세히 보기 펼침"); break
        except Exception: pass
    time.sleep(1.5)
    # 태그 입력 찾기
    ti = None
    for sel in ("#tags-container input", "input[aria-label*='태그']", "#text-input"):
        try:
            e = pg.locator(sel).first
            if e.is_visible(timeout=2000): ti = e; break
        except Exception: pass
    if ti is None: log("태그입력 못찾음"); pg.screenshot(path=f"scratch/yt/tags_{VID}_notfound.png"); sys.exit(1)
    # 전체 태그 삭제 버튼 클릭 (제일 확실) → 폴백 백스페이스
    cleared = False
    for al in ("모든 태그 삭제", "태그 모두 삭제", "모두 삭제"):
        try:
            btn = pg.get_by_label(al, exact=False).first
            if btn.count() and btn.is_visible(timeout=1500):
                btn.click(); log(f"전체삭제 {al}"); cleared = True; time.sleep(0.6); break
        except Exception: pass
    ti.scroll_into_view_if_needed(); ti.click(); time.sleep(0.3)
    if not cleared:
        for _ in range(3):
            pg.keyboard.press("Control+a"); pg.keyboard.press("Delete"); time.sleep(0.1)
        for i in range(150):
            pg.keyboard.press("Backspace"); time.sleep(0.012)
            if i % 30 == 29:
                try: ti.click()
                except Exception: pass
    time.sleep(0.4); pg.screenshot(path=f"scratch/yt/tags_{VID}_cleared.png")
    # 전체선택 후 붙여넣기(잔여 칩 있으면 대체) — 콤마로 칩 생성
    ti.click(); pg.keyboard.press("Control+a"); time.sleep(0.2)
    if HASCLIP:
        pyperclip.copy(TAGS + ","); pg.keyboard.press("Control+v")
    else:
        ti.type(TAGS + ",")
    time.sleep(1.2)
    pg.screenshot(path=f"scratch/yt/tags_{VID}.png")
    # 저장
    saved = False
    for sel in ("#save-button", "ytcp-button#save-button", "ytcp-button:has-text('저장')"):
        try:
            s = pg.locator(sel).first
            if s.is_visible(timeout=2000) and s.is_enabled(): s.click(); saved = True; log("저장 클릭"); break
        except Exception: pass
    time.sleep(4)
    log(f"=== {VID}: 붙여넣기=OK 저장={'OK' if saved else 'NO'} (clip={HASCLIP}) ===")
print("DONE")
