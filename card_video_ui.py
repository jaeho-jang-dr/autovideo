# -*- coding: utf-8 -*-
"""동영상 카드를 UI로 추가(검증된 경로). 사용:
python card_video_ui.py <VID> <search1> <titlefrag1> <time1> [<search2> <titlefrag2> <time2>] ... [--save]
예: python card_video_ui.py YTex0QGe17o "한국어 숫자" "한국어 숫자" 0:30 "한국어 인사말" "한국어 인사말" 3:45 --save"""
import time, sys, base64
from playwright.sync_api import sync_playwright

args = sys.argv[1:]
SAVE = "--save" in args
if SAVE: args.remove("--save")
VID = args[0]
rest = args[1:]
CARDS = [(rest[i], rest[i+1], rest[i+2]) for i in range(0, len(rest), 3)]

def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii","ignore").decode(), flush=True)

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(8000)
    def shot(n):
        pass  # 스크린샷 비활성(CDP send가 hang 유발) — 검증은 별도 순수CDP로
    posts = []
    def on_req(req):
        try:
            if "/youtubei/v1/" in req.url and req.method == "POST":
                ep = req.url.split("/youtubei/v1/")[1].split("?")[0]
                posts.append(ep)
                if "edit_video" in req.url:
                    open("scratch/yt/ev_save.json", "w", encoding="utf-8").write(req.post_data or "")
                    log("★ edit_video POST 발생")
        except Exception: pass
    pg.on("request", on_req)

    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); time.sleep(6)
    pg.get_by_role("button", name="카드", exact=True).first.click(timeout=6000); time.sleep(3)
    log("카드 편집기 열림")

    for idx, (search, frag, tstr) in enumerate(CARDS):
        log(f"--- 카드{idx+1}: '{search}' @ {tstr} ---")
        pg.get_by_role("button", name="카드 추가").first.click(timeout=6000); time.sleep(2)
        pg.mouse.click(272, 134); time.sleep(3)  # 동영상 옵션
        # 내 동영상 검색
        try:
            sb = pg.get_by_placeholder("내 동영상 검색")
            sb.first.click(); sb.first.fill(search); time.sleep(3)
            log(f"검색: {search}")
        except Exception as e: log("검색 실패 " + str(e)[:40])
        shot(f"cvu_{idx+1}_search")
        # 결과 클릭(제목 조각 매칭, 보이는 것)
        picked = False
        try:
            hits = pg.get_by_text(frag, exact=False)
            for i in range(hits.count()):
                bb = hits.nth(i).bounding_box()
                if bb and bb["y"] > 200 and bb["x"] < 900:
                    pg.mouse.click(bb["x"] + bb["width"]/2, bb["y"] - 40)  # 썸네일(제목 위) 클릭
                    picked = True; log(f"결과 클릭 @{round(bb['x'])},{round(bb['y'])}"); break
        except Exception as e: log("선택 실패 " + str(e)[:40])
        if not picked: log("결과 못찾음"); shot(f"cvu_{idx+1}_noresult")
        time.sleep(3); shot(f"cvu_{idx+1}_picked")
        # 티저 시작 시간 (env SET_TIME=1 일 때만; 마스크드 필드가 hang 유발해 기본 OFF)
        import os as _os
        if _os.environ.get("SET_TIME") == "1":
            try:
                tf = pg.locator("input[aria-label*='티저 시작 시간']").first
                tf.click(timeout=2500); time.sleep(0.3)
                pg.keyboard.press("Control+A"); pg.keyboard.press("Delete"); time.sleep(0.2)
                pg.keyboard.type(tstr, delay=50); pg.keyboard.press("Enter"); log(f"티저 시각 {tstr} 입력")
            except Exception as e: log("시각 스킵 " + str(e)[:40])
        else:
            log(f"시각 설정 생략(기본 0:00). 목표={tstr}")
        time.sleep(1.0)

    try: log(f"저장전 동영상카드수={pg.get_by_text('동영상 카드', exact=True).count()}")
    except Exception as e: log("카운트err " + str(e)[:30])
    if SAVE:
        # 모든 '저장' 후보 덤프+활성화된 것 모두 클릭(어느게 edit_video 쏘는지)
        cands = []
        for loc in (pg.get_by_role("button", name="저장"), pg.get_by_text("저장", exact=True)):
            for i in range(loc.count()):
                try:
                    bb = loc.nth(i).bounding_box(); en = loc.nth(i).is_enabled()
                    cands.append((loc.nth(i), bb, en))
                except Exception: pass
        # 활성+bbox 있는 것만, x 내림차순(가장 오른쪽=검은 저장버튼) 정렬해 첫번째만 클릭
        good = [(el, bb) for (el, bb, en) in cands if en and bb]
        good.sort(key=lambda t: -t[1]["x"])
        log(f"저장후보(활성) {len(good)}개, 오른쪽순 x={[round(b['x']) for _,b in good]}")
        # ★JS 클릭(actionability 우회) — 활성 후보를 오른쪽부터 순회, edit_video POST 뜨면 중단
        fired = False
        for el, bb in good:
            try:
                el.evaluate("e => e.click()"); log(f"  JS저장클릭 @{round(bb['x'])},{round(bb['y'])}")
                time.sleep(3)
                if any("edit_video" in p for p in posts): fired = True; break
            except Exception as e:
                log(f"  JS클릭실패 {str(e)[:22]}")
        time.sleep(8); log(f"저장 {'OK(edit_video)' if (fired or any('edit_video' in p for p in posts)) else 'MISS'}. youtubei POSTs={posts[-8:]}")
    else:
        log("(--save 없음)")
    ctx.close()
print("DONE")
