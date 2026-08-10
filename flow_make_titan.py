# -*- coding: utf-8 -*-
"""★titan_science 키프레임/클립 생성 (CDP 9222, 2026-08-03).

`flow_make_group_w24.py` 에서 실측 확정한 절차를 배경용으로 줄였다.
그룹 영상과 다른 점: ①**참조를 하나도 붙이지 않는다**(배경은 참조가 없다)
②정지 배경은 **이미지 모드**로 바꾼 뒤 `<img>` 를 받아 온다.

★생성 전 화면에 있던 미디어 src 를 기억해 **새 src 가 뜰 때만** 내려받는다.
  (안 하면 지난 회차 결과물을 그대로 받아 온다 — 2026-08-03 실측 사고)

사용:
  python flow_make_bg_w24.py --list
  python flow_make_bg_w24.py ddp_hall
  python flow_make_bg_w24.py --stills      # 정지 8키
  python flow_make_bg_w24.py --videos      # 동영상 4키
  python flow_make_bg_w24.py --all
"""
import argparse
import os
import re
import subprocess
import time

from playwright.sync_api import sync_playwright

import flow_cdp_pipeline as P
from gen_titan_prompts import SCENES as BGS

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

PROFILE = os.path.abspath("assets/chrome_profile")
PROMPT_DIR = "titan_science/prompts"
OUT_DIR = "titan_science/keyframes"
GEN_WAIT = 240

KIND = {k: t for k, t, _p in BGS}

JS_VID_SRCS = "() => [...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src||'').filter(Boolean)"
JS_IMG_SRCS = """() => [...document.querySelectorAll('img')]
  .filter(i => /media\\.getMediaUrlRedirect|googleusercontent/.test(i.src||'')
            && i.getBoundingClientRect().width > 150)
  .map(i => i.src)"""

JS_REFCOUNT = """() => {
  const box = document.querySelector("div[role='textbox'][contenteditable='true']");
  if (!box) return -1;
  let p = box.parentElement;
  for (let i = 0; i < 4 && p; i++, p = p.parentElement) {
    const n = p.querySelectorAll('img').length;
    if (n) return n;
  }
  return 0;
}"""

JS_CLEAR = """() => {
  const box = document.querySelector("div[role='textbox'][contenteditable='true']");
  if (!box) return false;
  let p = box.parentElement;
  for (let i = 0; i < 5 && p; i++, p = p.parentElement) {
    for (const b of p.querySelectorAll('button')) {
      const t = (b.innerText || '').trim();
      if (b.getBoundingClientRect().width > 0 && (t === 'close' || t === '×' || t === 'clear')) {
        b.click(); return true;
      }
    }
  }
  return false;
}"""


def log(m):
    print(m, flush=True)


def clear_refs(pg):
    for _ in range(10):
        if pg.evaluate(JS_REFCOUNT) <= 0:
            return
        if not pg.evaluate(JS_CLEAR):
            return
        time.sleep(1.2)


def chip(pg):
    """★설정 칩은 **모드에 따라 글자가 완전히 달라진다**(2026-08-03 실측):
         동영상 모드 → '동영상 · 10s | crop_16_9 | x1'
         이미지 모드 → '🍌 Nano Banana 2 | crop_16_9 | x1'
       그래서 '동영상·/이미지·'로 찾으면 이미지 모드에서 못 찾는다.
       두 모드에 공통으로 들어가는 **`crop_`** 을 기준으로 잡는다.
       ※이걸 놓쳐서 배경 동영상 6편이 이미지 모드로 생성됐다."""
    return pg.evaluate("""() => {
      for (const b of document.querySelectorAll('button')) {
        const t = (b.innerText||'').trim(); const r = b.getBoundingClientRect();
        if (r.width > 0 && r.top > 700 && /crop_|동영상\\s*·|Nano Banana/.test(t))
          return {t: t.replace(/\\n/g,' '), x: Math.round(r.left+r.width/2),
                  y: Math.round(r.top+r.height/2)};
      }
      return null;
    }""")


def pick(pg, want):
    it = pg.evaluate("""(w) => {
      for (const b of document.querySelectorAll("button,[role=menuitem],[role=option]")) {
        const t = (b.innerText||'').trim(); const r = b.getBoundingClientRect();
        if (r.width > 0 && t.replace(/\\s/g,'').includes(w.replace(/\\s/g,'')))
          return {x: Math.round(r.left+r.width/2), y: Math.round(r.top+r.height/2)};
      }
      return null;
    }""", want)
    if it:
        pg.mouse.click(it["x"], it["y"])
        time.sleep(2)
        log(f"    {want} 선택")
        return True
    log(f"    ({want} 항목 없음 — 유지)")
    return False


def set_mode(pg, kind):
    # ★새 프로젝트 직후엔 하단 바가 아직 안 그려져 있다 → 칩이 보일 때까지 몇 번 다시 본다
    c = None
    for _ in range(8):
        c = chip(pg)
        if c:
            break
        time.sleep(4)
    if not c:
        log("    ★설정 칩 없음 — 현재 설정으로 진행")
        return False
    log(f"    칩: {c['t'][:36]!r}")
    pg.mouse.click(c["x"], c["y"])
    time.sleep(2.5)
    if kind == "STILL":
        pick(pg, "이미지")
        pick(pg, "Nano Banana")
    else:
        pick(pg, "동영상")
        # ★2026-08-10 — 모델을 안 고르면 기본값으로 생성돼 실패하는 경우가 있다(S5, 240초 초과).
        #   flow_make_group_w24.set_chip 에서 검증된 방식: **모델이 이미 맞으면 건드리지 않는다**
        #   (드롭다운을 열었다 닫으면 패널째 닫혀 뒤 항목을 못 누른다).
        # ★사장님 지시(2026-08-10): "이 두 개(S5·S17)만 Quality 쓰고 이후부터는
        #   Veo 3.1 Lite만 쓴다. 토큰이 모자랄 것이다."
        #   → 기본값은 **Lite**. Quality 가 꼭 필요하면 TITAN_MODEL 로 그때만 올린다.
        model = os.environ.get("TITAN_MODEL", "Veo 3.1 - Lite")
        if not P.find_btn(pg, model.replace(" ", "\\s*")):
            P.click_btn(pg, "arrow_drop_down", label="모델 드롭다운")
            if not P.click_btn(pg, model, label=model):
                log(f"    ★모델 '{model}' 항목 없음 — 현재 모델로 진행")
            P.open_chip(pg)
        else:
            log(f"    모델 이미 {model}")
    pick(pg, "16:9")
    pg.keyboard.press("Escape")
    time.sleep(1.5)
    c = chip(pg)
    log(f"    확정: {(c['t'][:36] if c else '?')!r}")
    return True


def new_project(pg):
    """★결과물이 쌓인 프로젝트에서는 **설정 칩이 하단 바에서 사라진다**(2026-08-03 실측).
    칩이 있어야 이미지/동영상 모드와 16:9 를 고를 수 있으므로 **새 프로젝트**에서 시작한다."""
    pg.goto("https://labs.google/fx/ko/tools/flow", wait_until="domcontentloaded")
    time.sleep(8)
    # 프로모/보너스 배너가 '새 프로젝트' 클릭을 가로챈다 → 먼저 닫는다
    for x, y in ((2504, 182), (2491, 115)):
        pg.mouse.click(x, y)
        time.sleep(1.5)
    btn = pg.evaluate("""() => {
      for (const b of document.querySelectorAll('button')) {
        const t = (b.innerText||'').trim(); const r = b.getBoundingClientRect();
        if (t.includes('새 프로젝트') && r.width > 60)
          return {x: Math.round(r.left+r.width/2), y: Math.round(r.top+r.height/2)};
      }
      return null;
    }""")
    if not btn:
        log("    ★'새 프로젝트' 버튼 없음")
        return False
    # ★첫 클릭이 자주 먹지 않는다(배너 잔상·레이아웃 재배치) → 진입할 때까지 몇 번 더 누른다
    for attempt in range(4):
        pg.mouse.click(btn["x"], btn["y"])
        time.sleep(9)
        if "/project/" in pg.url:
            log(f"    새 프로젝트 진입 (시도 {attempt+1}) {pg.url[-14:]}")
            return True
        b2 = pg.evaluate("""() => {
          for (const b of document.querySelectorAll('button')) {
            const t = (b.innerText||'').trim(); const r = b.getBoundingClientRect();
            if (t.includes('새 프로젝트') && r.width > 60)
              return {x: Math.round(r.left+r.width/2), y: Math.round(r.top+r.height/2)};
          }
          return null;
        }""")
        if b2:
            btn = b2
    log(f"    ★새 프로젝트 진입 실패 {pg.url[-14:]}")
    return False


def run_one(pg, key, first):
    kind = KIND[key]
    pf = f"{PROMPT_DIR}/{key}.txt"
    if not os.path.exists(pf):
        log(f"★프롬프트 없음: {pf}")
        return False
    prompt = re.sub(r"\s+", " ", open(pf, encoding="utf-8").read()).strip()
    ext = "mp4" if kind == "VIDEO" else "png"
    out = os.path.abspath(f"{OUT_DIR}/{key}.{ext}")

    log(f"\n=== {key} [{kind}] ===")
    if first:
        # ★모드는 새 프로젝트에서 **한 번만** 잡는다. 이후 생성에는 설정이 유지된다.
        if not new_project(pg):
            return False
        clear_refs(pg)
        log(f"[1] 모드 설정 ({kind})")
        set_mode(pg, kind)
    else:
        log("[1] 모드 유지 (같은 프로젝트에서 이어서)")

    log(f"[2] 프롬프트 ({len(prompt)}자)")
    box = pg.locator("div[role='textbox'][contenteditable='true']").first
    box.click()
    time.sleep(0.4)
    box.press("Control+a")
    box.press("Delete")          # 이어서 만들 때 지난 프롬프트가 남아 있으면 안 된다
    time.sleep(0.3)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Set-Clipboard -Value ([Console]::In.ReadToEnd())"],
                   input=prompt, text=True, encoding="utf-8", check=False)
    box.press("Control+v")
    time.sleep(2)

    js = JS_VID_SRCS if kind == "VIDEO" else JS_IMG_SRCS
    before = set(pg.evaluate(js))
    log(f"[3] 만들기 (기존 미디어 {len(before)}개 기억)")
    go = pg.evaluate("""() => {
      for (const b of document.querySelectorAll('button')) {
        const t = (b.innerText||'').trim(); const r = b.getBoundingClientRect();
        if (t.startsWith('arrow_forward') && r.width > 0)
          return {x: Math.round(r.left+r.width/2), y: Math.round(r.top+r.height/2)};
      }
      return null;
    }""")
    if not go:
        log("★'만들기' 버튼 없음")
        return False
    pg.mouse.click(go["x"], go["y"])
    time.sleep(5)

    log(f"[4] 생성 대기 (최대 {GEN_WAIT}초) — 새 src 대기")
    new_src = None
    step = 10 if kind == "STILL" else 15
    for i in range(GEN_WAIT // step):
        time.sleep(step)
        fresh = [s for s in pg.evaluate(js) if s not in before]
        if fresh:
            new_src = fresh[0]
            log(f"    {(i+1)*step}s — 새 미디어 확인")
            break
    if not new_src:
        log("★생성 실패(시간 초과)")
        return False

    log("[5] 내려받기")
    time.sleep(2)
    r = pg.context.request.get(new_src, timeout=180000)
    body = r.body()
    if r.status != 200 or len(body) < 20000:
        log(f"    ★실패 status={r.status} {len(body)}B")
        return False
    os.makedirs(OUT_DIR, exist_ok=True)
    open(out, "wb").write(body)
    log(f"✅ {out}  {len(body)//1024}KB")
    return True


def main(keys):
    P.launch_chrome(PROFILE)
    done, fail = [], []
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(P.CDP_URL)
        ctx = b.contexts[0]
        pg = next((p for p in ctx.pages if "/project/" in p.url), None) or ctx.pages[0]
        pg.bring_to_front()
        time.sleep(2)
        for i, k in enumerate(keys):
            try:
                (done if run_one(pg, k, first=(i == 0)) else fail).append(k)
            except Exception as e:
                log(f"★{k} 예외: {str(e)[:120]}")
                fail.append(k)
    log(f"\n완료 {len(done)}/{len(keys)}: {', '.join(done)}")
    if fail:
        log(f"실패: {', '.join(fail)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--videos", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    allk = [k for k, *_ in BGS]
    if a.list:
        for k, t, _ in BGS:
            ext = "mp4" if t == "VIDEO" else "png"
            p = f"{OUT_DIR}/{k}.{ext}"
            print(f"[{'有' if os.path.exists(p) else '  '}] {k:18s} [{t}]")
    elif a.stills:
        main([k for k, t, _ in BGS if t == "STILL"])
    elif a.videos:
        main([k for k, t, _ in BGS if t == "VIDEO"])
    else:
        main(allk if a.all else (a.keys or [allk[0]]))
