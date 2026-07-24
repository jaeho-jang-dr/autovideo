# -*- coding: utf-8 -*-
"""현재 유튜브 스튜디오 UI에 맞는 자막 업로더.
사용: python yt_sub2.py <VID> <lang: ko|en> <srt> <add:0|1>
 add=1 이면 '언어 추가'로 새 언어(영어) 먼저 추가."""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]; LANG = sys.argv[2]; SRT = os.path.abspath(sys.argv[3])
ADD = len(sys.argv) > 4 and sys.argv[4] == "1"
LNAME = {"ko": "한국어", "en": "영어"}[LANG]
os.makedirs("scratch/yt", exist_ok=True)
def log(m): print(m, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(40000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded")
    pg.wait_for_timeout(8000)

    # 새 언어 추가(영어)
    if ADD:
        try:
            pg.get_by_text("언어 추가", exact=False).first.click(timeout=6000); pg.wait_for_timeout(1500)
            pg.get_by_text(LNAME, exact=True).first.click(timeout=6000); pg.wait_for_timeout(2500)
            log(f"언어 추가: {LNAME}")
        except Exception as e:
            log("언어추가 실패: " + str(e)[:70])
        pg.wait_for_timeout(2000)

    pg.screenshot(path=f"scratch/yt/s2_{VID}_{LANG}_1.png")

    # 해당 언어 행의 자막 셀 클릭(– 또는 추가). 행을 언어명으로 찾아 자막열 클릭
    opened = False
    for sel in [f"ytgn-cell-subtitles:below(:text('{LNAME}'))",
                f"tr:has-text('{LNAME}') a", f"tr:has-text('{LNAME}') >> text=추가",
                f"tr:has-text('{LNAME}') >> text=-",
                f"#subtitles-cell", "a:has-text('추가')"]:
        try:
            pg.locator(sel).first.click(timeout=3500); opened = True; log("자막셀 클릭 " + sel); break
        except Exception:
            pass
    if not opened:
        # 좌표: 첫 행 자막열(–) 클릭 시도
        try:
            row = pg.get_by_text(f"{LNAME} (동영상 언어)").first
            box = row.bounding_box()
            if box: pg.mouse.click(box["x"] + 620, box["y"] + 8); opened = True; log("자막셀 좌표클릭")
        except Exception as e: log("자막셀 실패: " + str(e)[:60])
    pg.wait_for_timeout(4000)
    pg.screenshot(path=f"scratch/yt/s2_{VID}_{LANG}_2editor.png")

    # 파일 업로드 → (타이밍 포함) → 파일 선택
    try:
        with pg.expect_file_chooser(timeout=15000) as fc:
            clicked = False
            for t in ["파일 업로드", "업로드", "Upload file"]:
                try: pg.get_by_text(t, exact=False).first.click(timeout=3500); clicked = True; break
                except Exception: pass
            # '타이밍 포함' 라디오
            for t in ["타이밍 포함", "타임코드 포함"]:
                try: pg.get_by_text(t, exact=False).first.click(timeout=2500); break
                except Exception: pass
            for t in ["계속", "Continue", "선택"]:
                try: pg.get_by_text(t, exact=True).first.click(timeout=2500); break
                except Exception: pass
        fc.value.set_files(SRT); log("파일 선택 OK")
    except Exception as e:
        log("파일업로드 실패: " + str(e)[:80])
    pg.wait_for_timeout(4000)
    pg.screenshot(path=f"scratch/yt/s2_{VID}_{LANG}_3uploaded.png")

    # 게시
    for t in ["게시", "PUBLISH", "저장", "Publish"]:
        try: pg.get_by_role("button", name=t, exact=False).first.click(timeout=4000); log("게시 " + t); break
        except Exception: pass
    pg.wait_for_timeout(4000)
    pg.screenshot(path=f"scratch/yt/s2_{VID}_{LANG}_4done.png")
    log(f"SUB2_DONE {VID} {LANG}")
    ctx.close()
