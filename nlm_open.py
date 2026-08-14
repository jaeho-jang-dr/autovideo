# -*- coding: utf-8 -*-
"""NotebookLM 노트북을 열어 내용을 그대로 받아온다.

★소통 방법 (2026-08-11 확정)
  `noterang` 자체 프로필은 **로그아웃 상태**고 `python -m noterang list` 는 **400** 을 뱉는다.
  이미 구글에 로그인된 크롬(`assets/chrome_profile`, CDP 9222)에 붙으면 그냥 된다.
  크롬 기동: chrome.exe --remote-debugging-port=9222 --user-data-dir=<autovideo>/assets/chrome_profile

    python nlm_open.py --list                 # 노트북 목록
    python nlm_open.py "drjayed w1d2 ko"      # 그 노트북을 열고 전부 덤프
"""
import argparse
import os
import re
import sys

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "research", "nlm")
CDP = "http://localhost:9222"


def log(m):
    print(m, flush=True)


def slug(s):
    return re.sub(r"[^0-9A-Za-z가-힣]+", "_", s)[:60]


def dump(pg, tag):
    os.makedirs(OUT, exist_ok=True)
    try:
        pg.screenshot(path=os.path.join(OUT, tag + ".png"))
    except Exception as e:
        log(f"  캡처 실패 {str(e)[:50]}")
    txt = pg.evaluate("() => document.body.innerText")
    open(os.path.join(OUT, tag + ".txt"), "w", encoding="utf-8").write(txt)
    return txt


def notebooks(txt):
    """대시보드 본문에서 (제목, 소스수) 를 뽑는다 — '소스 N개' 앞줄이 제목."""
    lines = [x.strip() for x in txt.splitlines() if x.strip()]
    out = []
    for i, l in enumerate(lines):
        m = re.match(r"^소스 (\d+)개", l)
        if m and i >= 1:
            out.append((lines[i - 1], int(m.group(1))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("title", nargs="?", help="열 노트북 제목(부분일치)")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(CDP)
        pg = b.contexts[0].new_page()
        pg.set_default_timeout(60000)
        pg.goto("https://notebooklm.google.com/", wait_until="domcontentloaded")
        pg.wait_for_timeout(11000)

        txt = dump(pg, "00_dashboard")
        nbs = notebooks(txt)
        log("노트북 %d개" % len(nbs))
        if a.list or not a.title:
            for t, n in nbs:
                log("  %-52s 소스 %d" % (t[:52], n))
            return 0

        log("[열기] '%s'" % a.title)
        hit = pg.evaluate("""(q) => {
          const cands = [...document.querySelectorAll('*')].filter(e => {
            const t = (e.textContent||'').trim();
            return t.includes(q) && t.length < 120 && e.getBoundingClientRect().width > 60;
          });
          if (!cands.length) return null;
          const el = cands[cands.length-1];
          el.scrollIntoView({block:'center'});
          el.click();
          return (el.textContent||'').trim().slice(0,80); }""", a.title)
        if not hit:
            log("  ★제목을 못 찾았다 — --list 로 정확한 제목을 확인해라")
            return 1
        log("  클릭: %s" % hit)
        pg.wait_for_timeout(12000)
        log("  URL: %s" % pg.url)

        body = dump(pg, "nb_" + slug(a.title))
        lines = [x.strip() for x in body.splitlines() if x.strip()]
        log("  본문 %d줄 → %s" % (len(lines), os.path.join(OUT, "nb_" + slug(a.title) + ".txt")))
        for ln in lines[:80]:
            log("    " + ln[:110])
        return 0


if __name__ == "__main__":
    sys.exit(main())
