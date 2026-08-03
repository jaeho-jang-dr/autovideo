# -*- coding: utf-8 -*-
"""등록된 Flow 캐릭터의 **설명을 상세본으로 교체**한다 (2026-07-28).

★첫 클립에서 캐릭터가 왜곡된 원인 = 등록 설명이 한 줄뿐이었다.
  `W24/char_descriptions.py` 의 상세 설명(키·얼굴·머리·옷·신발 색)으로 갈아 끼운다.
  이름이 비어 있는 캐릭터('Untitled Character')는 이름도 함께 넣는다.

사용:
  python flow_update_char_desc.py list          # 등록된 캐릭터 훑기
  python flow_update_char_desc.py all           # 전부 교체
"""
import os
import sys
import time

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "W24"))
from char_descriptions import DESC          # noqa: E402

SH = "scratch/yt"
os.makedirs(SH, exist_ok=True)


def log(m):
    print(m, flush=True)


def open_character_list(pg):
    """프로젝트 루트 → 좌측 '캐릭터' 클릭. 이미 편집기면 루트로 되돌아간다."""
    if "/character" in pg.url:
        pg.goto(pg.url.split("/character")[0], wait_until="domcontentloaded")
        time.sleep(10)
    ok = pg.evaluate("""() => {
        const el = [...document.querySelectorAll('span')]
            .find(e => (e.innerText||'').trim() === '캐릭터' && e.getBoundingClientRect().x < 340);
        if (!el) return false;
        (el.closest('button,[role=button],a,div') || el).click();
        return true;
    }""")
    time.sleep(6)
    return ok


def list_cards(pg):
    """캐릭터 카드 = 라벨 텍스트 + 클릭 좌표."""
    return pg.evaluate("""() => [...document.querySelectorAll('div,span,p')]
        .filter(e => {
            const t = (e.innerText||'').trim();
            const r = e.getBoundingClientRect();
            return e.children.length === 0 && t && t.length < 30 && r.width > 20 &&
                   r.width < 420 && r.height < 60 && r.x > 100;
        })
        .map(e => { const r = e.getBoundingClientRect();
            return {t: (e.innerText||'').trim(), x: Math.round(r.x + r.width/2),
                    y: Math.round(r.y + r.height/2)}; })
        .filter(o => /^(injun|jieun|madamjay|teacherjay|stickman|zollaman|zollagirl|Untitled Character)$/.test(o.t))""")


def set_desc(pg, text):
    for _ in range(8):
        ok = pg.evaluate("""(d) => {
            const t = [...document.querySelectorAll('textarea')]
                .find(x => (x.placeholder||'').includes('캐릭터의 행동'));
            if (!t) return false;
            const set = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
            set.call(t, d);
            t.dispatchEvent(new Event('input', {bubbles:true}));
            t.dispatchEvent(new Event('change', {bubbles:true}));
            return true;
        }""", text)
        if ok:
            return True
        time.sleep(3)
    return False


def set_name(pg, name):
    pg.evaluate("""() => { const e = [...document.querySelectorAll('button')]
        .find(x => (x.innerText||'').trim() === 'edit'); if (e) e.click(); }""")
    time.sleep(2)
    ok = pg.evaluate("""(n) => {
        const i = [...document.querySelectorAll('input')]
            .find(x => x.getBoundingClientRect().width > 60);
        if (!i) return false;
        const set = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
        set.call(i, n);
        i.dispatchEvent(new Event('input', {bubbles:true}));
        i.dispatchEvent(new Event('change', {bubbles:true}));
        return true;
    }""", name)
    pg.keyboard.press("Enter")
    time.sleep(2)
    return ok


def done(pg):
    r = pg.evaluate("""() => {
        const e = [...document.querySelectorAll('button')]
            .filter(x => x.getBoundingClientRect().width > 0)
            .find(x => (x.innerText||'').trim() === '완료');
        if (!e) return false; e.click(); return true;
    }""")
    time.sleep(6)
    return r


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://localhost:9222")
        ctx = b.contexts[0]
        pg = next((p for p in ctx.pages if "/project/" in p.url), None)
        if pg is None:
            raise SystemExit("Flow 프로젝트 탭 없음")
        pg.bring_to_front()
        open_character_list(pg)
        cards = list_cards(pg)
        log(f"캐릭터 카드 {len(cards)}개: {[c['t'] for c in cards]}")
        pg.screenshot(path=f"{SH}/desc_list.png")
        if mode == "list":
            return

        for idx in range(len(cards)):
            open_character_list(pg)
            cards = list_cards(pg)
            if idx >= len(cards):
                break
            c = cards[idx]
            log(f"--- [{idx}] {c['t']}")
            pg.mouse.dblclick(c["x"], c["y"])
            time.sleep(7)
            if "/character/" not in pg.url:
                log("  ★편집기 진입 실패"); continue
            # 현재 이름 확인 → DESC 키 결정
            cur = pg.evaluate("""() => [...document.querySelectorAll('span,h1,h2')]
                .map(e=>(e.innerText||'').trim())
                .find(t => /^(injun|jieun|madamjay|teacherjay|stickman|zollaman|zollagirl)$/.test(t)) || ''""")
            key = cur if cur in DESC else None
            if key is None:
                log(f"  이름 없음 → 건너뜀(수동 지정 필요)"); done(pg); continue
            log(f"  설명 교체: {key} ({len(DESC[key])}자) → {set_desc(pg, DESC[key])}")
            done(pg)


if __name__ == "__main__":
    main()
