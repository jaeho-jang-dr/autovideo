# -*- coding: utf-8 -*-
"""NotebookLM 노트북 안의 **기존 산출물**(메모·보고서·가이드)을 열어 본문을 읽어 온다.

    python nlm_artifact.py "<노트북 제목 일부>" "<산출물 제목 일부>"
    python nlm_artifact.py "한글 교육: 자음과 모음" --list        # 산출물 목록만
"""
import argparse
import os
import re

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "research", "nlm")
CDP = "http://localhost:9222"


def log(m):
    print(m, flush=True)


def slug(s):
    return re.sub(r"[^0-9A-Za-z가-힣]+", "_", s)[:50]


def close_backdrop(pg):
    """★노트북을 열면 오버레이 백드롭이 남아 클릭을 가로챈다."""
    for _ in range(4):
        n = pg.evaluate("""() => { const b=[...document.querySelectorAll('.cdk-overlay-backdrop')];
              b.forEach(x=>x.click()); return b.length; }""")
        if not n:
            break
        pg.keyboard.press("Escape")
        pg.wait_for_timeout(1000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("notebook")
    ap.add_argument("artifact", nargs="?")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(CDP)
        pg = b.contexts[0].new_page()
        pg.set_default_timeout(60000)
        pg.goto("https://notebooklm.google.com/", wait_until="domcontentloaded")
        pg.wait_for_timeout(11000)

        hit = pg.evaluate("""(q) => {
          const c=[...document.querySelectorAll('*')].filter(e=>{
            const t=(e.textContent||'').trim();
            return t.includes(q) && t.length<120 && e.getBoundingClientRect().width>60; });
          if(!c.length) return null;
          const el=c[c.length-1]; el.scrollIntoView({block:'center'}); el.click();
          return (el.textContent||'').trim().slice(0,60); }""", a.notebook)
        if not hit:
            log("★노트북 못 찾음: " + a.notebook)
            return 1
        log("노트북: %s" % hit)
        pg.wait_for_timeout(12000)
        close_backdrop(pg)

        if a.list or not a.artifact:
            txt = pg.evaluate("() => document.body.innerText")
            open(os.path.join(OUT, "studio_list.txt"), "w", encoding="utf-8").write(txt)
            log("→ studio_list.txt")
            return 0

        log("[산출물 열기] %s" % a.artifact)
        # ★산출물 카드는 **오른쪽 스튜디오 패널**에 있다. 화면 오른쪽 30% 로 범위를 좁혀야
        #   가운데 채팅 본문에 같은 낱말이 있어도 헛클릭하지 않는다.
        #   제목은 카드에서 잘려 나오므로(…) **앞 12자**로 맞춘다.
        # ★JS el.click() 은 이 카드에 안 먹는다(눌린 표시만 나고 안 열림 — Flow '만들기'와 같은 증상).
        #   **locator.click()** 으로 실제 이벤트를 쏜다.
        key = a.artifact[:12]
        W = pg.evaluate("() => window.innerWidth")
        cards = pg.get_by_text(key, exact=False)
        opened = None
        for i in range(cards.count()):
            c = cards.nth(i)
            try:
                bb = c.bounding_box()
            except Exception:
                continue
            if not bb or bb["x"] < W * 0.68 or bb["height"] < 15:
                continue
            try:
                c.scroll_into_view_if_needed()
                c.click(timeout=15000)
                opened = c.inner_text()[:80].replace("\n", " ")
                break
            except Exception as e:
                log(f"  클릭 실패 #{i}: {str(e)[:300]}")
                # 가로채는 요소가 있으면 force 로 한 번 더
                try:
                    c.click(timeout=8000, force=True)
                    opened = c.inner_text()[:80].replace("\n", " ")
                    log("  (force 클릭 성공)")
                    break
                except Exception as e2:
                    log(f"  force 도 실패: {str(e2)[:120]}")
        if not opened:
            log("  ★산출물 제목을 못 찾았다")
            return 1
        log("  클릭: %s" % opened)
        pg.wait_for_timeout(9000)
        close_backdrop(pg)
        pg.wait_for_timeout(2000)

        tag = "art_" + slug(a.artifact)
        pg.screenshot(path=os.path.join(OUT, tag + ".png"))
        txt = pg.evaluate("() => document.body.innerText")
        open(os.path.join(OUT, tag + ".txt"), "w", encoding="utf-8").write(txt)
        lines = [x.strip() for x in txt.splitlines() if x.strip()]
        log("본문 %d줄 → %s" % (len(lines), os.path.join(OUT, tag + ".txt")))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
