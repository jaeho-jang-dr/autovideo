#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""titan_chain.py — last image transition 으로 씬 안의 컷을 이어 만든다.

★사장님 지시(2026-08-10)
   "키프레임을 정해서 하나의 그룹을 만들고, 그 그룹 내에서는 last image transition 방식으로
    가야 한다. 연결해야 하고 동질성이 필요한 곳은 전부 이 기법으로 간다."

   앞 컷의 **마지막 프레임**을 뽑아 다음 컷의 첫 프레임으로 올린다.
   프롬프트는 장면을 다시 묘사하지 않고 **이어받는 카메라 동작**만 말한다
   (titan_science/motion/<키>.txt).

★새 절차가 아니다. 검증된 것을 호출만 한다.
   업로드/프롬프트첨부 = flow_walk_from_ref.attach_media
   설정 칩            = flow_make_group_w24.set_chip
   내려받기           = flow_make_group_w24.fetch_video
   업로드 탭 전환      = 여기서만 추가 (Flow UI 가 바뀌어 '업로드' 탭이 생겼다)

  python titan_chain.py s01_b s01_c
  python titan_chain.py --scene 1        # S1 의 이어받기 컷 전부
"""
import argparse
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from playwright.sync_api import sync_playwright        # noqa: E402
import flow_cdp_pipeline as P                          # noqa: E402
import flow_make_group_w24 as G                        # noqa: E402
import flow_walk_from_ref as W                         # noqa: E402
import autoveo_flow as avf                             # noqa: E402

CLIP_DIR = "titan_science/keyframes"
MOTION_DIR = "titan_science/motion"
LAST_DIR = "titan_science/_lastframe"
GEN_WAIT = 180
COOL = 10


def log(m):
    print(m, flush=True)


def prev_key(key):
    """s01_b → s01_wall_v,  s01_c → s01_b,  s04_d → s04_c 처럼 앞 컷을 찾는다."""
    m = re.match(r"(s\d\d)_([bcd])$", key)
    if not m:
        return None
    scene, letter = m.group(1), m.group(2)
    if letter == "b":                       # 1번 컷 = _b/_c/_d 가 아닌 그 씬의 파일
        for f in sorted(os.listdir(CLIP_DIR)):
            if f.startswith(scene + "_") and f.endswith(".mp4") \
               and not re.search(r"_[bcd]\.mp4$", f):
                return f[:-4]
        return None
    return f"{scene}_{chr(ord(letter) - 1)}"


def last_frame(key):
    """앞 컷의 **마지막 프레임**을 png 로 뽑는다."""
    src = os.path.join(CLIP_DIR, key + ".mp4")
    if not os.path.exists(src):
        raise RuntimeError(f"앞 컷 없음: {src}")
    os.makedirs(LAST_DIR, exist_ok=True)
    out = os.path.join(LAST_DIR, key + "_last.png")
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
        capture_output=True, text=True).stdout.strip())
    # 끝에서 0.1초 앞 — 마지막 프레임이 검게 나오는 인코딩을 피한다
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{max(0, dur - 0.12):.2f}",
                    "-i", src, "-frames:v", "1", out], check=True)
    log(f"    앞 컷 {key} 마지막 프레임 → {os.path.basename(out)}")
    return out


def kill_chrome():
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True, text=True)
    time.sleep(3)


def open_upload_tab(pg):
    """★Flow UI 변경 — 업로드한 파일은 '업로드' 탭에 들어간다."""
    return pg.evaluate("""() => {
      for (const e of document.querySelectorAll('button,div,span,a')) {
        const t = (e.innerText || '').trim();
        const b = e.getBoundingClientRect();
        if (b.width > 0 && b.left < 300 && /업로드/.test(t) && t.length < 20) { e.click(); return t; }
      }
      return null;
    }""")


def make_one(key):
    mp = os.path.join(MOTION_DIR, key + ".txt")
    if not os.path.exists(mp):
        raise RuntimeError(f"모션 프롬프트 없음: {mp}")
    prompt = re.sub(r"\s+", " ", open(mp, encoding="utf-8").read()).strip()
    pk = prev_key(key)
    if not pk:
        raise RuntimeError(f"앞 컷을 못 찾음: {key}")
    img = last_frame(pk)
    out = os.path.abspath(os.path.join(CLIP_DIR, key + ".mp4"))

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

        # ★2026-08-10 실측 확정 경로 — 타일 ⋮ 는 쓰지 않는다(상단 툴바를 눌러 버린다).
        #   숨은 file input 주입 → 프롬프트 바 '+' → 다이얼로그의 **넓은** '프롬프트에 추가'
        log("  [2-1] 숨은 file input 에 파일 주입")
        done = False
        for fr in pg.frames:
            try:
                inp = fr.locator("input[type='file']")
                for j in range(inp.count()):
                    try:
                        inp.nth(j).set_input_files(os.path.abspath(img), timeout=5000)
                        done = True
                        break
                    except Exception:
                        pass
            except Exception:
                pass
            if done:
                break
        if not done:
            raise RuntimeError("file input 주입 실패")
        log(f"    업로드 {os.path.basename(img)} → 25초 대기")
        pg.wait_for_timeout(25000)

        log("  [2-2] 프롬프트 바 '+' → 미디어 선택 → 프롬프트에 추가")
        # ★좌표를 쓰지 않는다 — 창 크기가 바뀌면 빗나간다. locator 로 DOM 요소를 잡는다.
        plus = pg.locator("button").filter(has_text=re.compile("add_2")).filter(
            has_text=re.compile("만들기|Create")).last
        if plus.count() == 0:
            raise RuntimeError("프롬프트 바 '+' 버튼을 못 찾았다")
        plus.click(timeout=15000)
        pg.wait_for_timeout(2800)
        # ★'프롬프트에 추가' 는 두 개다 — 다이얼로그 하단의 **넓은** 버튼(width>200)만 누른다
        hit = pg.evaluate("""() => {
          for (const e of document.querySelectorAll('button')) {
            const t = (e.innerText || '').trim();
            const b = e.getBoundingClientRect();
            if (b.width > 200 && t === '프롬프트에 추가') { e.click(); return Math.round(b.width); }
          }
          return 0;
        }""")
        pg.wait_for_timeout(3500)
        n = pg.evaluate("""() => {
          const box = document.querySelector("div[role='textbox'][contenteditable='true']");
          if (!box) return -1;
          let p = box.parentElement;
          for (let i = 0; i < 5 && p; i++, p = p.parentElement) {
            const c = p.querySelectorAll('img').length; if (c) return c; }
          return 0;
        }""")
        log(f"    넓은버튼 w={hit} · 프롬프트 창 이미지 {n}개")
        if n < 1:
            raise RuntimeError("프롬프트에 이미지가 안 붙었다")

        # ★사장님 지시(2026-08-10): "7개의 캐릭터 설정 때만 veo3.1lite 를 쓰고
        #   다른 것은 다 옴니플래쉬를 사용한다." — Veo 는 손·손가락 왜곡이 잦다(s01_b 실측).
        model = os.environ.get("TITAN_MODEL", "Omni Flash")
        log(f"  [3] 동영상 · {model} · 16:9 · 8초")
        G.set_chip(pg, model=model)

        log("  [4] 모션 프롬프트 → 만들기")
        before = set(pg.evaluate(
            "() => [...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src||'').filter(Boolean)"))
        avf.fill_prompt(pg, prompt)
        pg.wait_for_timeout(1500)
        # ★2026-08-10 실측 — avf.generate 는 실패해도 True 를 돌려준다(s01_c 사고).
        #   프롬프트 바 오른쪽 끝의 **arrow_forward|만들기** 를 직접 누르고 눌렸는지 확인한다.
        # ★JS el.click() 은 이 버튼에 안 먹는다(s01_c·s02_b 실측 — 눌린 표시만 나고 실행 안 됨).
        #   좌표도 쓰지 않는다(창 크기가 바뀌면 빗나간다).
        #   **Playwright locator.click()** — DOM 요소를 잡아 실제 이벤트를 쏜다.
        btn = pg.locator("button").filter(has_text=re.compile("arrow_forward")).filter(
            has_text=re.compile("만들기|Create|Generate")).last
        if btn.count() == 0:
            raise RuntimeError("'만들기'(arrow_forward) 버튼을 못 찾았다")
        btn.scroll_into_view_if_needed()
        btn.click(timeout=15000)
        log("    만들기(→) locator 클릭")
        pg.wait_for_timeout(4000)
        # ★재클릭은 함부로 하지 않는다 — 이미 눌린 상태에서 또 누르면 문제가 된다.
        #   프롬프트는 200단어가 넘으므로 **원문 길이의 절반 이상** 남아 있을 때만 안 눌린 것으로 본다.
        left = pg.evaluate("""() => { const b=document.querySelector("div[role='textbox'][contenteditable='true']");
          return b ? (b.innerText||'').trim().length : -1; }""")
        log(f"    프롬프트 잔여 {left}자 (원문 {len(prompt)}자)")
        if left > len(prompt) * 0.5:
            log("    안 눌린 것으로 보인다 — locator 로 한 번 더")
            try:
                btn.click(timeout=10000)
                pg.wait_for_timeout(4000)
            except Exception as e:
                log(f"    재클릭 실패: {str(e)[:60]}")

        log(f"  [5] 생성 대기 (최대 {GEN_WAIT}초)")
        src = None
        for i in range(GEN_WAIT // 15):
            pg.wait_for_timeout(15000)
            now = [s for s in pg.evaluate(
                "() => [...document.querySelectorAll('video')].map(v=>v.currentSrc||v.src||'').filter(Boolean)")
                if s not in before]
            if now:
                src = now[0]
                log(f"    {(i+1)*15}s — 새 미디어 확인")
                break
        if not src:
            raise RuntimeError("생성 실패(시간 초과)")

        log("  [6] 내려받기")
        if not G.fetch_video(pg, out, src):
            raise RuntimeError("내려받기 실패")
        log(f"  ✅ {out}  {os.path.getsize(out)//1024}KB")
        return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keys", nargs="*")
    ap.add_argument("--scene", type=int, help="그 씬의 이어받기 컷 전부")
    ap.add_argument("--rest", action="store_true", help="아직 안 만든 것 전부(의존 순서대로)")
    a = ap.parse_args()

    keys = a.keys
    if a.scene:
        keys = [k[:-4] for k in sorted(os.listdir(MOTION_DIR))
                if k.startswith(f"s{a.scene:02d}_")]
    if a.rest:
        keys = [k[:-4] for k in os.listdir(MOTION_DIR)
                if k.endswith(".txt")
                and not os.path.exists(os.path.join(CLIP_DIR, k[:-4] + ".mp4"))]
    # ★이어받기라 순서가 중요하다 — 씬 번호 → b,c,d 순
    keys = sorted(keys, key=lambda k: (int(k[1:3]), k[4] if len(k) > 4 else ""))
    if not keys:
        log("대상 없음"); return 1

    ok, fail = [], []
    for i, k in enumerate(keys, 1):
        log(f"\n{'='*54}\n[{i}/{len(keys)}] {k}\n{'='*54}")
        kill_chrome()
        time.sleep(COOL)
        try:
            make_one(k)
            ok.append(k)
        except Exception as e:
            log(f"  ★{k} 실패: {str(e)[:120]}")
            fail.append(k)
        kill_chrome()
        time.sleep(COOL)

    log(f"\n완료 {len(ok)}/{len(keys)}")
    if fail:
        log(f"실패: {', '.join(fail)}")
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main())
