# -*- coding: utf-8 -*-
"""유튜브 스튜디오에서 정주행(binge) 본편 찾기 + 현재 공개상태/처리상태 확인."""
import sys, os
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

def log(m): print(m, flush=True)

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    pg.goto("https://studio.youtube.com/channel/UC6KCrgUSdSVUd97b7ltJK_g/videos/upload",
            wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    os.makedirs("scratch/yt", exist_ok=True)
    pg.screenshot(path="scratch/yt/binge_list.png")
    rows = pg.evaluate("""() => {
      const out = [];
      document.querySelectorAll('ytcp-video-row').forEach(r => {
        const a = r.querySelector('a#video-title, a[href*="/video/"]');
        const href = a ? a.getAttribute('href') : '';
        const m = href ? href.match(/video\\/([A-Za-z0-9_-]{6,})/) : null;
        const t = (r.querySelector('#video-title')||{}).textContent||'';
        const vis = (r.querySelector('#visibility, [id*=visibility]')||{}).textContent||'';
        out.push((m?m[1]:'?') + ' :: ' + t.trim().slice(0,45) + ' :: ' + vis.trim().slice(0,20));
      });
      return out;
    }""")
    log("=== 스튜디오 업로드 목록 ===")
    for r in rows: log("  " + r)
    # 정주행 관련만
    log("=== 정주행/binge 후보 ===")
    for r in rows:
        if ('정주행' in r) or ('binge' in r.lower()) or ('Binge' in r):
            log("  ★ " + r)
    ctx.close()
log("DONE")
