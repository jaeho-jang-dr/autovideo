# -*- coding: utf-8 -*-
"""YouTube 스튜디오에 비공개 업로드(로그인 프로필). 각 단계 스크린샷 저장.
설정: 제목·설명(여민락 출처+AI 고지문)·썸네일·아동용아님·변경된콘텐츠 예·비공개."""
import sys, os, time
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

ROOT="D:/Entertainments/DevEnvironment/autovideo"
VIDEO=os.path.join(ROOT,"sejong_film/main/pkg/king_sejong_hangeul_4k.mp4")
THUMB=os.path.join(ROOT,"sejong_film/main/thumbnails/thumbnail_KO_B_1280x720.jpg")
DESC=open(os.path.join(ROOT,"sejong_film/main/pkg/yt_description.txt"),encoding="utf-8").read()
TITLE="세종대왕과 한글 창제 이야기 | 훈민정음은 어떻게 태어났을까? (King Sejong & Hangeul · 5 languages)"
SH=os.path.join(ROOT,"scratch","yt"); os.makedirs(SH,exist_ok=True)
def log(m): print(m,flush=True)
def shot(pg,n):
    try: pg.screenshot(path=os.path.join(SH,n)); log("shot "+n)
    except Exception as e: log("shot fail "+n+" "+str(e)[:60])

with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(af.PROFILE,channel="chrome",headless=False,locale="ko-KR",
        no_viewport=True,ignore_default_args=["--enable-automation"],
        args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg=ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(60000)
    pg.goto("https://studio.youtube.com/",wait_until="domcontentloaded"); pg.wait_for_timeout(9000)

    # 1) 업로드 모달 열기 → 모달 안 '파일 선택' 클릭 → 파일 선택창
    try:
        opened=False
        for sel in ["ytcp-button:has-text('동영상 업로드')","text=동영상 업로드"]:
            try: pg.locator(sel).first.click(timeout=4000); opened=True; break
            except Exception: pass
        if not opened:
            pg.locator("#create-icon").first.click(); pg.wait_for_timeout(1200)
            pg.get_by_text("동영상 업로드",exact=False).first.click()
        pg.wait_for_timeout(3500); shot(pg,"0_modal.png")
        with pg.expect_file_chooser(timeout=40000) as fc:
            fsok=False
            for sel in ["#select-files-button","ytcp-button:has-text('파일 선택')","text=파일 선택"]:
                try: pg.locator(sel).first.click(timeout=5000); fsok=True; break
                except Exception: pass
            if not fsok: raise Exception("파일 선택 버튼 못 찾음")
        fc.value.set_files(VIDEO); log("파일 선택 OK")
    except Exception as e:
        log("파일선택 실패: "+str(e)[:120]); shot(pg,"err_filechooser.png"); ctx.close(); sys.exit(1)
    pg.wait_for_timeout(9000); shot(pg,"1_details.png")

    # 2) 제목
    try:
        tb=pg.locator("#title-textarea #textbox, div[aria-label*='제목'][contenteditable]").first
        tb.click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(400)
        tb.type(TITLE,delay=8); log("제목 입력")
    except Exception as e: log("제목 실패 "+str(e)[:90])
    # 3) 설명
    try:
        db=pg.locator("#description-textarea #textbox, div[aria-label*='설명'][contenteditable]").first
        db.click(); pg.wait_for_timeout(300); db.type(DESC,delay=2); log("설명 입력")
    except Exception as e: log("설명 실패 "+str(e)[:90])
    pg.wait_for_timeout(1500); shot(pg,"2_title_desc.png")

    # 4) 썸네일 업로드
    try:
        with pg.expect_file_chooser(timeout=8000) as fc2:
            pg.locator("#select-button, ytcp-button:has-text('썸네일 업로드')").first.click(timeout=6000)
        fc2.value.set_files(THUMB); log("썸네일 업로드"); pg.wait_for_timeout(3000)
    except Exception as e: log("썸네일 스킵 "+str(e)[:80])
    shot(pg,"3_thumb.png")

    # 5) 아동용 아님
    try:
        pg.get_by_text("아니요, 아동용이 아닙니다",exact=False).first.click(timeout=6000); log("아동용 아님 선택")
    except Exception as e: log("아동용 라디오 실패 "+str(e)[:80])
    # 6) 자세히보기 → 변경된 콘텐츠 예
    try:
        pg.locator("#toggle-button, ytcp-button:has-text('자세히 보기')").first.click(timeout=6000); pg.wait_for_timeout(1500)
    except Exception as e: log("자세히보기 실패 "+str(e)[:70])
    pg.wait_for_timeout(800); shot(pg,"4_more.png")
    # 6b) 카테고리 = 교육
    try:
        pg.locator("#category-container, ytcp-form-select#category").first.click(timeout=5000); pg.wait_for_timeout(900)
        pg.get_by_text("교육",exact=True).first.click(timeout=4000); log("카테고리 교육"); pg.wait_for_timeout(600)
    except Exception as e: log("카테고리 실패 "+str(e)[:70])
    try:
        # 변경된 콘텐츠 '예' 라디오
        pg.get_by_role("radio",name="예").first.click(timeout=5000); log("변경된콘텐츠 예 선택")
    except Exception as e:
        try: pg.locator("tp-yt-paper-radio-button:has-text('예')").first.click(timeout=4000); log("변경된콘텐츠 예(대체)")
        except Exception as e2: log("변경콘텐츠 예 실패 "+str(e)[:70])
    pg.wait_for_timeout(1000); shot(pg,"5_altered.png")

    # 7) 다음 3번 → 공개상태
    for i in range(3):
        try: pg.locator("#next-button, ytcp-button:has-text('다음')").first.click(timeout=8000); log(f"다음{i+1}"); pg.wait_for_timeout(2500)
        except Exception as e: log(f"다음{i+1} 실패 "+str(e)[:60])
    shot(pg,"6_visibility.png")
    # 8) 비공개
    try:
        pg.get_by_role("radio",name="비공개").first.click(timeout=6000); log("비공개 선택")
    except Exception as e:
        try: pg.locator("tp-yt-paper-radio-button[name='PRIVATE']").first.click(timeout=4000); log("비공개(대체)")
        except Exception as e2: log("비공개 실패 "+str(e)[:70])
    pg.wait_for_timeout(1000); shot(pg,"7_private.png")
    # 9) 저장(업로드 계속 처리됨)
    try:
        pg.locator("#done-button, ytcp-button:has-text('저장'), ytcp-button:has-text('완료')").first.click(timeout=8000); log("저장 클릭")
    except Exception as e: log("저장 실패 "+str(e)[:70])
    pg.wait_for_timeout(6000); shot(pg,"8_saved.png")
    # 10) 파일 업로드 완료까지 브라우저 유지 (닫으면 업로드 중단됨) — 1.1GB
    import re
    log("업로드 완료 대기 (브라우저 유지)…")
    deadline=time.time()+3000  # 최대 50분
    last=""
    while time.time()<deadline:
        pg.wait_for_timeout(15000)
        try: body=pg.inner_text("body")
        except Exception: body=""
        # 파일 업로드 끝나면 '처리 중'/'처리 완료'/'업로드 완료' 표시
        if any(k in body for k in ["처리 중","처리 완료","업로드 완료","동영상 처리"]):
            log("업로드→처리 단계 감지(파일 업로드 완료)"); break
        m=re.search(r'([0-9]{1,3})\s*%',body)
        cur=m.group(1)+"%" if m else "…"
        if cur!=last: log("업로드 진행 "+cur); last=cur
    shot(pg,"9_uploaded.png")
    log("UPLOAD_FLOW_DONE")
    pg.wait_for_timeout(5000)
    ctx.close()
print("SCRIPT_END")
