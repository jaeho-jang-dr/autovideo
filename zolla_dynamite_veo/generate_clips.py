# -*- coding: utf-8 -*-
"""졸라 다이나마이트 S1~S7 Veo 클립 생성 — 흰 배경 캐릭터 댄스 플레이트.
가이드(G1~G4) 업로드 기반 + PREV last-frame 연결. 배경/자모는 컴파일에서 합성.
사용: python zolla_dynamite_veo/generate_clips.py        (전체)
      python zolla_dynamite_veo/generate_clips.py 4 5    (특정 씬)"""
import os, sys, time, json, traceback
import cv2
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT); os.chdir(ROOT)
import autoveo_flow as af
sys.path.append(os.path.join(ROOT, "channel"))
try: import content_db as cdb
except Exception: cdb = None
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

PROJECT = "zolla_dynamite"
PDIR = os.path.join(ROOT, "zolla_dynamite_veo")
GDIR = os.path.join(PDIR, "guides")
BASE = os.path.join(PDIR, "base_zolla_pair_beige.png")  # 기본 시작 이미지(원본 졸라 2인 PIL 합성, 불투명 베이지)
PROGRESS = os.path.join(PDIR, "progress_clips.json")
STYLE = (", hand-drawn black-ink stickman style, the same Zollaman with short black hair and Zollagirl "
         "with an orange bun, thick clean black outlines, plain solid opaque light beige background, "
         "BUT they move with the fluid, realistic, full-body mechanics of real professional human dancers, "
         "as if motion-captured from elite K-pop idol dancers — sharp, stylish, dynamic, powerful and smooth, "
         "real weight shifts, spins, footwork and isolations, NOT stiff and NOT cartoonish bouncing; "
         "each performs their OWN different moves (NOT mirrored, NOT synchronized clapping), moving and "
         "swapping positions across the frame, confident and cool, no text, no letters, no watermark")
# 전부 last image transition 체이닝: S1만 베이지 BASE에서 출발, 나머지는 PREV(직전 클립 마지막 프레임).
# 아이돌 댄서처럼: 남녀 각자 다른 동작·자리 이동·절도/다이나믹. 오리지널 안무.
SCENES = {
    1: ("BASE", "The two stick figures stand together, then break apart into a sharp K-pop idol opening — each striking a different confident dynamic pose, one stepping forward"),
    2: ("PREV", "Zollaman does a smooth body-roll and quick footwork on one side while Zollagirl does a sharp arm-wave and hip move on the other — each a different idol move, full of attitude"),
    3: ("PREV", "The two dancers glide across and SWAP positions, crossing past each other with stylish slick steps, landing in new spots each with a different sharp pose"),
    4: ("PREV", "Each freestyles a different dynamic move with level changes — one drops low into a crouch then pops up, the other spins and points — cool, sharp, powerful"),
    5: ("PREV", "On the beat both hit a sharp striking idol freeze for an instant in two different powerful poses, then explode back into distinct energetic grooves"),
    6: ("PREV", "High-energy idol footwork, both dancing hard with their own distinct moves, swapping sides again with a fast slide and a spin"),
    7: ("PREV", "They slide back together and snap into a final cool group pose facing the viewer, two different confident stylish stances"),
}

def extract_last_frame(video, out_png):
    if not os.path.exists(video): return False
    cap = cv2.VideoCapture(video)
    if not cap.isOpened(): return False
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); idx = n - 1; fr = None
    while idx >= 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx); ok, f = cap.read()
        if ok and f is not None: fr = f; break
        idx -= 1
    cap.release()
    if fr is None: return False
    cv2.imwrite(out_png, fr, [int(cv2.IMWRITE_PNG_COMPRESSION), 1]); return True

def resolve_ref(n, tag):
    if tag == "PREV":
        prev = os.path.join(PDIR, f"scene_{n-1}_last.png")
        if not os.path.exists(prev):
            extract_last_frame(os.path.join(PDIR, f"scene_{n-1}.mp4"), prev)
        return prev if os.path.exists(prev) else BASE
    if tag == "BASE":
        return BASE
    return os.path.join(GDIR, f"{tag}.png")

def main():
    af.OUT_DIR = PDIR
    only = [int(x) for x in sys.argv[1:] if x.isdigit()]
    todo = sorted(only) if only else sorted(SCENES)
    progress = {}
    if os.path.exists(PROGRESS):
        try: progress = json.load(open(PROGRESS, encoding="utf-8"))
        except Exception: pass
    if cdb:
        try: cdb.upsert_project(PROJECT, title_kr="졸라 다이나마이트 (Veo 댄스)",
            description="졸라 댄스 Veo 클립 + 통일 파르테논 + 한글 자모 스웜 오버레이. 세로 9:16",
            local_dir=PDIR, n_scenes=len(SCENES), status="generating",
            notes="흰배경 캐릭터 플레이트(Veo) + 배경/자모 합성. 영상=로컬/유튜브, 정보=DB")
        except Exception as e: print(f"[WARN] DB: {e}")

    with sync_playwright() as p:
        def launch():
            af.force_kill_profile_chrome()
            for lk in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
                q = os.path.join(af.PROFILE, lk)
                if os.path.exists(q):
                    try: os.remove(q)
                    except Exception: pass
            time.sleep(2)
            c = p.chromium.launch_persistent_context(
                af.PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
                accept_downloads=True, downloads_path=af.DL_DIR,
                ignore_default_args=["--enable-automation"],
                args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                      "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
            return c, (c.pages[0] if c.pages else c.new_page())
        ctx, page = launch()
        try:
            for n in todo:
                tag, motion = SCENES[n]
                out = os.path.join(PDIR, f"scene_{n}.mp4")
                if progress.get(str(n)) == "success" and os.path.exists(out) and os.path.getsize(out) > 0:
                    print(f"[SKIP] scene {n}")
                    nl = os.path.join(PDIR, f"scene_{n}_last.png")
                    if not os.path.exists(nl): extract_last_frame(out, nl)
                    continue
                ref = resolve_ref(n, tag)
                full = motion + STYLE
                print(f"\n[{n}/7] ref={tag} ({os.path.basename(ref)})\n  {motion[:70]}...")
                ok = False
                for attempt in range(1, 4):
                    try:
                        if af.make_scene_upload(page, n, ref, full): ok = True; break
                    except Exception as ex:
                        print(f"  예외: {ex}"); traceback.print_exc()
                    print(f"  재시도 {attempt}/3"); time.sleep(5)
                    try: ctx.close()
                    except Exception: pass
                    ctx, page = launch()
                progress[str(n)] = "success" if ok else "fail"
                json.dump(progress, open(PROGRESS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                last = os.path.join(PDIR, f"scene_{n}_last.png")
                if ok:
                    extract_last_frame(out, last); print(f"  ✅ scene {n}")
                else:
                    print(f"  ❌ scene {n}")
                if cdb:
                    try: cdb.log_clip(PROJECT, n, scene_name=f"{PROJECT}_scene_{n}",
                        ref_anchor=tag, base_image=ref, motion_prompt=motion,
                        transition_in=("last_frame" if tag == "PREV" else "cut"),
                        file_path=out if ok else None,
                        last_frame_path=last if ok and os.path.exists(last) else None,
                        status="success" if ok else "fail", distortion_check="pending" if ok else None)
                    except Exception as e: print(f"  [WARN] DB: {e}")
        finally:
            try: ctx.close()
            except Exception: pass
    print("Done.")

if __name__ == "__main__":
    main()
