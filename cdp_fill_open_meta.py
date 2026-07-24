# -*- coding: utf-8 -*-
"""이미 열린 제목·설명 번역 다이얼로그에 채우고 게시(navigate 안 함).
사용: python cdp_fill_open_meta.py <title.txt> <desc.txt>"""
import time, sys
from playwright.sync_api import sync_playwright
TITLE = open(sys.argv[1], encoding="utf-8").read().strip()
DESC = open(sys.argv[2], encoding="utf-8").read().strip()
def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii","ignore").decode(), flush=True)
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]; pg = pgs[-1]; pg.set_default_timeout(12000)
    els = pg.evaluate("""() => { const out=[]; document.querySelectorAll('div[contenteditable=true], textarea, [role=textbox], ytcp-social-suggestions-textbox #textbox').forEach(e=>{ const r=e.getBoundingClientRect(); if(e.offsetParent!==null && r.width>120 && r.x>700 && r.height>20) out.push({x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)}); }); return out; }""")
    log("우측 편집칸: " + str(els))
    els = sorted(els, key=lambda d: d["y"])
    filled = 0
    for i, (val, label) in enumerate([(TITLE, "제목"), (DESC, "설명")]):
        if i < len(els) and val:
            e = els[i]
            pg.mouse.click(e["x"] + e["w"] // 2, e["y"] + min(e["h"] // 2, 25)); time.sleep(0.4)
            try: pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); time.sleep(0.2)
            except Exception: pass
            pg.keyboard.type(val[:4800], delay=1); filled += 1; log(f"{label} 입력({len(val)}자)"); time.sleep(0.6)
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
    try: pg.screenshot(path="scratch/yt/en_zh_meta_done.png")
    except Exception: pass
    log(f"RESULT filled={filled} publish={pub}")
    ctx.close()
print("DONE")
