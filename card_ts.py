# -*- coding: utf-8 -*-
"""동영상 카드 추가(hang 없는 좌표 방식): 플레이헤드 이동 → +카드 → 동영상 → 검색 → 단일결과 → 저장.
hang 원인이던 Playwright 요소검사(actionability)를 결과선택 이후 전부 배제 — 좌표 마우스클릭+CDP스샷만 사용.
사용: python card_ts.py <VID> <영상길이초> <카드시각초> "<내동영상검색어>" [--save]"""
import sys, time, base64
from playwright.sync_api import sync_playwright

VID = sys.argv[1]; DUR = float(sys.argv[2]); T = float(sys.argv[3]); SEARCH = sys.argv[4]
SAVE = "--save" in sys.argv
# 타임라인 좌표(스샷 실측: 눈금 0:00=x494, 끝=x1464, 눈금줄 y=578)
X0, X1, RULER_Y = 494, 1464, 578
PX = round(X0 + (X1 - X0) * (T / DUR))

def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii", "ignore").decode(), flush=True)

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(8000)
    cdp = ctx.new_cdp_session(pg)
    def shot(n):
        try:
            d = cdp.send("Page.captureScreenshot", {"format": "png"})
            open(f"scratch/yt/{n}.png", "wb").write(base64.b64decode(d["data"]))
            log("shot " + n)
        except Exception as e: log("shot fail " + str(e)[:30])

    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); time.sleep(6)
    # 1) 카드 편집기 (여기까지 locator는 한 번도 hang 없었음)
    pg.get_by_role("button", name="카드", exact=True).first.click(timeout=6000); time.sleep(4)
    log("편집기 열림")
    # 2) 플레이헤드를 목표 시각으로 (타임라인 눈금 클릭)
    pg.mouse.click(PX, RULER_Y); time.sleep(1.5)
    log(f"플레이헤드 클릭 x={PX} (t={T}s)")
    shot("ct_1_playhead")
    # 3) + 카드 → 동영상
    pg.get_by_role("button", name="카드 추가").first.click(timeout=6000); time.sleep(2)
    pg.mouse.click(272, 134); time.sleep(4)   # 타입메뉴 '동영상' (실측좌표)
    # 4) 내 동영상 검색 → 단일 결과 클릭 (타일1 썸네일 중심 = 실측 440,284)
    sb = pg.get_by_placeholder("내 동영상 검색")
    sb.first.click(timeout=6000); sb.first.fill(SEARCH); time.sleep(3.5)
    shot("ct_2_search")
    pg.mouse.click(440, 284); time.sleep(3.5)  # ← 이후 locator 절대 금지(hang 지점)
    log("결과 클릭(440,284)")
    shot("ct_3_picked")
    # 5) 저장 (모달 헤더 저장 버튼 실측좌표 1429,97)
    if SAVE:
        pg.mouse.click(1429, 97); time.sleep(5)
        log("저장 클릭(1429,97)")
        shot("ct_4_saved")
    else:
        log("(--save 없음)")
    ctx.close()
print("DONE")
