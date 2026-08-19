# -*- coding: utf-8 -*-
"""W1-2 정지 포즈 생성 — 기준 이미지 업로드 + **이미지 모드**(Nano Banana).

★오늘(2026-08-12) 검증된 조각만 이어 붙였다:
  - 업로드·프롬프트·만들기 = `flow_make_motion6.py` 흐름 그대로 (동작 클립 19개 완주)
  - 이미지 모드 전환 = `flow_make_bg.set_image_mode()` (정지 배경 5장 완주)
  - 모든 클릭은 **locator.click()** — 좌표 클릭은 조용히 실패한다
    [[flow-coordinate-click-silent-fail]]

기존 `flow_make_pose.py` / `flow_make_pose_w24.py` 는 옛 `flow_make_clip`(flow_driver
좌표 클릭) 경로라 쓰지 않는다.

    python W1_2/flow_make_pose12.py --all
    python W1_2/flow_make_pose12.py zman_attention
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
import autoveo_flow as avf                               # noqa: E402
from W1_2 import flow_make_bg as BG                      # noqa: E402
import pose_defs as D                                    # noqa: E402

OUT = "W1_2/_poses_z"
SHOT = "W1_2/_failshot"
GEN_WAIT = 180
COOL = 10


def log(m):
    print(m, flush=True)


def kill_chrome():
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True, text=True)


def make_one(key):
    img = os.path.abspath(D.guide_of(key))
    prompt = re.sub(r"[ \t]+", " ", D.prompt(key)).strip()
    out = os.path.abspath(os.path.join(OUT, key + ".png"))
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
        pg.evaluate("""() => { for (const e of document.querySelectorAll('button')) {
            const t=(e.innerText||'').trim(); const b=e.getBoundingClientRect();
            if(b.width>200 && t==='프롬프트에 추가'){ e.click(); return true; } } return false; }""")
        pg.wait_for_timeout(2500)
        n = pg.evaluate("""() => { const box=document.querySelector("div[role='textbox'][contenteditable='true']");
            if(!box) return -1; let p=box.parentElement;
            for(let i=0;i<5&&p;i++,p=p.parentElement){ const c=p.querySelectorAll('img').length; if(c) return c; }
            return 0; }""")
        log("    프롬프트 창 이미지 %s개" % n)
        if n < 1:
            raise RuntimeError("이미지가 프롬프트에 안 붙었다")

        log("  [3] 이미지 모드 · Nano Banana")
        BG.set_image_mode(pg)

        log("  [4] 프롬프트 → 만들기 (%d자)" % len(prompt))
        before = pg.evaluate(
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
        for i in range(GEN_WAIT // 10):
            pg.wait_for_timeout(10000)
            now = [s for s in pg.evaluate(
                "() => [...document.querySelectorAll('img')].map(v=>v.currentSrc||v.src||'')"
                ".filter(s=>s&&s.startsWith('http'))") if s not in before]
            if now:
                src = now[0]
                log("    %ds — 새 이미지 확인" % ((i + 1) * 10))
                break
        if not src:
            os.makedirs(SHOT, exist_ok=True)
            try:
                pg.screenshot(path=os.path.join(SHOT, "pose_%s_fail.png" % key))
                log("    [실패화면] %s/pose_%s_fail.png" % (SHOT, key))
            except Exception:
                pass
            raise RuntimeError("생성 실패(시간 초과)")

        log("  [6] 내려받기")
        data = pg.evaluate("""async (u) => {
            const r = await fetch(u); const b = await r.arrayBuffer();
            return Array.from(new Uint8Array(b)); }""", src)
        open(out, "wb").write(bytes(data))
        if os.path.getsize(out) < 10000:
            raise RuntimeError("내려받기 실패(%d바이트)" % os.path.getsize(out))
        log("  ✅ %s  %dKB" % (out, os.path.getsize(out) // 1024))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    keys = a.keys
    if a.all or not keys:
        keys = [k for k, _, _ in D.POSES
                if not os.path.exists(os.path.join(OUT, k + ".png"))]
    if not keys:
        log("대상 없음 — 이미 다 있다")
        return 0
    ok, fail = [], []
    for i, k in enumerate(keys, 1):
        log("\n%s\n[%d/%d] %s\n%s" % ("=" * 54, i, len(keys), k, "=" * 54))
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
