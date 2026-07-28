# -*- coding: utf-8 -*-
"""최종화면의 '동영상' 요소를 **특정 동영상**으로 못박는다 (2026-07-28).

템플릿을 적용하면 동영상 요소가 `시청자 맞춤`(자동 추천)으로 들어간다. 사장님 원칙은
**정확한 이전 강의 지정**이므로 이걸 반드시 바꿔야 한다.

사용: python endscreen_pick_video.py <VID> "<검색어>" "<제목조각>"
"""
import sys
import time

from playwright.sync_api import sync_playwright

VID, QUERY, FRAG = sys.argv[1], sys.argv[2], sys.argv[3]
SH = "scratch/yt"


def log(m):
    print(m, flush=True)


with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222")
    ctx = b.contexts[0]
    pg = next((p for p in ctx.pages if "studio.youtube" in p.url), ctx.pages[-1])
    posts = []
    pg.on("request", lambda r: posts.append(r.url.split("youtubei/v1/")[-1].split("?")[0])
          if "youtubei/v1/" in r.url and r.method == "POST" else None)

    def shot(n):
        try:
            pg.screenshot(path=f"{SH}/pick_{n}.png", timeout=20000, animations="disabled")
        except Exception:
            pass

    # 편집기 열기
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded")
    time.sleep(7)
    row = pg.get_by_text("엔딩 화면", exact=True).first
    bb = row.bounding_box()
    pg.mouse.click(bb["x"] + 281, bb["y"] + bb["height"] / 2)
    time.sleep(7)
    shot("1_open")

    # 1) 타임라인/목록에서 '동영상' 요소 선택
    hit = pg.evaluate("""() => {
      const els=[...document.querySelectorAll('*')].filter(e=>{
        const t=(e.textContent||'').trim();
        return e.children.length===0 && (t.startsWith('동영상:'));
      });
      if(!els.length) return null;
      const e=els[els.length-1]; e.click();
      return e.textContent.trim().slice(0,40);
    }""")
    log(f"동영상 요소 클릭: {hit}")
    time.sleep(4)
    shot("2_selected")

    # 2) '특정 동영상 선택' 라디오
    ok = pg.evaluate("""() => {
      const els=[...document.querySelectorAll('*')].filter(e=>e.children.length===0 &&
        (e.textContent||'').includes('특정 동영상 선택'));
      if(!els.length) return false;
      els[0].click(); return true;
    }""")
    log(f"'특정 동영상 선택': {ok}")
    time.sleep(4)

    # 3) 검색 → 결과 클릭
    box = pg.locator("input[type='text']")
    for i in range(box.count()):
        try:
            if box.nth(i).is_visible():
                box.nth(i).fill(QUERY); log(f"검색: {QUERY}"); break
        except Exception:
            pass
    time.sleep(6)
    shot("3_search")
    picked = pg.evaluate("""(frag) => {
      const els=[...document.querySelectorAll('*')].filter(e=>e.children.length===0 &&
        (e.textContent||'').includes(frag));
      if(!els.length) return null;
      const e=els[0]; (e.closest('[role=option],ytcp-ve,div') || e).click();
      return e.textContent.trim().slice(0,50);
    }""", FRAG)
    log(f"결과 클릭: {picked}")
    time.sleep(5)
    shot("4_picked")

    # 4) 저장
    cands = []
    loc = pg.get_by_role("button", name="저장")
    for i in range(loc.count()):
        el = loc.nth(i)
        try:
            t = (el.inner_text() or "").strip()
            if "안함" in t or "취소" in t:
                continue
            b2 = el.bounding_box()
            if b2:
                cands.append((el, b2))
        except Exception:
            pass
    cands.sort(key=lambda t: -t[1]["x"])
    saved = False
    for el, b2 in cands:
        try:
            el.evaluate("e => e.click()")
            log(f"  JS저장클릭 @{round(b2['x'])},{round(b2['y'])}")
            time.sleep(4)
            if any("edit_video" in p for p in posts):
                saved = True; break
        except Exception:
            pass
    time.sleep(4)
    shot("5_saved")
    log(f"=== {VID} 특정영상 지정 저장 {'OK' if saved else 'MISS'} · POSTs={posts[-6:]} ===")
