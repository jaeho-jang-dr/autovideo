# -*- coding: utf-8 -*-
"""W1-3 배경 생성 — 청계천, 텍스트 전용(업로드 없음). **좌표 금지, locator.click() 만.**

`W1_2/flow_make_bg.py`(W1-2 광화문광장)와 완전히 같은 검증된 절차를 그대로 쓰되
프롬프트 데이터(`W1_3/bg_defs_cheonggye.py`)와 출력 경로만 청계천용으로 바꿨다.
새 자동화 절차를 만들지 않는다.

    python W1_3/flow_make_bg_cheonggye.py cheonggye_entrance   # 하나만
    python W1_3/flow_make_bg_cheonggye.py --all                # 미생성분 전부
"""
import argparse
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "W1_2"))
sys.path.insert(0, os.path.join(ROOT, "W1_3"))
os.chdir(ROOT)

from playwright.sync_api import sync_playwright          # noqa: E402
import flow_cdp_pipeline as P                             # noqa: E402
import flow_make_group_w24 as G                            # noqa: E402
import autoveo_flow as avf                                  # noqa: E402
import bg_defs_cheonggye as bg_defs                          # noqa: E402

OUT = "W1_3/bg"
SHOT = "W1_3/_failshot"
GEN_WAIT = 180
COOL = 10
PROFILE = os.path.abspath("assets/chrome_profile")


def log(m):
    print(m, flush=True)


def kill_chrome():
    # ★사장님 지시(2026-08-31): 자동화 프로필 크롬만 골라 끈다 — 통짜 taskkill 금지
    #   (보고 계신 다른 크롬 창까지 닫히는 사고 방지, [[never-kill-all-chrome]]).
    avf.force_kill_profile_chrome(PROFILE)


def make_one(key):
    kind, _, _ = bg_defs.BY[key]
    prompt = re.sub(r"[ \t]+", " ", bg_defs.prompt(key)).strip()
    ext = "mp4" if kind == "video" else "png"
    out = os.path.abspath(os.path.join(OUT, "%s.%s" % (key, ext)))
    os.makedirs(OUT, exist_ok=True)

    P.launch_chrome(PROFILE)
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

        log("  [2] 설정 — 동영상 · Omni Flash · 16:9 · 8초")
        G.set_chip(pg, model=os.environ.get("W1D3_BG_MODEL", "Omni Flash"))

        log("  [3] 프롬프트 → 만들기 (%d자)" % len(prompt))
        before_v = pg.evaluate(
            "() => [...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src||'').filter(Boolean)")
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

        log("  [4] 생성 대기 (최대 %d초)" % GEN_WAIT)
        src, step = None, 15
        for i in range(GEN_WAIT // step):
            pg.wait_for_timeout(step * 1000)
            now = [s for s in pg.evaluate(
                "() => [...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src||'').filter(Boolean)")
                if s not in before_v]
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

        log("  [5] 내려받기 (src 직접 fetch — G.fetch_video)")
        ok = G.fetch_video(pg, out, src)
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
