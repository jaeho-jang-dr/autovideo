# -*- coding: utf-8 -*-
"""카드 편집기 UI 정찰: 동영상 카드 추가 버튼·비디오 피커·시간 필드 확인."""
import time, sys
from playwright.sync_api import sync_playwright
VID = sys.argv[1] if len(sys.argv) > 1 else "YTex0QGe17o"
def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii","ignore").decode(), flush=True)
def shot(pg, n):
    try: pg.screenshot(path=f"scratch/yt/{n}.png", timeout=6000)
    except Exception: pass
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(12000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); time.sleep(6)
    for sel in ("#cards-button", "#card-edit-button", "#info-cards-button"):
        try:
            e = pg.locator(sel).first
            if e.count() and e.is_visible(timeout=1200): e.click(); log("카드편집 열림 "+sel); break
        except Exception: pass
    time.sleep(4); shot(pg, "recon_cards_1")
    # 카드 추가 메뉴 텍스트/버튼 덤프
    d = pg.evaluate("""() => {
        const out=[];
        document.querySelectorAll('*').forEach(e=>{ if(e.children.length===0){ const t=(e.textContent||'').trim(); if(['동영상','재생목록','채널','링크','카드','카드 추가','카드추가'].includes(t)){ const r=e.getBoundingClientRect(); if(e.offsetParent!==null&&r.width>0) out.push(t+'@('+Math.round(r.x)+','+Math.round(r.y)+')'); } } });
        return out;
    }""")
    log("메뉴 항목: " + str(d))
    # 시간/타임코드 관련 입력 필드
    tf = pg.evaluate("""() => {
        const out=[];
        document.querySelectorAll('input, [contenteditable=true]').forEach(e=>{ const r=e.getBoundingClientRect(); if(e.offsetParent!==null&&r.width>0){ out.push((e.getAttribute('aria-label')||e.getAttribute('placeholder')||e.type||'?')+'@('+Math.round(r.x)+','+Math.round(r.y)+')'); } });
        return out;
    }""")
    log("입력 필드: " + str(tf))
    ctx.close()
print("DONE")
