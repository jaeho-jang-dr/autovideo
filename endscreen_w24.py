#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""endscreen_w24.py — 최종 화면에 '특정 동영상 + 구독'을 넣는다 (2026-08-08 실전 검증).

★기존 endscreen_video_ui.py 가 안 먹는 이유 — 스튜디오 UI가 바뀌었다.
   · 사이드바 행 라벨: '엔딩 화면' → **'최종 화면'**
   · 진입: 텍스트 오른쪽 281px 연필이 아니라 **행 오른쪽 끝의 + **
   · /video/<VID>/editor 로 들어가면 '시작하기' 버튼을 한 번 눌러야 편집기가 열린다
   · 템플릿 타일은 aria-label='동영상 1개, 구독 1개' 를 **JS 클릭**(포인터 가로채기 회피)
   · 동영상 요소 선택은 **타임라인 칩을 실제 마우스로** 클릭(JS click 안 먹음)
   · 저장은 '저장' 버튼 JS 클릭 + **edit_video POST** 로 검증

사용:
    python endscreen_w24.py <VID> "<검색어>" "<제목조각>"
예:
    python endscreen_w24.py HIvrnNWk3K8 "Making Plans" "Making Plans"
"""
import sys, json, time
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
SEARCH = sys.argv[2]
FRAG = sys.argv[3] if len(sys.argv) > 3 else SEARCH


def log(m):
    print(m, flush=True)


def leaf_texts(pg, prefixes):
    return json.loads(pg.evaluate("""(pfx) => {
      const out=[];
      document.querySelectorAll('*').forEach(el=>{
        if(el.children.length) return;
        const t=(el.textContent||'').trim();
        if(pfx.some(p=>t.startsWith(p))){
          const b=el.getBoundingClientRect();
          if(b.width>0) out.push({t:t.slice(0,60), x:Math.round(b.x+b.width/2), y:Math.round(b.y+b.height/2)});
        }
      });
      return JSON.stringify(out);
    }""", prefixes))


def main():
    posts = []
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://localhost:9222")
        pg = b.contexts[0].new_page()
        pg.set_default_timeout(20000)
        pg.on("request", lambda r: posts.append(r.url.split("/")[-1].split("?")[0])
              if r.method == "POST" and "youtubei" in r.url else None)

        pg.goto(f"https://studio.youtube.com/video/{VID}/editor", wait_until="domcontentloaded")
        pg.wait_for_timeout(10000)
        try:
            pg.get_by_role("button", name="시작하기").first.click(timeout=6000)
            log("시작하기 클릭"); pg.wait_for_timeout(8000)
        except Exception:
            log("시작하기 없음(이미 편집기)")

        # 이미 최종화면이 있으면 중단 — 덮어쓰지 않는다
        cur = leaf_texts(pg, ["동영상:", "구독:"])
        if cur:
            log("이미 최종화면 요소가 있다: " + str([c["t"] for c in cur]))
            return 0

        # ① 행 오른쪽 끝 + 클릭
        bb = pg.get_by_text("최종 화면", exact=True).first.bounding_box()
        row = pg.locator("xpath=//*[normalize-space(text())='최종 화면']"
                         "/ancestor::*[self::div or self::ytve-editor-menu-item][1]").first.bounding_box()
        pg.mouse.click(row["x"] + row["width"] - 30, bb["y"] + bb["height"] / 2)
        log("최종화면 + 클릭"); pg.wait_for_timeout(7000)

        # ② 템플릿 '동영상 1개, 구독 1개' JS 클릭
        r = pg.evaluate("""() => {
          const want='동영상 1개, 구독 1개'; let hit=null;
          document.querySelectorAll('*').forEach(el=>{
            if(hit) return;
            if(el.getAttribute && el.getAttribute('aria-label')===want) hit=el;
          });
          if(!hit) return 'NOTFOUND';
          hit.click(); return 'OK';
        }""")
        log("템플릿: " + r); pg.wait_for_timeout(7000)

        # ③ 타임라인 '동영상:' 칩을 실제 마우스로 클릭
        chips = [c for c in leaf_texts(pg, ["동영상:"])]
        if not chips:
            log("★동영상 칩 없음"); return 1
        c = chips[-1]
        pg.mouse.click(c["x"], c["y"]); log(f"동영상 요소 선택 @({c['x']},{c['y']})")
        pg.wait_for_timeout(5000)

        # ④ '특정 동영상' → 검색 → 썸네일 클릭
        t = pg.get_by_text("특정 동영상", exact=False).first.bounding_box()
        pg.mouse.click(t["x"] + t["width"] / 2, t["y"] + t["height"] / 2)
        log("'특정 동영상' 클릭"); pg.wait_for_timeout(6000)

        sb = pg.get_by_placeholder("내 동영상 검색").first
        sb.click(); sb.fill(SEARCH); log("검색: " + SEARCH); pg.wait_for_timeout(6000)

        h = pg.get_by_text(FRAG, exact=False).first
        hb = h.bounding_box()
        pg.mouse.click(hb["x"] + hb["width"] / 2, hb["y"] - 40)     # 제목 위 썸네일
        log("썸네일 클릭"); pg.wait_for_timeout(6000)

        picked = leaf_texts(pg, ["동영상:"])
        log("선택됨: " + str([p["t"] for p in picked][:1]))

        # ⑤ 저장 — '변경사항 저장 안함' 배제, JS 클릭 + edit_video 검증
        cands = json.loads(pg.evaluate("""() => {
          const out=[];
          document.querySelectorAll('button, ytcp-button, tp-yt-paper-button').forEach(el=>{
            if((el.innerText||'').trim()==='저장'){
              const b=el.getBoundingClientRect();
              if(b.width>0) out.push({x:Math.round(b.x), y:Math.round(b.y+b.height/2)});
            }
          });
          return JSON.stringify(out);
        }"""))
        for cd in sorted(cands, key=lambda z: -z["x"]):
            pg.evaluate("""(pt) => {
              const els=[...document.querySelectorAll('button, ytcp-button, tp-yt-paper-button')]
                .filter(e=>(e.innerText||'').trim()==='저장');
              const el=els.find(e=>Math.abs(e.getBoundingClientRect().x-pt.x)<3);
              if(el) el.click();
            }""", cd)
            log(f"  JS저장클릭 @({cd['x']},{cd['y']})")
            pg.wait_for_timeout(6000)
            if any("edit_video" in p for p in posts):
                break
        ok = any("edit_video" in p for p in posts)
        log("저장: " + ("OK(edit_video)" if ok else "MISS"))

        # ⑥ 재로드 검증
        pg.goto(f"https://studio.youtube.com/video/{VID}/editor", wait_until="domcontentloaded")
        pg.wait_for_timeout(10000)
        try:
            pg.get_by_role("button", name="시작하기").first.click(timeout=5000); pg.wait_for_timeout(8000)
        except Exception:
            pass
        after = leaf_texts(pg, ["동영상:", "구독:"])
        log("재로드 후: " + str([a["t"] for a in after]))
        return 0 if after else 1


if __name__ == "__main__":
    sys.exit(main())
