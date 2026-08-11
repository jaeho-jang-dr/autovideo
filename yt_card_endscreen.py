# -*- coding: utf-8 -*-
"""정보 카드 / 최종 화면 — 2026-08-10 새 편집기 UI 기준.

★UI 가 또 바뀌었다. card_w24.py / endscreen_w24.py 의 경로(행의 '수정'·'+')는 없어졌고,
  편집기 안에 **'정보 카드 추가' · '최종 화면 추가' 버튼이 직접** 있다.

사용:
    python yt_card_endscreen.py card <VID> "<검색어>"
    python yt_card_endscreen.py end  <VID> "<검색어>"
    python yt_card_endscreen.py dump <VID> card|end     # 패널 구조만 본다
"""
import os
import sys

from playwright.sync_api import sync_playwright

MODE = sys.argv[1]
VID = sys.argv[2]
ARG = sys.argv[3] if len(sys.argv) > 3 else ""
SH = "scratch/yt"
os.makedirs(SH, exist_ok=True)


def log(m):
    print(m, flush=True)


def shot(pg, n):
    p = f"{SH}/ce_{VID}_{n}.png"
    try:
        pg.screenshot(path=p)
        log(f"    [shot] {p}")
    except Exception as e:
        log(f"    shot 실패 {str(e)[:40]}")


def open_editor(pg):
    pg.goto(f"https://studio.youtube.com/video/{VID}/editor",
            wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    # ★'시작하기' 를 누르지 않으면 편집기가 안 열린다
    for nm in ("시작하기", "Get started"):
        try:
            el = pg.get_by_text(nm, exact=False).first
            if el.count() and el.is_visible():
                el.evaluate("e => e.click()")
                pg.wait_for_timeout(6000)
                log(f"  '{nm}' 클릭")
                break
        except Exception:
            pass


def click_add(pg, label):
    """'정보 카드 추가' / '최종 화면 추가' 버튼 — aria-label 로 잡는다."""
    n = pg.evaluate("""(lab) => {
      const cands = [...document.querySelectorAll('button,ytcp-button,[role=button]')]
        .filter(e => ((e.innerText||'') + ' ' + (e.getAttribute('aria-label')||'')).includes(lab));
      if (!cands.length) return 0;
      cands[0].click();
      return cands.length; }""", label)
    log(f"  '{label}' 클릭 (후보 {n}개)")
    pg.wait_for_timeout(4500)
    return n


def pick_kind_video(pg):
    """'정보 카드 추가' 를 누르면 동영상/재생목록/채널/링크 드롭다운이 뜬다 → '동영상'."""
    n = pg.evaluate("""() => {
      const items = [...document.querySelectorAll('tp-yt-paper-item,[role=option],[role=menuitem],li,button')]
        .filter(e => (e.innerText||'').trim() === '동영상');
      if (!items.length) return 0;
      items[items.length-1].click();
      return items.length; }""")
    log(f"  '동영상' 선택 (후보 {n}개)")
    pg.wait_for_timeout(4500)
    return n


def dump_panel(pg, tag):
    shot(pg, tag)
    txt = pg.evaluate("() => document.body.innerText")
    lines = [x.strip() for x in txt.splitlines() if x.strip()]
    log("  --- 화면 문구 %d줄 ---" % len(lines))
    for x in lines[-45:]:
        log("    " + x[:95])
    btns = pg.evaluate("""() => [...document.querySelectorAll('button,ytcp-button,[role=button],tp-yt-paper-item')]
        .map(e => (e.innerText||e.getAttribute('aria-label')||'').trim())
        .filter(t => t && t.length < 40)""")
    log("  --- 버튼 ---")
    for t in list(dict.fromkeys(btns)):
        log("    " + t)


def pick_specific(pg):
    """최종 화면 전용 — '동영상 요소' 는 기본이 **'최근 업로드된 동영상'** 이다.
    ★그대로 두면 특정 영상이 아니라 '최근 업로드'가 걸린다(W23 실패 원인).
      반드시 '특정 동영상 선택' 라디오를 먼저 누른다."""
    n = pg.evaluate("""() => {
      const rs = [...document.querySelectorAll("tp-yt-paper-radio-button,[role=radio]")]
        .filter(e => (e.textContent||'').includes('특정 동영상 선택'));
      if (!rs.length) return 0;
      rs[0].click();
      return rs.length; }""")
    log(f"  '특정 동영상 선택' 라디오 클릭 (후보 {n}개)")
    pg.wait_for_timeout(4000)
    return n


def pick_video(pg, query):
    """'특정 동영상 선택' 대화상자에서 내 영상을 고른다.

    ★검색창이 **두 개**다 — 왼쪽 '내 동영상 검색', 오른쪽은 유튜브 전체 검색.
      오른쪽에 넣으면 남의 영상이 뜨고 하나도 안 맞는다(2026-08-10 실측).
    """
    # ①왼쪽 '내 동영상 검색' 에 **키보드로** 친다(fill 은 검색을 안 돌린다)
    box = pg.locator("input[placeholder*='내 동영상']").first
    if box.count():
        box.click()
        box.fill("")
        pg.wait_for_timeout(300)
        pg.keyboard.type(query, delay=60)
        pg.wait_for_timeout(5000)
    shot(pg, "search")

    # ②그래도 안 보이면 목록 컨테이너를 **JS 로** 굴려 찾는다(mouse.wheel 은 대화상자에 안 먹는다)
    if not pg.evaluate("(q) => document.body.innerText.includes(q)", query):
        for step in range(30):
            moved = pg.evaluate("""() => {
              const sc = [...document.querySelectorAll('div')]
                .filter(e => e.scrollHeight > e.clientHeight + 80 && e.clientHeight > 200);
              if (!sc.length) return false;
              const el = sc[sc.length-1];
              const before = el.scrollTop;
              el.scrollTop = before + el.clientHeight * 0.9;
              return el.scrollTop > before; }""")
            pg.wait_for_timeout(800)
            if pg.evaluate("(q) => document.body.innerText.includes(q)", query):
                log(f"  목록에서 발견 (JS 스크롤 {step})")
                break
            if not moved:
                break
        else:
            log("  ★목록 끝까지 훑어도 못 찾았다")
        shot(pg, "search2")
    hit = pg.evaluate("""(q) => {
      // 카드 형태 — 제목 텍스트를 담은 가장 작은 클릭 가능 조상을 누른다
      const cands = [...document.querySelectorAll('div,li,ytcp-video-picker-item')]
        .filter(e => (e.textContent||'').includes(q) && e.getBoundingClientRect().width > 80
                     && e.getBoundingClientRect().width < 400);
      if (!cands.length) return 0;
      cands[cands.length-1].click();
      return cands.length; }""", query)
    log(f"  결과 클릭 ({hit}개 일치)")
    pg.wait_for_timeout(3500)
    return bool(hit)


def save(pg):
    n = pg.evaluate("""() => {
      const b = [...document.querySelectorAll('button,ytcp-button')]
        .filter(e => ['저장','SAVE'].includes((e.innerText||'').trim()));
      if (!b.length) return 0;
      b[b.length-1].click();
      return b.length; }""")
    log(f"  '저장' 클릭 (후보 {n}개)")
    pg.wait_for_timeout(6000)
    return n


with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222")
    pg = b.contexts[0].new_page()
    pg.set_default_timeout(30000)
    open_editor(pg)
    shot(pg, "0_editor")

    LABEL = "정보 카드 추가" if MODE in ("card",) or ARG == "card" else "최종 화면 추가"
    if MODE == "dump":
        LABEL = "정보 카드 추가" if ARG == "card" else "최종 화면 추가"
        click_add(pg, LABEL)
        pick_kind_video(pg)
        dump_panel(pg, "1_panel")
    else:
        click_add(pg, LABEL)
        pick_kind_video(pg)
        if MODE == "end":
            pick_specific(pg)
        shot(pg, "1_panel")
        if pick_video(pg, ARG):
            save(pg)
            shot(pg, "2_saved")
        else:
            log("★영상 선택 실패 — 저장하지 않음")
            dump_panel(pg, "2_fail")
