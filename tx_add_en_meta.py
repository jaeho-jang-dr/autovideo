# -*- coding: utf-8 -*-
"""영어 제목/설명 번역 추가: /translations → 영어행 '제목 및 설명' 셀 클릭 → 입력 → 게시.
사용: python tx_add_en_meta.py <VID>"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
CG = "D:/Entertainments/DevEnvironment/autovideo/child_growth_science"
EN_TITLE = "How Tall Will My Child Grow? | The Science of Child Growth & Height (A Must for Parents)"
EN_DESC = open(os.path.join(CG, "desc_main_en.txt"), encoding="utf-8").read()
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)
def shot(pg, n):
    try: pg.screenshot(path=os.path.join(SH, n)); log("shot " + n)
    except Exception as e: log("shot fail " + n + " " + str(e)[:50])

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
        no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(40000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded"); pg.wait_for_timeout(9000)

    # 영어 행 Y + '제목 및 설명' 열 X 로 셀 클릭
    try:
        en = pg.get_by_text("영어", exact=True).first
        eb = en.bounding_box()
        rowy = eb["y"] + eb["height"]/2
        # '제목 및 설명' 헤더 x
        hx = None
        for h in pg.get_by_text("제목 및 설명", exact=True).all():
            b = h.bounding_box()
            if b: hx = b["x"] + b["width"]/2; break
        if hx is None: hx = eb["x"] + 1400
        log(f"영어 제목·설명 셀 클릭 좌표=({round(hx)},{round(rowy)})")
        pg.mouse.click(round(hx), round(rowy)); pg.wait_for_timeout(5000)
    except Exception as e:
        log("셀 클릭 실패 " + str(e)[:70]); shot(pg, "tx_e0_fail.png"); ctx.close(); sys.exit(1)
    log("URL:" + pg.url); shot(pg, "tx_e1_editor.png")

    # 편집기 입력 구조 덤프
    for sel in ["#title-textarea #textbox", "#description-textarea #textbox",
                "ytgn-video-translation-section textarea", "textarea",
                "input[aria-label*='제목']", "div[contenteditable='true']"]:
        try: log(f"COUNT {sel}: {pg.locator(sel).count()}")
        except Exception: pass

    # 편집 가능한(오른쪽 번역칸) textarea 2개를 Y좌표 순으로: 상단=제목, 하단=설명
    def fill_translation():
        filled_t = filled_d = False
        tas = pg.locator("textarea")
        editable = []
        for i in range(tas.count()):
            el = tas.nth(i)
            try:
                if el.is_visible() and el.is_editable():
                    bb = el.bounding_box()
                    if bb: editable.append((bb["y"], el))
            except Exception: pass
        editable.sort(key=lambda x: x[0])
        log(f"편집가능 textarea 수: {len(editable)}")
        if len(editable) >= 2:
            title_el = editable[0][1]; desc_el = editable[1][1]
            try:
                title_el.click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(200)
                title_el.type(EN_TITLE, delay=6); filled_t = True; log("제목 입력(상단)")
            except Exception as e: log("제목 실패 " + str(e)[:50])
            try:
                desc_el.click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(200)
                desc_el.type(EN_DESC, delay=1); filled_d = True; log("설명 입력(하단)")
            except Exception as e: log("설명 실패 " + str(e)[:50])
        elif len(editable) == 1:
            log("편집칸 1개만 감지 — 구조 확인 필요")
        return filled_t, filled_d
    ft, fd = fill_translation()
    log(f"제목={ft} 설명={fd}")
    pg.wait_for_timeout(1000); shot(pg, "tx_e2_filled.png")

    # 게시
    pub = False
    for t in ["게시", "저장", "PUBLISH"]:
        try:
            b = pg.get_by_role("button", name=t).first
            if b.is_visible(timeout=2500) and b.is_enabled(): b.click(); pub = True; log(f"'{t}' 클릭"); break
        except Exception: pass
    if not pub:
        for sel in ["#publish-button", "ytcp-button:has-text('게시')", "ytcp-button:has-text('저장')"]:
            try: pg.locator(sel).first.click(timeout=3000, force=True); pub = True; log("게시(sel) " + sel); break
            except Exception: pass
    pg.wait_for_timeout(5000); shot(pg, "tx_e3_published.png")

    # 검증
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded"); pg.wait_for_timeout(7000)
    try:
        rows = pg.locator("tr, [class*='language-row']").all()
        for r in rows[:8]:
            t = r.inner_text()[:70].replace("\n", " | ")
            if "영어" in t: log("EN ROW: " + t)
    except Exception: pass
    shot(pg, "tx_e4_verify.png")
    log(f"EN_META_DONE title={ft} desc={fd} pub={pub}")
    pg.wait_for_timeout(2000); ctx.close()
print("END")
