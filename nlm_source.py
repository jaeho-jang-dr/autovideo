# -*- coding: utf-8 -*-
"""열려 있는 NotebookLM 노트북의 **소스 원문**을 읽어 온다.

    python nlm_source.py "drjayed w1d2 ko"
"""
import os
import re
import sys

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "research", "nlm")
CDP = "http://localhost:9222"
TITLE = sys.argv[1]


def log(m):
    print(m, flush=True)


def slug(s):
    return re.sub(r"[^0-9A-Za-z가-힣]+", "_", s)[:60]


with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp(CDP)
    pg = b.contexts[0].new_page()
    pg.set_default_timeout(60000)
    pg.goto("https://notebooklm.google.com/", wait_until="domcontentloaded")
    pg.wait_for_timeout(11000)

    # 노트북 열기
    hit = pg.evaluate("""(q) => {
      const c = [...document.querySelectorAll('*')].filter(e => {
        const t=(e.textContent||'').trim();
        return t.includes(q) && t.length < 120 && e.getBoundingClientRect().width > 60; });
      if (!c.length) return null;
      const el = c[c.length-1]; el.scrollIntoView({block:'center'}); el.click();
      return (el.textContent||'').trim().slice(0,60); }""", TITLE)
    log("노트북 열기: %s" % hit)
    pg.wait_for_timeout(12000)

    # 소스 패널 열기 — 왼쪽 '소스' 목록의 첫 항목을 누른다
    opened = pg.evaluate("""() => {
      // 소스 목록 항목 후보
      const items = [...document.querySelectorAll('[role=listitem], .source-item, button, div')]
        .filter(e => {
          const t=(e.textContent||'').trim();
          const b=e.getBoundingClientRect();
          return b.width>120 && b.height>20 && b.left < 420 &&
                 /\\.(txt|pdf|md|docx)$|소스|Source/i.test(t) === false &&
                 t.length>3 && t.length<90; });
      if (!items.length) return 'no-item';
      items[0].click();
      return (items[0].textContent||'').trim().slice(0,60); }""")
    log("소스 클릭: %s" % opened)
    pg.wait_for_timeout(7000)

    os.makedirs(OUT, exist_ok=True)
    tag = "src_" + slug(TITLE)
    pg.screenshot(path=os.path.join(OUT, tag + ".png"))
    txt = pg.evaluate("() => document.body.innerText")
    open(os.path.join(OUT, tag + ".txt"), "w", encoding="utf-8").write(txt)
    lines = [x.strip() for x in txt.splitlines() if x.strip()]
    log("본문 %d줄 → %s" % (len(lines), os.path.join(OUT, tag + ".txt")))
    for ln in lines:
        log("  " + ln[:120])
