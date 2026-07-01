# -*- coding: utf-8 -*-
"""
[파라미터화] DB의 캐릭터 베이스 사진(레퍼런스)으로 '같은 캐릭터의 새 동작 사진'을 생성.
검증된 순서(flow_jump_v2와 동일): 업로드→~25초→타일 더보기(⋮)→"프롬프트에 추가"→스크립트→ENTER
→45초→왼편 '새' 타일 다운로드→md5 중복검증(스테일 방지).

사용:
  python scratch/flow_pose.py --ref-key jieun_base_side --out-key jieun_walking \
      --prompt "walking briskly, mid-stride, full-body left side profile view"

옵션:
  --ref-key   DB(character_assets) key (기본 jieun_base_front). storage_url로 받아 레퍼런스로 업로드.
  --out-key   결과 파일명(home_vocab/<out-key>.png) 및 등록 key.
  --prompt    동작 구절(영문). 공통 캐릭터-일관성 프리픽스/서픽스로 감싼다.
  --transparent  배경 투명화(기본: 불투명 원본).
  --retries   스테일/실패 재시도 횟수(기본 3).
"""
import os
import sys
import glob
import argparse
import hashlib
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    except Exception:
        pass

import autoveo_flow as af  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

PREFIX = ("Using the uploaded reference image, keep the EXACT same Korean schoolgirl "
          "character Jieun — same long brown hair, same face, same navy and white sailor "
          "school uniform with a red neckerchief and a navy pleated skirt — but now draw her ")
SUFFIX = (", ONE single full-body figure (no extra figures, no character sheet), minimalist "
          "2D line art, thick clean black outlines, clean whiteboard marker drawing style, on "
          "a solid flat light beige background (#F5F5F0), no text, no signatures")

TILES_JS = r"""
() => { const o=[]; for (const im of document.querySelectorAll('img')){const s=im.getAttribute('src')||'';
if(!/media\.getMediaUrlRedirect|googleusercontent/.test(s))continue; const r=im.getBoundingClientRect();
if(r.width<200||r.height<120||r.width>1200||r.height>900)continue;
const p=im.closest('div'); if(p&&(p.querySelector('svg')||p.querySelector('[class*="spinner"]')||p.querySelector('[class*="loading"]')))continue;
o.push({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),left:Math.round(r.x),src:s});}
o.sort((a,b)=>a.left-b.left); return o; }
"""
SRCS_JS = r"""
() => { const o=[]; for (const im of document.querySelectorAll('img')){const s=im.getAttribute('src')||'';
if(!/media\.getMediaUrlRedirect|googleusercontent/.test(s))continue; const r=im.getBoundingClientRect();
if(r.width<200||r.height<120||r.width>1200||r.height>900)continue; o.push(s);} return o; }
"""
NEW_LEFT_JS = r"""
(known) => { let best=null,bl=Infinity; for (const im of document.querySelectorAll('img')){const s=im.getAttribute('src')||'';
if(!/media\.getMediaUrlRedirect|googleusercontent/.test(s))continue; const r=im.getBoundingClientRect();
if(r.width<200||r.height<120||r.width>1200||r.height>900)continue;
const p=im.closest('div'); if(p&&(p.querySelector('svg')||p.querySelector('[class*="spinner"]')||p.querySelector('[class*="loading"]')))continue;
if(known.includes(s))continue; if(r.x<bl){bl=r.x; best={x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),left:Math.round(r.x),src:s};}}
return best; }
"""


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(65536), b""):
            h.update(b)
    return h.hexdigest()


def env(p=os.path.join(ROOT, ".env")):
    d = {}
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, v = ln.split("=", 1)
            d[k.strip()] = v.strip().strip('"').strip("'")
    return d


def fetch_ref(ref_key):
    # Check local assets/characters first
    local_path = os.path.join(ROOT, "assets", "characters", f"{ref_key}.png")
    if os.path.exists(local_path):
        af.log(f"[LOCAL] {ref_key} found locally: {local_path}")
        return local_path
    local_path_alt = os.path.join(ROOT, "assets", "characters", f"dr_{ref_key}.png")
    if os.path.exists(local_path_alt):
        af.log(f"[LOCAL] {ref_key} found locally (alt): {local_path_alt}")
        return local_path_alt

    import psycopg2
    e = env()
    cn = psycopg2.connect(host=e["SUPABASE_DB_HOST"], port=e["SUPABASE_DB_PORT"],
                          user=e["SUPABASE_DB_USER"], password=e["SUPABASE_DB_PASSWORD"],
                          dbname=e["SUPABASE_DB_NAME"], sslmode="require", connect_timeout=20)
    cur = cn.cursor()
    cur.execute("SELECT storage_url FROM character_assets WHERE key=%s", (ref_key,))
    row = cur.fetchone()
    cn.close()
    if not row:
        raise SystemExit(f"[FAIL] DB에 ref-key 없음: {ref_key}")
    local = os.path.join(ROOT, "home_vocab", f"_dbref_{ref_key}.png")
    urllib.request.urlretrieve(row[0], local)
    af.log(f"[DB] {ref_key} → {local} ({os.path.getsize(local)} bytes)")
    return local


def shot(page, name):
    try:
        page.screenshot(path=os.path.join(ROOT, "scratch", name))
    except Exception:
        pass


def make_one(page, ref, full_prompt, out, existing, transparent):
    """검증된 순서로 1장 생성. 성공 시 True. 스테일이면 False(재시도용)."""
    if not af.open_new_project(page):
        af.log("  [WARN] 새 프로젝트 실패"); return False
    af.set_image_mode(page)
    if not af.upload_image(page, os.path.abspath(ref)):
        af.log("  [WARN] 업로드 실패"); return False
    page.wait_for_timeout(25000)                      # 타일 ~25초
    tiles = page.evaluate(TILES_JS) or []
    if not tiles:
        af.log("  [WARN] 업로드 타일 미출현"); return False
    # 타일 더보기(⋮) → 프롬프트에 추가
    added = False
    if af.open_tile_menu(page, tiles[0]):
        page.wait_for_timeout(700)
        for label in ("추가하기", "프롬프트에 추가", "장면에 추가", "추가", "Add to prompt", "Add"):
            if af.click_text(page, label):
                added = True; break
    if not added:
        af.log("  [WARN] 더보기→추가 실패"); return False
    page.wait_for_timeout(2500)
    af.fill_prompt(page, full_prompt)
    page.wait_for_timeout(800)
    known = page.evaluate(SRCS_JS) or []
    page.keyboard.press("Enter")
    page.wait_for_timeout(3000)
    if len(page.evaluate(SRCS_JS) or []) == len(known):
        af.generate(page)                             # ENTER 무반응 시 '만들기' 폴백
    page.wait_for_timeout(45000)                      # 생성 ~45초
    new = None
    for _ in range(20):
        new = page.evaluate(NEW_LEFT_JS, known)
        if new:
            break
        page.wait_for_timeout(3000)
    if not new:
        af.log("  [WARN] 왼편 새 타일 미출현"); return False
    page.wait_for_timeout(3000)
    raw = out + ".raw.png"
    try:
        with page.expect_download(timeout=30000) as dl:
            if not af.open_tile_menu(page, new):
                raise RuntimeError("타일 ⋮ 실패")
            af.click_text(page, "다운로드")
            page.wait_for_timeout(900)
            (af.click_text(page, "원본 크기") or af.click_text(page, "720p 원본 크기")
             or af.click_text(page, "원본") or af.click_text(page, "720p"))
        dl.value.save_as(raw)
        try:
            page.keyboard.press("Escape")
        except Exception:
            pass
    except Exception as ex:
        af.log(f"  [WARN] 다운로드 실패: {str(ex)[:100]}"); return False
    from PIL import Image
    if transparent:
        from gen_assets_flow import make_bg_transparent
        if not make_bg_transparent(raw, out):
            Image.open(raw).convert("RGBA").save(out)
    else:
        Image.open(raw).convert("RGBA").save(out)
    try:
        os.remove(raw)
    except Exception:
        pass
    m = md5(out)
    if m in existing:
        af.log(f"  [STALE] 기존 '{existing[m]}'와 동일(md5={m}) — 잘못된 타일. 재시도.")
        try:
            os.remove(out)
        except Exception:
            pass
        return False
    af.log(f"  [OK] {os.path.basename(out)} ({os.path.getsize(out)} bytes, md5={m}, 중복아님)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-key", default="jieun_base_front")
    ap.add_argument("--out-key", required=True)
    ap.add_argument("--prompt", required=True, help="동작 구절(영문)")
    ap.add_argument("--transparent", action="store_true")
    ap.add_argument("--casual", action="store_true", help="Use casual clothes prefix for Jieun")
    ap.add_argument("--retries", type=int, default=3)
    args = ap.parse_args()

    out = os.path.join(ROOT, "home_vocab", f"{args.out_key}.png")
    status = os.path.join(ROOT, "scratch", f"pose_{args.out_key}_status.txt")
    try:
        os.remove(status)
    except Exception:
        pass

    ref = fetch_ref(args.ref_key)
    # Character-specific prefix & suffix selection
    if "injun_jieun" in args.ref_key:
        prefix_char = ("Using the uploaded reference image, keep the EXACT same two Korean characters "
                       "standing side-by-side — Injun (a Korean boy with short neat black hair, wearing "
                       "a simple casual short-sleeve navy t-shirt and pants) and Jieun (a Korean schoolgirl "
                       "with long brown hair, wearing a navy and white sailor school uniform with a red neckerchief "
                       "and a navy pleated skirt) — but now draw them ")
        suffix_char = SUFFIX
    elif "injun" in args.ref_key:
        shirt_color = "navy t-shirt" if "navy" in args.ref_key else "t-shirt"
        prefix_char = (f"Using the uploaded reference image, keep the EXACT same Korean boy "
                       f"character Injun — same short neat black hair, same face, same casual "
                       f"short-sleeve {shirt_color} and pants — but now draw him ")
        suffix_char = SUFFIX
    elif "zollaman" in args.ref_key:
        prefix_char = ("Using the uploaded reference image, keep the EXACT same black short-hair "
                       "male stickman character named jjolla-man — same minimalist wobbly pen outline "
                       "body, same black short hair — but now draw him ")
        suffix_char = (", ONE single full-body figure (no extra figures, no character sheet), "
                       "loose sketchy hand-drawn black pen line doodle style, minimalist whiteboard-doodle "
                       "sketch style, on a solid flat pure white background, no text, no signatures")
    elif "zollanyeo" in args.ref_key:
        prefix_char = ("Using the uploaded reference image, keep the EXACT same orange short-hair "
                       "female stickman character named jjolla-nyeo — same minimalist wobbly pen outline "
                       "body, same orange short hair — but now draw her ")
        suffix_char = (", ONE single full-body figure (no extra figures, no character sheet), "
                       "loose sketchy hand-drawn black pen line doodle style, minimalist whiteboard-doodle "
                       "sketch style, on a solid flat pure white background, no text, no signatures")
    elif "zolla_pair" in args.ref_key or "zolla_handshake" in args.ref_key:
        prefix_char = ("Using the uploaded reference image, keep the EXACT same two stickman characters — "
                       "jjolla-man (black short-hair male stickman) and jjolla-nyeo (orange short-hair female stickman) — "
                       "but now draw them ")
        suffix_char = (", loose sketchy hand-drawn black pen line doodle style, minimalist whiteboard-doodle "
                       "sketch style, on a solid flat pure white background, no text, no signatures")
    elif args.casual:
        prefix_char = ("Using the uploaded reference image, keep the EXACT same Korean girl "
                       "character Jieun — same long brown hair, same face, same body build — "
                       "but now wearing casual everyday clothes (a simple casual t-shirt, casual pants, "
                       "and sneakers, NOT a school uniform), draw her in a ")
        suffix_char = SUFFIX
    elif "jay" in args.ref_key:
        prefix_char = ("Using the uploaded reference image, keep the EXACT same minimalist 2D single-line stickman character named Jay — "
                       "same thin solid black lines body, same simple empty circle head, same two black dot eyes, "
                       "same smiling mouth, same exactly two strands of thin black hair on top of his head, "
                       "same simple empty oval outlines for his hands and feet — but now draw him ")
        suffix_char = (", ONE single full-body figure (no extra figures, no character sheet), "
                       "minimalist 2D line art, thin clean black outlines, whiteboard marker drawing style, "
                       "on a solid flat light beige background (#F5F5F0), no text, no signatures")
    else:
        prefix_char = PREFIX
        suffix_char = SUFFIX

    full_prompt = prefix_char + args.prompt.strip() + suffix_char
    af.log(f"[PROMPT] {full_prompt[:90]}...")

    existing = {}
    for f in glob.glob(os.path.join(ROOT, "home_vocab", "*.png")):
        if os.path.basename(f) != f"{args.out_key}.png":
            try:
                existing[md5(f)] = os.path.basename(f)
            except Exception:
                pass

    af.force_kill_profile_chrome()
    lk = os.path.join(af.PROFILE, "SingletonLock")
    if os.path.exists(lk):
        try:
            os.remove(lk)
        except Exception:
            pass

    ok = False
    with sync_playwright() as pw:
        ctx = pw.chromium.launch_persistent_context(
            af.PROFILE, channel="chrome", headless=False, locale="ko-KR",
            no_viewport=True, accept_downloads=True, downloads_path=af.DL_DIR,
            ignore_default_args=["--enable-automation"],
            args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                  "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for attempt in range(1, args.retries + 1):
            af.log(f"=== {args.out_key} 시도 {attempt}/{args.retries} (ref={args.ref_key}) ===")
            try:
                if make_one(page, ref, full_prompt, out, existing, args.transparent):
                    ok = True
                    break
            except Exception as ex:
                af.log(f"  [ERR] {str(ex)[:120]}")
            page.wait_for_timeout(6000)
        try:
            ctx.close()
        except Exception:
            pass

    msg = (f"[OK] {args.out_key} → home_vocab/{args.out_key}.png ({os.path.getsize(out)} bytes)"
           if ok else f"[FAIL] {args.out_key} 생성 실패")
    open(status, "w", encoding="utf-8").write(msg + "\n")
    af.log(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
