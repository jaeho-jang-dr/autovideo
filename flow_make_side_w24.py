# -*- coding: utf-8 -*-
"""등록된 Flow 캐릭터로 **오른쪽 측면 정지컷** 1장 만들기 (나노 바나나).
   ★사장님 지시(2026-08-04): "정면 띄우고 프롬프트로 설정 클릭하고 이미지 나노 바나나로,
     그다음 프롬프트 넣기." — 타일 더블클릭으로 편집기에 들어가는 경로는 실패했다.
     동영상 만들 때와 **같은 경로**로 가고 설정 칩만 이미지/나노바나나로 바꾼다.

   캐릭터는 이미 Flow 에 등록돼 있으므로 정면 이미지를 따로 올리지 않고 `@이름`을 참조로 붙인다.
   절차는 flow_make_group_w24 의 검증된 함수를 그대로 쓴다(재발명 금지).

   사용: python flow_make_side_w24.py teacherjay
"""
import argparse
import os
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

import flow_cdp_pipeline as P
import flow_make_group_w24 as G

OUT_DIR = "W24/guides"
GEN_WAIT = 180

PROMPT = (
    "A single character, alone in the frame, standing still in a FULL RIGHT-SIDE PROFILE: the body "
    "is turned ninety degrees so we see him from his left side, one shoulder toward the camera, the "
    "nose and chin clearly in profile, both eyes NOT visible, looking straight ahead to the RIGHT. "
    "He stands upright and relaxed with BOTH ARMS HANGING NATURALLY at his sides and BOTH HANDS "
    "EMPTY - he holds nothing at all. Feet flat on the ground, weight even.\n"
    "Keep the character exactly as registered: same face, same bald head with the single curl, same "
    "blue and white checked shirt with rolled sleeves, same beige trousers, same WHITE sneakers on "
    "BOTH feet, same flat cartoon style with clean black outlines and the same body proportions.\n"
    "ANATOMY: exactly one head, two arms with two hands, two legs, two white sneakers. Nothing extra.\n"
    "FULL BODY from the top of the head to below the shoes is inside the frame, with clear empty "
    "space above the head and below the shoes.\n"
    "BACKGROUND: pure flat white (#FFFFFF), completely empty - no chair, no furniture, no props, no "
    "floor line, no shadow, no scenery, no text, no watermark."
)


def log(m):
    print(m, flush=True)


def set_image_chip(pg):
    """설정 칩 → '이미지' → 모델 나노 바나나. (동영상 경로의 set_chip 과 같은 방식)"""
    log(f"    칩(전): {G.chip_text(pg)[:40]!r}")
    P.open_chip(pg)
    # ★왼쪽 레일에도 'image 이미지 보기'가 있어 그걸 눌러버린다(x≈40). 설정 패널은 x>900 이다.
    #   좌표로 걸러 **설정 패널 안의 '이미지'** 만 누른다.
    it = pg.evaluate("""() => {
      for (const b of document.querySelectorAll('button,[role=menuitem],[role=option]')) {
        const r = b.getBoundingClientRect(); const t = (b.innerText||'').trim();
        if (r.width > 0 && r.left > 900 && /^image\\n?이미지$/.test(t))
          return {x: Math.round(r.left + r.width/2), y: Math.round(r.top + r.height/2)};
      }
      return null;
    }""")
    if not it:
        log("    ★설정 패널의 '이미지' 항목을 못 찾음")
        return False
    pg.mouse.click(it["x"], it["y"])
    log(f"    이미지 선택 ({it['x']},{it['y']})")
    time.sleep(1.5)
    if not P.find_btn(pg, "Nano\\s*Banana"):
        P.click_btn(pg, "arrow_drop_down", label="모델 드롭다운")
        P.click_btn(pg, "Nano", label="Nano Banana")
        P.open_chip(pg)
    else:
        log("    모델 이미 Nano Banana")
    pg.keyboard.press("Escape")
    time.sleep(1.0)
    now = G.chip_text(pg)
    log(f"    칩(후): {now[:40]!r}")
    return "Nano" in now or "이미지" in now


def run(name):
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.abspath(f"{OUT_DIR}/{name}_side_right.png")
    P.launch_chrome(os.path.abspath("assets/chrome_profile"))
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(P.CDP_URL)
        ctx = b.contexts[0]
        pg = next((p for p in ctx.pages if "/project/" in p.url), None) or ctx.pages[0]
        pg.bring_to_front()
        log(f"\n=== {name} 오른쪽 측면 정지컷 ===")
        pg.goto(G.CHAR_PROJECT, wait_until="domcontentloaded")
        time.sleep(9)

        log("[1] 설정 — 이미지 / 나노 바나나")
        if not set_image_chip(pg):
            log("    ★이미지 모드 전환 실패 — 멈춘다")
            return False

        log(f"[2] 이전 참조 지우기 (현재 {G.refcount(pg)}개)")
        G.clear_refs(pg)
        log(f"[3] @{name} 참조 붙이기")
        G.add_ref(pg, name)
        if G.refcount(pg) != 1:
            log(f"    ★참조 {G.refcount(pg)}개 — 1개여야 한다. 멈춘다")
            return False

        log(f"[4] 프롬프트 입력 ({len(PROMPT)}자)")
        box = pg.locator("div[role='textbox'][contenteditable='true']").first
        box.click()
        time.sleep(0.4)
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Set-Clipboard -Value ([Console]::In.ReadToEnd())"],
                       input=PROMPT, text=True, encoding="utf-8", check=False)
        box.press("Control+v")
        time.sleep(2)

        before = set(pg.evaluate(G.JS_SRCS if hasattr(G, "JS_SRCS") else "() => []"))
        log("[5] 만들기")
        if not P.click_btn(pg, "arrow_forward", label="만들기"):
            log("    ★'만들기' 클릭 실패")
            return False
        log(f"[6] 생성 대기 (최대 {GEN_WAIT}초)")
        for i in range(GEN_WAIT // 10):
            time.sleep(10)
            n = pg.evaluate("() => document.querySelectorAll('img[src^=\"blob:\"],"
                            "img[src*=\"googleusercontent\"]').length")
            if i and i % 3 == 0:
                log(f"    {(i + 1) * 10}s — 이미지 {n}개")
        log(f"[7] 결과는 화면에서 확인 → 다운로드는 수동 또는 후속 단계")
        log(f"    저장 예정 경로: {out}")
        return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?", default="teacherjay")
    raise SystemExit(0 if run(ap.parse_args().name) else 1)
