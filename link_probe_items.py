# -*- coding: utf-8 -*-
"""피커 그리드 아이템 DOM 덤프 v2: 기본 그리드 + 검색 그리드 각각 img src(video id) 추출.
사용: python link_probe_items.py [short_id] [search_term]"""
import sys, os, re
sys.path.insert(0, os.getcwd())
import autoveo_flow as af
from playwright.sync_api import sync_playwright

SID = sys.argv[1] if len(sys.argv) > 1 else "OAnDgIm3M_g"
TERM = sys.argv[2] if len(sys.argv) > 2 else "우리"
os.makedirs("scratch/yt", exist_ok=True)

def dump_ids(pg, tag):
    try:
        srcs = pg.eval_on_selector_all(
            "ytcp-video-pick-dialog img, tp-yt-paper-dialog img",
            "els => els.map(e => e.src || e.getAttribute('src') || '')")
    except Exception as e:
        print(f"[{tag}] img err", str(e)[:80]); return []
    ids = []
    for s in srcs:
        m = re.search(r"/vi/([A-Za-z0-9_-]{11})/", s or "")
        if m:
            ids.append(m.group(1)); print(f"[{tag}] ID={m.group(1)}  {(s or '')[:70]}")
    if not ids: print(f"[{tag}] (no video-id thumbnails)")
    return ids

with sync_playwright() as pw:
    ctx = pw.chromium.launch_persistent_context(af.PROFILE, channel="chrome", headless=False,
        locale="ko-KR", no_viewport=True, ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--no-first-run", "--lang=ko-KR", "--disable-gpu"])
    pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.set_default_timeout(45000)
    pg.goto(f"https://studio.youtube.com/video/{SID}/edit", wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    pg.locator("ytcp-shorts-content-links-picker ytcp-dropdown-trigger").first.click(timeout=6000)
    pg.wait_for_timeout(3500)

    print("=== DEFAULT GRID ===")
    dump_ids(pg, "default")
    pg.screenshot(path="scratch/yt/probe_default.png", full_page=True)

    # 검색 (placeholder 타겟 + 실제 타이핑)
    print(f"=== SEARCH '{TERM}' ===")
    try:
        sb = pg.get_by_placeholder("내 동영상 검색")
        sb.wait_for(state="visible", timeout=6000)
        sb.click()
        sb.type(TERM, delay=90)
        pg.wait_for_timeout(4500)
    except Exception as e:
        print("search err", str(e)[:100])
    dump_ids(pg, "search")
    pg.screenshot(path="scratch/yt/probe_search.png", full_page=True)

    # 결과 항목의 클릭 가능 컨테이너 파악(첫 항목 img의 조상들 태그)
    try:
        info = pg.eval_on_selector("ytcp-video-pick-dialog img[src*='/vi/']",
            "el => { let out=[]; let n=el; for(let i=0;i<8;i++){ if(!n) break; out.push(n.tagName+'.'+(n.className||'').split(' ')[0]); n=n.parentElement;} return out.join(' > '); }")
        print("ANCESTORS:", info)
    except Exception as e:
        print("anc err", str(e)[:80])

    pg.wait_for_timeout(4000)
    ctx.close()
print("END")
