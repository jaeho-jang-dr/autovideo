# -*- coding: utf-8 -*-
"""W23 최종화면 — 템플릿 먼저 → 특정 동영상 교체 → 저장 (2026-07-28).

★실측 함정
 - `/endscreens` 직행 URL 은 에러 → 세부정보의 '엔딩 화면' 연필로 연다.
 - 저장 버튼은 `변경사항 저장 안함` 과 이름이 겹친다 → **'안함' 제외 + 오른쪽 것**만.
 - ytcp-button 은 is_enabled()가 False로 나와도 눌린다 → JS 클릭 + `edit_video` POST 로 검증.
 - 요소를 직접 추가하는 경로는 상태가 잘 깨진다 → **템플릿('동영상 1개, 구독 1개')을 먼저** 고른다.

사용: python endscreen_w23.py <VID> "<검색어>" "<제목조각>"
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
            pg.screenshot(path=f"{SH}/w23es_{n}.png", timeout=20000, animations="disabled")
        except Exception:
            pass

    # 편집기가 닫혀 있으면 세부정보에서 연필로 연다
    if "엔딩 화면" not in (pg.content() or "") or not pg.get_by_text("최종 화면", exact=True).count():
        pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded")
        time.sleep(6)
        row = pg.get_by_text("엔딩 화면", exact=True).first
        bb = row.bounding_box()
        if bb:
            pg.mouse.click(bb["x"] + 281, bb["y"] + bb["height"] / 2)   # 연필 = 텍스트 오른쪽 281px
            time.sleep(6)
    shot("1_open")

    # 1) 템플릿 — '동영상 1개, 구독 1개'
    # ★텍스트를 누르면 카드(gridcell)가 포인터를 가로챈다 → 카드 자체를 JS 클릭한다
    tpl = pg.locator('div[role="gridcell"][aria-label="동영상 1개, 구독 1개"]')
    if tpl.count():
        tpl.first.evaluate("e => e.click()")
        log("템플릿 '동영상 1개, 구독 1개' 선택")
        time.sleep(6)
    shot("2_template")

    # 2) 동영상 요소 클릭 → 특정 동영상 선택 → 검색 → 결과
    for sel in ("동영상: ", "최근 업로드된 동영상", "시청자 맞춤"):
        e = pg.get_by_text(sel, exact=False)
        if e.count():
            try:
                e.first.click(); time.sleep(2)
            except Exception:
                pass
            break
    # ★중간 단계가 실패해도 **저장까지는 반드시 간다**(템플릿만이라도 남기고 2패스로 채운다)
    try:
        pick = pg.get_by_text("특정 동영상 선택", exact=False)
        if pick.count():
            pick.first.click(); log("'특정 동영상 선택' 클릭"); time.sleep(3)
    except Exception as e:
        log(f"(특정영상 선택 건너뜀: {str(e)[:30]})")
    box = pg.locator("input[type='text'], input#search-input, ytcp-searchbox input")
    for i in range(box.count()):
        try:
            box.nth(i).fill(QUERY); log(f"검색: {QUERY}"); break
        except Exception:
            pass
    time.sleep(5)
    shot("3_search")
    try:
        res = pg.get_by_text(FRAG, exact=False)
        if res.count():
            res.first.click(); log(f"결과 클릭: {FRAG}"); time.sleep(4)
    except Exception as e:
        log(f"(결과 클릭 건너뜀: {str(e)[:30]})")
    shot("4_picked")

    # 3) 저장 — '안함' 제외, 오른쪽부터 JS 클릭, edit_video 로 검증
    cands = []
    for i in range(pg.get_by_role("button", name="저장").count()):
        el = pg.get_by_role("button", name="저장").nth(i)
        try:
            t = (el.inner_text() or "").strip()
            if "안함" in t or "취소" in t:
                continue
            bb = el.bounding_box()
            if bb:
                cands.append((el, bb))
        except Exception:
            pass
    cands.sort(key=lambda t: -t[1]["x"])
    log(f"저장후보 {len(cands)}개 x={[round(c[1]['x']) for c in cands]}")
    ok = False
    for el, bb in cands:
        try:
            el.evaluate("e => e.click()")
            log(f"  JS저장클릭 @{round(bb['x'])},{round(bb['y'])}")
            time.sleep(4)
            if any("edit_video" in p for p in posts):
                ok = True; break
        except Exception as e:
            log(f"  실패 {str(e)[:30]}")
    time.sleep(4)
    shot("5_saved")
    log(f"=== {VID} 최종화면 저장 {'OK(edit_video)' if ok else 'MISS'} · POSTs={posts[-6:]} ===")
