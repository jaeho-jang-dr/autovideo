# -*- coding: utf-8 -*-
"""언어행 제목및설명 편집기 열고 번역 제목·설명 입력 → 게시. (한국어 넣은 방식과 동일)
사용: python yt_meta_fill.py <VIDEO_ID> <UI언어명> <DB언어코드>"""
import sys, os, sqlite3
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID=sys.argv[1]; UILANG=sys.argv[2]; DBLANG=sys.argv[3]
def log(m): print(m, flush=True)

c=sqlite3.connect("channel/content.db"); cur=c.cursor()
row=cur.execute("SELECT title,description FROM video_localizations WHERE video_id=? AND lang=?",(VID,DBLANG)).fetchone()
c.close()
if not row: log("DB에 번역 없음: "+DBLANG); sys.exit(1)
TITLE, DESC = row

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, accept_downloads=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    os.makedirs("scratch/yt",exist_ok=True)
    def shot(n):
        try: pg.screenshot(path=f"scratch/yt/mf_{DBLANG}_{n}.png")
        except Exception: pass

    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    # 언어행 제목및설명 셀 좌표
    lb = pg.get_by_text(UILANG, exact=True).first.bounding_box()
    if not lb: log("언어행 못찾음:"+UILANG); ctx.close(); sys.exit(1)
    hx=None
    for h in pg.get_by_text("제목 및 설명", exact=True).all():
        b=h.bounding_box()
        if b: hx=b["x"]+b["width"]/2; break
    cy=lb["y"]+lb["height"]/2
    log(f"셀=({round(hx)},{round(cy)})")
    pg.mouse.move(hx,cy); pg.wait_for_timeout(1000)
    pg.mouse.click(hx,cy); pg.wait_for_timeout(5000); shot("01editor")

    # 제목(제목*) + 설명(오른쪽) 입력
    ok_t=ok_d=False
    try:
        t=pg.locator('textarea[placeholder="제목*"]').first
        t.click(); t.fill(TITLE); ok_t=True; log("제목 입력")
    except Exception as e: log("제목 실패:"+str(e)[:50])
    try:
        # 설명 textarea 중 오른쪽(x>900) = 번역칸
        descs=pg.locator('textarea[placeholder="설명"]')
        target=None
        for i in range(descs.count()):
            b=descs.nth(i).bounding_box()
            if b and b["x"]>900: target=descs.nth(i); break
        if target is None: target=descs.last
        target.click(); target.fill(DESC); ok_d=True; log("설명 입력")
    except Exception as e: log("설명 실패:"+str(e)[:50])
    pg.wait_for_timeout(1000); shot("02filled")

    # 게시
    pub=False
    for t in ["게시","저장"]:
        try:
            b=pg.get_by_text(t, exact=True).first
            if b.is_visible(timeout=2500): b.click(); pub=True; log("'"+t+"' 클릭"); break
        except Exception: pass
    pg.wait_for_timeout(5000); shot("03done")
    log(f"=== {UILANG}: 제목={ok_t} 설명={ok_d} 게시={'✅' if pub else '❌'} ===")
    pg.wait_for_timeout(1000); ctx.close()
log("DONE")
