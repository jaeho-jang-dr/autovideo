# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    pg.goto("https://studio.youtube.com/", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    try: pg.get_by_text("콘텐츠", exact=True).first.click(timeout=6000); pg.wait_for_timeout(6000)
    except Exception: pass
    rows = pg.evaluate("""() => {
      const out = [];
      document.querySelectorAll('ytcp-video-row').forEach(r => {
        const a = r.querySelector('a#video-title, a[href*="/video/"], a[href*="/edit"]');
        const href = a ? a.getAttribute('href') : '';
        const m = href ? href.match(/video\\/([A-Za-z0-9_-]{6,})/) : null;
        const t = (r.querySelector('#video-title')||{}).textContent||'';
        const v = (r.querySelector('#visibility, [id*=visibility]')||{}).textContent||'';
        out.push((m?m[1]:'?') + ' :: ' + t.trim().slice(0,40) + ' :: ' + v.trim().slice(0,16));
      });
      return out;
    }""")
    print("[uploads]")
    for r in rows: print("  " + r)
    ctx.close()
print("DONE")
