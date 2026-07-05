# -*- coding: utf-8 -*-
"""유튜브 스튜디오에 자막 파일 1개 업로드 (언어 추가 → 파일 업로드 → 게시).
사용: python yt_add_sub.py <VIDEO_ID> <UI언어명> <srt경로>
예:   python yt_add_sub.py 6lGedBJ5xx4 영어 sejong_film/main/pkg/sub_en.srt"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]; UILANG = sys.argv[2]; SRT = os.path.abspath(sys.argv[3])
TAG = UILANG
def log(m): print(m, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, accept_downloads=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    os.makedirs("scratch/yt", exist_ok=True)
    def shot(name):
        try: pg.screenshot(path=f"scratch/yt/sub_{TAG}_{name}.png")
        except Exception: pass

    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded")
    pg.wait_for_timeout(8000); shot("01_page")

    # 이미 해당 언어가 있는지 확인
    if pg.get_by_text(f"{UILANG} (동영상 언어)", exact=False).count() == 0 and pg.locator(f"text={UILANG}").count() <= 1:
        # 1) 언어 추가
        try:
            pg.get_by_text("언어 추가", exact=True).first.click(timeout=6000); log("언어 추가 클릭")
        except Exception as e:
            log("언어 추가 실패: "+str(e)[:60])
        pg.wait_for_timeout(2000); shot("02_langlist")
        # 2) 목록에서 언어 선택 (검색 입력 있으면 입력)
        try:
            box = pg.locator("input[type='text'],input[aria-label*='검색']").first
            if box.count() and box.is_visible(timeout=1500):
                box.fill(UILANG); pg.wait_for_timeout(1200)
        except Exception: pass
        try:
            pg.get_by_text(UILANG, exact=True).first.click(timeout=6000); log(f"{UILANG} 선택")
        except Exception as e:
            log(f"{UILANG} 선택 실패: "+str(e)[:60])
        pg.wait_for_timeout(3000); shot("03_added")

    # 3) 해당 언어 행의 자막 '추가' 클릭 (행을 텍스트로 찾아 그 안의 추가/버튼)
    row = pg.locator("tr,ytgn-video-translation-row, ytcp-video-row").filter(has_text=UILANG).first
    clicked = False
    for target in ["자막 추가", "추가"]:
        try:
            if row.count():
                row.get_by_text(target, exact=False).first.click(timeout=4000); clicked=True; log(f"행 내 '{target}' 클릭"); break
        except Exception: pass
    if not clicked:
        try: pg.get_by_text("자막 추가", exact=False).first.click(timeout=4000); clicked=True; log("페이지 '자막 추가' 클릭")
        except Exception as e: log("자막추가 클릭 실패: "+str(e)[:60])
    pg.wait_for_timeout(2500); shot("04_addmenu")

    # 4) '파일 업로드' → 파일 선택 (파일 다이얼로그)
    try:
        with pg.expect_file_chooser(timeout=8000) as fc:
            # 파일 업로드 클릭
            for t in ["파일 업로드","업로드","Upload file"]:
                try: pg.get_by_text(t, exact=False).first.click(timeout=3000); log(f"'{t}' 클릭"); break
                except Exception: pass
        fc.value.set_files(SRT); log("파일 지정: "+os.path.basename(SRT))
    except Exception as e:
        log("파일업로드/다이얼로그 실패: "+str(e)[:80]); shot("04b_nofile")
        # '시간코드 포함' 먼저 나오는 UI 대응
        try:
            pg.get_by_text("시간 코드 포함", exact=False).first.click(timeout=3000)
            with pg.expect_file_chooser(timeout=6000) as fc2:
                pg.get_by_text("계속", exact=False).first.click(timeout=3000)
            fc2.value.set_files(SRT); log("시간코드포함 경로로 파일 지정")
        except Exception as e2: log("2차 파일업로드 실패: "+str(e2)[:80])
    pg.wait_for_timeout(3500); shot("05_uploaded")

    # 5) 게시
    published = False
    for t in ["게시","저장","PUBLISH","Publish"]:
        try:
            b = pg.get_by_text(t, exact=True).first
            if b.is_visible(timeout=2000): b.click(); published=True; log(f"'{t}' 클릭"); break
        except Exception: pass
    pg.wait_for_timeout(4000); shot("06_done")
    log("게시완료" if published else "게시버튼 못찾음(스샷확인)")
    pg.wait_for_timeout(1000); ctx.close()
log("DONE")
