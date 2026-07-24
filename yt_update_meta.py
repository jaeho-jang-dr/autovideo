# -*- coding: utf-8 -*-
"""YouTube Studio 메타데이터(제목·설명·태그) 편집 — youtube_meta.json 기반.
사용: python yt_update_meta.py <video_id> [--nosave]
로그인된 chrome_profile(autoveo_flow.PROFILE) 사용. 단계별 스크린샷 저장.
"""
import sys, os, json
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
NOSAVE = "--nosave" in sys.argv
META = json.load(open("youtube_meta.json", encoding="utf-8"))[VID]
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); pg.wait_for_timeout(9000)
    pg.screenshot(path=f"{SH}/m_{VID}_0.png")

    def clear_fill(loc_sel, text, label, delay=3):
        try:
            box = pg.locator(loc_sel).first
            box.click(); pg.wait_for_timeout(300)
            pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); pg.wait_for_timeout(300)
            box.type(text, delay=delay); log(f"{label} 입력 OK"); pg.wait_for_timeout(500)
            return True
        except Exception as e:
            log(f"{label} 실패: {str(e)[:70]}"); return False

    # 제목
    clear_fill("#title-textarea #textbox, ytcp-video-title #textbox", META["title"], "제목", delay=6)
    # 설명
    clear_fill("#description-textarea #textbox", META["description"], "설명", delay=1)
    # 태그: '자세히 보기' 펼치기
    try:
        pg.locator("ytcp-button#toggle-button, #toggle-button, ytcp-button:has-text('자세히 보기')").first.click(timeout=5000)
        pg.wait_for_timeout(1500); log("자세히 보기 열기")
    except Exception as e: log("자세히보기 실패: " + str(e)[:40])
    try:
        ti = pg.locator("#tags-container input, input[aria-label*='태그'], #text-input").first
        ti.click(); pg.wait_for_timeout(300)
        for t in META["tags"]:
            ti.type(t, delay=4); pg.keyboard.press("Enter"); pg.wait_for_timeout(100)
        log(f"태그 {len(META['tags'])}개 입력")
    except Exception as e: log("태그 실패: " + str(e)[:70])
    pg.wait_for_timeout(800); pg.screenshot(path=f"{SH}/m_{VID}_filled.png")

    if NOSAVE:
        log("--nosave: 저장 생략(검증용)")
    else:
        try:
            pg.locator("#save-button, ytcp-button#save").first.click(timeout=8000)
            log("저장 클릭"); pg.wait_for_timeout(7000)
        except Exception as e: log("저장 실패: " + str(e)[:60])
        pg.screenshot(path=f"{SH}/m_{VID}_saved.png")
    log(f"META_{VID}_DONE"); pg.wait_for_timeout(2000); ctx.close()
print("END")
