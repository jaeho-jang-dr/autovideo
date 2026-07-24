# -*- coding: utf-8 -*-
"""중국어 자막 업로드(CDP). 행은 메타 게시로 persist됨 → 자막칸(jamakX,rowY) 클릭 → 파일업로드 → 게시.
사용: python cdp_zh_sub.py <VID> <zh.srt>"""
import time, sys, os
from playwright.sync_api import sync_playwright
VID = sys.argv[1]; SRT = os.path.abspath(sys.argv[2])
def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii","ignore").decode(), flush=True)

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(15000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded"); time.sleep(7)

    def info():
        return pg.evaluate("""() => {
            let rowY=null;
            for(const e of document.querySelectorAll('*')){ const t=(e.textContent||'').trim(); if(e.children.length===0 && (t==='중국어'||t==='중국어(중국)') && e.offsetParent!==null){ const r=e.getBoundingClientRect(); if(r.x<560&&r.y>150&&r.y<950){ rowY=Math.round(r.y+r.height/2); break; } } }
            let jx=null; for(const e of document.querySelectorAll('*')){ if(e.children.length===0 && (e.textContent||'').trim()==='자막' && e.offsetParent!==null){ const r=e.getBoundingClientRect(); if(r.x>300){ jx=Math.round(r.x+r.width/2); break; } } }
            return {rowY, jamakX:jx};
        }""")
    c = info(); log("info: " + str(c))
    if c["rowY"] is None:  # 혹시 사라졌으면 재추가(사용자 방법)
        try: pg.get_by_text("언어 추가", exact=False).first.click(timeout=5000)
        except Exception: pass
        time.sleep(1.8)
        pg.evaluate("""() => { for(const e of document.querySelectorAll('*')){ if(e.children.length===0 && (e.textContent||'').trim()==='중국어(중국)'){ let n=e; for(let i=0;i<6&&n;i++){ if(n.matches&&n.matches('tp-yt-paper-item,[role=option],ytcp-menu-item,li,ytcp-text-menu-item')) break; n=n.parentElement; } (n||e).scrollIntoView({block:'center'}); (n||e).click(); return; } } }""")
        time.sleep(2); c = info()
    rowY, jamakX = c["rowY"], c["jamakX"] or 875
    if rowY is None:
        pg.screenshot(path="scratch/yt/zh_sub_norow.png"); log("행 없음"); ctx.close(); raise SystemExit

    log(f"자막칸 클릭 ({jamakX},{rowY})")
    pg.mouse.click(jamakX, rowY); time.sleep(3)
    try: pg.wait_for_load_state("networkidle", timeout=8000)
    except Exception: pass
    time.sleep(2); log("URL: " + pg.url)
    try: pg.screenshot(path="scratch/yt/zh_sub_ed.png", timeout=8000); log("shot ed")
    except Exception as e: log("shot skip " + str(e)[:40])

    def try_upload():
        try:
            with pg.expect_file_chooser(timeout=6000) as fc:
                for t in ["파일 업로드", "업로드", "Upload file"]:
                    try: pg.get_by_text(t, exact=False).first.click(timeout=2500); log("클릭 " + t); break
                    except Exception: pass
            fc.value.set_files(SRT); log("파일 지정(직접)"); return True
        except Exception: pass
        try:
            for t in ["시간 코드 포함", "시간 코드가 포함", "타임코드 포함"]:
                try: pg.get_by_text(t, exact=False).first.click(timeout=2500); log("시간코드포함"); break
                except Exception: pass
            time.sleep(0.6)
            with pg.expect_file_chooser(timeout=6000) as fc2:
                for t in ["계속", "파일 선택", "업로드", "Continue"]:
                    try: pg.get_by_text(t, exact=False).first.click(timeout=2500); log("클릭 " + t); break
                    except Exception: pass
            fc2.value.set_files(SRT); log("파일 지정(2단계)"); return True
        except Exception as e: log("업로드 실패 " + str(e)[:60]); return False
    ok = try_upload(); time.sleep(4)
    try: pg.screenshot(path="scratch/yt/zh_sub_up.png")
    except Exception: pass

    pub = False
    for t in ["게시", "저장", "완료", "PUBLISH"]:
        try:
            btns = pg.get_by_role("button", name=t)
            for i in range(btns.count()):
                bt = btns.nth(i)
                if bt.is_visible() and bt.is_enabled(): bt.click(); pub = True; log(f"'{t}' 클릭"); break
            if pub: break
        except Exception: pass
    time.sleep(4)
    try: pg.screenshot(path="scratch/yt/zh_sub_done.png")
    except Exception: pass
    log(f"RESULT upload={ok} publish={pub}")
    ctx.close()
print("DONE")
