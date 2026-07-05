# -*- coding: utf-8 -*-
"""동영상 1개 비공개 업로드(범용). 사용: python upload_one.py <video> <desc.txt> "<title>" <tag>"""
import sys, os, time
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
VIDEO=os.path.abspath(sys.argv[1]); DESC=open(sys.argv[2],encoding="utf-8").read(); TITLE=sys.argv[3]; TAG=sys.argv[4]
SH="scratch/yt"; os.makedirs(SH,exist_ok=True)
def log(m): print(m,flush=True)
def shot(pg,n):
    try: pg.screenshot(path=SH+f"/u_{TAG}_{n}.png")
    except Exception: pass
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(af.PROFILE,channel="chrome",headless=False,locale="ko-KR",no_viewport=True,ignore_default_args=["--enable-automation"],args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg=ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto("https://studio.youtube.com/",wait_until="domcontentloaded"); pg.wait_for_timeout(9000)
    # 업로드 모달 → 파일 선택
    try:
        op=False
        for sel in ["#upload-icon", "ytcp-icon-button#upload-icon", "ytcp-button:has-text('동영상 업로드')", "text=동영상 업로드"]:
            try: pg.locator(sel).first.click(timeout=4000); op=True; break
            except Exception: pass
        if not op:
            try:
                pg.locator("ytcp-button:has-text('만들기')").first.click(timeout=4000)
                pg.wait_for_timeout(1200)
                pg.get_by_text("동영상 업로드",exact=False).first.click(timeout=4000)
                op=True
            except Exception: pass
        if not op:
            raise Exception("업로드 버튼 클릭 실패")
        pg.wait_for_timeout(3500)
        with pg.expect_file_chooser(timeout=40000) as fc:
            for sel in ["#select-files-button","ytcp-button:has-text('파일 선택')","text=파일 선택"]:
                try: pg.locator(sel).first.click(timeout=5000); break
                except Exception: pass
        fc.value.set_files(VIDEO); log("파일선택 OK")
    except Exception as e: log("파일선택 실패 "+str(e)[:100]); shot(pg,"err"); ctx.close(); sys.exit(1)
    pg.wait_for_timeout(8000)
    # 제목
    try:
        tb=pg.locator("[contenteditable='true'][aria-label*='제목']").first
        tb.click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(400)
        pg.keyboard.insert_text(TITLE); log("제목")
    except Exception as e: log("제목 실패 "+str(e)[:70])
    # 설명
    try:
        db=pg.locator("[contenteditable='true'][aria-label*='설명해']").first
        db.click(); pg.wait_for_timeout(300); pg.keyboard.insert_text(DESC); log("설명")
    except Exception as e: log("설명 실패 "+str(e)[:70])
    pg.wait_for_timeout(1000); shot(pg,"1details")
    # 아동용 아님
    try:
        r=pg.get_by_role("radio",name="아동용이 아닙니다",exact=False).first
        r.scroll_into_view_if_needed(); pg.wait_for_timeout(300); r.click(); log("아동용아님")
    except Exception as e: log("아동용 실패 "+str(e)[:60])
    # 자세히 보기
    try: pg.locator("ytcp-button:has-text('자세히 보기'),#toggle-button").first.click(timeout=6000); pg.wait_for_timeout(1800); log("자세히보기")
    except Exception as e: log("자세히 실패 "+str(e)[:50])
    # AI 예
    try:
        r=pg.get_by_role("radio",name="AI가 사용되었습니다",exact=False).first
        r.scroll_into_view_if_needed(); pg.wait_for_timeout(300); r.click(); log("AI예")
    except Exception as e: log("AI 실패 "+str(e)[:60])
    # 카테고리 교육 (best-effort)
    try:
        for t in ["인물/블로그","엔터테인먼트","카테고리 선택","교육"]:
            try:
                el=pg.get_by_text(t,exact=True).first
                if el.is_visible(timeout=1500): el.scroll_into_view_if_needed(); el.click(); pg.wait_for_timeout(1000); break
            except Exception: pass
        pg.get_by_text("교육",exact=True).first.click(timeout=4000); log("카테고리 교육")
        pg.keyboard.press("Escape"); pg.wait_for_timeout(1000)
    except Exception as e: log("카테고리 스킵 "+str(e)[:50]); pg.keyboard.press("Escape")
    shot(pg,"2set")
    # 다음 x3
    for i in range(3):
        try: pg.locator("#next-button, ytcp-button:has-text('다음')").first.click(timeout=8000); pg.wait_for_timeout(2500)
        except Exception as e: log(f"다음{i+1} 실패 "+str(e)[:40])
    shot(pg,"3vis")
    # 비공개
    try:
        pg.get_by_role("radio",name="비공개",exact=True).first.click(timeout=6000); log("비공개")
    except Exception as e:
        try: pg.get_by_text("비공개",exact=True).first.click(timeout=4000); log("비공개(text)")
        except Exception as e2: log("비공개 실패 "+str(e)[:50])
    pg.wait_for_timeout(1000)
    # 저장/완료
    try: pg.locator("#done-button, ytcp-button:has-text('저장'), ytcp-button:has-text('완료')").first.click(timeout=8000); log("저장")
    except Exception as e: log("저장 실패 "+str(e)[:50])
    pg.wait_for_timeout(4000); shot(pg,"4done")
    # 업로드 완료 대기
    import re
    dl=time.time()+600
    while time.time()<dl:
        pg.wait_for_timeout(10000)
        try: body=pg.inner_text("body")
        except Exception: body=""
        if any(k in body for k in ["처리 중","업로드 완료","처리 완료","동영상 처리"]): log("업로드 완료"); break
    shot(pg,"5uploaded")
    log(f"UPLOAD_{TAG}_DONE"); pg.wait_for_timeout(3000); ctx.close()
print("END")
