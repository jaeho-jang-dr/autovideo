#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""card_w24.py — 정보 카드(동영상)를 UI로 넣는다. 2026-08-08 실전 검증본.

★기존 card_video_ui.py 가 2번째 카드부터 죽는 이유 — 44줄이 하드코딩 좌표다.
     pg.mouse.click(272, 134)   # 카드가 1개라도 있으면 메뉴가 밀려 빗나감
   여기서는 **매번 DOM에서 좌표를 다시 구한다**.

검증된 경로
  1) /video/<VID>/editor → '시작하기' JS 클릭 (안 누르면 편집기가 안 열린다)
  2) '정보 카드' 행의 '수정' 버튼을 JS 클릭 (조상 6단계까지 올라가며 찾는다)
  3) '카드' 버튼 좌표를 DOM에서 얻어 클릭 → 드롭다운 '동영상'
  4) '내 동영상 검색' fill → 결과 **제목 위 40px(썸네일)** 클릭
  5) 저장은 '저장' JS 클릭 + **edit_video POST** 로 검증

★티저 시각은 건드리지 않는다(전부 0:00).
  마스크드 입력이라 '034000' 을 치면 9시간 26분 40초가 되어 영상 길이를 넘어간다.
  레포에 성공 이력이 없는 미검증 경로다 — 손대지 않는 편이 안전하다.

사용:
    python card_w24.py <VID> "<검색어1>" "<제목조각1>" ["<검색어2>" "<제목조각2>" ...]
"""
import sys, json
from playwright.sync_api import sync_playwright

VID = sys.argv[1]
rest = sys.argv[2:]
PAIRS = [(rest[i], rest[i + 1]) for i in range(0, len(rest) - 1, 2)]


def log(m):
    print(m, flush=True)


def cards(pg):
    return json.loads(pg.evaluate("""() => {
      const o=[]; document.querySelectorAll('*').forEach(e=>{
        if(e.children.length) return;
        const t=(e.textContent||'').trim();
        if(t.startsWith('동영상:')) o.push(t.slice(4,44));});
      return JSON.stringify([...new Set(o)]);}"""))


def btn_xy(pg, label, ymax=400):
    r = json.loads(pg.evaluate("""(a) => {
      const o=[]; document.querySelectorAll('button,ytcp-button,tp-yt-paper-button').forEach(e=>{
        const t=(e.innerText||'').trim(); const b=e.getBoundingClientRect();
        if(t===a.label && b.width>0 && b.y<a.ymax)
          o.push({x:Math.round(b.x+b.width/2), y:Math.round(b.y+b.height/2)});});
      return JSON.stringify(o);}""", {"label": label, "ymax": ymax}))
    return r[0] if r else None


def main():
    posts = []
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp("http://localhost:9222")
        pg = b.contexts[0].new_page()
        pg.set_default_timeout(25000)
        pg.on("request", lambda r: posts.append(r.url.split("/")[-1].split("?")[0])
              if r.method == "POST" and "youtubei" in r.url else None)

        pg.goto(f"https://studio.youtube.com/video/{VID}/editor", wait_until="domcontentloaded")
        pg.wait_for_timeout(11000)
        pg.evaluate("""()=>{const b=[...document.querySelectorAll('button,ytcp-button,tp-yt-paper-button')]
          .find(e=>(e.innerText||'').trim()==='시작하기'); if(b)b.click();}""")
        pg.wait_for_timeout(9000)

        # ★'정보 카드' 행으로 들어가는 법이 두 가지다(실측):
        #     카드가 이미 있으면 → 그 행의 **'수정'** 버튼
        #     카드가 하나도 없으면 → 그 행 **오른쪽 끝의 '+'**
        #   조상 탐색으로 하면 바로 위 '최종 화면' 행을 잡아 엉뚱한 편집기로 들어간다.
        ly = pg.evaluate("""()=>{
          let y=null;
          document.querySelectorAll('*').forEach(e=>{
            if(y!==null||e.children.length)return;
            if((e.textContent||'').trim()==='정보 카드'){
              const b=e.getBoundingClientRect(); if(b.width>0) y=b.y+b.height/2;}});
          return y;}""")
        if ly is None:
            log("★'정보 카드' 라벨 없음"); return 1
        hit = pg.evaluate("""(ly)=>{
          let best=null, bd=1e9;
          document.querySelectorAll('button,ytcp-button').forEach(e=>{
            if((e.innerText||'').trim()!=='수정')return;
            const b=e.getBoundingClientRect(); if(b.width<=0)return;
            const d=Math.abs((b.y+b.height/2)-ly);
            if(d<bd){bd=d; best=e;}});
          if(best && bd<=20){ best.click(); return 'EDIT'; }
          return 'NOEDIT';}""", ly)
        if hit == "NOEDIT":                     # 카드 0개 → 행 오른쪽 끝 +
            row = pg.locator("xpath=//*[normalize-space(text())='정보 카드']"
                             "/ancestor::*[self::div or self::ytve-editor-menu-item][1]").first.bounding_box()
            pg.mouse.click(row["x"] + row["width"] - 30, ly)
            pg.wait_for_timeout(4000)
            m = json.loads(pg.evaluate("""()=>{const o=[];
              document.querySelectorAll('tp-yt-paper-item,[role="menuitem"],[role="option"]').forEach(e=>{
                const t=(e.innerText||'').trim(); const b=e.getBoundingClientRect();
                if(t==='동영상'&&b.width>0)o.push({x:Math.round(b.x+b.width/2),y:Math.round(b.y+b.height/2)});});
              return JSON.stringify(o);}"""))
            if m:                               # +를 누르면 바로 유형 메뉴가 뜬다
                pg.mouse.click(m[0]["x"], m[0]["y"]); pg.wait_for_timeout(5000)
                sb = pg.get_by_placeholder("내 동영상 검색").first
                s0, f0 = PAIRS[0]
                sb.click(); sb.fill(s0); pg.wait_for_timeout(6000)
                h = pg.get_by_text(f0, exact=False)
                for i in range(min(h.count(), 5)):
                    bb = h.nth(i).bounding_box()
                    if bb and bb["y"] > 150 and bb["x"] < 1100:
                        pg.mouse.click(bb["x"] + bb["width"] / 2, bb["y"] - 40); break
                log(f"  '{s0}' → 첫 카드 생성")
                pg.wait_for_timeout(6000)
                PAIRS.pop(0)
        log("정보 카드 진입: " + hit)
        pg.wait_for_timeout(8000)
        # ★진입 검증 — 카드 편집기에는 '카드' 버튼이, 최종화면 편집기에는 '요소' 버튼이 있다
        if btn_xy(pg, "카드", ymax=400) is None:
            log("★카드 편집기가 아니다(최종화면으로 들어갔다) — 중단, 저장하지 않음")
            return 1
        log("기존 카드: " + str(cards(pg)))

        for search, frag in PAIRS:
            c = btn_xy(pg, "카드", ymax=400)
            if not c:
                log("★'카드' 버튼 못찾음"); break
            pg.mouse.click(c["x"], c["y"]); pg.wait_for_timeout(4500)
            m = json.loads(pg.evaluate("""()=>{const o=[];
              document.querySelectorAll('tp-yt-paper-item,[role="menuitem"],[role="option"]').forEach(e=>{
                const t=(e.innerText||'').trim(); const b=e.getBoundingClientRect();
                if(t==='동영상'&&b.width>0)o.push({x:Math.round(b.x+b.width/2),y:Math.round(b.y+b.height/2)});});
              return JSON.stringify(o);}"""))
            if not m:
                log(f"★'동영상' 메뉴 없음 ({search})"); continue
            pg.mouse.click(m[0]["x"], m[0]["y"]); pg.wait_for_timeout(5000)

            sb = pg.get_by_placeholder("내 동영상 검색").first
            sb.click(); sb.fill(search); pg.wait_for_timeout(6000)
            h = pg.get_by_text(frag, exact=False)
            done = False
            for i in range(min(h.count(), 5)):
                bb = h.nth(i).bounding_box()
                if bb and bb["y"] > 150 and bb["x"] < 1100:
                    pg.mouse.click(bb["x"] + bb["width"] / 2, bb["y"] - 40)
                    done = True; break
            log(f"  '{search}' → " + ("선택" if done else "★결과 못찾음"))
            pg.wait_for_timeout(6000)

        log("추가 후 카드: " + str(cards(pg)))

        cands = json.loads(pg.evaluate("""()=>{const o=[];
          document.querySelectorAll('button, ytcp-button, tp-yt-paper-button').forEach(e=>{
            if((e.innerText||'').trim()==='저장'){const b=e.getBoundingClientRect();
            if(b.width>0)o.push({x:Math.round(b.x),y:Math.round(b.y+b.height/2)});}});
          return JSON.stringify(o);}"""))
        for cd in sorted(cands, key=lambda z: -z["x"]):
            pg.evaluate("""(pt)=>{const els=[...document.querySelectorAll('button, ytcp-button, tp-yt-paper-button')]
              .filter(e=>(e.innerText||'').trim()==='저장');
              const el=els.find(e=>Math.abs(e.getBoundingClientRect().x-pt.x)<3); if(el)el.click();}""", cd)
            log(f"  JS저장클릭 @({cd['x']},{cd['y']})")
            pg.wait_for_timeout(7000)
            if any("edit_video" in p for p in posts):
                break
        ok = any("edit_video" in p for p in posts)
        log("저장: " + ("OK(edit_video)" if ok else "MISS"))
        return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
