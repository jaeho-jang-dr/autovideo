# -*- coding: utf-8 -*-
"""AI 고지(변경된 콘텐츠 = 예) 를 스튜디오 UI 로 설정한다.

★API 로는 안 된다 — videos.insert 에 containsSyntheticMedia=True 를 넣어도
  응답이 None 으로 돌아온다(W24R·titan 실측). 그래서 UI 로만 잡힌다.

사용: python yt_ai_disclosure.py <VID>
"""
import sys
import time

from playwright.sync_api import sync_playwright

VID = sys.argv[1]
SH = "scratch/yt"


def log(m):
    print(m, flush=True)


def shot(pg, n):
    import os
    os.makedirs(SH, exist_ok=True)
    p = f"{SH}/ai_{VID}_{n}.png"
    try:
        pg.screenshot(path=p)
        log(f"    [shot] {p}")
    except Exception as e:
        log(f"    shot 실패 {str(e)[:40]}")


with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222")
    ctx = b.contexts[0]
    pg = ctx.new_page()
    pg.set_default_timeout(30000)
    pg.goto(f"https://studio.youtube.com/video/{VID}/edit",
            wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    shot(pg, "0_edit")

    # '모두 표시' / '자세히 보기' 를 눌러 하단 항목까지 펼친다
    for name in ("자세히 보기", "모두 표시", "SHOW MORE"):
        try:
            el = pg.get_by_text(name, exact=False).first
            if el.count() and el.is_visible():
                el.click(timeout=4000)
                pg.wait_for_timeout(2500)
                log(f"  '{name}' 펼침")
                break
        except Exception:
            pass
    shot(pg, "1_expanded")

    # ★2026-08-10 UI 실측 — 항목 이름이 '변경된 콘텐츠'가 아니라 **'AI 사용'** 이다.
    #   물음: "다음과 같은 방식으로 AI를 사용하여 콘텐츠를 생성하거나 수정했나요?" → 예/아니요
    found = False
    for step in range(16):
        hit = pg.evaluate("""() => {
          for (const el of document.querySelectorAll('*')) {
            const t = (el.textContent||'').trim();
            if (t.length < 120 && t === 'AI 사용') { el.scrollIntoView({block:'center'}); return t; }
          }
          return null; }""")
        if hit:
            log(f"  'AI 사용' 섹션 발견 (스크롤 {step})")
            pg.wait_for_timeout(1500)
            shot(pg, "2_section")
            found = True
            break
        pg.mouse.wheel(0, 900)
        pg.wait_for_timeout(600)

    if found:
        # ★'예' 라디오는 **AI 사용 물음 아래 것**만 골라야 한다(아동용 '예'를 누르면 안 된다)
        clicked = pg.evaluate("""() => {
          const q = '다음과 같은 방식으로 AI를 사용';
          const owns = [...document.querySelectorAll('*')].filter(e => {
            const t=(e.textContent||'').trim();
            return t.includes(q) && t.length < 2500; });
          const sec = owns[owns.length-1];
          if (!sec) return 'no-sec';
          const radios = [...sec.querySelectorAll("tp-yt-paper-radio-button,[role='radio']")];
          for (const r of radios) {
            const t=(r.textContent||'').trim();
            if (t === '예') { r.click(); return 'clicked 예 / radios=' + radios.length; }
          }
          return 'no-yes radios=' + radios.length + ' texts=' +
                 radios.map(r=>(r.textContent||'').trim().slice(0,12)).join('|'); }""")
        log(f"  라디오 클릭 결과: {clicked}")
        pg.wait_for_timeout(2000)
    shot(pg, "3_selected")

    if not found:
        log("★'변경된 콘텐츠' 항목을 못 찾았다 — 화면 캡처 확인 필요")

    # 저장
    for nm in ("저장", "SAVE"):
        try:
            btn = pg.locator(f"ytcp-button:has-text('{nm}')").first
            if btn.count():
                btn.evaluate("e => e.click()")
                pg.wait_for_timeout(4000)
                log(f"  '{nm}' 클릭")
                break
        except Exception:
            pass
    shot(pg, "4_saved")
    time.sleep(1)
    log("완료")
