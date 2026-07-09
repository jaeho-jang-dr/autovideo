# -*- coding: utf-8 -*-
"""안정적 자막 업로드+게시 v2 — input set → 형식다이얼로그 대기·처리 → 로드 대기 → 게시 활성화 대기 → 검증.
사용: python cap_robust.py <VID> <UI언어명> <srt>"""
import sys, os, time
from playwright.sync_api import sync_playwright
VID, LANG, SRT = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3])
ADD = (len(sys.argv) > 4 and sys.argv[4] == "1")  # 언어행 없으면 1
def log(m): print(m, flush=True)
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pg = [p for p in ctx.pages if "youtube.com" in p.url][-1]; pg.set_default_timeout(15000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded"); time.sleep(6)
    # 필요 시 언어 추가 (검색 방식)
    if ADD:
        try:
            pg.get_by_text("언어 추가", exact=True).first.click(); time.sleep(1.5)
            for ph in ("언어 검색", "검색"):
                try: pg.get_by_placeholder(ph).fill(LANG, timeout=2000); break
                except Exception: pass
            time.sleep(1)
            pg.get_by_text(LANG, exact=True).first.click(); log("언어추가 " + LANG); time.sleep(2.5)
        except Exception as e: log("언어추가 실패/이미있음 " + str(e)[:40])
    # 자막 셀 클릭
    lb = pg.get_by_text(LANG, exact=True).first.bounding_box()
    hx = None
    for h in pg.get_by_text("자막", exact=True).all():
        bb = h.bounding_box()
        if bb and bb["x"] > 400: hx = bb["x"] + bb["width"] / 2; break
    pg.mouse.click(hx, lb["y"] + lb["height"] / 2); time.sleep(4)
    # '파일 업로드' 클릭(파일선택기 시도) → 실패시 #captions-file-loader 직접 set (cap_clean 검증방식)
    loaded = False
    try:
        with pg.expect_file_chooser(timeout=7000) as fc:
            pg.get_by_text("파일 업로드", exact=True).first.click()
        fc.value.set_files(SRT); log("파일선택기 set"); loaded = True
    except Exception:
        try:
            pg.locator("#captions-file-loader").last.set_input_files(SRT); log("숨김input set"); loaded = True
        except Exception as e: log("파일 set 실패 " + str(e)[:40])
    # 형식 다이얼로그("업로드할 자막 파일 형식 선택") 뜰 때까지 대기 → 오류허용 + 계속 (여러 셀렉터)
    cont = False
    for _ in range(15):
        dlg = False
        for probe in ("업로드할 자막 파일 형식", "타이밍 포함"):
            try:
                if pg.get_by_text(probe, exact=False).first.is_visible(timeout=600): dlg = True; break
            except Exception: pass
        if dlg:
            try:
                cb = pg.get_by_text("오류를 허용하고 계속 진행", exact=False).first
                if cb.is_visible(timeout=500): cb.click(); log("오류허용"); time.sleep(0.4)
            except Exception: pass
            for getc in (lambda: pg.locator("#confirm-button").first,
                         lambda: pg.get_by_role("button", name="계속").first,
                         lambda: pg.locator("ytcp-button:has-text('계속')").first,
                         lambda: pg.get_by_text("계속", exact=True).first):
                try:
                    c = getc()
                    if c.is_visible(timeout=700): c.click(); log("계속"); cont = True; break
                except Exception: pass
            if cont: break
        time.sleep(1)
    if not cont: log("형식다이얼로그 처리 안됨")
    # 자막 로드 대기(자막 텍스트 행 or '텍스트로 편집' 나타날 때까지, 최대 12초)
    for _ in range(12):
        try:
            if pg.get_by_text("텍스트로 편집", exact=False).first.is_visible(timeout=1000): break
        except Exception: pass
        time.sleep(1)
    time.sleep(2)
    # 게시 버튼 활성화 대기 후 클릭(최대 15초)
    pub = False
    for _ in range(15):
        for getb in (lambda: pg.get_by_role("button", name="게시").first,
                     lambda: pg.locator("ytcp-button:has-text('게시')").first):
            try:
                btn = getb()
                if btn.is_visible(timeout=800) and btn.is_enabled():
                    btn.click(timeout=3000); log("게시 클릭"); pub = True; break
            except Exception: pass
        if pub: break
        time.sleep(1)
    time.sleep(6)
    # 검증: 편집기 닫히고 그 언어행 자막='게시됨' 인지
    ok = False
    try:
        time.sleep(2)
        row_txt = ""
        rows = pg.locator("tr, ytcp-video-row").filter(has_text=LANG)
        # 간단 검증: 페이지에 그 언어 옆 '게시됨' 있는지는 배치 후 별도 verify로. 여기선 게시 클릭 여부만.
        ok = pub
    except Exception: pass
    log(f"=== {LANG}: 로드={loaded} 계속={cont} 게시={'OK' if pub else 'NO'} ===")
print("END")
