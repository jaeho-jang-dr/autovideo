# -*- coding: utf-8 -*-
"""아이키성장 v3(scene9 수정본) 4K → 유튜브 '일부 공개' 업로드.
제목·설명(AI 고지 포함)·썸네일·아동용아님·변경된콘텐츠 예·교육 카테고리·일부공개."""
import sys, os, time, re
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

ROOT = "D:/Entertainments/DevEnvironment/autovideo"
CG = os.path.join(ROOT, "child_growth_science")
VIDEO = os.path.join(CG, "child_growth_4k_noout.mp4")   # v4 한글우선·아웃트로없음
THUMB = os.path.join(CG, "thumb_ko_1280.jpg")
DESC = open(os.path.join(CG, "desc_main_ko.txt"), encoding="utf-8").read()
TITLE = "우리 아이 키 얼마나 클까? | 소아 성장·키 크는 과학 (부모 필독)"
VIS = "일부 공개"   # unlisted
SH = os.path.join(ROOT, "scratch", "yt"); os.makedirs(SH, exist_ok=True)

def log(m): print(m, flush=True)
def shot(pg, n):
    try: pg.screenshot(path=os.path.join(SH, n)); log("shot " + n)
    except Exception as e: log("shot fail " + n + " " + str(e)[:60])

assert os.path.exists(VIDEO), "v3 마스터 없음: " + VIDEO
log(f"VIDEO={VIDEO} ({os.path.getsize(VIDEO)/1e6:.0f}MB)")

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
        no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(60000)
    pg.goto("https://studio.youtube.com/", wait_until="domcontentloaded"); pg.wait_for_timeout(9000)

    # 1) '만들기' → '동영상 업로드' → 파일 선택
    try:
        # 만들기 버튼 열기
        opened = False
        for sel in ["ytcp-button:has-text('만들기')", "#create-icon", "tp-yt-paper-icon-button#create-icon", "button:has-text('만들기')"]:
            try: pg.locator(sel).first.click(timeout=5000); opened = True; log("만들기 클릭 " + sel); break
            except Exception: pass
        if not opened:
            pg.get_by_text("만들기", exact=False).first.click(timeout=5000); log("만들기(텍스트)")
        pg.wait_for_timeout(1800); shot(pg, "g0_modal.png")
        # 파일 chooser는 '동영상 업로드' 또는 이어지는 '파일 선택' 클릭에서 열림 — 둘 다 감싼다
        with pg.expect_file_chooser(timeout=40000) as fc:
            for sel in ["tp-yt-paper-item:has-text('동영상 업로드')", "ytcp-text-menu tp-yt-paper-item:has-text('동영상')", "text=동영상 업로드"]:
                try: pg.locator(sel).first.click(timeout=5000); log("동영상 업로드 클릭 " + sel); break
                except Exception: pass
            pg.wait_for_timeout(2500)
            for sel in ["#select-files-button", "ytcp-button:has-text('파일 선택')", "text=파일 선택"]:
                try: pg.locator(sel).first.click(timeout=5000); log("파일 선택 클릭"); break
                except Exception: pass
        fc.value.set_files(VIDEO); log("파일 선택 OK")
    except Exception as e:
        log("파일선택 실패: " + str(e)[:120]); shot(pg, "gerr_filechooser.png"); ctx.close(); sys.exit(1)
    pg.wait_for_timeout(9000); shot(pg, "g1_details.png")

    # 2) 제목
    try:
        tb = pg.locator("#title-textarea #textbox, div[aria-label*='제목'][contenteditable]").first
        tb.click(); pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(400)
        tb.type(TITLE, delay=8); log("제목 입력")
    except Exception as e: log("제목 실패 " + str(e)[:90])
    # 3) 설명
    try:
        db = pg.locator("#description-textarea #textbox, div[aria-label*='설명'][contenteditable]").first
        db.click(); pg.wait_for_timeout(300); db.type(DESC, delay=2); log("설명 입력")
    except Exception as e: log("설명 실패 " + str(e)[:90])
    pg.wait_for_timeout(1500); shot(pg, "g2_title_desc.png")

    # 4) 썸네일
    try:
        with pg.expect_file_chooser(timeout=8000) as fc2:
            pg.locator("#select-button, ytcp-button:has-text('썸네일 업로드')").first.click(timeout=6000)
        fc2.value.set_files(THUMB); log("썸네일 업로드"); pg.wait_for_timeout(3000)
    except Exception as e: log("썸네일 스킵 " + str(e)[:80])
    shot(pg, "g3_thumb.png")

    # 5) 아동용 아님
    try:
        pg.get_by_text("아니요, 아동용이 아닙니다", exact=False).first.click(timeout=6000); log("아동용 아님")
    except Exception as e: log("아동용 실패 " + str(e)[:80])
    # 6) 자세히 보기 → 카테고리 교육 + 변경된 콘텐츠 예
    try:
        pg.locator("#toggle-button, ytcp-button:has-text('자세히 보기')").first.click(timeout=6000); pg.wait_for_timeout(1500)
    except Exception as e: log("자세히보기 실패 " + str(e)[:70])
    pg.wait_for_timeout(800); shot(pg, "g4_more.png")
    try:
        pg.locator("#category-container, ytcp-form-select#category").first.click(timeout=5000); pg.wait_for_timeout(900)
        pg.get_by_text("교육", exact=True).first.click(timeout=4000); log("카테고리 교육"); pg.wait_for_timeout(600)
    except Exception as e: log("카테고리 실패 " + str(e)[:70])
    try:
        pg.get_by_role("radio", name="예").first.click(timeout=5000); log("변경된콘텐츠 예")
    except Exception as e:
        try: pg.locator("tp-yt-paper-radio-button:has-text('예')").first.click(timeout=4000); log("변경된콘텐츠 예(대체)")
        except Exception as e2: log("변경콘텐츠 예 실패 " + str(e)[:70])
    pg.wait_for_timeout(1000); shot(pg, "g5_altered.png")

    # 7) 다음 3번 → 공개상태
    for i in range(3):
        try: pg.locator("#next-button, ytcp-button:has-text('다음')").first.click(timeout=8000); log(f"다음{i+1}"); pg.wait_for_timeout(2500)
        except Exception as e: log(f"다음{i+1} 실패 " + str(e)[:60])
    shot(pg, "g6_visibility.png")
    # 8) 일부 공개 — 실제 radio 보일 때까지 대기 후 선택
    try:
        r = pg.get_by_role("radio", name=VIS).first
        r.wait_for(state="visible", timeout=8000)
        r.click(timeout=6000); log(f"{VIS} 선택")
    except Exception as e:
        try: pg.locator("tp-yt-paper-radio-button[name='UNLISTED']").first.click(timeout=4000); log("일부공개(대체)")
        except Exception as e2: log("일부공개 실패 " + str(e)[:70])
    pg.wait_for_timeout(1000); shot(pg, "g7_unlisted.png")
    # 9) 저장/완료 (ripple 대비 force + JS 폴백)
    saved = False
    for attempt in range(3):
        try:
            pg.locator("#done-button, ytcp-button:has-text('저장'), ytcp-button:has-text('완료')").first.click(timeout=8000, force=True)
            saved = True; log(f"저장 클릭(attempt {attempt})"); break
        except Exception as e:
            log(f"저장 실패 {attempt} " + str(e)[:60])
            try:
                pg.eval_on_selector("#done-button", "el => { const b = el.querySelector('button') || el; b.click(); }")
                saved = True; log("JS 폴백 저장"); break
            except Exception: pass
        pg.wait_for_timeout(1500)
    pg.wait_for_timeout(6000); shot(pg, "g8_saved.png")

    # 10) 업로드/처리 완료까지 브라우저 유지 + VID 캡처(다이얼로그 내부 링크만)
    vid = None
    log("업로드 완료 대기 (브라우저 유지)…")
    deadline = time.time() + 3600  # 최대 60분(1.6GB)
    last = ""
    while time.time() < deadline:
        # VID 캡처 시도(다이얼로그 스코프)
        if not vid:
            for sel in ["ytcp-uploads-dialog a[href*='/watch?v=']", "ytcp-uploads-dialog a[href*='youtu.be/']"]:
                try:
                    href = pg.locator(sel).first.get_attribute("href", timeout=2000)
                    m = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{9,})", href or "")
                    if m: vid = m.group(1); log("VIDEO_ID=" + vid); break
                except Exception: pass
        try: body = pg.inner_text("body")
        except Exception: body = ""
        if any(k in body for k in ["처리 중", "처리 완료", "업로드 완료", "동영상 처리", "SD 처리 완료", "HD 처리 중"]):
            log("업로드→처리 단계 감지(파일 업로드 완료)"); break
        m = re.search(r'([0-9]{1,3})\s*%', body); cur = m.group(1) + "%" if m else "…"
        if cur != last: log("업로드 진행 " + cur); last = cur
        pg.wait_for_timeout(15000)
    # VID 재시도
    if not vid:
        for sel in ["ytcp-uploads-dialog a[href*='/watch?v=']", "ytcp-uploads-dialog a[href*='youtu.be/']"]:
            try:
                href = pg.locator(sel).first.get_attribute("href", timeout=2000)
                m = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{9,})", href or "")
                if m: vid = m.group(1); log("VIDEO_ID(late)=" + vid); break
            except Exception: pass
    shot(pg, "g9_uploaded.png")
    log("UPLOAD_FLOW_DONE VID=" + (vid or "?"))
    pg.wait_for_timeout(5000)
    ctx.close()
print("SCRIPT_END")
