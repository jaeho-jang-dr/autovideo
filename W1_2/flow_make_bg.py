# -*- coding: utf-8 -*-
"""W1-2 배경 생성 — 텍스트 전용(업로드 없음). **좌표 금지, locator.click() 만.**

`W1_2/flow_make_clips.py` 와 같은 경로를 쓰되 **이미지 업로드 단계가 없다**.
배경은 참조 이미지가 필요 없으므로 새 프로젝트에서 곧바로 프롬프트를 넣는다.

    python W1_2/flow_make_bg.py gwanghwamun_bench      # 하나만
    python W1_2/flow_make_bg.py --all                  # 미생성분 전부
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
from W1_2 import bg_defs                                 # noqa: E402

OUT = "W1_2/bg"
SHOT = "W1_2/_failshot"
GEN_WAIT = 180
COOL = 10


def log(m):
    print(m, flush=True)


def kill_chrome():
    # ★사장님 지시(2026-08-31): 통짜 taskkill은 보고 계신 다른 크롬 창까지 닫는다 —
    #   자동화 프로필(assets/chrome_profile)의 크롬만 골라 끈다 [[never-kill-all-chrome]].
    avf.force_kill_profile_chrome(os.path.abspath("assets/chrome_profile"))


def set_image_mode(pg):
    """정지 배경용 — 칩을 **이미지 모드**로 바꾼다. ★좌표 대신 locator 로 누른다.

    ★고를 때마다 메뉴가 닫힌다 → **항목 하나 고를 때마다 칩을 다시 연다**
      (flow_make_group_w24.set_chip 에서 검증된 순서).
    """
    def open_chip():
        c = pg.locator("button").filter(
            has_text=re.compile("동영상 ·|이미지 ·|Nano Banana")).last
        if c.count() == 0:
            return False
        c.scroll_into_view_if_needed()
        c.click(timeout=12000)
        pg.wait_for_timeout(2500)
        return True

    def pick(name):
        it = pg.locator("button, [role=menuitem], [role=option], tp-yt-paper-item").filter(
            has_text=re.compile(name)).last
        if it.count() == 0:
            log("      (%s 항목 없음)" % name)
            return False
        it.click(timeout=12000)
        pg.wait_for_timeout(2500)
        log("      %s 선택" % name)
        return True

    for _ in range(8):                       # 새 프로젝트 직후엔 하단 바가 늦게 그려진다
        if open_chip():
            break
        pg.wait_for_timeout(4000)
    else:
        log("    ★설정 칩 없음 — 현재 설정으로 진행")
        return False

    # ★이미지 모드에는 비율 항목이 없다 — 칩이 기본으로 crop_16_9 다.
    #   없는 항목을 누르려다 12초 타임아웃으로 죽었다(2026-08-11 실측).
    pick("이미지")
    if open_chip():
        pick("Nano Banana")
    chip = pg.locator("button").filter(
        has_text=re.compile("이미지 ·|Nano Banana|동영상 ·")).last
    log("    칩(후): %r" % (chip.inner_text().strip()[:44] if chip.count() else "?"))
    return True


def make_one(key):
    kind, _, _ = bg_defs.BY[key]
    prompt = re.sub(r"[ \t]+", " ", bg_defs.prompt(key)).strip()
    ext = "mp4" if kind == "video" else "png"
    out = os.path.abspath(os.path.join(OUT, "%s.%s" % (key, ext)))
    os.makedirs(OUT, exist_ok=True)

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
        pg.wait_for_timeout(3500)

        log("  [2] 설정 — %s · 16:9" % ("동영상 · Omni Flash · 8초" if kind == "video"
                                        else "이미지 · Nano Banana"))
        if kind == "video":
            G.set_chip(pg, model=os.environ.get("W1D2_BG_MODEL", "Omni Flash"))
        else:
            set_image_mode(pg)

        log("  [3] 프롬프트 → 만들기 (%d자)" % len(prompt))
        before_v = pg.evaluate(
            "() => [...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src||'').filter(Boolean)")
        before_i = pg.evaluate(
            "() => [...document.querySelectorAll('img')].map(v=>v.currentSrc||v.src||'').filter(s=>s&&s.startsWith('http'))")
        avf.fill_prompt(pg, prompt)
        pg.wait_for_timeout(1500)
        btn = pg.locator("button").filter(has_text=re.compile("arrow_forward")).filter(
            has_text=re.compile("만들기|Create|Generate")).last
        if btn.count() == 0:
            raise RuntimeError("'만들기' 버튼 없음")
        btn.scroll_into_view_if_needed()
        btn.click(timeout=15000)
        log("    만들기(→) locator 클릭")
        pg.wait_for_timeout(4000)
        left = pg.evaluate("""() => { const b=document.querySelector("div[role='textbox'][contenteditable='true']");
            return b ? (b.innerText||'').trim().length : -1; }""")
        log("    프롬프트 잔여 %d자 (원문 %d자)" % (left, len(prompt)))
        if left > len(prompt) * 0.5:
            log("    안 눌린 것 같다 — 한 번 더")
            try:
                btn.click(timeout=10000)
                pg.wait_for_timeout(4000)
            except Exception as e:
                log("    재클릭 실패: " + str(e)[:60])

        log("  [4] 생성 대기 (최대 %d초)" % GEN_WAIT)
        src, step = None, 15 if kind == "video" else 10
        for i in range(GEN_WAIT // step):
            pg.wait_for_timeout(step * 1000)
            if kind == "video":
                now = [s for s in pg.evaluate(
                    "() => [...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src||'').filter(Boolean)")
                    if s not in before_v]
            else:
                now = [s for s in pg.evaluate(
                    "() => [...document.querySelectorAll('img')].map(v=>v.currentSrc||v.src||'').filter(s=>s&&s.startsWith('http'))")
                    if s not in before_i]
            if now:
                src = now[0]
                log("    %ds — 새 미디어 확인" % ((i + 1) * step))
                break
        if not src:
            os.makedirs(SHOT, exist_ok=True)
            try:
                pg.screenshot(path=os.path.join(SHOT, "bg_%s_fail.png" % key))
                log("    [실패화면] %s/bg_%s_fail.png" % (SHOT, key))
            except Exception:
                pass
            raise RuntimeError("생성 실패(시간 초과)")

        log("  [5] 내려받기")
        if kind == "video":
            ok = G.fetch_video(pg, out, src)
        else:
            ok = G.fetch_image(pg, out, src) if hasattr(G, "fetch_image") else False
            if not ok:
                # 이미지가 전용 함수가 없으면 src 를 직접 받는다
                data = pg.evaluate("""async (u) => {
                    const r = await fetch(u); const b = await r.arrayBuffer();
                    return Array.from(new Uint8Array(b)); }""", src)
                open(out, "wb").write(bytes(data))
                ok = os.path.getsize(out) > 10000
        if not ok:
            raise RuntimeError("내려받기 실패")
        log("  ✅ %s  %dKB" % (out, os.path.getsize(out) // 1024))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    keys = a.keys
    if a.all or not keys:
        keys = [k for k, kind, _, _ in bg_defs.BGS
                if not os.path.exists(os.path.join(
                    OUT, "%s.%s" % (k, "mp4" if kind == "video" else "png")))]
    if not keys:
        log("대상 없음")
        return 0
    ok, fail = [], []
    for i, k in enumerate(keys, 1):
        log("\n%s\n[%d/%d] %s (%s)\n%s"
            % ("=" * 54, i, len(keys), k, bg_defs.BY[k][0], "=" * 54))
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
