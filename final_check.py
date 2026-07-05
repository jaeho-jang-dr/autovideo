import sys,os; sys.path.insert(0,os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(af.PROFILE,channel="chrome",headless=False,locale="ko-KR",no_viewport=True,ignore_default_args=["--enable-automation"],args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg=ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    for tab,label in [("upload","동영상"),("short","쇼츠")]:
        pg.goto(f"https://studio.youtube.com/channel/UC6KCrgUSdSVUd97b7ltJK_g/videos/{tab}",wait_until="domcontentloaded"); pg.wait_for_timeout(9000)
        rows=pg.evaluate("""()=>{const o=[];document.querySelectorAll('ytcp-video-row').forEach(r=>{const t=(r.querySelector('#video-title')||{}).textContent||'';const v=[...r.querySelectorAll('.tablecell-visibility,#visibility,ytcp-video-visibility-select')].map(e=>e.textContent.trim()).join('');o.push(t.trim().slice(0,24)+' :: '+v.slice(0,16))});return o;}""")
        print(f"[{label}]")
        for r in rows: print("  "+r)
    ctx.close()
