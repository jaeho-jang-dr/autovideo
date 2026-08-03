# -*- coding: utf-8 -*-
"""W24 플래시몹 BGM 후보 고르기 — 유튜브 오디오 보관함(저작권 안전) (2026-07-28).

밝은 분위기 + 댄스/팝 계열 + 1분40초~4분20초 트랙을 모아 후보를 뽑고, 지정하면 내려받는다.
로그인된 디버그 크롬(CDP 9222)에 붙는다.

사용:
  python pick_w24_bgm.py list                  # 후보 수집·출력
  python pick_w24_bgm.py get "제목1" "제목2" …  # 지정 트랙 내려받기
"""
import json
import os
import re
import sys
import time

from playwright.sync_api import sync_playwright

DL = os.path.abspath("assets/audio/w24_bgm")
CAND = "scratch/_bgm_cands.json"
GOOD_MOOD = {"밝음", "행복", "신남", "영감"}
GOOD_GENRE = {"댄스/일렉트로닉", "팝", "힙합/랩", "R&B/소울", "어린이"}
os.makedirs(DL, exist_ok=True)
os.makedirs("scratch", exist_ok=True)

ROW_JS = """() => [...document.querySelectorAll('ytmus-library-row')].map(r => {
    const t = (r.innerText || '').split('\\n').map(s => s.trim()).filter(Boolean);
    return t.slice(0, 5);
})"""


def secs(d):
    m = re.match(r"(\d+):(\d+)", d or "")
    return int(m.group(1)) * 60 + int(m.group(2)) if m else 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://localhost:9222")
        ctx = b.contexts[0]
        pg = next((p for p in ctx.pages if "/music" in p.url), None)
        if pg is None:
            pg = ctx.new_page()
            pg.goto("https://studio.youtube.com/channel/UC6KCrgUSdSVUd97b7ltJK_g/music",
                    wait_until="domcontentloaded")
            time.sleep(10)

        if mode == "list":
            # ★표가 가상 스크롤러 안에 있다 — 페이지 휠은 안 먹는다. 마지막 행을 계속
            #   scrollIntoView 해서 다음 묶음을 불러온다.
            seen = {}
            stall = 0
            for _ in range(60):
                for r in pg.evaluate(ROW_JS):
                    if len(r) >= 5:
                        seen[r[0]] = r
                n0 = len(seen)
                pg.evaluate("""() => {
                    const rs = document.querySelectorAll('ytmus-library-row');
                    if (rs.length) rs[rs.length - 1].scrollIntoView({block: 'end'});
                    document.scrollingElement.scrollTop = document.scrollingElement.scrollHeight;
                }""")
                time.sleep(1.4)
                for r in pg.evaluate(ROW_JS):
                    if len(r) >= 5:
                        seen[r[0]] = r
                stall = stall + 1 if len(seen) == n0 else 0
                if stall >= 4:
                    break
                print(f"  …{len(seen)}곡", flush=True)
            cands = []
            for r in seen.values():
                title, genre, mood, artist, dur = r[0], r[1], r[2], r[3], r[4]
                if mood in GOOD_MOOD and genre in GOOD_GENRE and 100 <= secs(dur) <= 260:
                    cands.append({"title": title, "genre": genre, "mood": mood,
                                  "artist": artist, "dur": dur})
            cands.sort(key=lambda c: (c["mood"] != "밝음", secs(c["dur"])))
            print(f"수집 {len(seen)}곡 → 후보 {len(cands)}곡")
            for i, c in enumerate(cands, 1):
                print(f"{i:3d}  {c['title'][:40]:42s} {c['genre']:14s} {c['mood']:5s} "
                      f"{c['dur']:>5s}  {c['artist'][:22]}")
            json.dump(cands, open(CAND, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print(f"\n저장: {CAND}")
        else:
            for frag in sys.argv[2:]:
                print(f"--- {frag}")
                before = set(os.listdir(DL))
                res = pg.evaluate("""(frag) => {
                    const rs = [...document.querySelectorAll('ytmus-library-row')]
                        .filter(r => (r.innerText || '').includes(frag));
                    if (!rs.length) return 'row없음';
                    const r = rs[0];
                    r.scrollIntoView({block:'center'});
                    const b = [...r.querySelectorAll('button, ytcp-icon-button, a')]
                        .find(x => /다운로드|download|오프라인/i.test(
                            (x.getAttribute('aria-label')||'') + (x.innerText||'')));
                    if (!b) return '버튼없음';
                    b.click(); return 'clicked';
                }""", frag)
                print(f"  {res}")
                for _ in range(24):
                    time.sleep(1.5)
                    new = [f for f in os.listdir(DL) if f not in before and not f.endswith(".crdownload")]
                    if new:
                        print(f"  ✅ {new[0]}")
                        break
                else:
                    print("  ★다운로드 안 떨어짐")


if __name__ == "__main__":
    main()
