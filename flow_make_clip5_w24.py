# -*- coding: utf-8 -*-
"""★W24 플래시몹 클립5(폭죽 피날레) 생성 — CDP 9222 + 7캐릭터 참조 + 라스트신 (2026-08-03).

사장님 지시(2026-08-03): ①캐릭터 7개 다 등록 ②라스트신을 프롬프트로 사용
③클립5 프롬프트 투입 ④**캐릭터 일관성 유지가 최우선**.

절차 (실측 확정):
 1. CDP 9222 로 붙는다(크롬은 flow_cdp_pipeline.launch_chrome 으로 띄운다)
 2. 프로젝트 루트 → 프롬프트 바의 `+`(add_2) → 애셋 피커
 3. 피커 목록에서 **캐릭터 7종 + 라스트신 이미지**를 골라 `프롬프트에 추가`
 4. 설정 칩 확인(16:9 / 10s) · 모델은 참조 7개를 받는 것으로
 5. 프롬프트 붙여넣기(★`@이름` 유지 — 이제 등록돼 있으므로 살아 있는 참조다)
 6. `만들기` → 생성 대기 → 왼편 타일 → 편집화면 → 다운로드

★클립1~4의 '이름표' 사고 원인: 캐릭터가 **등록돼 있지 않은 채** `@이름`을 넣어서
  모델이 그 글자를 그림 안에 라벨로 그렸다. 등록 후에는 살아 있는 참조가 된다.

사용:
  python flow_make_clip5_w24.py           # 전체
  python flow_make_clip5_w24.py --refs-only   # 참조 붙이기까지만
"""
import argparse
import os
import re
import shutil
import time

from playwright.sync_api import sync_playwright

import flow_cdp_pipeline as P

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

PROFILE = os.path.abspath("assets/chrome_profile")
FIRST_FRAME_NAME = "clip4_lastframe.png"
PROMPT_FILE = "W24/clip5_prompt.txt"
OUT = os.path.abspath("W24/dance/clip5_finale.mp4")
DL_DIR = "debug/downloads"
CHARS = ["teacherjay", "zollaman", "zollagirl", "stickman", "injun", "jieun", "madamjay"]

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


def agree(pg, rounds=4):
    for _ in range(rounds):
        if pg.evaluate(JS_AGREE):
            log("    권리 확인 동의")
            time.sleep(2)
            return
        time.sleep(2)


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
    time.sleep(4)
    return True


def ref_count(pg):
    """프롬프트 바에 붙은 참조 썸네일 개수."""
    return pg.evaluate("""() => {
      const box = document.querySelector("div[role='textbox'][contenteditable='true']");
      if (!box) return -1;
      let p = box.parentElement;
      for (let i = 0; i < 4 && p; i++, p = p.parentElement) {
        const n = p.querySelectorAll('img').length;
        if (n) return n;
      }
      return 0;
    }""")


def pick_refs(pg):
    """★피커는 **단일 선택**이다 — 한 번에 하나씩 골라 '프롬프트에 추가'를 반복해 누적한다.
    (여러 개를 연달아 클릭하면 마지막 하나만 붙는다 — 2026-08-03 실측)"""
    want = [(f"{c}|캐릭터", c) for c in CHARS] + [(f"{FIRST_FRAME_NAME}|이미지", "라스트신")]
    picked = []
    for key, label in want:
        if not open_picker(pg):
            log("    ★피커 안 열림"); break
        rows = pg.evaluate(JS_ROWS)
        hit = next((r for r in rows if r["t"] == key), None)
        if not hit:
            log(f"    ★목록에 없음: {key}")
            pg.keyboard.press("Escape"); time.sleep(1)
            continue
        pg.mouse.click(hit["x"], hit["y"])
        time.sleep(1.2)
        add = pg.locator("button:has-text('프롬프트에 추가')").first
        if add.count() == 0:
            log(f"    ★'프롬프트에 추가' 없음 ({label})")
            pg.keyboard.press("Escape"); time.sleep(1)
            continue
        add.click()
        time.sleep(3)
        agree(pg, rounds=2)
        picked.append(label)
        log(f"    + {label}  (붙은 참조 {ref_count(pg)}개)")
    return picked


def main(refs_only=False, skip_refs=False):
    prompt = open(PROMPT_FILE, encoding="utf-8").read()
    prompt = re.sub(r"\s+", " ", prompt).strip()      # ★@이름은 그대로 살린다
    log(f"프롬프트 {len(prompt)}자 · @참조 {len(re.findall(r'@\\w+', prompt))}개")

    P.launch_chrome(PROFILE)
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(P.CDP_URL)
        ctx = b.contexts[0]
        pg = next((p for p in ctx.pages if "/project/" in p.url), None) or ctx.pages[0]
        pg.bring_to_front()
        time.sleep(2)
        root = pg.url.split("/character")[0]
        log(f"[1] 프로젝트 {root[-12:]}")
        if not skip_refs:
            pg.goto(root, wait_until="domcontentloaded")
            time.sleep(9)
            log("[2~3] 참조 하나씩 누적 — 캐릭터 7 + 라스트신")
            picked = pick_refs(pg)
            pg.screenshot(path="scratch/yt/clip5_refs.png")
            log(f"    붙인 참조 {len(picked)}개 / 화면 확인 {ref_count(pg)}개 "
                f"→ scratch/yt/clip5_refs.png")
        else:
            log(f"[2~3] 참조 붙이기 건너뜀 (현재 {ref_count(pg)}개 부착됨)")
        if refs_only:
            return True

        log("[4] 프롬프트 입력")
        box = pg.locator("div[role='textbox'][contenteditable='true']").first
        box.click()
        time.sleep(0.4)
        import subprocess
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Set-Clipboard -Value ([Console]::In.ReadToEnd())"],
                       input=prompt, text=True, encoding="utf-8", check=False)
        box.press("Control+v")
        time.sleep(2)
        pg.screenshot(path="scratch/yt/clip5_prompt_in.png")

        log("[5] 만들기")
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

        log("[6] 생성 대기 (최대 300초)")
        before = set(os.listdir(DL_DIR)) if os.path.isdir(DL_DIR) else set()
        for i in range(20):
            time.sleep(15)
            tiles = P.media_tiles(pg)
            has_vid = pg.evaluate("() => document.querySelectorAll('video').length")
            log(f"    {(i+1)*15}s — 타일 {len(tiles)} · video {has_vid}")
            if has_vid:
                break
        pg.screenshot(path="scratch/yt/clip5_generated.png")
        return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--refs-only", action="store_true")
    ap.add_argument("--skip-refs", action="store_true")
    a = ap.parse_args()
    main(a.refs_only, a.skip_refs)
