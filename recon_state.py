# -*- coding: utf-8 -*-
import sys,os,json; sys.path.insert(0,os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright
OUT=open("scratch/recon.log","w",encoding="utf-8")
def w(s): OUT.write(s+"\n"); OUT.flush()
with sync_playwright() as pw:
    ctx=pw.chromium.launch_persistent_context(af.PROFILE,channel="chrome",headless=False,locale="ko-KR",no_viewport=True,ignore_default_args=["--enable-automation"],args=["--start-maximized","--no-first-run","--lang=ko-KR","--disable-gpu"])
    pg=ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(30000)
    pg.goto("https://studio.youtube.com/video/6lGedBJ5xx4/edit",wait_until="domcontentloaded"); pg.wait_for_timeout(9000)
    try: pg.locator("ytcp-button:has-text('자세히 보기'),#toggle-button").first.click(timeout=6000); pg.wait_for_timeout(2000)
    except Exception: pass
    d=pg.evaluate("""()=>{
      const title=(document.querySelector('[contenteditable=true][aria-label*=제목]')||{}).textContent||'';
      const rads=[...document.querySelectorAll('tp-yt-paper-radio-button,[role=radio]')].map(e=>({n:(e.getAttribute('aria-label')||e.textContent||'').trim().replace(/\\s+/g,' ').slice(0,45),c:e.getAttribute('aria-checked')||(e.hasAttribute('active')?'active':'')}));
      const cat=(document.querySelector('#category-container, ytcp-form-select#category')||{}).textContent||'';
      return {title:title.slice(0,90), rads:rads.filter(r=>r.n), cat:cat.replace(/\\s+/g,' ').slice(0,60)};
    }""")
    w("TITLE: "+d["title"])
    w("CAT: "+d["cat"])
    w("RADIOS:")
    for r in d["rads"]:
        mk=" <<CHECKED>>" if r["c"] in ("true","active") else ""
        w(f"   [{r['c']}] {r['n']}{mk}")
    pg.screenshot(path="scratch/yt/recon_state.png")
    ctx.close()
OUT.write("RECON_END\n"); OUT.close()
