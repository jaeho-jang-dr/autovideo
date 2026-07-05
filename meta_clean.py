# -*- coding: utf-8 -*-
"""제목·설명 번역 입력 (CDP판) — 살아있는 크롬(9222)에 붙어 언어행 제목및설명 채우고 게시.
사용: python meta_clean.py <VIDEO_ID> <UI언어명> <DB언어코드>
  ex: python meta_clean.py JohmMBxizkg 영어 en"""
import sys, os, sqlite3
from playwright.sync_api import sync_playwright

VID=sys.argv[1]; UILANG=sys.argv[2]; DBLANG=sys.argv[3]
def log(m): print(m, flush=True)

c=sqlite3.connect("channel/content.db"); cur=c.cursor()
row=cur.execute("SELECT title,description FROM video_localizations WHERE video_id=? AND lang=?",(VID,DBLANG)).fetchone()
c.close()
if not row: log("DB에 번역 없음: "+DBLANG); sys.exit(1)
TITLE, DESC = row

with sync_playwright() as pw:
    b=pw.chromium.connect_over_cdp("http://localhost:9222")
    ctx=b.contexts[0]; pg=None
    for p in ctx.pages:
        if "studio.youtube.com" in p.url: pg=p
    if pg is None: pg=ctx.pages[-1]
    pg.set_default_timeout(15000)
    os.makedirs("scratch/yt",exist_ok=True)
    def shot(n):
        try: pg.screenshot(path=f"scratch/yt/mf_{DBLANG}_{n}.png")
        except Exception: pass

    # translations 페이지 보장
    if "/translations" not in pg.url:
        pg.goto(f"https://studio.youtube.com/video/{VID}/translations",wait_until="domcontentloaded"); pg.wait_for_timeout(7000)

    # 언어행 × 제목및설명 셀
    lb=pg.get_by_text(UILANG, exact=True).first.bounding_box()
    if not lb: log("언어행 못찾음:"+UILANG); shot("norow"); sys.exit(1)
    hx=None
    for h in pg.get_by_text("제목 및 설명", exact=True).all():
        bb=h.bounding_box()
        if bb: hx=bb["x"]+bb["width"]/2; break
    cy=lb["y"]+lb["height"]/2
    log(f"셀=({round(hx)},{round(cy)})")
    pg.mouse.click(hx,cy); pg.wait_for_timeout(5000); shot("01editor")

    ok_t=ok_d=False
    try:
        t=pg.locator('textarea[placeholder="제목*"]').first
        t.click(); t.fill(TITLE); ok_t=True; log("제목 입력")
    except Exception as e: log("제목 실패:"+str(e)[:50])
    try:
        descs=pg.locator('textarea[placeholder="설명"]')
        target=None
        for i in range(descs.count()):
            bb=descs.nth(i).bounding_box()
            if bb and bb["x"]>900: target=descs.nth(i); break
        if target is None: target=descs.last
        target.click(); target.fill(DESC); ok_d=True; log("설명 입력")
    except Exception as e: log("설명 실패:"+str(e)[:50])
    pg.wait_for_timeout(1000); shot("02filled")

    pub=False
    for t in ["게시","저장"]:
        try:
            btn=pg.get_by_text(t, exact=True).first
            if btn.is_visible(timeout=2500): btn.click(); pub=True; log("'"+t+"' 클릭"); break
        except Exception: pass
    pg.wait_for_timeout(5000); shot("03done")
    log(f"=== {UILANG}: 제목={ok_t} 설명={ok_d} 게시={'OK' if pub else 'NO'} ===")
print("DONE")
