# -*- coding: utf-8 -*-
"""W1-2 삽화 카드 생성 — **텍스트 전용**(업로드 없음) · 이미지 모드.

`flow_make_bg.py` 의 정지 이미지 경로와 같다. 카드는 참조 이미지가 필요 없으므로
새 프로젝트에서 곧바로 프롬프트를 넣는다. 모든 클릭은 **locator.click()**.

    python W1_2/flow_make_card.py --all
    python W1_2/flow_make_card.py oi
"""
import argparse
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

from playwright.sync_api import sync_playwright          # noqa: E402
import flow_cdp_pipeline as P                            # noqa: E402
import autoveo_flow as avf                               # noqa: E402
from W1_2 import flow_make_bg as BG                      # noqa: E402
import card_defs as D                                    # noqa: E402

OUT = "W1_2/cards"
SHOT = "W1_2/_failshot"
GEN_WAIT = 180
COOL = 10


def log(m):
    print(m, flush=True)


def kill_chrome():
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True, text=True)


def make_one(key):
    prompt = re.sub(r"[ \t]+", " ", D.prompt(key)).strip()
    out = os.path.abspath(os.path.join(OUT, "card_%s.png" % key))
    os.makedirs(OUT, exist_ok=True)

    P.launch_chrome(os.path.abspath("assets/chrome_profile"))
    time.sleep(3)
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(P.CDP_URL)
        pg = next((p for p in b.contexts[0].pages if "labs.google" in p.url), None) \
            or b.contexts[0].pages[0]
        pg.bring_to_front()
        pg.set_default_timeout(30000)

        log("  [1] 새 프로젝트")
        avf.open_new_project(pg)
        pg.wait_for_timeout(3500)

        log("  [2] 이미지 모드 · Nano Banana")
        BG.set_image_mode(pg)

        log("  [3] 프롬프트 → 만들기 (%d자)" % len(prompt))
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
        pg.wait_for_timeout(4000)
        left = pg.evaluate("""() => { const b=document.querySelector("div[role='textbox'][contenteditable='true']");
            return b ? (b.innerText||'').trim().length : -1; }""")
        log("    프롬프트 잔여 %d자 (원문 %d자)" % (left, len(prompt)))
        if left > len(prompt) * 0.5:
            try:
                btn.click(timeout=10000)
                pg.wait_for_timeout(4000)
            except Exception as e:
                log("    재클릭 실패: " + str(e)[:60])

        log("  [4] 생성 대기 (최대 %d초)" % GEN_WAIT)
        src = None
        for i in range(GEN_WAIT // 10):
            pg.wait_for_timeout(10000)
            now = [s for s in pg.evaluate(
                "() => [...document.querySelectorAll('img')].map(v=>v.currentSrc||v.src||'')"
                ".filter(s=>s&&s.startsWith('http'))") if s not in before]
            if now:
                src = now[0]
                log("    %ds — 새 이미지 확인" % ((i + 1) * 10))
                break
        if not src:
            os.makedirs(SHOT, exist_ok=True)
            try:
                pg.screenshot(path=os.path.join(SHOT, "card_%s_fail.png" % key))
            except Exception:
                pass
            raise RuntimeError("생성 실패(시간 초과)")

        log("  [5] 내려받기")
        data = pg.evaluate("""async (u) => {
            const r = await fetch(u); const b = await r.arrayBuffer();
            return Array.from(new Uint8Array(b)); }""", src)
        open(out, "wb").write(bytes(data))
        if os.path.getsize(out) < 10000:
            raise RuntimeError("내려받기 실패(%d바이트)" % os.path.getsize(out))
        log("  ✅ %s  %dKB" % (out, os.path.getsize(out) // 1024))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    keys = a.keys
    if a.all or not keys:
        keys = [k for k, _, _, _ in D.CARDS
                if not os.path.exists(os.path.join(OUT, "card_%s.png" % k))]
    if not keys:
        log("대상 없음")
        return 0
    ok, fail = [], []
    for i, k in enumerate(keys, 1):
        w = D.BY[k][0]
        log("\n%s\n[%d/%d] %s (%s)\n%s" % ("=" * 54, i, len(keys), k, w, "=" * 54))
        kill_chrome()
        time.sleep(COOL)
        try:
            make_one(k)
            ok.append(k)
        except Exception as e:
            log("  ★%s 실패: %s" % (k, str(e)[:140]))
            fail.append(k)
        kill_chrome()
        time.sleep(COOL)
    log("\n완료 %d/%d" % (len(ok), len(keys)))
    if fail:
        log("실패: " + ", ".join(fail))
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
