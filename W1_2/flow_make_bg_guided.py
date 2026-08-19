# -*- coding: utf-8 -*-
"""배경 생성 — **기준 그림을 주고** 만든다 (이미지→동영상).

★사장님 지시(2026-08-14) "광화문 그림을 하나 줘. 그리고 정확하게 말해 다시 뽑아."

`flow_make_bg.py` 는 글로만 시킨다. 그러니 Flow 가 광화문을 유럽풍 석조 건물로
그려 놓는 일이 생긴다(터널분수 2판). 여기서는 **광화문광장 그림 한 장을 붙여** 두고
글로 고쳐 나가게 한다 — 건물·산·하늘이 우리 채널의 그 광장에서 안 벗어난다.

★경로는 검증된 `flow_make_motion6.py` 와 **한 글자도 다르지 않게** 밟는다:
  숨은 file input 주입 → 미디어 타일 뜨기를 기다림 → '+' → 넓은 '프롬프트에 추가'
  → Omni Flash·8초·16:9 → locator.click() 으로 만들기 → 내려받기.
  좌표 클릭은 쓰지 않는다(가로채이면 오류 없이 240초를 날린다).

    python W1_2/flow_make_bg_guided.py perf_tunnel
    python W1_2/flow_make_bg_guided.py perf_tunnel --guide W1_2/motion_src/guide_x.png
"""
import argparse
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
os.chdir(ROOT)

from playwright.sync_api import sync_playwright          # noqa: E402
import flow_cdp_pipeline as P                            # noqa: E402
import flow_make_group_w24 as G                          # noqa: E402
import autoveo_flow as avf                               # noqa: E402
import bg_defs as B                                      # noqa: E402

OUT = "W1_2/bg"
SHOT = "W1_2/_failshot"
GUIDE = "W1_2/motion_src/guide_gwanghwamun.png"
GEN_WAIT = 180


def log(m):
    print(m, flush=True)


def make_one(key, guides, still=False):
    """guides = 기준 그림 **한 장 또는 여러 장**.

    ★두 장을 주면 "왕은 이것으로, 계단과 돌판은 이것처럼" 처럼 나눠 지시할 수 있다
      (사장님 지시 2026-08-14). 한 장만 주면 그 그림을 통째로 이어받는다.
    """
    if isinstance(guides, str):
        guides = [guides]
    imgs = [os.path.abspath(g) for g in guides]
    img = imgs[0]
    prompt = re.sub(r"[ \t]+", " ", B.prompt(key)).strip()
    out = os.path.abspath(os.path.join(OUT, key + ".mp4"))
    os.makedirs(OUT, exist_ok=True)
    for g in imgs:
        if not os.path.exists(g):
            raise RuntimeError("기준 그림 없음: " + g)

    P.launch_chrome(os.path.abspath("assets/chrome_profile"))
    time.sleep(3)
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(P.CDP_URL)
        pg = next((p for p in b.contexts[0].pages if "labs.google" in p.url), None) \
            or b.contexts[0].pages[0]
        pg.bring_to_front()
        pg.set_default_timeout(30000)

        log("  [1] 새 프로젝트")
        avf.open_new_project(pg)
        pg.wait_for_timeout(3000)

        # ★정지 이미지는 **칩을 먼저 이미지 모드로 바꾸고** 그림을 물린다
        #   (사장님 지시 2026-08-14 "칩에서 정지 이미지 먼저 바꾸고
        #    다시 이미지 띄워서 프롬프트에 추가해").
        #   순서가 뒤바뀌면 동영상으로 나온다.
        if still:
            log("  [1-2] 칩 → 이미지 모드")
            import flow_make_bg as FB
            FB.set_image_mode(pg)
            pg.wait_for_timeout(1500)

        # ★여러 장을 한꺼번에 넣으면 하나만 붙는다(2026-08-14 실측).
        #   **한 장씩 넣고 그때마다 미디어 타일이 늘어나는지 세어** 확인한다.
        log("  [2-1] 기준 그림 주입 (%s)" % ", ".join(os.path.basename(g) for g in imgs))
        for gi, g in enumerate(imgs, 1):
            done = False
            for fr in pg.frames:
                inp = fr.locator("input[type='file']")
                for j in range(inp.count()):
                    try:
                        inp.nth(j).set_input_files(g, timeout=8000)
                        done = True
                        break
                    except Exception:
                        pass
                if done:
                    break
            if not done:
                raise RuntimeError("file input 주입 실패: " + g)
            # ★이미지 모드에선 media_tiles 가 타일을 못 찾는다(동영상 모드 전용).
            #   그냥 25초 기다린다 — 검증된 flow_make_motion6 과 같은 값.
            pg.wait_for_timeout(25000)
            log("    %d/%d %s 올림" % (gi, len(imgs), os.path.basename(g)))

        log("  [2-2] '+' → 프롬프트에 추가")
        def count_imgs():
            return pg.evaluate("""() => { const box=document.querySelector("div[role='textbox'][contenteditable='true']");
                if(!box) return 0; let p=box.parentElement;
                for(let i=0;i<5&&p;i++,p=p.parentElement){ const c=p.querySelectorAll('img').length; if(c) return c; }
                return 0; }""")

        # ★검증된 단순 흐름 — '+' 한 번, 넓은 '프롬프트에 추가' 한 번.
        #   타일을 골라 누르는 짓을 끼워 넣었더니 오히려 0개가 됐다(2026-08-14).
        plus = pg.locator("button").filter(has_text=re.compile("add_2")).filter(
            has_text=re.compile("만들기|Create")).last
        if plus.count() == 0:
            raise RuntimeError("'+' 버튼 없음")
        plus.click(timeout=15000)
        w = 0
        for _ in range(24):
            pg.wait_for_timeout(400)
            w = pg.evaluate("""() => { for (const e of document.querySelectorAll('button')) {
                const t=(e.innerText||'').trim(); const b=e.getBoundingClientRect();
                if(b.width>200 && t==='프롬프트에 추가'){ e.click(); return Math.round(b.width); } }
                return 0; }""")
            if w:
                break
        pg.wait_for_timeout(2000)
        log("    넓은버튼 w=%s · 프롬프트 그림 %d개" % (w, count_imgs()))
        n = count_imgs()
        log("    프롬프트 창 그림 %d개 (필요 %d개)" % (n, len(imgs)))
        if n < 1:
            raise RuntimeError("그림이 프롬프트에 안 붙었다")

        if not still:
            log("  [3] 동영상 · Omni Flash · 16:9 · 8s")
            G.set_chip(pg, model=os.environ.get("W1D2_MODEL", "Omni Flash"), secs="8s")
        else:
            log("  [3] 이미지 모드 유지 (칩은 앞에서 바꿨다)")

        log("  [4] 프롬프트 → 만들기 (%d자)" % len(prompt))
        before = pg.evaluate(
            "() => [...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src||'').filter(Boolean)")
        before_i = pg.evaluate(
            "() => [...document.querySelectorAll('img')].map(v=>v.currentSrc||v.src||'')"
            ".filter(s=>s&&s.startsWith('http'))")
        avf.fill_prompt(pg, prompt)
        pg.wait_for_timeout(1500)
        btn = pg.locator("button").filter(has_text=re.compile("arrow_forward")).filter(
            has_text=re.compile("만들기|Create|Generate")).last
        if btn.count() == 0:
            raise RuntimeError("'만들기' 버튼 없음")
        btn.scroll_into_view_if_needed()
        btn.click(timeout=15000)
        pg.wait_for_timeout(4000)

        if still:
            # ★검증된 flow_make_bg.py 와 똑같이 — 생성 **전** img 목록을 찍어 두고
            #   새로 생긴 것을 잡는다. 크기로 고르려 했더니 못 찾았다(2026-08-14).
            log("  [5] 이미지 생성 대기 (최대 %d초)" % GEN_WAIT)
            out_png = out[:-4] + ".png"
            got = None
            for i in range(GEN_WAIT // 10):
                pg.wait_for_timeout(10000)
                now = [x for x in pg.evaluate(
                    "() => [...document.querySelectorAll('img')].map(v=>v.currentSrc||v.src||'')"
                    ".filter(s=>s&&s.startsWith('http'))") if x not in before_i]
                if now:
                    got = now[0]
                    log("    %ds — 새 그림 확인" % ((i + 1) * 10))
                    break
            if not got:
                os.makedirs(SHOT, exist_ok=True)
                try:
                    pg.screenshot(path=os.path.join(SHOT, "bg_%s_fail.png" % key))
                    log("    [실패화면] %s/bg_%s_fail.png" % (SHOT, key))
                except Exception:
                    pass
                raise RuntimeError("이미지 생성 실패(시간 초과)")
            log("  [6] 내려받기")
            ok = G.fetch_image(pg, out_png, got) if hasattr(G, "fetch_image") else False
            if not ok:
                data = pg.evaluate("""async (u) => {
                    const r = await fetch(u); const b = await r.arrayBuffer();
                    return Array.from(new Uint8Array(b)); }""", got)
                open(out_png, "wb").write(bytes(data))
                ok = os.path.getsize(out_png) > 20000
            if not ok:
                raise RuntimeError("내려받기 실패(그림이 너무 작다)")
            log("  ✅ %s  %dKB" % (out_png, os.path.getsize(out_png) // 1024))
            return

        log("  [5] 생성 대기 (최대 %d초)" % GEN_WAIT)
        src = None
        for i in range(GEN_WAIT // 15):
            pg.wait_for_timeout(15000)
            now = [s for s in pg.evaluate(
                "() => [...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src||'').filter(Boolean)")
                if s not in before]
            if now:
                src = now[0]
                log("    %ds — 새 미디어 확인" % ((i + 1) * 15))
                break
        if not src:
            os.makedirs(SHOT, exist_ok=True)
            try:
                pg.screenshot(path=os.path.join(SHOT, "bg_%s_fail.png" % key))
                log("    [실패화면] %s/bg_%s_fail.png" % (SHOT, key))
            except Exception:
                pass
            raise RuntimeError("생성 실패(시간 초과)")

        log("  [6] 내려받기")
        if not G.fetch_video(pg, out, src):
            raise RuntimeError("내려받기 실패")
        log("  ✅ %s  %dKB" % (out, os.path.getsize(out) // 1024))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("key")
    ap.add_argument("--guide", default=[GUIDE], nargs="+")
    ap.add_argument("--still", action="store_true", help="정지 이미지로 뽑는다")
    a = ap.parse_args()
    print("=" * 54)
    print("%s (기준 그림 %s)" % (a.key, ", ".join(os.path.basename(g) for g in a.guide)))
    print("=" * 54)
    make_one(a.key, a.guide, a.still)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
