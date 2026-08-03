# -*- coding: utf-8 -*-
"""W24 플래시몹 — Flow 군무 클립 4개 생성 (2026-07-28).

★사장님 확정 절차 (이대로만)
 1. 프롬프트 창에 **@이름** 으로 7캐릭터를 모두 부른다
 2. 이어서 상황 프롬프트를 넣는다 (예: @injun 과 @jieun 이 마주보고 춤춘다)
 3. 실행(→) 누르고 생성 대기
 4. 생성물 다운로드
 5. **마지막 컷을 이미지로 뽑아 업로드** → 그것을 첫 프레임으로 다음 클립
 6. 2~5를 반복해 4장

★모델은 **Omni Flash** 여야 한다 — 참조 7개까지. Veo 3.1은 3개까지라 7명 동시 불가.

사용:
  python flow_make_dance.py 1        # 1번 클립만
  python flow_make_dance.py all      # 1~4 연속
"""
import os
import re
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
OUT = "W24/dance"
DL = "debug/downloads"
SH = "scratch/yt"
os.makedirs(OUT, exist_ok=True)
os.makedirs(SH, exist_ok=True)

CALL = "@injun @zollaman @teacherjay @stickman @jieun @zollagirl @madamjay"

TAIL = (" STYLE: flat cartoon illustration, bold clean black outlines, flat colours. "
        "@stickman @zollagirl @zollaman stay hand-drawn ink line figures; @jieun @injun @madamjay "
        "@teacherjay stay fully coloured cartoon people. "
        "HEIGHT ORDER: @injun tallest, then @zollaman, then @teacherjay and @stickman, then @jieun, "
        "then @zollagirl, then @madamjay shortest. "
        "Each character has exactly one head, two arms with two hands and two legs - no extra or "
        "missing limbs. Everyone stays whole and fully inside the frame. "
        "No text, no letters, no logos, no watermark. 16:9.")

CLIPS = {
 1: (CALL + " dance a flash mob in a wide evening plaza in front of a silver curved modern building, "
     "surrounded by a ring of onlookers. @teacherjay starts alone in the middle, raising his right arm "
     "high and waving twice. The move spreads outward like a wave - @zollaman copies it, then "
     "@zollagirl, then @stickman, then @injun, then @jieun, then @madamjay, each half a beat later, "
     "so the wave visibly travels. By the end all seven move together on the same beat in a loose "
     "semicircle facing the camera, and the onlookers start clapping." + TAIL),

 2: (CALL + " keep dancing in the same plaza, sky turning orange. Each one dances DIFFERENTLY. "
     "@zollaman and @zollagirl HOLD BOTH HANDS and dance as a couple - swinging their joined arms "
     "side to side, spinning once around each other, then leaning back pulling against each other's "
     "hands, laughing. @injun and @jieun FACE EACH OTHER and mirror each other's steps like a call "
     "and response, never touching. @madamjay turns to the onlookers and claps overhead, pulling them "
     "into the rhythm. @teacherjay conducts from the middle, pointing to each pair in turn. "
     "@stickman leaves the group and walks INTO the crowd, weaving between the onlookers and leading "
     "them; his ink lines glow like a bright neon tube." + TAIL),

 3: (CALL + " seen from a HIGH OVERHEAD SHOT looking down at the whole plaza at dusk, neon lights "
     "switching on around the square. @stickman, glowing bright in the dark crowd, runs through the "
     "mass of people drawing a path with his own light, leading them into a formation. The onlookers "
     "he passes follow him and stop where he places them, so a shape builds out of the crowd. Seen "
     "from above the standing people slowly form two large Korean letter blocks on the plaza floor. "
     "The other six dance in the open space between the two blocks, still on the beat. The letters "
     "are formed by BODIES AND THE GLOWING TRAIL ONLY - do not draw or overlay any printed text or "
     "graphic letters." + TAIL),

 4: (CALL + " finish the flash mob. The crowd formation holds for one beat, then the camera drops "
     "back down to eye level at the front of the plaza, now fully night with coloured neon reflecting "
     "off the ground. The seven run forward out of the formation and line up in one row facing the "
     "camera, left to right: @injun, @zollaman, @teacherjay, @stickman, @jieun, @zollagirl, "
     "@madamjay. On the final beat they finish together - both arms thrown wide and up in a big V - "
     "and hold perfectly still, smiling straight at the camera. The crowd behind them freezes "
     "mid-cheer. @stickman still glows, the brightest thing in the frame. The camera pulls back and "
     "rises." + TAIL),
}


def log(m):
    print(m, flush=True)


def shot(pg, n):
    try:
        pg.screenshot(path=f"{SH}/dance_{n}.png", timeout=20000, animations="disabled")
    except Exception:
        pass


def project_page(ctx):
    pg = next((p for p in ctx.pages if "/project/" in p.url and "/character" not in p.url), None)
    if pg is None:
        pg = next((p for p in ctx.pages if "labs.google" in p.url), ctx.new_page())
    pg.bring_to_front()
    if "/character" in pg.url:
        pg.goto(pg.url.split("/character")[0], wait_until="domcontentloaded")
        time.sleep(10)
    return pg


def type_prompt(pg, text):
    """프롬프트 창에 @호출 + 상황을 넣는다. @ 자동완성 팝업이 뜨면 Escape 로 닫는다."""
    box = next((e for e in pg.query_selector_all("div[role='textbox'],textarea")
                if e.is_visible()), None)
    if box is None:
        return False
    box.click()
    time.sleep(0.5)
    pg.keyboard.press("Control+A")
    pg.keyboard.press("Delete")
    for chunk in re.findall(r"@\w+|[^@]+", text):
        pg.keyboard.type(chunk, delay=8)
        if chunk.startswith("@"):
            time.sleep(1.2)          # 자동완성 목록이 뜨는 시간
            pg.keyboard.press("Enter")   # 첫 후보(등록한 캐릭터) 확정
            time.sleep(0.4)
    return True


def generate(pg, n):
    log(f"[{n}] 프롬프트 입력")
    if not type_prompt(pg, CLIPS[n]):
        log("  ★프롬프트 창 없음"); return None
    time.sleep(2)
    shot(pg, f"{n}_prompt")
    ok = pg.evaluate("""() => {
        const b = [...document.querySelectorAll('button')]
            .find(e => /arrow_forward/.test((e.innerText||'') + (e.getAttribute('aria-label')||'')));
        if (!b) return false; b.click(); return true;
    }""")
    log(f"  실행: {ok}")
    if not ok:
        return None
    log("  생성 대기 120초")
    time.sleep(120)
    shot(pg, f"{n}_made")
    return True


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "1"
    nums = [1, 2, 3, 4] if which == "all" else [int(which)]
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://localhost:9222")
        ctx = b.contexts[0]
        pg = project_page(ctx)
        log(f"URL: {pg.url[:90]}")
        for n in nums:
            generate(pg, n)
            log(f"[{n}] → 화면에서 결과 확인 후 다운로드 (scratch/yt/dance_{n}_made.png)")


if __name__ == "__main__":
    main()
