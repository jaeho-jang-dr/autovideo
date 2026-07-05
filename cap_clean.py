# -*- coding: utf-8 -*-
"""자막 업로드 클린 플로우 — 살아있는 크롬(CDP 9222)에 붙어 한 언어 자막 업로드.
   숨김 input 사전지정 금지. '파일 업로드'→파일선택기 가로채기→계속→게시.
사용: python cap_clean.py <lang_ui_name> <srt> [add:0|1]
  ex: python cap_clean.py "한국어 (동영상 언어)" hypnosis_science/hypnosis_science.ko.srt 0
      python cap_clean.py "영어" hypnosis_science/hypnosis_science.en.srt 1"""
import sys, os
from playwright.sync_api import sync_playwright

LANG=sys.argv[1]; SRT=os.path.abspath(sys.argv[2]); ADD=(len(sys.argv)>3 and sys.argv[3]=="1")
def log(m): print(m,flush=True)

with sync_playwright() as pw:
    b=pw.chromium.connect_over_cdp("http://localhost:9222")
    ctx=b.contexts[0]; pg=None
    for p in ctx.pages:
        if "studio.youtube.com" in p.url: pg=p
    if pg is None: pg=ctx.pages[-1]
    pg.set_default_timeout(15000)
    os.makedirs("scratch/yt",exist_ok=True)
    def shot(n):
        try: pg.screenshot(path=f"scratch/yt/clean_{n}.png")
        except Exception: pass

    # 0) 필요 시 언어 추가
    if ADD:
        try:
            pg.get_by_text("언어 추가",exact=True).first.click(); pg.wait_for_timeout(1500)
            pg.get_by_text(LANG,exact=True).last.click(); log(f"언어추가 {LANG}"); pg.wait_for_timeout(2500)
        except Exception as e: log("언어추가 실패 "+str(e)[:50])
        shot("0add")

    # 1) 자막 셀 클릭(언어행 × '자막' 열) → 편집기
    lb=pg.get_by_text(LANG,exact=True).first.bounding_box()
    if not lb: log("언어행 못찾음 "+LANG); shot("norow"); sys.exit(1)
    hx=None
    for h in pg.get_by_text("자막",exact=True).all():
        bb=h.bounding_box()
        if bb and bb["x"]>400: hx=bb["x"]+bb["width"]/2; break
    pg.mouse.click(hx, lb["y"]+lb["height"]/2); pg.wait_for_timeout(4000); shot("1editor")
    log("편집기 오픈")

    # 2) '파일 업로드' 클릭 → 파일선택기 가로채기 (사전지정 안 함이 핵심)
    try:
        with pg.expect_file_chooser(timeout=10000) as fc:
            pg.get_by_text("파일 업로드",exact=True).first.click()
        fc.value.set_files(SRT); log("파일선택기로 지정 "+os.path.basename(SRT))
    except Exception as e:
        log("파일선택기 실패, 숨김input 폴백 "+str(e)[:50])
        L=pg.locator("#captions-file-loader")
        try: L.last.set_input_files(SRT); log("숨김input set")
        except Exception as e2: log("폴백도 실패 "+str(e2)[:40])
    pg.wait_for_timeout(3500); shot("2loaded")

    # 3) 형식 다이얼로그: 타이밍 포함(기본) → 계속  (Playwright 네이티브 locator)
    try:
        btn=pg.locator("#confirm-button")
        if btn.count() and btn.first.is_visible():
            btn.first.click(); log("계속(locator)")
        else:
            pg.get_by_role("button",name="계속").first.click(); log("계속(role)")
    except Exception as e:
        log("계속 실패 "+str(e)[:50])
    pg.wait_for_timeout(4000); shot("3continued")

    # 4) 게시 (편집기 우상단)
    try:
        pub=pg.get_by_role("button",name="게시").first
        pub.click(); log("게시")
    except Exception as e:
        log("게시 실패 "+str(e)[:50])
    pg.wait_for_timeout(6000); shot("4published")
    log(f"=== {LANG} 완료 시도 끝 ===")
print("END")
