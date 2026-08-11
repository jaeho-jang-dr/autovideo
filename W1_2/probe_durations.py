# -*- coding: utf-8 -*-
"""Flow 설정 칩에 어떤 **길이 옵션**이 있는지 눈으로 확인한다.

★모르고 10s 를 눌러봐야 항목이 없으면 조용히 8초로 나온다 — 생성 한 번을 통째로
  버리게 된다. 그래서 만들기 전에 옵션 목록만 먼저 읽는다.
"""
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from playwright.sync_api import sync_playwright        # noqa: E402
import flow_cdp_pipeline as P                          # noqa: E402
import autoveo_flow as avf                             # noqa: E402


def main():
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
    time.sleep(4)
    P.launch_chrome(os.path.abspath("assets/chrome_profile"))
    time.sleep(3)
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(P.CDP_URL)
        pg = next((p for p in b.contexts[0].pages if "labs.google" in p.url), None) \
            or b.contexts[0].pages[0]
        pg.bring_to_front()
        pg.set_default_timeout(30000)
        avf.open_new_project(pg)
        pg.wait_for_timeout(3000)
        P.open_chip(pg)
        pg.wait_for_timeout(1500)
        opts = pg.evaluate("""() => {
          const out = [];
          for (const b of document.querySelectorAll('button,[role=menuitem],[role=option]')) {
            const r = b.getBoundingClientRect();
            const t = (b.innerText || '').trim();
            if (r.width > 0 && r.left > 900 && t && t.length < 40) out.push(t);
          }
          return out;
        }""")
        print("설정 패널 항목 %d개:" % len(opts))
        for t in opts:
            print("   ", repr(t))
        secs = [t for t in opts if re.match(r"^\d+\s*s$", t)]
        print("\n★길이 옵션:", secs or "(없음 — 길이 선택 항목을 못 찾음)")
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)


if __name__ == "__main__":
    main()
