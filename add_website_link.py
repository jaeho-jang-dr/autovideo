# -*- coding: utf-8 -*-
"""영상/쇼츠 설명란 끝에 웹사이트 링크 1줄 추가(중복 시 스킵). 게시본만.
사용: python add_website_link.py <VIDEO_ID>"""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
LINE = "🌐 웹사이트 | Website ▶ https://drjayed.com"
SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
def log(m): print(m, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
        no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(40000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); pg.wait_for_timeout(8000)

    db = pg.locator("#description-textarea #textbox").first
    try:
        cur = db.inner_text(timeout=6000)
    except Exception as e:
        log("설명 읽기 실패 " + str(e)[:60]); ctx.close(); sys.exit(1)
    if "drjayed.com" in cur:
        log(f"{VID}: 이미 웹사이트 링크 있음 — 스킵"); ctx.close(); sys.exit(0)

    # 설명 끝으로 커서 이동 후 링크 append (기존 내용 보존)
    try:
        db.click(timeout=6000)
        pg.keyboard.press("Control+End"); pg.wait_for_timeout(300)
        pg.keyboard.type("\n\n" + LINE, delay=4)
        log("링크 추가 입력")
    except Exception as e:
        log("입력 실패 " + str(e)[:60]); ctx.close(); sys.exit(1)

    # 저장
    saved = False
    for attempt in range(4):
        try:
            btn = pg.locator("ytcp-button#save, #save-button").first
            btn.wait_for(state="visible", timeout=6000)
            btn.click(timeout=5000, force=True); saved = True; log(f"저장(attempt {attempt})"); break
        except Exception as e:
            log(f"저장 실패 {attempt} " + str(e)[:45])
            try: pg.eval_on_selector("ytcp-button#save, #save-button", "el=>{const b=el.querySelector('button')||el;b.click();}"); saved = True; log("JS 저장"); break
            except Exception: pass
            pg.wait_for_timeout(1200)
    pg.wait_for_timeout(4000)

    # 검증
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); pg.wait_for_timeout(6000)
    ok = False
    try:
        d = pg.locator("#description-textarea #textbox").first.inner_text(timeout=4000)
        ok = "drjayed.com" in d
    except Exception: pass
    log(f"{VID}: RESULT={'OK ✔' if ok else '실패 ✗'} saved={saved}")
    try: pg.screenshot(path=os.path.join(SH, f"web_{VID}.png"))
    except Exception: pass
    pg.wait_for_timeout(1500); ctx.close()
print("END")
