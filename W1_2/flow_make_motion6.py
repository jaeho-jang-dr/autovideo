# -*- coding: utf-8 -*-
"""스틱맨 이동 동작 6종 생성 — Flow 이미지→동영상.

★검증된 경로 그대로: 숨은 file input 주입 → 프롬프트 바 '+' → 넓은 '프롬프트에 추가'
  → Omni Flash → **locator.click()** (좌표 금지) → 클립 1개마다 크롬 재기동.

    python W1_2/flow_make_motion6.py walk_side     # 하나만
    python W1_2/flow_make_motion6.py --all         # 미생성분 전부
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
import motion6_defs as M                                 # noqa: E402

OUT = "W1_2/motion6"
SHOT = "W1_2/_failshot"
GEN_WAIT = 180
COOL = 10


def log(m):
    print(m, flush=True)


def kill_chrome():
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True, text=True)


def make_one(key):
    img = os.path.abspath(M.guide_of(key))
    prompt = re.sub(r"[ \t]+", " ", M.prompt(key)).strip()
    out = os.path.abspath(os.path.join(OUT, key + ".mp4"))
    os.makedirs(OUT, exist_ok=True)
    if not os.path.exists(img):
        raise RuntimeError("기준 이미지 없음: " + img)

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

        log("  [2-1] 기준 이미지 주입 (%s)" % os.path.basename(img))
        done = False
        for fr in pg.frames:
            inp = fr.locator("input[type='file']")
            for j in range(inp.count()):
                try:
                    inp.nth(j).set_input_files(img, timeout=5000)
                    done = True
                    break
                except Exception:
                    pass
            if done:
                break
        if not done:
            raise RuntimeError("file input 주입 실패")
        pg.wait_for_timeout(25000)

        log("  [2-2] '+' → 프롬프트에 추가")
        plus = pg.locator("button").filter(has_text=re.compile("add_2")).filter(
            has_text=re.compile("만들기|Create")).last
        if plus.count() == 0:
            raise RuntimeError("'+' 버튼 없음")
        plus.click(timeout=15000)
        pg.wait_for_timeout(2800)
        w = pg.evaluate("""() => { for (const e of document.querySelectorAll('button')) {
            const t=(e.innerText||'').trim(); const b=e.getBoundingClientRect();
            if(b.width>200 && t==='프롬프트에 추가'){ e.click(); return Math.round(b.width); } }
            return 0; }""")
        pg.wait_for_timeout(2500)
        n = pg.evaluate("""() => { const box=document.querySelector("div[role='textbox'][contenteditable='true']");
            if(!box) return -1; let p=box.parentElement;
            for(let i=0;i<5&&p;i++,p=p.parentElement){ const c=p.querySelectorAll('img').length; if(c) return c; }
            return 0; }""")
        log("    넓은버튼 w=%s · 프롬프트 창 이미지 %s개" % (w, n))
        if n < 1:
            raise RuntimeError("이미지가 프롬프트에 안 붙었다")

        # ★길이 옵션은 4s/6s/8s/10s 네 개다(2026-08-11 UI 실측 — probe_durations.py).
        #   키 끝이 '10' 이면 10초로 만든다. 항목이 없는 값을 누르면 조용히 8초로 나온다.
        secs = "10s" if key.endswith("10") else os.environ.get("W1D2_SECS", "8s")
        log("  [3] 동영상 · Omni Flash · 16:9 · %s" % secs)
        G.set_chip(pg, model=os.environ.get("W1D2_MODEL", "Omni Flash"), secs=secs)

        log("  [4] 프롬프트 → 만들기 (%d자)" % len(prompt))
        before = pg.evaluate(
            "() => [...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src||'').filter(Boolean)")
        avf.fill_prompt(pg, prompt)
        pg.wait_for_timeout(1500)
        btn = pg.locator("button").filter(has_text=re.compile("arrow_forward")).filter(
            has_text=re.compile("만들기|Create|Generate")).last
        if btn.count() == 0:
            raise RuntimeError("'만들기' 버튼 없음")
        btn.scroll_into_view_if_needed()
        btn.click(timeout=15000)
        pg.wait_for_timeout(4000)
        left = pg.evaluate("""() => { const b=document.querySelector("div[role='textbox'][contenteditable='true']");
            return b ? (b.innerText||'').trim().length : -1; }""")
        log("    프롬프트 잔여 %d자 (원문 %d자)" % (left, len(prompt)))
        if left > len(prompt) * 0.5:
            try:
                btn.click(timeout=10000)
                pg.wait_for_timeout(4000)
            except Exception as e:
                log("    재클릭 실패: " + str(e)[:60])

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
                pg.screenshot(path=os.path.join(SHOT, "m6_%s_fail.png" % key))
                log("    [실패화면] %s/m6_%s_fail.png" % (SHOT, key))
            except Exception:
                pass
            raise RuntimeError("생성 실패(시간 초과)")

        log("  [6] 내려받기")
        if not G.fetch_video(pg, out, src):
            raise RuntimeError("내려받기 실패")
        log("  ✅ %s  %dKB" % (out, os.path.getsize(out) // 1024))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    keys = a.keys
    if a.all or not keys:
        keys = [k for k, _, _ in M.MOTIONS
                if not os.path.exists(os.path.join(OUT, k + ".mp4"))]
    if not keys:
        log("대상 없음 — 이미 다 있다")
        return 0
    ok, fail = [], []
    for i, k in enumerate(keys, 1):
        log("\n%s\n[%d/%d] %s (기준 %s)\n%s"
            % ("=" * 54, i, len(keys), k, M.BY[k][0], "=" * 54))
        kill_chrome()
        time.sleep(COOL)
        try:
            make_one(k)
            ok.append(k)
        except Exception as e:
            log("  ★%s 실패: %s" % (k, str(e)[:140]))
            fail.append(k)
        kill_chrome()
        time.sleep(COOL)
    log("\n완료 %d/%d" % (len(ok), len(keys)))
    if fail:
        log("실패: " + ", ".join(fail))
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
