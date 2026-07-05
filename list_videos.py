# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    pg.set_default_timeout(30000)
    pg.goto("https://studio.youtube.com/channel/UC6KCrgUSdSVUd97b7ltJK_g/videos/upload", wait_until="domcontentloaded")
    pg.wait_for_timeout(10000)
    pg.screenshot(path="scratch/yt/content_list.png")
    # 각 행의 제목+공개상태 텍스트 추출
    rows = pg.evaluate("""() => {
      const out = [];
      document.querySelectorAll('ytcp-video-row').forEach(r => {
        const t = (r.querySelector('#video-title')||{}).textContent||'';
        const v = (r.querySelector('[id*=visibility], .ytcp-video-visibility-select, #visibility-column')||{}).textContent||'';
        out.push((t.trim().slice(0,40)) + ' | ' + v.trim().slice(0,30));
      });
      return out;
    }""")
    print("ROWS:")
    for r in rows:
        print("  " + r)
    ctx.close()
print("DONE")
