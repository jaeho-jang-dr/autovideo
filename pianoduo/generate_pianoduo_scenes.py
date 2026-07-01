# -*- coding: utf-8 -*-
"""pianoduo 씬 생성기 — 이미지 업로드 기반 Veo 클립 생성.
졸라 왈츠 패턴 + 씬별 ref 앵커 선택(왜곡 누적 방지) + PREV 마지막-프레임 연장.
사용:  python pianoduo/generate_pianoduo_scenes.py            (전체 1~25)
       python pianoduo/generate_pianoduo_scenes.py 5 6 7     (특정 씬만)
"""
import os, sys, time, json, re, traceback
import cv2
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path: sys.path.append(ROOT)
os.chdir(ROOT)
import autoveo_flow as af
sys.path.append(os.path.join(ROOT, "channel"))
try:
    import content_db as cdb   # 영상 제작 정보 DB 기록
except Exception as _e:
    cdb = None
    print(f"[WARN] content_db import 실패(기록 생략): {_e}")
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

PROJECT = "pianoduo"
PDIR = os.path.join(ROOT, "pianoduo")
SCENARIO = os.path.join(PDIR, "scenario.txt")
PROGRESS = os.path.join(PDIR, "progress_scenes.json")
HV = os.path.join(ROOT, "home_vocab")
# ★ 피드백 반영: 항상 나란히(절대 마주보지 않음). 화려함 과장 문구 제거(인준은 적당한 퍼포먼스).
STYLE = (", clean 2D line-art cartoon animation, thick black outlines, flat minimal colors, "
         "the same Korean boy Injun in a navy t-shirt and Korean girl Jieun in a navy-white sailor school uniform, "
         "always seated side by side on the same bench with Injun on the left and Jieun on the right, "
         "they never swap sides and never turn to face each other, both always facing forward toward the keyboard, "
         "the same large black grand piano, plain light background, smooth jimmy-jib style cinematic camera movement, "
         "no camera or crane visible, no equipment, no text, no watermark, no subtitles")
ANCHOR = {
    "piano_stand": os.path.join(HV, "injun_jieun_piano_stand.png"),
    "piano_back":  os.path.join(HV, "injun_jieun_piano_back.png"),
    "piano_front": os.path.join(HV, "injun_jieun_piano_front.png"),
    "piano_side":  os.path.join(HV, "injun_jieun_piano_side.png"),
}
# 청크 구조(빠른전환 경계 그룹) — scenario.txt 와 동일하게 유지.
CHUNKS = [[1], [2,3,4,5,6], [7,8,9,10,11], [12,13,14,15],
          [16,17,18], [19,20], [21,22,23,24], [25]]

def chunk_of(n):
    for i, grp in enumerate(CHUNKS):
        if n in grp: return i
    return -1

def transition_of(n, ref_tag):
    # 청크 첫 씬(=새 기본이미지/PREV 아님) → 'fast'(빠른 화면전환), 내부 → 'last_frame'(무이음)
    return "last_frame" if ref_tag.lower() == "prev" else "fast"

def extract_last_frame(video_path, out_png):
    if not os.path.exists(video_path): return False
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened(): return False
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); idx = n - 1; frame = None
    while idx >= 0:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx); ok, fr = cap.read()
        if ok and fr is not None: frame = fr; break
        idx -= 1
    cap.release()
    if frame is None: return False
    cv2.imwrite(out_png, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 1])
    print(f"[FRAME] {os.path.basename(video_path)} -> {os.path.basename(out_png)}")
    return True

def parse_scenario():
    scenes = {}
    pat = re.compile(r"\[Scene\s+(\d+)\s*\|\s*ref=([A-Za-z_]+)\s*\]\s*(.*)", re.I)
    for line in open(SCENARIO, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"): continue
        m = pat.match(line)
        if m: scenes[int(m.group(1))] = (m.group(2).strip(), m.group(3).strip())
    return scenes

def resolve_ref(n, ref_tag):
    if ref_tag.lower() == "prev":
        prev = os.path.join(PDIR, f"scene_{n-1}_last.png")
        if not os.path.exists(prev):
            pv = os.path.join(PDIR, f"scene_{n-1}.mp4")
            if not extract_last_frame(pv, prev):
                print(f"[WARN] PREV 없음 → piano_side 앵커로 대체 (scene {n})")
                return ANCHOR["piano_side"]
        return prev
    return ANCHOR.get(ref_tag, ANCHOR["piano_side"])

def clip_seconds(path):
    try:
        cap = cv2.VideoCapture(path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 24
        n = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
        cap.release()
        return round(n / fps, 2) if fps else None
    except Exception:
        return None

def main():
    af.OUT_DIR = PDIR
    os.makedirs(PDIR, exist_ok=True)
    scenes = parse_scenario()
    print(f"Loaded {len(scenes)} scenes")
    if cdb:
        try:
            cdb.upsert_project(PROJECT, title_kr="인준·지은 피아노 연탄 연주",
                description="four-hands 피아노 연탄곡 25씬 / 2분30초 (v2 재작업)",
                local_dir=PDIR, final_path=os.path.join(PDIR, "pianoduo.mp4"),
                bgm_path=os.path.join(PDIR, "pianoduo_bgm.wav"),
                n_scenes=len(scenes), status="generating",
                notes="영상 바이너리는 로컬/유튜브에만, 제작정보는 DB에 링크 저장")
        except Exception as e:
            print(f"[WARN] upsert_project 실패: {e}")
    only = [int(x) for x in sys.argv[1:] if x.isdigit()]
    todo = sorted(only) if only else sorted(scenes)

    progress = {}
    if os.path.exists(PROGRESS):
        try: progress = json.load(open(PROGRESS, encoding="utf-8"))
        except Exception: pass

    with sync_playwright() as p:
        def launch():
            # 매 실행 전 프로필 잠금 정리(이미 실행 중 오류 방지)
            af.force_kill_profile_chrome()
            for lkname in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
                lk = os.path.join(af.PROFILE, lkname)
                if os.path.exists(lk):
                    try: os.remove(lk)
                    except Exception: pass
            time.sleep(2)
            for attempt in range(3):
                try:
                    c = p.chromium.launch_persistent_context(
                        af.PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
                        accept_downloads=True, downloads_path=af.DL_DIR,
                        ignore_default_args=["--enable-automation"],
                        args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                              "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
                    return c, (c.pages[0] if c.pages else c.new_page())
                except Exception as ex:
                    print(f"  [launch retry {attempt+1}/3] {ex}")
                    af.force_kill_profile_chrome(); time.sleep(4)
            raise RuntimeError("Chrome 프로필 실행 반복 실패")
        ctx, page = launch()
        try:
            for n in todo:
                ref_tag, motion = scenes[n]
                out = os.path.join(PDIR, f"scene_{n}.mp4")
                if progress.get(str(n)) == "success" and os.path.exists(out) and os.path.getsize(out) > 0:
                    print(f"[SKIP] scene {n}")
                    nl = os.path.join(PDIR, f"scene_{n}_last.png")
                    if not os.path.exists(nl): extract_last_frame(out, nl)
                    continue
                ref = resolve_ref(n, ref_tag)
                full = motion + STYLE
                print(f"\n[{n}/25] ref={ref_tag} ({os.path.basename(ref)})\n  {motion[:80]}...")
                ok = False
                for attempt in range(1, 4):
                    try:
                        if af.make_scene_upload(page, n, ref, full):
                            ok = True; break
                    except Exception as ex:
                        print(f"  예외: {ex}"); traceback.print_exc()
                    print(f"  재시도 {attempt}/3"); time.sleep(5)
                    try: ctx.close()
                    except Exception: pass
                    ctx, page = launch()
                progress[str(n)] = "success" if ok else "fail"
                json.dump(progress, open(PROGRESS, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                last_png = os.path.join(PDIR, f"scene_{n}_last.png")
                if ok:
                    extract_last_frame(out, last_png)
                    print(f"  ✅ scene {n}")
                else:
                    print(f"  ❌ scene {n} 실패")
                # ★ 모든 클립 제작정보를 DB에 기록(영상 바이너리 제외, 경로/링크만)
                if cdb:
                    try:
                        cdb.log_clip(PROJECT, n,
                            scene_name=f"{PROJECT}_scene_{n}",
                            chunk=chunk_of(n), ref_anchor=ref_tag,
                            base_image=ref, motion_prompt=motion,
                            image_prompt=ref_tag, transition_in=transition_of(n, ref_tag),
                            duration_sec=clip_seconds(out) if ok else None,
                            file_path=out if ok else None,
                            last_frame_path=last_png if ok and os.path.exists(last_png) else None,
                            status="success" if ok else "fail",
                            distortion_check="pending" if ok else None)
                    except Exception as e:
                        print(f"  [WARN] DB 기록 실패(scene {n}): {e}")
        finally:
            try: ctx.close()
            except Exception: pass
    print("Done.")

if __name__ == "__main__":
    main()
