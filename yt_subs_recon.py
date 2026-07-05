# -*- coding: utf-8 -*-
"""유튜브 스튜디오 자막/언어 UI 정찰 — 세종 영상의 자막 페이지 열고 스크린샷+버튼목록."""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

VID = sys.argv[1] if len(sys.argv) > 1 else "6lGedBJ5xx4"
def log(m): print(m, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    os.makedirs("scratch/yt", exist_ok=True)
    # 자막(번역) 페이지
    pg.goto(f"https://studio.youtube.com/video/{VID}/translations", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    pg.screenshot(path="scratch/yt/subs_page.png", full_page=True)
    # 화면 텍스트/버튼 수집
    info = pg.evaluate("""() => {
      const btns = [];
      document.querySelectorAll('button,ytcp-button,a,[role=button]').forEach(b=>{
        const t=(b.textContent||'').trim().replace(/\\s+/g,' ');
        if(t && t.length<40) btns.push(t);
      });
      const langs = [];
      document.querySelectorAll('*').forEach(e=>{
        const t=(e.childElementCount===0?(e.textContent||''):'').trim();
        if(/한국어|영어|일본어|중국어|스페인어|원본|추가|언어/.test(t) && t.length<20) langs.push(t);
      });
      return {url:location.href, btns:[...new Set(btns)].slice(0,40), langs:[...new Set(langs)].slice(0,30)};
    }""")
    log("URL: "+info["url"])
    log("버튼: "+str(info["btns"]))
    log("언어관련: "+str(info["langs"]))
    pg.wait_for_timeout(1500)
    ctx.close()
log("DONE")
