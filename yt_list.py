# -*- coding: utf-8 -*-
"""스튜디오 콘텐츠 목록 스크레이프: 제목/길이/공개상태/videoId 덤프."""
import sys, os, json
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

SH = "scratch/yt"; os.makedirs(SH, exist_ok=True)
with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto("https://studio.youtube.com/channel/UC/videos/upload", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    try: pg.screenshot(path=f"{SH}/list.png", full_page=True)
    except Exception: pass
    rows = pg.evaluate(r"""() => {
      const out = [];
      document.querySelectorAll('ytcp-video-row').forEach(r => {
        const a = r.querySelector('a#video-title, a.ytcp-video-row');
        const href = a ? a.getAttribute('href') : '';
        const m = href ? href.match(/video\/([A-Za-z0-9_-]{6,})/) : null;
        const title = (r.querySelector('#video-title')||{}).textContent || '';
        const vis = (r.querySelector('#visibility, .visibility, ytcp-video-visibility-select')||{}).textContent || '';
        const dur = (r.querySelector('.thumbnail-duration, ytcp-video-thumbnail #time-status, .style-scope.ytcp-video-thumbnail')||{}).textContent || '';
        out.push({id: m?m[1]:'', title: title.trim().slice(0,60), vis: vis.trim().slice(0,30), dur: dur.trim().slice(0,20)});
      });
      return out;
    }""")
    print(json.dumps(rows, ensure_ascii=False, indent=1))
    ctx.close()
print("END")
