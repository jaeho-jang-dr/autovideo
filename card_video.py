# -*- coding: utf-8 -*-
"""타임드 동영상 카드 추가(CDP). card.py의 검증된 열기 로직 재사용.
사용: python card_video.py <VID> <target_vid1> "<시각1 M:SS>" "<제목키1>" [<target_vid2> "<시각2>" "<제목키2>"] ...
예:   python card_video.py YTex0QGe17o xp9ktV7zOYY 0:30 숫자  zVVrm8De8QY 3:45 인사말"""
import sys, time
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
# 나머지 인자를 3개씩 묶음: (target_vid, time, title_key)
rest = sys.argv[2:]
CARDS = [(rest[i], rest[i+1], rest[i+2]) for i in range(0, len(rest), 3)]

def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii","ignore").decode(), flush=True)
def shot(pg, n):
    try: pg.screenshot(path=f"scratch/yt/{n}.png", timeout=4000)
    except Exception: pass

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(12000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); time.sleep(6)

    # === 카드 편집기 열기 (card.py 검증 로직) ===
    opened = False
    for sel in ("#cards-button", "#card-edit-button", "#info-cards-button"):
        try:
            e = pg.locator(sel).first
            if e.count() and e.is_visible(timeout=1500): e.click(); opened = True; log("카드편집 열림 "+sel); break
        except Exception: pass
    if not opened:
        try: pg.get_by_text("카드", exact=True).first.click(); opened = True; log("카드 텍스트 클릭")
        except Exception: pass
    time.sleep(5); shot(pg, f"cv_{VID}_open")

    added = 0
    for (tvid, tstr, tkey) in CARDS:
        log(f"--- 카드: {tvid} @ {tstr} ({tkey}) ---")
        # '동영상' 행의 + 버튼 (card.py의 재생목록 로직을 동영상으로)
        try:
            target = None
            for el in pg.get_by_text("동영상", exact=True).all():
                bb = el.bounding_box()
                if bb and bb["y"] < 500: target = el; break
            if not target:
                log("동영상 행 못찾음"); shot(pg, f"cv_{VID}_novid"); continue
            tb = target.bounding_box(); cy = tb["y"] + tb["height"]/2
            clicked = False
            btns = pg.locator("ytcp-icon-button, tp-yt-paper-icon-button")
            for i in range(btns.count()):
                bb = btns.nth(i).bounding_box()
                if bb and abs(bb["y"]+bb["height"]/2 - cy) < 22 and bb["x"] > tb["x"]+tb["width"]:
                    btns.nth(i).click(); clicked = True; log("동영상+ 클릭"); break
            if not clicked:
                pg.mouse.click(tb["x"]+460, cy); log("동영상+ 좌표")
            time.sleep(3)
        except Exception as e:
            log("동영상+ 실패 "+str(e)[:40]); continue
        shot(pg, f"cv_{VID}_picker")

        # 비디오 피커: 검색창에 URL 붙여 정확히 선택
        picked = False
        url = f"https://youtu.be/{tvid}"
        try:
            sb = pg.get_by_placeholder("동영상 검색")
            if not sb.count(): sb = pg.locator("input[type=text]:visible, input#search-input")
            sb.first.click(); time.sleep(0.3)
            sb.first.fill(url); time.sleep(2.5)
            log("URL 검색: "+url)
        except Exception as e: log("검색 실패 "+str(e)[:40])
        shot(pg, f"cv_{VID}_search")
        # 검색 결과 첫 항목(내 영상) 클릭 — 제목키로 확인
        try:
            hit = pg.get_by_text(tkey, exact=False)
            if hit.count():
                for i in range(hit.count()):
                    bb = hit.nth(i).bounding_box()
                    if bb and bb["y"] > 120:
                        hit.nth(i).click(); picked = True; log("제목키 클릭 "+tkey); break
            if not picked:
                # 결과 첫 썸네일 클릭
                res = pg.locator("ytcp-video-pick-dialog #contents *, tp-yt-paper-item").first
                res.click(); picked = True; log("첫 결과 클릭")
        except Exception as e: log("선택 실패 "+str(e)[:40])
        time.sleep(2.5); shot(pg, f"cv_{VID}_picked")

        # 시작 시각 설정
        try:
            ti = pg.get_by_label("시작")
            if not ti.count(): ti = pg.locator("input[aria-label*='시간'], input[aria-label*='시작']")
            if ti.count():
                ti.first.click(); pg.keyboard.press("Control+A"); ti.first.type(tstr, delay=30); log("시각 입력 "+tstr)
            else: log("시각 필드 못찾음")
        except Exception as e: log("시각 실패 "+str(e)[:40])
        added += 1
        time.sleep(1.5)

    # 저장
    saved = False
    for sel in ("#save-button", "ytcp-button#save-button"):
        try:
            s = pg.locator(sel).first
            if s.is_visible(timeout=1500) and s.is_enabled(): s.click(); saved = True; break
        except Exception: pass
    time.sleep(4); shot(pg, f"cv_{VID}_saved")
    log(f"=== {VID}: 카드추가={added} 저장={'OK' if saved else 'NO'} ===")
    ctx.close()
print("DONE")
