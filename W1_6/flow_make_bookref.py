# -*- coding: utf-8 -*-
r"""W1_6 인준 — **기준 이미지 한 장**을 Nano Banana(이미지 모드)로 만든다.

★왜 이것이 필요한가 (2026-08-24 · 교정 2차)
  사장님이 씬14(해례본)를 보시고 짚으셨다 —
    "책을 보고 있는 방향을 **좌측 3/4** 으로 바꾸어 줘 · 서 있는 것도 좌측 3/4 으로 ·
     설명하며 책장 넘기는 것도 좌 3/4 으로"
  지금 m21_read_book · m22_turn_page 는 **정면**이라 책이 카메라를 납작하게 마주 본다.

★고칠 수 있는 곳은 프롬프트가 아니라 **기준 이미지**다.
  이 레포에 이미 두 번 적혀 있는 성질이다 —
    · act_defs_v2._RETAKE5 : "front.png 는 빈 손이라 말로 '0초부터 들고 있어라' 해도
      빈 손에서 출발한다" → 그래서 front_book.png 를 만들었다
    · move_defs._DIAG_LOCK : "45도를 지켜라라고 숫자를 못 박으면 Flow 가 8초·10초 둘 다
      실패했다. 그래서 숫자 대신 **첫 프레임의 각도를 그대로 유지하라**고만 말한다"
  → 각도도 소품도 **기준 이미지가 정한다.** 그러니 기준 이미지를
     **좌 3/4 로 서서 그 책을 든 그림**으로 새로 만들어 주는 것이 유일한 길이다.

★입력은 m21 클립의 마지막 부근 프레임(f182)이다.
  · 그 프레임에 **지금 쓰고 있는 바로 그 책**이 있다(마룬 표지·크림색 낱장·어깨 너비).
    책을 새로 그리게 하지 않고 **돌리기만** 시키므로 두 벌의 책이 어긋날 수가 없다.
  · pick_ref.py 로 다른 기준 이미지와 같은 규격에 앉혀 두었다
    (흰 1280x720 · 키 661px · 발끝 y691).

★클릭 경로는 새로 짜지 않는다.
    크롬·프로젝트 = W1_6/flow_make_lv  (동작 36벌·배경 27편을 뽑아 낸 경로)
    기준 이미지 붙이기 = W1_6/flow_make_act.attach_guide
    이미지 모드 전환 = W1_2/flow_make_bg.set_image_mode  (전부 locator.click)
  ★flow_make_pose12.py 는 쓰지 않는다 — 그 안의 kill_chrome() 이
    `taskkill /F /IM chrome.exe` 라 사장님 창까지 닫는다. 여기서는 LV.safe_kill 만 쓴다.

    python W1_6/flow_make_bookref.py                       # 좌 3/4 책 기준 만들기
    python W1_6/flow_make_bookref.py --in ... --out ...
"""
import argparse
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_6"))
os.chdir(ROOT)

for _st in (sys.stdout, sys.stderr):
    try:
        _st.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from playwright.sync_api import sync_playwright          # noqa: E402
import autoveo_flow as avf                               # noqa: E402
import flow_make_lv as LV                                # noqa: E402
import flow_make_act as FMA                              # noqa: E402
from W1_2 import flow_make_bg as BG                      # noqa: E402

PROFILE = FMA.PROFILE                                    # assets/chrome_profile_0
PORT = FMA.PORT                                          # 9344
SHOT = "W1_6/_actfail"
GEN_WAIT = 240

IN_DEFAULT = "scratch/injun_ref_facing_left_3q.png"
OUT_DEFAULT = "scratch/injun_pure_flow_left_hangul.png"

# ── 프롬프트 ─────────────────────────────────────────────────────────
PROMPT = """Using the uploaded reference image, keep the EXACT same Korean boy character Injun:
- Same friendly face, same smiling eyes, same short neat black hair
- Same navy blue short-sleeve t-shirt
- Same beige chino trousers and white sneakers
- Same minimalist 2D clean line art illustration style with bold crisp black outlines and solid flat colors.

POSE & ORIENTATION:
- Standing full body from head to shoes, exactly matching the three-quarter angle facing LEFT as shown in the reference image (facing 45 degrees toward the left side of the frame).
- He is holding a closed traditional Korean antique Hanji book (Hunminjeongeum) with both hands held in front of his chest.

THE TRADITIONAL KOREAN ANTIQUE BOOK:
- An authentic vintage light-tan mulberry Hanji paper book cover with traditional Korean stitched binding on the spine.
- On the front cover of the book, there is a clean white rectangular vertical title label strip.
- On this white label strip, the exact Korean Hangul letters "훈민정음" are printed vertically down in elegant black Korean ink:
  훈
  민
  정
  음
- The Korean letters must be standard readable upright Korean Hangul, perfectly legible and clear.

COMPOSITION:
- ONE single full-body figure standing on a flat solid pure white background (#FFFFFF).
- Clear empty space around the character, no extra objects, no tables, no other text."""


def log(m):
    print(m, flush=True)


def make(img, out, prompt, profile=PROFILE, port=PORT):
    img = os.path.abspath(img)
    out = os.path.abspath(out)
    if not os.path.exists(img):
        raise RuntimeError("입력 이미지 없음: " + img)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    os.makedirs(SHOT, exist_ok=True)
    prompt = re.sub(r"[ \t]+", " ", prompt).strip()

    cdp = LV.launch(profile, port)
    time.sleep(3)
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(cdp)
        pg = next((p for p in b.contexts[0].pages if "labs.google" in p.url), None) \
            or b.contexts[0].pages[0]
        pg.bring_to_front()
        pg.set_default_timeout(30000)

        log("  [1] 새 프로젝트")
        if not LV.ensure_project(pg):
            raise RuntimeError("프롬프트 창이 안 뜬다 — 프로젝트가 안 열렸다")
        pg.wait_for_timeout(3000)

        log("  [2] 기준 이미지 붙이기 (%s)" % os.path.basename(img))
        FMA.attach_guide(pg, img)

        log("  [3] 이미지 모드 · Nano Banana")
        BG.set_image_mode(pg)

        log("  [4] 프롬프트 → 만들기 (%d자)" % len(prompt))
        before = pg.evaluate(
            "() => [...document.querySelectorAll('img')].map(v=>v.currentSrc||v.src||'')"
            ".filter(s=>s&&s.startsWith('http'))")
        avf.fill_prompt(pg, prompt)
        pg.wait_for_timeout(1500)
        btn = pg.locator("button").filter(has_text=re.compile("arrow_forward")).filter(
            has_text=re.compile("만들기|Create|Generate")).last
        if btn.count() == 0:
            raise RuntimeError("'만들기' 버튼 없음")
        btn.scroll_into_view_if_needed()
        btn.click(timeout=15000)
        log("    만들기(→) locator 클릭")
        pg.wait_for_timeout(4000)
        left = pg.evaluate(FMA.JS_LEFT)
        log("    프롬프트 잔여 %d자 (원문 %d자)" % (left, len(prompt)))
        if left > len(prompt) * 0.5:
            log("    안 눌린 것 같다 — 한 번 더")
            try:
                btn.click(timeout=10000)
                pg.wait_for_timeout(4000)
            except Exception as e:
                log("    재클릭 실패: " + str(e)[:60])

        log("  [5] 생성 대기 (최대 %d초)" % GEN_WAIT)
        src, step = None, 10
        for i in range(GEN_WAIT // step):
            pg.wait_for_timeout(step * 1000)
            now = [s for s in pg.evaluate(
                "() => [...document.querySelectorAll('img')].map(v=>v.currentSrc||v.src||'')"
                ".filter(s=>s&&s.startsWith('http'))") if s not in before]
            if now:
                src = now[0]
                log("    %ds — 새 이미지 확인" % ((i + 1) * step))
                break
        if not src:
            try:
                pg.screenshot(path=os.path.join(SHOT, "bookref_fail.png"))
                open(os.path.join(SHOT, "bookref_fail.txt"), "w", encoding="utf-8").write(
                    pg.evaluate("() => document.body.innerText"))
                log("    [실패화면] %s/bookref_fail.png (+txt)" % SHOT)
            except Exception:
                pass
            raise RuntimeError("생성 실패(시간 초과)")

        log("  [6] 내려받기")
        r = pg.context.request.get(src, timeout=180000)
        body = r.body()
        if r.status != 200 or len(body) < 10000:
            raise RuntimeError("내려받기 실패 status=%s %dB" % (r.status, len(body)))
        open(out, "wb").write(body)
        log("  OK %s  %dKB" % (out, os.path.getsize(out) // 1024))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", default=IN_DEFAULT)
    ap.add_argument("--out", default=OUT_DEFAULT)
    ap.add_argument("--profile", default=PROFILE)
    ap.add_argument("--port", type=int, default=PORT)
    a = ap.parse_args()

    log("입력 %s → 출력 %s" % (a.src, a.out))
    LV.safe_kill(a.profile)
    time.sleep(6)
    try:
        make(a.src, a.out, PROMPT, a.profile, a.port)
        rc = 0
    except Exception as e:
        log("  ★실패: %s" % str(e)[:220])
        rc = 1
    LV.safe_kill(a.profile)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
