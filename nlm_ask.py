# -*- coding: utf-8 -*-
"""NotebookLM 노트북에 **질문해서 발췌**해 온다. 답은 그 노트북의 소스에 근거한다.

★소통 방법 (2026-08-11 확정)
  `noterang` 자체 프로필은 로그아웃 상태고 `python -m noterang list` 는 400 을 뱉는다.
  **이미 구글에 로그인된 크롬**(`assets/chrome_profile`, CDP 9222)에 붙으면 그냥 된다.

    python nlm_ask.py "<노트북 제목 일부>" "<질문>"
    python nlm_ask.py "한글 교육: 자음과 모음" "W1-2 …" --wait 180
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("notebook")
    ap.add_argument("question")
    ap.add_argument("--wait", type=int, default=150, help="답 기다리는 최대 초")
    ap.add_argument("--tag", default=None)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(CDP)
        pg = b.contexts[0].new_page()
        pg.set_default_timeout(60000)
        pg.goto("https://notebooklm.google.com/", wait_until="domcontentloaded")
        pg.wait_for_timeout(11000)

        hit = pg.evaluate("""(q) => {
          const c = [...document.querySelectorAll('*')].filter(e => {
            const t=(e.textContent||'').trim();
            return t.includes(q) && t.length < 120 && e.getBoundingClientRect().width > 60; });
          if (!c.length) return null;
          const el = c[c.length-1]; el.scrollIntoView({block:'center'}); el.click();
          return (el.textContent||'').trim().slice(0,60); }""", a.notebook)
        if not hit:
            log("★노트북을 못 찾았다: " + a.notebook)
            return 1
        log("노트북: %s" % hit)
        pg.wait_for_timeout(12000)

        before = pg.evaluate("() => document.body.innerText").strip()

        # ★노트북을 열면 오버레이 백드롭(cdk-overlay-backdrop)이 남아 클릭을 가로챈다.
        #   Esc + 백드롭 클릭으로 먼저 걷어낸다.
        for _ in range(4):
            n = pg.evaluate("""() => {
              const bs=[...document.querySelectorAll('.cdk-overlay-backdrop')];
              bs.forEach(b=>b.click()); return bs.length; }""")
            if not n:
                break
            log("  백드롭 %d개 닫는 중" % n)
            pg.keyboard.press("Escape")
            pg.wait_for_timeout(1200)

        # 채팅 입력창 — aria-label='쿼리 상자' / placeholder='질문하거나 창작하세요'
        box = pg.locator("textarea[aria-label='쿼리 상자']").last
        if not box.count():
            box = pg.locator("textarea[placeholder*='질문']").last
        if not box.count():
            box = pg.locator("textarea").last
        if not box.count():
            box = pg.locator("div[contenteditable='true']").last
        if not box.count():
            log("★질문 입력창을 못 찾았다")
            pg.screenshot(path=os.path.join(OUT, "ask_noinput.png"))
            return 1
        try:
            box.click(timeout=15000)
        except Exception:
            # 그래도 가로채면 포커스만 준다
            box.evaluate("e => e.focus()")
            log("  (클릭 대신 focus)")
        pg.wait_for_timeout(500)
        # ★fill 은 이벤트를 안 일으키는 경우가 있다 — 키보드로 친다
        pg.keyboard.type(a.question, delay=8)
        pg.wait_for_timeout(1200)
        pg.keyboard.press("Enter")
        log("질문 보냄 (%d자)" % len(a.question))

        # 답이 자라는 동안 기다린다 — 본문 길이가 멈추면 끝난 것으로 본다
        prev, stable = -1, 0
        for i in range(a.wait // 5):
            pg.wait_for_timeout(5000)
            cur = len(pg.evaluate("() => document.body.innerText"))
            if cur == prev:
                stable += 1
                if stable >= 3:
                    log("  %ds — 답 안정" % ((i + 1) * 5))
                    break
            else:
                stable = 0
            prev = cur

        tag = a.tag or ("ask_" + slug(a.notebook) + "_" + slug(a.question[:30]))
        pg.screenshot(path=os.path.join(OUT, tag + ".png"))
        after = pg.evaluate("() => document.body.innerText")
        open(os.path.join(OUT, tag + ".txt"), "w", encoding="utf-8").write(after)

        # 늘어난 부분만 뽑아 보여준다
        addl = after[len(before):] if after.startswith(before[:200]) else after
        lines = [x.strip() for x in addl.splitlines() if x.strip()]
        log("→ %s  (%d줄)" % (os.path.join(OUT, tag + ".txt"), len(lines)))
        for ln in lines[:200]:
            log("  " + ln[:120])
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
