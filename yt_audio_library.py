# -*- coding: utf-8 -*-
"""유튜브 오디오 보관함에서 무료 음악 후보를 찾아 내려받는다 (2026-07-28).

W24 플래시몹용. 저작권 안전한 트랙만 쓰기 위해 **유튜브 스튜디오 오디오 보관함**에서 직접 받는다.
로그인된 디버그 크롬(CDP 9222)에 붙어 조작한다.

사용:
  python yt_audio_library.py list                 # 목록만 훑기(필터 적용 후 상위 N)
  python yt_audio_library.py get "트랙명조각" ...   # 지정 트랙 내려받기
"""
import os
import sys
import time

from playwright.sync_api import sync_playwright

CHANNEL = "UC6KCrgUSdSVUd97b7ltJK_g"
URL = f"https://studio.youtube.com/channel/{CHANNEL}/music"
DL = os.path.abspath("assets/audio/w24_bgm")
SH = "scratch/yt"
os.makedirs(DL, exist_ok=True)
os.makedirs(SH, exist_ok=True)


def log(m):
    print(m, flush=True)


def rows(pg):
    """트랙 행 → (제목, 아티스트, 장르, 분위기, 길이) 목록."""
    return pg.evaluate("""() => {
      const out=[];
      document.querySelectorAll('ytmus-track-row, tr, [role=row]').forEach(r=>{
        const t=(r.innerText||'').trim();
        if(!t || t.length<4) return;
        const cells=t.split('\\n').map(s=>s.trim()).filter(Boolean);
        if(cells.length>=2) out.push(cells.slice(0,6));
      });
      return out.slice(0, 60);
    }""")


with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp("http://localhost:9222")
    ctx = b.contexts[0]
    pg = ctx.new_page()
    pg.goto(URL, wait_until="domcontentloaded")
    time.sleep(10)
    pg.screenshot(path=f"{SH}/audio_lib.png")
    log(f"URL: {pg.url[:100]}")

    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    if mode == "list":
        for i, r in enumerate(rows(pg)[:40], 1):
            log(f"{i:3d} {' | '.join(r)[:120]}")
    else:
        for frag in sys.argv[2:]:
            log(f"--- 검색: {frag}")
            box = pg.locator("input[type='text'], input#search-input").first
            try:
                box.fill(frag); time.sleep(4)
            except Exception as e:
                log(f"  검색창 없음 {str(e)[:40]}")
            before = set(os.listdir(DL))
            ok = pg.evaluate("""(frag) => {
              const rs=[...document.querySelectorAll('[role=row], tr')].filter(r=>(r.innerText||'').includes(frag));
              if(!rs.length) return 'row없음';
              const r=rs[0];
              const btns=[...r.querySelectorAll('button, ytcp-icon-button, a')];
              const dl=btns.find(b=>/다운로드|download/i.test((b.getAttribute('aria-label')||'')+b.innerText));
              if(!dl) return '버튼없음';
              dl.click(); return 'clicked';
            }""", frag)
            log(f"  {ok}")
            for _ in range(20):
                time.sleep(1.5)
                new = [f for f in os.listdir(DL) if f not in before]
                if new:
                    log(f"  ✅ 받음: {new[0]}"); break
            else:
                log("  ★다운로드 안 떨어짐")
    pg.screenshot(path=f"{SH}/audio_lib_after.png")
