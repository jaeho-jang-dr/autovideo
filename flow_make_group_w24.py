# -*- coding: utf-8 -*-
"""★W24 그룹 동작 영상 생성 — 등록 캐릭터 참조 + 8초 + 16:9 (2026-08-03).

`flow_make_clip5_w24.py` 에서 실측 확정한 절차를 그룹용으로 일반화했다.
클립5와 다른 점: ①라스트신 대신 **그 그룹의 캐릭터만** 참조로 붙인다
②길이를 **8초**로 맞춘다(24fps × 8s = 192프레임 → 3장 중 1장 = 64컷)
③매 회차 시작에 **이전 참조를 지운다**(안 지우면 지난 그룹이 섞여 들어온다)

전제: 크롬이 CDP 9222 로 떠 있고 캐릭터 7종이 등록돼 있어야 한다.
      → `python flow_register_chars_w24.py all` 이 끝난 상태

사용:
  python flow_make_group_w24.py --list
  python flow_make_group_w24.py a_write_jamo
  python flow_make_group_w24.py --all
"""
import argparse
import os
import re
import subprocess
import time

from playwright.sync_api import sync_playwright

import flow_cdp_pipeline as P
from gen_w24_group_prompts import ACTS

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

PROFILE = os.path.abspath("assets/chrome_profile")
PROMPT_DIR = "W24/prompts"
OUT_DIR = "W24/group_clips"
GEN_WAIT = 420   # ★7참조 통짜 컷은 더 오래 걸린다          # 생성 대기 상한(초)

# ★★Flow 캐릭터는 **프로젝트별**이다(2026-08-03 실측 사고).
#   배경 작업이 설정 칩을 잡으려고 새 프로젝트를 여럿 만들어 놨는데, 거기엔 캐릭터가 없다.
#   "열려 있는 아무 프로젝트"를 쓰면 참조 0개로 엉뚱한 인물이 생성된다(b_jump 폐기).
#   → 7종이 등록된 프로젝트를 **못박는다.**
CHAR_PROJECT = ("https://labs.google/fx/ko/tools/flow/project/"
                "f51ea4d3-90ac-43be-b0af-f7d5b254a452")

REFS = {k: refs for k, _g, refs, _s, _a in ACTS}
SCENES = {k: s for k, _g, _r, s, _a in ACTS}

JS_ROWS = """() => {
  const out = [];
  for (const e of document.querySelectorAll('*')) {
    if (e.children.length > 3) continue;
    const t = (e.innerText || '').trim();
    if (!t || t.split('\\n').length !== 2) continue;
    const r = e.getBoundingClientRect();
    if (r.width < 150 || r.width > 460 || r.height < 28 || r.height > 64) continue;
    out.push({t: t.replace('\\n', '|'), x: Math.round(r.left + r.width / 2),
              y: Math.round(r.top + r.height / 2)});
  }
  return out;
}"""

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

# 프롬프트 바 안의 '×'(참조 전체 지우기) — textbox 조상 안에서만 찾는다
JS_CLEAR = """() => {
  const box = document.querySelector("div[role='textbox'][contenteditable='true']");
  if (!box) return false;
  let p = box.parentElement;
  for (let i = 0; i < 5 && p; i++, p = p.parentElement) {
    for (const b of p.querySelectorAll('button')) {
      const t = (b.innerText || '').trim();
      const r = b.getBoundingClientRect();
      if (r.width > 0 && (t === 'close' || t === '×' || t === 'clear')) { b.click(); return true; }
    }
  }
  return false;
}"""

JS_AGREE = """() => {
  for (const b of document.querySelectorAll('button,[role=button],a')) {
    if ((b.innerText||'').trim() === '동의함' && b.getBoundingClientRect().width > 0) {
      b.click(); return true;
    }
  }
  return false;
}"""


def log(m):
    print(m, flush=True)


def refcount(pg):
    return pg.evaluate(JS_REFCOUNT)


def clear_refs(pg):
    for _ in range(12):
        if refcount(pg) <= 0:
            return True
        if not pg.evaluate(JS_CLEAR):
            break
        time.sleep(1.2)
    return refcount(pg) <= 0


def open_picker(pg):
    plus = pg.evaluate("""() => {
      for (const b of document.querySelectorAll('button')) {
        const t = (b.innerText||'').trim(); const r = b.getBoundingClientRect();
        if (t.startsWith('add_2') && r.width > 0)
          return {x: Math.round(r.left+r.width/2), y: Math.round(r.top+r.height/2)};
      }
      return null;
    }""")
    if not plus:
        return False
    pg.mouse.click(plus["x"], plus["y"])
    time.sleep(3.5)
    return True


def add_ref(pg, name):
    """★피커는 단일 선택 — 하나 고르고 '프롬프트에 추가'를 반복해 누적한다."""
    if not open_picker(pg):
        return False
    rows = pg.evaluate(JS_ROWS)
    hit = next((r for r in rows if r["t"] == f"{name}|캐릭터"), None)
    if not hit:
        log(f"    ★목록에 없음: {name}")
        pg.keyboard.press("Escape"); time.sleep(1)
        return False
    pg.mouse.click(hit["x"], hit["y"])
    time.sleep(1.2)
    add = pg.locator("button:has-text('프롬프트에 추가')").first
    if add.count() == 0:
        pg.keyboard.press("Escape"); time.sleep(1)
        return False
    add.click()
    time.sleep(2.5)
    for _ in range(2):
        if pg.evaluate(JS_AGREE):
            time.sleep(1.5)
            break
        time.sleep(1)
    return True


def set_chip(pg, want=("동영상", "8s", "16:9")):
    """설정 칩을 열어 길이·비율을 맞춘다. 항목이 없으면 현재 설정을 유지한다."""
    chip = pg.evaluate("""() => {
      for (const b of document.querySelectorAll('button')) {
        const t = (b.innerText||'').trim(); const r = b.getBoundingClientRect();
        if (r.width > 0 && r.top > 700 && /crop_|동영상\\s*·|Nano Banana/.test(t))
          return {t: t.replace(/\\n/g,' '), x: Math.round(r.left+r.width/2),
                  y: Math.round(r.top+r.height/2)};
      }
      return null;
    }""")
    if not chip:
        log("    ★설정 칩 없음 — 현재 설정으로 진행")
        return False
    log(f"    칩: {chip['t'][:34]!r}")
    pg.mouse.click(chip["x"], chip["y"])
    time.sleep(2.5)
    for w in want:
        it = pg.evaluate("""(w) => {
          for (const b of document.querySelectorAll("button,[role=menuitem],[role=option]")) {
            const t = (b.innerText||'').trim(); const r = b.getBoundingClientRect();
            if (r.width > 0 && t.replace(/\\s/g,'').includes(w.replace(/\\s/g,'')))
              return {x: Math.round(r.left+r.width/2), y: Math.round(r.top+r.height/2)};
          }
          return null;
        }""", w)
        if it:
            pg.mouse.click(it["x"], it["y"])
            time.sleep(2)
            log(f"    {w} 선택")
        else:
            log(f"    ({w} 항목 없음 — 유지)")
    pg.keyboard.press("Escape")
    time.sleep(1.5)
    now = pg.evaluate("""() => {
      for (const b of document.querySelectorAll('button')) {
        const t = (b.innerText||'').trim();
        if (b.getBoundingClientRect().width > 0 && /crop_|동영상\\s*·|Nano Banana/.test(t))
          return t.replace(/\\n/g,' ');
      }
      return '?';
    }""")
    log(f"    확정: {now[:34]!r}")
    return True


JS_SRCS = """() => [...document.querySelectorAll('video')]
  .map(v => v.currentSrc || v.src || '').filter(Boolean)"""


def fetch_video(pg, out, src):
    """★타일 클릭/다운로드 버튼보다 <video> 의 src 를 직접 받는 게 확실하다."""
    if not src:
        return False
    r = pg.context.request.get(src, timeout=180000)
    body = r.body()
    if r.status != 200 or body[4:8] != b"ftyp":
        log(f"    ★내려받기 실패 status={r.status} head={body[:12]}")
        return False
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "wb").write(body)
    return True


def run_one(pg, key):
    prompt_file = f"{PROMPT_DIR}/{key}.txt"
    if not os.path.exists(prompt_file):
        log(f"★프롬프트 없음: {prompt_file}"); return False
    prompt = re.sub(r"\s+", " ", open(prompt_file, encoding="utf-8").read()).strip()
    out = os.path.abspath(f"{OUT_DIR}/{key}.mp4")
    refs = REFS[key]

    log(f"\n=== {key}  ({len(refs)}인: {', '.join(refs)})  씬 {SCENES[key]} ===")
    # ★반드시 캐릭터가 등록된 프로젝트로 간다(위 CHAR_PROJECT 주석 참조)
    pg.goto(CHAR_PROJECT, wait_until="domcontentloaded")
    time.sleep(9)

    log(f"[1] 이전 참조 지우기 (현재 {refcount(pg)}개)")
    clear_refs(pg)
    log(f"    남은 참조 {refcount(pg)}개")

    log("[2] 이 그룹의 캐릭터만 참조로 붙이기")
    for nm in refs:
        add_ref(pg, nm)
        log(f"    + {nm}  (붙은 참조 {refcount(pg)}개)")
    # ★참조가 하나라도 모자라면 **그 자리에서 멈춘다.** 그냥 만들면 엉뚱한 인물이 나오고
    #   크레딧만 버린다(2026-08-03 b_jump 사고).
    got = refcount(pg)
    if got != len(refs):
        log(f"    ★참조 개수 불일치: {got} ≠ {len(refs)} — 생성하지 않고 중단한다")
        return False

    log("[3] 설정 — 8초 / 16:9")
    set_chip(pg)

    log(f"[4] 프롬프트 입력 ({len(prompt)}자)")
    box = pg.locator("div[role='textbox'][contenteditable='true']").first
    box.click()
    time.sleep(0.4)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Set-Clipboard -Value ([Console]::In.ReadToEnd())"],
                   input=prompt, text=True, encoding="utf-8", check=False)
    box.press("Control+v")
    time.sleep(2)

    # ★생성 전에 화면에 이미 있던 동영상 src 를 기억한다.
    #   이걸 안 하면 지난 회차 영상을 '완성'으로 오인해 그대로 내려받는다(2026-08-03 실측 사고).
    before = set(pg.evaluate(JS_SRCS))
    log(f"[5] 만들기 (기존 동영상 {len(before)}개 기억)")
    go = pg.evaluate("""() => {
      for (const b of document.querySelectorAll('button')) {
        const t = (b.innerText||'').trim(); const r = b.getBoundingClientRect();
        if (t.startsWith('arrow_forward') && r.width > 0)
          return {x: Math.round(r.left+r.width/2), y: Math.round(r.top+r.height/2)};
      }
      return null;
    }""")
    if not go:
        log("★'만들기' 버튼 없음"); return False
    pg.mouse.click(go["x"], go["y"])
    time.sleep(5)

    log(f"[6] 생성 대기 (최대 {GEN_WAIT}초) — ★새 src 가 뜰 때까지")
    new_src = None
    for i in range(GEN_WAIT // 15):
        time.sleep(15)
        fresh = [s for s in pg.evaluate(JS_SRCS) if s not in before]
        if fresh:
            new_src = fresh[0]
            log(f"    {(i+1)*15}s — 새 동영상 확인")
            break
        if (i + 1) % 4 == 0:
            log(f"    {(i+1)*15}s …")
    if not new_src:
        log("★생성 실패(시간 초과 — 새 동영상 없음)"); return False

    log("[7] 내려받기")
    time.sleep(3)
    if not fetch_video(pg, out, new_src):
        return False
    import subprocess as sp
    d = sp.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "csv=p=0", out], capture_output=True, text=True).stdout.strip()
    log(f"✅ {out}  {os.path.getsize(out)//1024}KB  {d}s")
    return True


def main(keys):
    os.makedirs(OUT_DIR, exist_ok=True)
    P.launch_chrome(PROFILE)
    done, fail = [], []
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(P.CDP_URL)
        ctx = b.contexts[0]
        pg = next((p for p in ctx.pages if "/project/" in p.url), None) or ctx.pages[0]
        pg.bring_to_front()
        time.sleep(2)
        for k in keys:
            try:
                (done if run_one(pg, k) else fail).append(k)
            except Exception as e:
                log(f"★{k} 예외: {str(e)[:120]}")
                fail.append(k)
    log(f"\n완료 {len(done)}/{len(keys)}: {', '.join(done)}")
    if fail:
        log(f"실패: {', '.join(fail)}")
    return not fail


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    allk = [k for k, *_ in ACTS]
    if a.list:
        for k in allk:
            p = f"{OUT_DIR}/{k}.mp4"
            print(f"[{'有' if os.path.exists(p) else '  '}] {k:16s} {len(REFS[k])}인  씬 {SCENES[k]}")
    else:
        main(allk if a.all else (a.keys or allk[:1]))
