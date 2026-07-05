# -*- coding: utf-8 -*-
"""동영상 업로드(일부공개 기본) + 썸네일 + AI=예 + 카테고리 교육 + video_id 캡처.
사용: python upload_hyp.py <video> <desc.txt> "<title>" <tag> <thumb.jpg> [visibility=unlisted|private|public]"""
import sys, os, time, re
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VIDEO=os.path.abspath(sys.argv[1]); DESC=open(sys.argv[2],encoding="utf-8").read()
TITLE=sys.argv[3]; TAG=sys.argv[4]
THUMB=None if sys.argv[5].lower()=="none" else os.path.abspath(sys.argv[5])
VIS=sys.argv[6] if len(sys.argv)>6 else "unlisted"
VISNAME={"unlisted":"일부 공개","private":"비공개","public":"공개"}[VIS]
SH="scratch/yt"; os.makedirs(SH,exist_ok=True)
def log(m): print(m,flush=True)
def shot(pg,n):
    try: pg.screenshot(path=SH+f"/uh_{n}.png")
    except Exception: pass

with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(af.PROFILE,channel="chrome",headless=False,locale="ko-KR",no_viewport=True,ignore_default_args=["--enable-automation"],args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg=ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto("https://studio.youtube.com/",wait_until="domcontentloaded"); pg.wait_for_timeout(9000)
    # 업로드 모달 → 파일
    try:
        op=False
        for sel in ["#upload-icon","ytcp-icon-button#upload-icon","ytcp-button:has-text('동영상 업로드')","text=동영상 업로드"]:
            try: pg.locator(sel).first.click(timeout=4000); op=True; break
            except Exception: pass
        if not op:
            pg.locator("ytcp-button:has-text('만들기')").first.click(timeout=4000); pg.wait_for_timeout(1200)
            pg.get_by_text("동영상 업로드",exact=False).first.click(timeout=4000); op=True
        pg.wait_for_timeout(3500)
        with pg.expect_file_chooser(timeout=40000) as fc:
            for sel in ["#select-files-button","ytcp-button:has-text('파일 선택')","text=파일 선택"]:
                try: pg.locator(sel).first.click(timeout=5000); break
                except Exception: pass
        fc.value.set_files(VIDEO); log("파일선택 OK")
    except Exception as e: log("파일선택 실패 "+str(e)[:100]); shot(pg,"err"); ctx.close(); sys.exit(1)
    pg.wait_for_timeout(9000)
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
    # 썸네일 (쇼츠 등 세로영상은 none → 스킵)
    if THUMB:
        try:
            pg.locator("ytcp-thumbnail-uploader input[type=file]").first.set_input_files(THUMB); pg.wait_for_timeout(3000); log("썸네일 업로드")
        except Exception as e: log("썸네일 실패 "+str(e)[:70])
    else:
        log("썸네일 스킵(none)")
    # video_id 캡처 — 반드시 업로드 다이얼로그 내부 링크만 (배경 페이지 링크 오인 방지)
    VID=""
    try:
        for sel in ["ytcp-uploads-dialog a[href*='/shorts/']","ytcp-uploads-dialog a[href*='youtu.be/']",
                    "ytcp-uploads-dialog a[href*='/watch?v=']","a[href*='youtube.com/shorts/']"]:
            try:
                href=pg.locator(sel).first.get_attribute("href",timeout=2000)
                m=re.search(r"(?:shorts/|youtu\.be/|v=)([A-Za-z0-9_-]{9,})",href or "")
                if m: VID=m.group(1); break
            except Exception: pass
    except Exception: pass
    log("VIDEO_ID="+(VID or "미확인"))
    shot(pg,"1details")
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
    # 카테고리 교육
    try:
        for t in ["인물/블로그","엔터테인먼트","카테고리 선택"]:
            try:
                el=pg.get_by_text(t,exact=True).first
                if el.is_visible(timeout=1500): el.scroll_into_view_if_needed(); el.click(); pg.wait_for_timeout(1000); break
            except Exception: pass
        pg.get_by_text("교육",exact=True).first.click(timeout=4000); log("카테고리 교육"); pg.keyboard.press("Escape"); pg.wait_for_timeout(1000)
    except Exception as e: log("카테고리 스킵 "+str(e)[:50]); pg.keyboard.press("Escape")
    shot(pg,"2set")
    # 다음 x3
    for i in range(3):
        try: pg.locator("#next-button, ytcp-button:has-text('다음')").first.click(timeout=8000); pg.wait_for_timeout(2500)
        except Exception as e: log(f"다음{i+1} 실패 "+str(e)[:40])
    shot(pg,"3vis")
    # 공개상태
    try:
        pg.get_by_role("radio",name=VISNAME,exact=True).first.click(timeout=6000); log(VISNAME)
    except Exception:
        try: pg.get_by_text(VISNAME,exact=True).first.click(timeout=4000); log(VISNAME+"(text)")
        except Exception as e2: log("공개상태 실패 "+str(e2)[:50])
    pg.wait_for_timeout(1500)
    # 저장/완료 (리플 오버레이가 클릭 가로채므로 force + JS 폴백)
    saved=False
    try:
        btn=pg.locator("#done-button").first
        btn.wait_for(state="visible", timeout=12000)
        for attempt in range(3):
            try:
                btn.click(timeout=5000, force=True); saved=True; break
            except Exception:
                try:
                    pg.eval_on_selector("#done-button","el=>{const b=el.querySelector('button')||el;b.click();}"); saved=True; break
                except Exception: pg.wait_for_timeout(1500)
        log("저장/게시" if saved else "저장 클릭 실패")
    except Exception as e: log("저장 실패 "+str(e)[:70])
    pg.wait_for_timeout(6000); shot(pg,"4done")
    # 게시 확인: 다이얼로그 닫힘 또는 '처리 중' 텍스트
    try:
        pg.wait_for_selector("ytcp-video-thumbnail-with-details, tp-yt-paper-dialog:has-text('처리'), :text('동영상 처리')", timeout=20000); log("게시확인")
    except Exception: log("게시확인 스킵")
    # 업로드 처리 대기
    dl=time.time()+600
    while time.time()<dl:
        pg.wait_for_timeout(10000)
        try: body=pg.inner_text("body")
        except Exception: body=""
        if any(k in body for k in ["처리 중","업로드 완료","처리 완료","SD 처리","동영상 처리"]): break
    shot(pg,"5uploaded")
    log("VIDEO_ID_FINAL="+(VID or "미확인")); log("UPLOAD_DONE"); pg.wait_for_timeout(3000); ctx.close()
print("END")
