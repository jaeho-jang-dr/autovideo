# -*- coding: utf-8 -*-
"""채널 콘텐츠 목록에서 각 영상 제목·조회수·video_id 덤프(CDP).
사용: python scrape_views.py"""
import time, sys
from playwright.sync_api import sync_playwright
CH = "UC6KCrgUSdSVUd97b7ltJK_g"
def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii","ignore").decode(), flush=True)
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(15000)
    pg.goto(f"https://studio.youtube.com/channel/{CH}/videos/upload", wait_until="domcontentloaded"); time.sleep(7)
    # 전부 로드되게 스크롤
    for _ in range(12):
        pg.mouse.wheel(0, 3000); time.sleep(1.2)
    time.sleep(2)
    rows = pg.evaluate("""() => {
        const out=[];
        document.querySelectorAll('ytcp-video-row').forEach(r=>{
            let title='', vid='', views='';
            const a = r.querySelector('a#video-title, a.ytcp-video-row, a[href*="/video/"]');
            if(a){ title=(a.textContent||'').trim(); const m=(a.href||'').match(/\\/video\\/([^\\/]+)/); if(m) vid=m[1]; }
            // 조회수 셀
            const cells = r.querySelectorAll('.ytcp-video-row, #cell, .tablecell-views, [id*="views"]');
            r.querySelectorAll('*').forEach(e=>{ if(e.children.length===0){ const t=(e.textContent||'').trim(); if(/^[\\d,\\.]+$/.test(t) && views==='' && t.length<10){} } });
            // views: 'views' 컬럼 텍스트
            const vc = r.querySelector('#views, .views, span.ytcp-video-row');
            out.push({title, vid});
        });
        return out;
    }""")
    # 조회수는 별도로: 각 행의 텍스트 전체에서 추출이 불안정 → 행 텍스트 통째 덤프
    raw = pg.evaluate("""() => {
        const out=[];
        document.querySelectorAll('ytcp-video-row').forEach(r=>{
            const a = r.querySelector('a[href*="/video/"]');
            let vid=''; if(a){ const m=(a.href||'').match(/\\/video\\/([^\\/]+)/); if(m) vid=m[1]; }
            out.push({vid, txt:(r.innerText||'').replace(/\\n+/g,' | ').slice(0,200)});
        });
        return out;
    }""")
    log(f"총 {len(raw)}개 영상")
    for r in raw:
        log(f"{r['vid']}\t{r['txt']}")
    ctx.close()
print("DONE")
