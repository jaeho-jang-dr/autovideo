# -*- coding: utf-8 -*-
"""졸라 다이나마이트 가이드 이미지 G1~G4를 Google Flow(이미지 9:16)에서 생성.
flow_jump_v2 검증 방식: 졸라페어 업로드 → 타일 ⋮ → '추가하기' → 프롬프트 → 생성 → 왼편 새 타일 다운.
배경=옅은 파르테논(50% 워터마크처럼). 캐릭터=업로드 레퍼런스로 일관성 유지. 안무는 오리지널."""
import os, sys, glob, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
import autoveo_flow as af
from playwright.sync_api import sync_playwright
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception: pass

REF = os.path.join(ROOT, "home_vocab", "zolla_pair_base.png")
GDIR = os.path.join(ROOT, "zolla_dynamite_veo", "guides")
SD = os.path.join(ROOT, "scratch")
os.makedirs(GDIR, exist_ok=True)

# 캐릭터는 흰 배경에서 생성(통일 파르테논 배경을 뒤에 합성하기 위함 — multiply 블렌드로 흰색 투과)
PRE = ("Using the uploaded reference image of the two hand-drawn black-ink stick-figure characters "
       "— a boy 'Zollaman' with short messy black hair and a girl 'Zollagirl' with an orange hair bun — "
       "keep their EXACT same simple hand-drawn black-ink stickman style. Draw BOTH of them LARGE, "
       "filling most of the tall vertical frame, on a plain solid PURE WHITE background (#FFFFFF) with "
       "absolutely NO temple, NO scenery and NO background objects at all. Minimalist 2D line art, thick "
       "clean black outlines, vertical 9:16 composition, no text, no letters, no watermark, no signature. ")
# 통일 배경(파르테논) — 텍스트만, 업로드 없음
PBG_PROMPT = ("A classical ancient Greek Parthenon temple with tall marble columns and a triangular pediment, "
              "centered and filling a tall vertical 9:16 frame, soft pale low-contrast pastel illustration, "
              "bright soft daylight, clean simple flat art style, calm, no people, no text, no watermark.")
GUIDES = [
    ("PBG", PBG_PROMPT),  # 업로드 없이 텍스트→이미지 (배경 한 장)
    ("G1", PRE + "The two characters stand close together in the center HOLDING HANDS and smiling warmly at the viewer."),
    ("G2", PRE + "The two characters stand side by side in an energetic ready-to-dance stance, knees slightly bent, arms loose, smiling, about to start dancing."),
    ("G3", PRE + "The two characters hit a sharp synchronized celebratory jump in perfect unison, BOTH arms thrown straight up high, both feet off the ground, big excited smiles, a dynamic energetic original dance pose."),
    ("G4", PRE + "The two characters dance happily side by side, each with one arm raised high and a big smile, mid-groove."),
]

TILES_JS = r"""
() => { const o=[]; for (const im of document.querySelectorAll('img')){const s=im.getAttribute('src')||'';
if(!/media\.getMediaUrlRedirect|googleusercontent/.test(s))continue; const r=im.getBoundingClientRect();
if(r.width<160||r.height<160)continue;
const p=im.closest('div'); if(p&&(p.querySelector('svg')||p.querySelector('[class*="spinner"]')||p.querySelector('[class*="loading"]')))continue;
o.push({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),left:Math.round(r.x),src:s});}
o.sort((a,b)=>a.left-b.left); return o; }
"""
SRCS_JS = r"""
() => { const o=[]; for (const im of document.querySelectorAll('img')){const s=im.getAttribute('src')||'';
if(/media\.getMediaUrlRedirect|googleusercontent/.test(s))o.push(s);} return o; }
"""
NEW_LEFT_JS = r"""
(known) => { let best=null,bl=Infinity; for (const im of document.querySelectorAll('img')){const s=im.getAttribute('src')||'';
if(!/media\.getMediaUrlRedirect|googleusercontent/.test(s))continue; const r=im.getBoundingClientRect();
if(r.width<160||r.height<160)continue;
const p=im.closest('div'); if(p&&(p.querySelector('svg')||p.querySelector('[class*="spinner"]')||p.querySelector('[class*="loading"]')))continue;
if(known.includes(s))continue; if(r.x<bl){bl=r.x; best={x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),left:Math.round(r.x),src:s};}}
return best; }
"""

def md5(p):
    h = hashlib.md5(); h.update(open(p, "rb").read()); return h.hexdigest()

def shot(page, n):
    try: page.screenshot(path=os.path.join(SD, n))
    except Exception: pass

def make_one(page, gid, prompt, seen_md5, upload=True):
    out = os.path.join(GDIR, f"{gid}.png")
    af.log(f"\n===== {gid} 생성 시작 =====")
    if not af.open_new_project(page):
        af.log(f"[{gid}] 새 프로젝트 실패"); return False
    af.set_image_mode(page, aspect="9:16")
    if upload:
        if not af.upload_image(page, os.path.abspath(REF)):
            af.log(f"[{gid}] 업로드 실패"); shot(page, f"_{gid}_upload_fail.png"); return False
        page.wait_for_timeout(25000)
        tiles = page.evaluate(TILES_JS) or []
        if not tiles:
            af.log(f"[{gid}] 업로드 타일 미출현"); shot(page, f"_{gid}_no_tile.png"); return False
        # 타일 ⋮ → 추가하기
        added = False
        if af.open_tile_menu(page, tiles[0]):
            page.wait_for_timeout(700)
            for lab in ("추가하기", "프롬프트에 추가", "장면에 추가", "추가", "Add to prompt", "Add"):
                if af.click_text(page, lab): added = True; break
        if not added:
            af.log(f"[{gid}] 타일→추가 실패"); shot(page, f"_{gid}_add_fail.png"); return False
        page.wait_for_timeout(2000)
    af.fill_prompt(page, prompt)
    page.wait_for_timeout(800)
    known = page.evaluate(SRCS_JS) or []
    page.keyboard.press("Enter"); page.wait_for_timeout(3000)
    if len(page.evaluate(SRCS_JS) or []) == len(known):
        af.generate(page)
    page.wait_for_timeout(40000)
    new = None
    for _ in range(20):
        new = page.evaluate(NEW_LEFT_JS, known)
        if new: break
        page.wait_for_timeout(3000)
    if not new:
        af.log(f"[{gid}] 새 타일 미출현"); shot(page, f"_{gid}_no_new.png"); return False
    page.wait_for_timeout(2500); shot(page, f"_{gid}_gen.png")
    raw = out + ".raw.png"
    try:
        with page.expect_download(timeout=30000) as dl:
            if not af.open_tile_menu(page, new): raise RuntimeError("⋮ 실패")
            af.click_text(page, "다운로드"); page.wait_for_timeout(900)
            (af.click_text(page, "원본 크기") or af.click_text(page, "720p 원본 크기")
             or af.click_text(page, "원본") or af.click_text(page, "720p"))
        dl.value.save_as(raw)
        try: page.keyboard.press("Escape")
        except Exception: pass
    except Exception as ex:
        af.log(f"[{gid}] 다운로드 실패: {str(ex)[:100]}"); shot(page, f"_{gid}_dl_fail.png"); return False
    from PIL import Image
    Image.open(raw).convert("RGB").save(out)
    try: os.remove(raw)
    except Exception: pass
    m = md5(out)
    if m in seen_md5:
        af.log(f"[{gid}] STALE(직전과 동일 md5) — 재시도 필요"); os.remove(out); return False
    seen_md5.add(m)
    af.log(f"[{gid}] ✅ 저장 {out} ({os.path.getsize(out)} bytes)")
    return True

def launch(pw):
    """가이드마다 깨끗한 브라우저 새로 (컨텍스트 크래시 연쇄 방지)."""
    import time
    af.force_kill_profile_chrome()
    for lk in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        p = os.path.join(af.PROFILE, lk)
        if os.path.exists(p):
            try: os.remove(p)
            except Exception: pass
    time.sleep(2)
    ctx = pw.chromium.launch_persistent_context(
        af.PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
        accept_downloads=True, downloads_path=af.DL_DIR,
        ignore_default_args=["--enable-automation"],
        args=["--start-maximized", "--disable-blink-features=AutomationControlled",
              "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
    return ctx, (ctx.pages[0] if ctx.pages else ctx.new_page())

def main():
    seen = set()
    for f in glob.glob(os.path.join(ROOT, "home_vocab", "*.png"))[:300]:
        try: seen.add(md5(f))
        except Exception: pass
    only = [a for a in sys.argv[1:] if a.startswith("G")]
    results = {}
    with sync_playwright() as pw:
        for gid, prompt in GUIDES:
            out = os.path.join(GDIR, f"{gid}.png")
            if only and gid not in only:
                continue
            if os.path.exists(out) and os.path.getsize(out) > 0:
                af.log(f"[{gid}] 이미 있음 — 건너뜀"); results[gid] = "SKIP"; continue
            ok = False
            for attempt in range(1, 3):
                try:
                    ctx, page = launch(pw)
                except Exception as ex:
                    af.log(f"[{gid}] launch 실패: {str(ex)[:100]}"); continue
                try:
                    if make_one(page, gid, prompt, seen, upload=(gid != "PBG")): ok = True
                except Exception as ex:
                    af.log(f"[{gid}] 예외(시도 {attempt}): {str(ex)[:120]}")
                try: ctx.close()
                except Exception: pass
                if ok: break
                af.log(f"[{gid}] 재시도 {attempt}/2")
            results[gid] = "OK" if ok else "FAIL"
        af.log(f"\n결과: {results}")

if __name__ == "__main__":
    main()
