# -*- coding: utf-8 -*-
"""오디오 보관함 필터 적용 → 후보 수집 (2026-07-28).

필터 메뉴: 검색 / 트랙 제목 / 장르 / 분위기 / 아티스트 이름 / 길이 / 저작자 표시 필요 없음
사용: python filter_bgm.py 분위기 밝음
      python filter_bgm.py 장르 "댄스/일렉트로닉"
"""
import json
import sys
import time

from playwright.sync_api import sync_playwright

ROW_JS = """() => [...document.querySelectorAll('ytmus-library-row')].map(r => {
    const t = (r.innerText || '').split('\\n').map(s => s.trim()).filter(Boolean);
    return t.slice(0, 5);
})"""


def click_text(pg, txt, exact=True):
    return pg.evaluate("""([txt, exact]) => {
        const els = [...document.querySelectorAll('tp-yt-paper-item,[role=option],li,div,span')]
            .filter(e => e.children.length === 0 &&
                (exact ? (e.innerText||'').trim() === txt : (e.innerText||'').includes(txt)));
        if (!els.length) return false;
        (els[0].closest('tp-yt-paper-item,[role=option],li') || els[0]).click();
        return true;
    }""", [txt, exact])


with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222")
    ctx = b.contexts[0]
    pg = next(p for p in ctx.pages if "/music" in p.url)
    field, value = sys.argv[1], sys.argv[2]

    pg.locator("ytmus-library-filter input").first.click()
    time.sleep(1.5)
    print(f"필터 '{field}' 클릭:", click_text(pg, field))
    time.sleep(2)
    print(f"값 '{value}' 클릭:", click_text(pg, value))
    time.sleep(3)
    pg.keyboard.press("Escape")
    time.sleep(2)
    pg.screenshot(path="scratch/yt/bgm_filtered.png")

    seen = {}
    for _ in range(30):
        for r in pg.evaluate(ROW_JS):
            if len(r) >= 5:
                seen[r[0]] = r
        n0 = len(seen)
        pg.evaluate("""() => { const rs = document.querySelectorAll('ytmus-library-row');
            if (rs.length) rs[rs.length-1].scrollIntoView({block:'end'}); }""")
        time.sleep(1.3)
        for r in pg.evaluate(ROW_JS):
            if len(r) >= 5:
                seen[r[0]] = r
        if len(seen) == n0:
            break
    print(f"수집 {len(seen)}곡")
    out = [{"title": r[0], "genre": r[1], "mood": r[2], "artist": r[3], "dur": r[4]}
           for r in seen.values()]
    json.dump(out, open("scratch/_bgm_cands.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    for i, c in enumerate(out, 1):
        print(f"{i:3d}  {c['title'][:38]:40s} {c['genre']:14s} {c['mood']:5s} {c['dur']:>5s}  {c['artist'][:20]}")
