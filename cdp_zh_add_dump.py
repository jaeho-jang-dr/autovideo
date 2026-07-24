# -*- coding: utf-8 -*-
"""중국어 add 직후 행/셀 좌표 덤프(CDP). add하고 그 자리를 기록 → 다음엔 그 좌표 클릭."""
import time, sys
from playwright.sync_api import sync_playwright
VID = sys.argv[1] if len(sys.argv) > 1 else "YTex0QGe17o"
def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii","ignore").decode(), flush=True)
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(15000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded"); time.sleep(7)
    try: pg.get_by_text("언어 추가", exact=False).first.click(timeout=5000); log("언어추가 클릭")
    except Exception as e: log("언어추가 실패 " + str(e)[:40])
    time.sleep(2)
    try:
        sb = pg.get_by_placeholder("언어 검색"); sb.click(); sb.type("중국어", delay=80); time.sleep(1.6); log("검색 입력")
    except Exception as e: log("검색 실패 " + str(e)[:40])
    pg.screenshot(path="scratch/yt/zh_dd.png"); log("shot zh_dd")
    ok = pg.evaluate("""() => {
        for(const e of document.querySelectorAll('*')){
            if(e.children.length===0 && (e.textContent||'').trim()==='중국어(중국)'){
                let n=e; for(let i=0;i<6&&n;i++){ if(n.matches&&n.matches('tp-yt-paper-item,[role=option],ytcp-menu-item,li,ytcp-text-menu-item')) break; n=n.parentElement; }
                (n||e).scrollIntoView({block:'center'}); (n||e).click(); return true;
            }
        }
        return false;
    }""")
    log("중국어(중국) 클릭: " + str(ok)); time.sleep(3)
    pg.screenshot(path="scratch/yt/zh_added.png"); log("shot zh_added")
    dump = pg.evaluate("""() => {
        function cx(txt,minx){ for(const e of document.querySelectorAll('*')){ if(e.children.length===0 && (e.textContent||'').trim()===txt && e.offsetParent!==null){ const r=e.getBoundingClientRect(); if(r.x>minx) return Math.round(r.x+r.width/2); } } return null; }
        let rowY=null;
        for(const e of document.querySelectorAll('*')){ if(e.children.length===0 && (e.textContent||'').trim()==='중국어' && e.offsetParent!==null){ const r=e.getBoundingClientRect(); if(r.x<560 && r.y>150 && r.y<950){ rowY=Math.round(r.y+r.height/2); break; } } }
        return {rowY, jamak:cx('자막',300), meta:cx('제목 및 설명',300), vw:window.innerWidth, vh:window.innerHeight};
    }""")
    log("덤프: " + str(dump))
    ctx.close()
print("DONE")
