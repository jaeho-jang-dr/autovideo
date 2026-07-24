# -*- coding: utf-8 -*-
"""중국어 제목·설명 채우고 게시(CDP). 핵심: 새 중국어는 '동영상 언어'가 있던 자리에 생김
   → add 전 그 Y 기억 → add → 그 자리 클릭 → 제목/설명(우측) 채움 → 게시(persist).
사용: python cdp_zh_meta.py <VID> <title.txt> <desc.txt>"""
import time, sys
from playwright.sync_api import sync_playwright
VID = sys.argv[1]; TITLE = open(sys.argv[2], encoding="utf-8").read().strip(); DESC = open(sys.argv[3], encoding="utf-8").read().strip()
def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii","ignore").decode(), flush=True)

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(15000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded"); time.sleep(7)

    # ① add 전: '동영상 언어' 행 Y(=중국어가 생길 자리) + 제목설명 컬럼 X
    pre = pg.evaluate("""() => {
        function anchorY(){ for(const e of document.querySelectorAll('*')){ if(e.children.length===0 && (e.textContent||'').includes('동영상 언어') && e.offsetParent!==null) return e.getBoundingClientRect().y+e.getBoundingClientRect().height/2; } return null; }
        function hdrX(t){ for(const e of document.querySelectorAll('*')){ if(e.children.length===0 && (e.textContent||'').trim()===t && e.offsetParent!==null){ const r=e.getBoundingClientRect(); if(r.x>300) return Math.round(r.x+r.width/2); } } return null; }
        function has(t){ for(const e of document.querySelectorAll('*')){ if(e.children.length===0 && (e.textContent||'').trim()===t && e.offsetParent!==null){ const r=e.getBoundingClientRect(); if(r.x<560&&r.y>150) return true; } } return false; }
        return {anchorY: anchorY(), metaX: hdrX('제목 및 설명'), zhExists: has('중국어')||has('중국어(중국)')};
    }""")
    log("pre: " + str(pre))
    targetY = round(pre["anchorY"]); metaX = pre["metaX"] or 1487

    if not pre["zhExists"]:
        try: pg.get_by_text("언어 추가", exact=False).first.click(timeout=5000); log("언어추가")
        except Exception: pass
        time.sleep(1.8)
        pg.evaluate("""() => { for(const e of document.querySelectorAll('*')){ if(e.children.length===0 && (e.textContent||'').trim()==='중국어(중국)'){ let n=e; for(let i=0;i<6&&n;i++){ if(n.matches&&n.matches('tp-yt-paper-item,[role=option],ytcp-menu-item,li,ytcp-text-menu-item')) break; n=n.parentElement; } (n||e).scrollIntoView({block:'center'}); (n||e).click(); return; } } }""")
        time.sleep(2)
    # ★ 앵커 아니라 실제 중국어 행 Y를 찾는다(동영상언어가 중간일 수 있음 — 영어판)
    y = pg.evaluate("""() => { for(const e of document.querySelectorAll('*')){ const t=(e.textContent||'').trim(); if(e.children.length===0 && (t==='중국어'||t==='중국어(중국)') && e.offsetParent!==null){ const r=e.getBoundingClientRect(); if(r.x<560&&r.y>150&&r.y<950) return Math.round(r.y+r.height/2); } } return null; }""")
    if y is not None: targetY = y
    log("중국어 실제 행 Y=" + str(y))

    log(f"제목설명칸 클릭 ({metaX},{targetY})")
    pg.mouse.click(metaX, targetY); time.sleep(3)
    try: pg.wait_for_load_state("networkidle", timeout=8000)
    except Exception: pass
    time.sleep(2)
    try: pg.screenshot(path="scratch/yt/zh_meta_ed.png", timeout=8000)
    except Exception: pass

    # ② 우측(번역) 편집 박스: x>1000, y순 → 위=제목, 아래=설명
    handles = []
    for sel in ["div[contenteditable=true]", "textarea", "#textbox"]:
        for e in pg.locator(sel).all():
            try:
                if e.is_visible():
                    bb = e.bounding_box()
                    if bb and bb["x"] > 950: handles.append((bb["y"], e))
            except Exception: pass
    handles.sort(key=lambda t: t[0])
    log(f"우측 편집박스 {len(handles)}개 (y={[round(h[0]) for h in handles]})")
    filled = 0
    for i, (val, label) in enumerate([(TITLE, "제목"), (DESC, "설명")]):
        if i < len(handles) and val:
            try:
                _, box = handles[i]; box.click(); time.sleep(0.4)
                pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); time.sleep(0.2)
                pg.keyboard.type(val[:4800], delay=1); filled += 1; log(f"{label} 입력({len(val)}자)"); time.sleep(0.5)
            except Exception as e: log(f"{label} 실패 " + str(e)[:40])

    # ③ 게시
    pub = False
    for t in ["게시", "저장", "PUBLISH"]:
        try:
            btns = pg.get_by_role("button", name=t)
            for i in range(btns.count()):
                bt = btns.nth(i)
                if bt.is_visible() and bt.is_enabled(): bt.click(); pub = True; log(f"'{t}' 클릭"); break
            if pub: break
        except Exception: pass
    time.sleep(4)
    try: pg.screenshot(path="scratch/yt/zh_meta_done.png")
    except Exception: pass
    log(f"RESULT filled={filled} publish={pub}")
    ctx.close()
print("DONE")
