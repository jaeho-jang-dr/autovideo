"""
pipeline.py — Unified Video Production Pipeline

Combines:
  1. Google Flow browser automation (image gen -> animation -> download)
  2. Narration TTS generation (gTTS) with forced cache refresh & 1.1x speed
  3. Video compilation (MoviePy 2.2.1) with absolute font Korean subtitles & transitions

Usage:
  python pipeline.py --scenario scenario.txt --output joint_pop_sound.mp4
  python pipeline.py --scenario scenario.txt --scene 1 --force
  python pipeline.py --scenario scenario.txt --skip-gen
"""

import os
import re
import sys
import time
import shutil
import argparse
import traceback
from playwright.sync_api import sync_playwright
from gtts import gTTS
from moviepy import AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, VideoFileClip
import moviepy.video.fx as fx

# Force UTF-8 encoding for standard streams
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

FLOW_BASE = "https://labs.google/fx/tools/flow"
PROFILE = os.path.abspath("assets/chrome_profile")
DBG = "debug"
DL_DIR = os.path.abspath(os.path.join(DBG, "downloads"))
OUT_DIR = os.path.abspath("assets/videos")
PROMPT_SELECTOR = "div[role='textbox'][contenteditable='true']"

# JS Selectors
BIG_MEDIA_IMG_JS = r"""
() => {
  let best=null, area=0;
  for (const im of document.querySelectorAll('img')) {
    const s = im.getAttribute('src')||'';
    if (!/media\.getMediaUrlRedirect|googleusercontent\.com\/(?:fife|gen)/.test(s)) continue;
    const r = im.getBoundingClientRect();
    if (r.width<250 || r.height<150 || r.y>540) continue;
    const a=r.width*r.height;
    if (a>area){area=a; best={x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2)};}
  }
  return best;
}
"""

POSTERS_JS = r"""
() => {
  const out=[];
  for (const im of document.querySelectorAll('img')) {
    const s = im.getAttribute('src')||'';
    if (!/media\.getMediaUrlRedirect|googleusercontent\.com\/(?:fife|gen)/.test(s)) continue;
    const r = im.getBoundingClientRect();
    if (r.width<250 || r.height<150 || r.y>540) continue;
    out.push({x:Math.round(r.x+r.width/2), y:Math.round(r.y+r.height/2), left:Math.round(r.x)});
  }
  out.sort((a,b)=>a.left-b.left);
  return out;
}
"""

HAS_CHIP_JS = r"""
() => {
  for (const b of document.querySelectorAll('button')) {
    const t=b.textContent||''; const r=b.getBoundingClientRect();
    if (r.y>540 && (t.includes('Nano Banana')||t.includes('crop_16_9')||
        t.includes('동영상 ·')||t.includes('이미지 ·'))) return true;
  }
  return false;
}
"""

MORE_NEAR_JS = r"""
(t) => {
  let best=null, bd=1e9;
  for (const b of document.querySelectorAll('button')) {
    const tx=b.textContent||'';
    if (!(tx.includes('더 생성하기') || tx.includes('more_vert'))) continue;
    const r=b.getBoundingClientRect();
    if (r.y<60 || r.width<=0) continue;
    const cx=r.x+r.width/2, cy=r.y+r.height/2, d=Math.hypot(cx-t.x, cy-t.y);
    if (d<bd){bd=d; best={x:Math.round(cx), y:Math.round(cy)};}
  }
  return best;
}
"""


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def shot(page, name):
    try:
        page.screenshot(path=os.path.abspath(os.path.join(DBG, f"{name}.png")))
    except Exception:
        pass


def is_mp4(path):
    try:
        with open(path, "rb") as f:
            head = f.read(16)
        return b"ftyp" in head
    except Exception:
        return False


def parse_scenario(path):
    """Parses a scenario file containing Scene blocks:
    [Scene N]
    text: ...
    image: ...
    motion: ...
    """
    scenes = {}
    if not os.path.exists(path):
        log(f"[ERR] 시나리오 파일 없음: {path}")
        return scenes

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by [Scene <num>]
    blocks = re.split(r"\[Scene\s+(\d+)\]", content, flags=re.IGNORECASE)
    # blocks[0] is header/empty
    # blocks[1] is number, blocks[2] is content block
    for i in range(1, len(blocks), 2):
        n = int(blocks[i])
        body = blocks[i+1]
        lines = [line.strip() for line in body.split("\n") if line.strip()]
        data = {}
        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                data[key.strip().lower()] = val.strip()
        
        scenes[n] = {
            "text": data.get("text", ""),
            "image": data.get("image", ""),
            "motion": data.get("motion", "")
        }
    return scenes


def wrap_text(text, max_chars=30):
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        if len(' '.join(current_line + [word])) <= max_chars:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return '\n'.join(lines)


def dismiss(page):
    for sel in ["button:has-text('Agree')", "button:has-text('동의')",
                "button:has-text('No thanks')", "button:has-text('확인')",
                "button:has-text('시작하기')", "button:has-text('시작')"]:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=400):
                loc.click(timeout=2000, force=True)
                page.wait_for_timeout(500)
        except Exception:
            pass


def click_text(page, t, ymin=None, timeout=4000):
    for sel in (f"button:has-text('{t}')", f"[role='button']:has-text('{t}')",
                f"[aria-label*='{t}']", f"text={t}"):
        try:
            locs = page.locator(sel)
            for i in range(locs.count()):
                loc = locs.nth(i)
                if loc.is_visible():
                    box = loc.bounding_box()
                    if ymin is not None and (not box or box["y"] < ymin):
                        continue
                    loc.click(timeout=timeout)
                    return True
        except Exception:
            pass
    return False


def open_new_project(page):
    page.goto(FLOW_BASE, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(3500)
    if "accounts.google.com" in page.url:
        log("로그인 필요 — labs.google 복귀 대기(90s)")
        try:
            page.wait_for_url("**/labs.google/**", timeout=90000)
        except Exception:
            pass
    dismiss(page)
    if "/project/" not in page.url:
        click_text(page, "새 프로젝트") or click_text(page, "New project")
        page.wait_for_timeout(4000)
        dismiss(page)
    for _ in range(40):
        try:
            if page.locator(PROMPT_SELECTOR).first.is_visible(timeout=500):
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def set_image_mode(page, aspect="16:9", count="1x"):
    if not page.evaluate(HAS_CHIP_JS):
        click_text(page, "에이전트", ymin=540)
        page.wait_for_timeout(900)
    for t in ("Nano Banana", "crop_16_9", "동영상", "이미지"):
        if click_text(page, t, ymin=540):
            break
    page.wait_for_timeout(1200)
    click_text(page, "이미지")
    page.wait_for_timeout(250)
    click_text(page, aspect)
    page.wait_for_timeout(250)
    click_text(page, count)
    page.wait_for_timeout(250)
    page.keyboard.press("Escape")
    page.wait_for_timeout(500)


def fill_prompt(page, text):
    b = page.locator(PROMPT_SELECTOR).first
    b.click()
    page.wait_for_timeout(150)
    try:
        b.press("Control+A")
        b.press("Delete")
    except Exception:
        pass
    page.keyboard.type(text, delay=4)
    page.wait_for_timeout(300)


def generate(page):
    return click_text(page, "arrow_forward", ymin=540)


def wait_image(page, timeout=120):
    page.wait_for_timeout(25000)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if page.evaluate(BIG_MEDIA_IMG_JS):
            page.wait_for_timeout(1500)
            return True
        time.sleep(3)
    return False


def open_tile_menu(page, center):
    page.mouse.move(center["x"], center["y"])
    page.wait_for_timeout(1000)
    more = page.evaluate(MORE_NEAR_JS, center)
    if not more:
        page.mouse.move(center["x"], center["y"] - 20)
        page.wait_for_timeout(800)
        more = page.evaluate(MORE_NEAR_JS, center)
    if not more:
        return False
    page.mouse.click(more["x"], more["y"])
    page.wait_for_timeout(900)
    return True


def animate_image(page):
    center = page.evaluate(BIG_MEDIA_IMG_JS)
    if not center or not open_tile_menu(page, center):
        return False
    return click_text(page, "애니메이션 적용")


def try_download_leftmost(page, tmp_path):
    posters = page.evaluate(POSTERS_JS)
    if not posters:
        return False
    target = posters[0]
    try:
        with page.expect_download(timeout=60000) as dl:
            if not open_tile_menu(page, target):
                raise RuntimeError("tile ⋮ open fail")
            click_text(page, "다운로드")
            page.wait_for_timeout(800)
            (click_text(page, "원본 크기") or click_text(page, "720p")
             or click_text(page, "원본"))
        d = dl.value
        d.save_as(tmp_path)
    except Exception as e:
        log(f"  download try 실패: {str(e)[:90]}")
        return False
    if is_mp4(tmp_path):
        return True
    try:
        os.remove(tmp_path)
    except Exception:
        pass
    return False


def make_video(page, out_path, motion_prompt, n, budget_s=360):
    fill_prompt(page, motion_prompt)
    if not generate(page):
        log("[ERR] 동영상 생성 버튼 클릭 실패")
        return False
    log("동영상 생성 중... (이미지보다 오래 걸림)")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tmp = os.path.join(DL_DIR, f"_scene_{n}.bin")
    page.wait_for_timeout(110000)
    deadline = time.time() + budget_s
    while time.time() < deadline:
        shot(page, f"s{n}_vid_poll")
        if try_download_leftmost(page, tmp):
            shutil.move(tmp, out_path)
            return True
        log(f"  ... 아직 렌더링 중, 20s 후 재시도 ({int(deadline-time.time())}s 남음)")
        time.sleep(20)
    return False


def make_scene(page, n, image_prompt, motion_prompt, force=False):
    out_path = os.path.join(OUT_DIR, f"scene_{n}.mp4")
    if (not force) and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        log(f"[SKIP] 존재함: {out_path}")
        return True
    log(f"=== Scene {n} ===")
    if not open_new_project(page):
        log("[ERR] 프로젝트/컴포저 진입 실패")
        return False
    shot(page, f"s{n}_00_editor")

    set_image_mode(page)
    fill_prompt(page, image_prompt)
    if not generate(page):
        log("[ERR] 이미지 생성 버튼 클릭 실패")
        return False
    log("이미지 생성 중... (~35-40s)")
    if not wait_image(page):
        log("[ERR] 이미지 미생성(timeout)")
        shot(page, f"s{n}_img_timeout")
        return False
    shot(page, f"s{n}_01_image")

    if not animate_image(page):
        log("[ERR] '애니메이션 적용' 실패")
        shot(page, f"s{n}_animate_fail")
        return False
    page.wait_for_timeout(1200)
    shot(page, f"s{n}_02_animate")

    if make_video(page, out_path, motion_prompt, n):
        log(f"[OK] Scene {n} → {out_path}")
        shot(page, f"s{n}_03_done")
        return True
    log(f"[FAIL] Scene {n} 영상 생성/다운로드 실패")
    return False


def compile_final_video(scenes, output_path):
    """TTS generation with speed Multiplier, font overlay, and CrossFade compilation."""
    os.makedirs("assets/audio", exist_ok=True)
    clips = []
    
    # Pre-flight check
    missing = [n for n in scenes if not os.path.exists(f"assets/videos/scene_{n}.mp4")]
    if missing:
        log(f"[ERR] 다음 씬 비디오 클립 누락: {missing}")
        sys.exit(1)

    log("컴파일 프로세스 시작...")
    for n in sorted(scenes):
        scene = scenes[n]
        audio_path = f"assets/audio/scene_{n}.mp3"
        video_path = f"assets/videos/scene_{n}.mp4"

        # Generate fresh TTS (forced overwrite)
        log(f"Scene {n}: TTS 생성 중...")
        if os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except Exception:
                pass
        tts = gTTS(text=scene['text'], lang='ko')
        tts.save(audio_path)

        # Apply speed multiplier 1.1
        audio_clip = AudioFileClip(audio_path)
        audio_clip = audio_clip.with_effects([fx.MultiplySpeed(1.1)])
        duration = audio_clip.duration

        # Load video and scale speed
        base_clip = VideoFileClip(video_path)
        speed_factor = base_clip.duration / duration
        base_clip = base_clip.with_effects([fx.MultiplySpeed(speed_factor)]).with_audio(audio_clip)
        w, h = base_clip.size

        # Subtitle TextClip (Malgun Gothic)
        wrapped_text = wrap_text(scene['text'], max_chars=35)
        try:
            txt_clip = TextClip(
                text=wrapped_text,
                font=r'C:\Windows\Fonts\malgun.ttf',
                font_size=24,
                color='white',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(w - 100, 200)
            )
        except Exception:
            txt_clip = TextClip(
                text=wrapped_text,
                font_size=24,
                color='white',
                stroke_color='black',
                stroke_width=2,
                method='caption',
                size=(w - 100, 200)
            )

        txt_clip = txt_clip.with_position(('center', h - 230)).with_duration(duration)
        scene_clip = CompositeVideoClip([base_clip, txt_clip])
        scene_clip = scene_clip.with_effects([fx.CrossFadeIn(0.5)])
        
        clips.append(scene_clip)
        log(f"Scene {n} 준비 완료 (길이: {duration:.2f}초)")

    log("모든 씬을 병합하는 중...")
    final_video = concatenate_videoclips(clips, method="compose")
    final_video.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )
    log(f"[SUCCESS] 최종 렌더링 완료 -> {output_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="scenario.txt")
    ap.add_argument("--output", default="joint_pop_sound.mp4")
    ap.add_argument("--scene", type=int)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--skip-gen", action="store_true")
    args = ap.parse_args()

    os.makedirs(DBG, exist_ok=True)
    os.makedirs(DL_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    scenes = parse_scenario(args.scenario)
    if not scenes:
        log("시나리오를 찾을 수 없습니다.")
        return

    if not args.skip_gen:
        todo = [args.scene] if args.scene else sorted(scenes)
        ok, fail = [], []
        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(
                PROFILE, channel="chrome", headless=False, locale="ko-KR", no_viewport=True,
                accept_downloads=True, downloads_path=DL_DIR,
                ignore_default_args=["--enable-automation"],
                args=["--start-maximized", "--disable-blink-features=AutomationControlled",
                      "--no-first-run", "--disable-session-crashed-bubble", "--lang=ko-KR"])
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            for n in todo:
                if n not in scenes:
                    continue
                try:
                    s_data = scenes[n]
                    if make_scene(page, n, s_data["image"], s_data["motion"], force=args.force):
                        ok.append(n)
                    else:
                        fail.append(n)
                except Exception as e:
                    log(f"[ERR] Scene {n}: {e}")
                    traceback.print_exc()
                    shot(page, f"s{n}_error")
                    fail.append(n)
            ctx.close()
        log(f"Flow 자동화 완료 — 성공: {ok} / 실패: {fail}")
        if fail:
            log("일부 씬 생성 실패로 최종 병합을 건너뜁니다.")
            sys.exit(1)

    # Compile the video
    if args.scene is None:
        compile_final_video(scenes, args.output)


if __name__ == "__main__":
    main()
