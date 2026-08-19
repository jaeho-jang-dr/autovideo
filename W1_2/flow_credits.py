# -*- coding: utf-8 -*-
"""Flow 크레딧 잔량을 읽는다 — 모델별 클립당 소모량을 실측하기 위해.

★사장님 지시(2026-08-12): "이번에는 토큰 양 재 보자."
  레포에 적힌 값(Veo Fast ≈ 12·10 / Lite ≈ 10 / Quality = 100)은 세종 영상 때 것이라
  Veo 3.1 세대·Omni Flash 는 확인된 바 없다. 생성 전후로 잔량을 읽어 차감분을 잰다.

    python W1_2/flow_credits.py           # 잔량 출력
    python W1_2/flow_credits.py --scan    # 후보 텍스트를 전부 덤프(표시 위치가 바뀌었을 때)
"""
import argparse
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from playwright.sync_api import sync_playwright          # noqa: E402
import flow_cdp_pipeline as P                            # noqa: E402

# ★실측 표기는 "8663 Google Flow 크레딧" — 숫자와 '크레딧' 사이에 낱말이 낀다(2026-08-12).
#   "크레딧 1,234" · "1234 credits" 형태도 함께 잡는다.
PAT = re.compile(
    r"([\d,]{2,9})\s*(?:[A-Za-z가-힣]+\s+){0,3}(?:크레딧|credits?)\b"
    r"|(?:크레딧|credits?)\s*[:\s]\s*([\d,]{2,9})", re.I)


def read_credits(pg, scan=False):
    """화면 전체에서 크레딧 표시를 찾는다. 없으면 계정 메뉴를 열어 한 번 더 본다."""
    # ★'크레딧' 글자와 숫자가 **다른 요소**에 나뉘어 있다(2026-08-12 실측).
    #   그래서 그 글자를 찾은 뒤 **조상 3대까지 올라가며 통째 텍스트**를 본다.
    js = """() => {
      const out = [];
      const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let n;
      while ((n = walk.nextNode())) {
        const t = (n.textContent || '').trim();
        if (!t || t.length > 60) continue;
        if (!/크레딧|credit/i.test(t)) continue;
        let e = n.parentElement;
        const r = e ? e.getBoundingClientRect() : null;
        out.push({t: t, x: r ? Math.round(r.left) : -1, y: r ? Math.round(r.top) : -1});
        for (let i = 0; i < 3 && e && e.parentElement; i++) {
          e = e.parentElement;
          const s = (e.innerText || '').replace(/\\s+/g, ' ').trim();
          if (s && s.length <= 200) out.push({t: s, x: -1, y: -1});
        }
      }
      return out;
    }"""
    hits = pg.evaluate(js)
    if scan:
        for h in hits:
            print("    후보 %r  (%s,%s)" % (h["t"], h["x"], h["y"]))
    for h in hits:
        m = PAT.search(h["t"])
        if m:
            return int((m.group(1) or m.group(2)).replace(",", "")), h["t"]
    return None, hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--label", default="")
    a = ap.parse_args()

    P.launch_chrome(os.path.abspath("assets/chrome_profile"))
    time.sleep(3)
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(P.CDP_URL)
        pg = next((p for p in b.contexts[0].pages if "labs.google" in p.url), None) \
            or b.contexts[0].pages[0]
        pg.bring_to_front()
        pg.set_default_timeout(30000)
        if "labs.google" not in pg.url:
            pg.goto("https://labs.google/fx/tools/flow", timeout=60000)
        pg.wait_for_timeout(6000)

        val, info = read_credits(pg, a.scan)
        if val is None:
            print("  ★화면에서 크레딧 표시를 못 찾았다 — 계정 메뉴를 열어 본다")
            # 우상단 아바타/설정을 눌러 본다
            for rx in ("settings", "account_circle", "ULTRA"):
                if P.click_btn(pg, rx, label=rx):
                    pg.wait_for_timeout(2500)
                    val, info = read_credits(pg, a.scan)
                    if val is not None:
                        break
        if val is None:
            print("  ★못 찾음. --scan 으로 후보를 확인하라")
            return 1
        print("  크레딧 %s%s  (원문 %r)" % (val, (" · " + a.label) if a.label else "", info))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
