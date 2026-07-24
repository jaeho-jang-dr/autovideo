# -*- coding: utf-8 -*-
"""다국어 제목/설명 번역 추가(tx_add_ko_meta의 다국어판): /translations → <행텍스트> '제목 및 설명' 셀 클릭 → 입력 → 게시.
사용: python tx_meta.py <VID> "<행텍스트>" "<제목>" <설명파일>
  예: python tx_meta.py Qlr6VRthasw "일본어" "..." w9pkg/ko_ja_desc.txt"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
LANG = sys.argv[2]                       # 행 텍스트(예: 영어 / 일본어 / 중국어(간체) / 스페인어 / 한국어)
TITLE = sys.argv[3]
DESC = open(sys.argv[4], encoding="utf-8").read()
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)
def shot(pg, n):
    try: pg.screenshot(path=os.path.join(SH, n))
    except Exception: pass

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222")   # 로그인된 디버그 크롬 재사용(프로필 충돌 회피)
    ctx = b.contexts[0]
    pg = ctx.new_page(); pg.set_default_timeout(40000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded"); pg.wait_for_timeout(9000)
    # <LANG> 행 Y + '제목 및 설명' 열 X 로 셀 클릭
    try:
        en = pg.get_by_text(LANG, exact=True).first
        eb = en.bounding_box()
        rowy = eb["y"] + eb["height"]/2
        hx = None
        for h in pg.get_by_text("제목 및 설명", exact=True).all():
            b = h.bounding_box()
            if b: hx = b["x"] + b["width"]/2; break
        if hx is None: hx = eb["x"] + 1400
        log(f"{LANG} 제목·설명 셀 클릭 ({round(hx)},{round(rowy)})")
        pg.mouse.click(round(hx), round(rowy)); pg.wait_for_timeout(5000)
    except Exception as e:
        log("셀 클릭 실패 " + str(e)[:70]); shot(pg, "txm_fail.png"); pg.close(); sys.exit(1)
    log("URL:" + pg.url)
    # 편집 가능한(오른쪽 번역칸) textarea 2개: 상단=제목, 하단=설명
    def fill_translation():
        ft = fd = False
        tas = pg.locator("textarea"); editable = []
        for i in range(tas.count()):
            el = tas.nth(i)
            try:
                if el.is_visible() and el.is_editable():
                    bb = el.bounding_box()
                    if bb: editable.append((bb["y"], el))
            except Exception: pass
        editable.sort(key=lambda x: x[0])
        log(f"편집가능 textarea: {len(editable)}")
        if len(editable) >= 2:
            try:
                editable[0][1].click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(200)
                editable[0][1].type(TITLE, delay=5); ft = True; log("제목 입력")
            except Exception as e: log("제목 실패 " + str(e)[:50])
            try:
                editable[1][1].click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(200)
                editable[1][1].type(DESC, delay=1); fd = True; log("설명 입력")
            except Exception as e: log("설명 실패 " + str(e)[:50])
        return ft, fd
    ft, fd = fill_translation()
    pg.wait_for_timeout(1000); shot(pg, "txm_filled.png")
    # 게시
    pub = False
    for t in ["게시", "저장", "PUBLISH"]:
        try:
            b = pg.get_by_role("button", name=t).first
            if b.is_visible(timeout=2500) and b.is_enabled(): b.click(); pub = True; log(f"'{t}' 클릭"); break
        except Exception: pass
    if not pub:
        for sel in ["#publish-button", "ytcp-button:has-text('게시')", "ytcp-button:has-text('저장')"]:
            try: pg.locator(sel).first.click(timeout=3000, force=True); pub = True; break
            except Exception: pass
    pg.wait_for_timeout(5000); shot(pg, "txm_pub.png")
    log(f"=== {LANG}: 제목={ft} 설명={fd} 게시={'OK' if pub else 'NO'} ===")
    pg.wait_for_timeout(1500); pg.close()
print("END")
