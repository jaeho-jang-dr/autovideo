# -*- coding: utf-8 -*-
"""최종화면을 '특정 동영상' + '구독'으로 UI 구성(검증된 경로). 자동추천(시청자 맞춤) 금지 —
   사장님 지시: 최종화면은 **정확한 이전 강의**를 지정한다.

사용: python endscreen_video_ui.py <VID> "<검색어>" "<제목조각>" [--save]
예:   python endscreen_video_ui.py CZMYZUehC7k "인물 묘사 한국어" "인물 묘사" --save

★함정 메모
 - /video/<VID>/endscreens 직행 URL은 에러 페이지 → 세부정보 사이드패널의 연필을 눌러 연다.
   연필 = '엔딩 화면' 텍스트 오른쪽 약 281 CSS px (ENDSCREEN_DX 로 조정 가능).
 - 저장 버튼은 Locator.click()이 actionability로 타임아웃 → el.evaluate("e=>e.click()") + edit_video POST로 검증.
   (card_video_ui.py와 동일 전략)
"""
import os, sys, time
from playwright.sync_api import sync_playwright

args = sys.argv[1:]
SAVE = "--save" in args
if SAVE:
    args.remove("--save")
VID, SEARCH, FRAG = args[0], args[1], args[2]
DX = int(os.environ.get("ENDSCREEN_DX", "281"))
SH = "scratch/yt"
os.makedirs(SH, exist_ok=True)


def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii", "ignore").decode(), flush=True)


with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(9000)

    posts = []
    def on_req(req):
        try:
            if "/youtubei/v1/" in req.url and req.method == "POST":
                ep = req.url.split("/youtubei/v1/")[1].split("?")[0]
                posts.append(ep)
                if "edit_video" in req.url:
                    log("★ edit_video POST 발생")
        except Exception:
            pass
    pg.on("request", on_req)

    def shot(n):
        try:
            pg.screenshot(path=f"{SH}/es_{VID}_{n}.png", timeout=25000, animations="disabled")
            log("shot " + n)
        except Exception as e:
            log(f"shot {n} 실패 {str(e)[:30]}")

    # 1) 엔딩 화면 편집기 열기
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded")
    time.sleep(8)
    bb = pg.get_by_text("엔딩 화면", exact=True).first.bounding_box()
    pg.mouse.click(bb["x"] + DX, bb["y"] + bb["height"] / 2)
    time.sleep(8)
    if not pg.get_by_role("button", name="요소").count():
        log("★ 편집기 안 열림 — ENDSCREEN_DX 조정 필요"); shot("0_notopen"); sys.exit(1)
    log("엔딩 화면 편집기 열림")

    # 2) 요소 → 동영상
    pg.get_by_role("button", name="요소").first.click(); time.sleep(3)
    shot("1_elements")
    picked_menu = False
    for nm in ("동영상", "동영상 추가"):
        try:
            it = pg.get_by_role("menuitem", name=nm).first
            if not it.count():
                it = pg.locator("tp-yt-paper-item").filter(has_text=nm).first
            if it.count() and it.is_visible(timeout=2500):
                it.click(); picked_menu = True; log(f"'{nm}' 클릭"); break
        except Exception:
            pass
    if not picked_menu:
        log("동영상 메뉴 못찾음"); shot("1b_nomenu"); sys.exit(1)
    time.sleep(4); shot("2_videoopts")

    # 3) '특정 동영상 선택'
    chosen = False
    for nm in ("특정 동영상 선택", "동영상 선택", "특정 동영상"):
        try:
            el = pg.get_by_text(nm, exact=False).first
            if el.count() and el.is_visible(timeout=2500):
                el.click(); chosen = True; log(f"'{nm}' 클릭"); break
        except Exception:
            pass
    if not chosen:
        log("'특정 동영상 선택' 못찾음 — 자동추천으로 빠질 위험, 중단"); shot("2b_nospecific"); sys.exit(1)
    time.sleep(4)

    # 4) 내 동영상 검색 → 결과 클릭
    try:
        sb = pg.get_by_placeholder("내 동영상 검색")
        sb.first.click(); sb.first.fill(SEARCH); time.sleep(4)
        log(f"검색: {SEARCH}")
    except Exception as e:
        log("검색창 실패 " + str(e)[:40])
    shot("3_search")
    picked = False
    try:
        hits = pg.get_by_text(FRAG, exact=False)
        for i in range(hits.count()):
            hb = hits.nth(i).bounding_box()
            if hb and hb["y"] > 200 and hb["x"] < 900:
                pg.mouse.click(hb["x"] + hb["width"] / 2, hb["y"] - 40)   # 썸네일(제목 위)
                picked = True; log(f"결과 클릭 @{round(hb['x'])},{round(hb['y'])}"); break
    except Exception as e:
        log("결과 선택 실패 " + str(e)[:40])
    if not picked:
        log("검색 결과 못찾음"); shot("3b_noresult"); sys.exit(1)
    time.sleep(5); shot("4_videoadded")

    # 5) 요소 → 구독
    try:
        pg.get_by_role("button", name="요소").first.click(); time.sleep(3)
        sub = pg.locator("tp-yt-paper-item").filter(has_text="구독").first
        if sub.count() and sub.is_visible(timeout=2500):
            sub.click(); log("'구독' 요소 추가")
        else:
            log("구독 항목 못찾음(동영상 요소만 유지)")
    except Exception as e:
        log("구독 추가 실패 " + str(e)[:40])
    time.sleep(4); shot("5_subscribe")

    # 6) 저장 — JS 클릭 + edit_video POST 검증
    if SAVE:
        cands = []
        for loc in (pg.get_by_role("button", name="저장"), pg.get_by_text("저장", exact=True)):
            for i in range(loc.count()):
                try:
                    bb2 = loc.nth(i).bounding_box()
                    if bb2 and loc.nth(i).is_enabled():
                        cands.append((loc.nth(i), bb2))
                except Exception:
                    pass
        cands.sort(key=lambda t: -t[1]["x"])
        log(f"저장후보(활성) {len(cands)}개, 오른쪽순 x={[round(c[1]['x']) for c in cands]}")
        for el, bb2 in cands:
            try:
                el.evaluate("e => e.click()"); log(f"  JS저장클릭 @{round(bb2['x'])},{round(bb2['y'])}")
                time.sleep(3)
                if any("edit_video" in p for p in posts):
                    break
            except Exception as e:
                log(f"  JS클릭실패 {str(e)[:22]}")
        time.sleep(8); shot("6_saved")
        ok = any("edit_video" in p for p in posts)
        log(f"저장 {'OK(edit_video)' if ok else 'MISS'}. youtubei POSTs={posts[-8:]}")
    else:
        log("(--save 없음)")
    ctx.close()
print("DONE")
