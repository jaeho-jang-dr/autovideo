# -*- coding: utf-8 -*-
"""카드 편집기가 부르는 read 엔드포인트+스키마 캡처(쓰기 없음). 사용: python cap_cards.py <VID>"""
import time, sys, json
from playwright.sync_api import sync_playwright
VID = sys.argv[1] if len(sys.argv) > 1 else "YTex0QGe17o"
def log(m):
    try: print(m, flush=True)
    except Exception: print(str(m).encode("ascii","ignore").decode(), flush=True)
hits = []
with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222"); ctx = b.contexts[0]
    pgs = [p for p in ctx.pages if "youtube.com" in p.url]
    pg = pgs[-1] if pgs else ctx.new_page(); pg.set_default_timeout(12000)

    def on_resp(resp):
        u = resp.url
        if any(k in u for k in ("video_editor", "edit_video", "get_creator", "endscreen", "info_card", "cards")):
            try: body = resp.json()
            except Exception:
                try: body = resp.text()[:400]
                except Exception: body = "<no body>"
            hits.append((resp.request.method, u.split("?")[0], body))
    pg.on("response", on_resp)

    pg.goto(f"https://studio.youtube.com/video/{VID}/edit", wait_until="domcontentloaded"); time.sleep=__import__("time").sleep
    time.sleep(6)
    # 카드 기능 버튼 눌러 read 유도
    try: pg.get_by_role("button", name="카드", exact=True).first.click(timeout=4000); log("카드버튼 클릭")
    except Exception:
        try: pg.locator("#cards-button").first.click(timeout=4000); log("#cards-button 클릭")
        except Exception as e: log("클릭 실패 "+str(e)[:30])
    time.sleep=__import__("time").sleep; time.sleep(6)

    log(f"=== 캡처 {len(hits)}건 ===")
    for m, u, body in hits:
        log(f"\n### {m} {u}")
        if isinstance(body, (dict, list)):
            s = json.dumps(body, ensure_ascii=False)
            # infoCard/card 관련 키 위주로
            log("keys: " + str(list(body.keys()))[:300] if isinstance(body, dict) else "list")
            idx = s.lower().find("card")
            if idx >= 0: log("...card 구간: " + s[max(0,idx-60):idx+500])
            else: log(s[:400])
        else:
            log(str(body)[:300])
    ctx.close()
print("DONE")
