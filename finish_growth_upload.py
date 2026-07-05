# -*- coding: utf-8 -*-
"""아이키성장 업로드 마무리: 초안 편집페이지에서 카테고리(교육)+변경된콘텐츠(예)+일부공개 설정 후 저장.
사용: python finish_growth_upload.py <VIDEO_ID>"""
import sys, os, time
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)
def shot(pg, n):
    try: pg.screenshot(path=os.path.join(SH, n)); log("shot " + n)
    except Exception as e: log("shot fail " + n + " " + str(e)[:50])

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
        no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); pg.wait_for_timeout(9000)
    shot(pg, "f0_edit.png")

    # 아동용 아님
    try:
        pg.get_by_text("아니요, 아동용이 아닙니다", exact=False).first.click(timeout=5000); log("아동용 아님")
    except Exception as e: log("아동용 스킵 " + str(e)[:50])

    # 자세히 보기 펼치기
    try:
        pg.locator("#toggle-button, ytcp-button:has-text('자세히 보기')").first.click(timeout=5000); pg.wait_for_timeout(1200); log("자세히 보기")
    except Exception as e: log("자세히보기 스킵 " + str(e)[:50])

    # 카테고리 = 교육 (드롭다운 확실히 닫기)
    try:
        pg.locator("#category-container, ytcp-form-select#category").first.click(timeout=5000); pg.wait_for_timeout(1200)
        # 옵션 아이템 클릭
        picked = False
        for sel in ["tp-yt-paper-item:has-text('교육')", "ytcp-text-menu tp-yt-paper-item:has-text('교육')", "#text-item-2"]:
            try:
                pg.locator(sel).first.click(timeout=3000); picked = True; log("카테고리 교육 " + sel); break
            except Exception: pass
        if not picked: pg.keyboard.press("Escape")
        pg.wait_for_timeout(1000)
    except Exception as e: log("카테고리 스킵 " + str(e)[:50])
    shot(pg, "f1_category.png")

    # 변경된 콘텐츠(합성/AI) = 예  — '변경된 콘텐츠' 섹션까지 스크롤 후 라디오
    try:
        # 섹션 라벨로 스크롤
        try:
            pg.get_by_text("변경된 콘텐츠", exact=False).first.scroll_into_view_if_needed(timeout=4000)
        except Exception: pass
        pg.wait_for_timeout(600)
        done = False
        for sel in ["#radio-yes", "ytcp-video-altered-content tp-yt-paper-radio-button:has-text('예')",
                    "tp-yt-paper-radio-button[name='ALTERED_CONTENT_YES']"]:
            try: pg.locator(sel).first.click(timeout=3000); done = True; log("변경된콘텐츠 예 " + sel); break
            except Exception: pass
        if not done:
            # role radio 이름 '예' 중 altered-content 컨테이너 내부
            try:
                pg.locator("ytcp-video-altered-content").get_by_role("radio", name="예").first.click(timeout=3000); done = True; log("변경된콘텐츠 예(role)")
            except Exception as e: log("변경콘텐츠 예 실패 " + str(e)[:50])
    except Exception as e: log("변경콘텐츠 스킵 " + str(e)[:50])
    shot(pg, "f2_altered.png")

    # 저장(세부정보) — #save
    for attempt in range(3):
        try:
            pg.locator("ytcp-button#save, #save-button").first.click(timeout=5000, force=True); log(f"세부정보 저장(attempt {attempt})"); break
        except Exception as e:
            log(f"저장 실패 {attempt} " + str(e)[:50]); pg.wait_for_timeout(1200)
    pg.wait_for_timeout(4000); shot(pg, "f3_saved_details.png")

    # 공개 상태 = 일부 공개  (편집페이지 상단 공개상태 드롭다운)
    try:
        # 공개상태 셀렉트 열기
        opened = False
        for sel in ["ytcp-video-visibility-select", "#visibility-container ytcp-video-visibility-select",
                    "ytcp-dropdown-trigger:near(:text('공개 상태'))"]:
            try: pg.locator(sel).first.click(timeout=4000); opened = True; log("공개상태 드롭다운 " + sel); break
            except Exception: pass
        if not opened:
            pg.get_by_text("공개 상태", exact=False).first.click(timeout=4000); log("공개상태(텍스트)")
        pg.wait_for_timeout(2000)
        shot(pg, "f4_vis_open.png")
        # 일부 공개 라디오
        r = pg.get_by_role("radio", name="일부 공개").first
        r.wait_for(state="visible", timeout=6000); r.click(timeout=5000); log("일부공개 선택")
        pg.wait_for_timeout(1000)
        # 저장 버튼(다이얼로그)
        for sel in ["ytcp-button#save-button", "#save-button", "ytcp-button:has-text('저장')"]:
            try: pg.locator(sel).first.click(timeout=4000, force=True); log("공개상태 저장 " + sel); break
            except Exception: pass
    except Exception as e:
        log("공개상태 설정 실패 " + str(e)[:70])
    pg.wait_for_timeout(5000); shot(pg, "f5_done.png")

    # 검증: 리로드 후 공개상태 텍스트
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); pg.wait_for_timeout(7000)
    try:
        body = pg.inner_text("body")
        for k in ["일부 공개", "비공개", "공개", "초안"]:
            if k in body: log("상태 텍스트 포함: " + k)
    except Exception: pass
    shot(pg, "f6_verify.png")
    log("FINISH_DONE VID=" + VID)
    pg.wait_for_timeout(3000)
    ctx.close()
print("SCRIPT_END")
