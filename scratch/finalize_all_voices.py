#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""모든 무료 Neural 목소리(sunhi, injoon, hyunsu) 순차 비디오 생성 및 구글 드라이브 업로드 마스터 래퍼."""
import os
import sys
import shutil
import subprocess
import glob

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.append(ROOT)

KE = os.path.join(ROOT, "korean_education")
OUT_BASE = os.path.join(KE, "korean_education.mp4")
DRIVE = r"G:\내 드라이브\AutoVideo\korean_education"
AUDIO_DIR = os.path.join(ROOT, "assets", "audio")

VOICES = ["sunhi", "injoon", "hyunsu"]


def run(cmd, log_path):
    print(f"Executing: {' '.join(cmd)}")
    with open(log_path, "w", encoding="utf-8") as f:
        return subprocess.run(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT).returncode


def swap_audio_cache(target_voice, current_active_voice):
    """목소리별로 assets/audio 내의 scene_*.mp3 및 .txt 캐시 폴더를 교체하여 충돌 방지 및 100% Cache HIT 지원."""
    # 1. 현재 assets/audio의 파일들을 직전 목소리의 캐시 백업 폴더로 복사
    if current_active_voice:
        backup_dir = os.path.join(ROOT, "assets", f"audio_cache_{current_active_voice}")
        os.makedirs(backup_dir, exist_ok=True)
        print(f"[CACHE] Backing up current audio cache to: {backup_dir}")
        for f in glob.glob(os.path.join(AUDIO_DIR, "scene_*.*")):
            shutil.copy2(f, os.path.join(backup_dir, os.path.basename(f)))

    # 2. assets/audio 폴더 비우기
    print("[CACHE] Clearing assets/audio for the next voice...")
    for f in glob.glob(os.path.join(AUDIO_DIR, "scene_*.*")):
        try:
            os.remove(f)
        except Exception as e:
            print(f"[CACHE] Warning: Failed to remove {f}: {e}")

    # 3. 새 목소리의 캐시 백업 폴더가 존재하면 복원, 없으면 비워둔 상태 유지
    restore_dir = os.path.join(ROOT, "assets", f"audio_cache_{target_voice}")
    if os.path.exists(restore_dir):
        print(f"[CACHE] Restoring audio cache from: {restore_dir}")
        for f in glob.glob(os.path.join(restore_dir, "scene_*.*")):
            shutil.copy2(f, os.path.join(AUDIO_DIR, os.path.basename(f)))
    else:
        print(f"[CACHE] No existing cache found for {target_voice}. Starting fresh.")


def backup_and_rename_outputs(voice):
    """최종 빌드된 korean_education.mp4 및 srt, m4a, thumbnail 파일들을 목소리 명칭이 포함된 이름으로 리네임 보존."""
    print(f"[RENAME] Renaming final files for voice: {voice}...")
    base_name = os.path.splitext(OUT_BASE)[0]  # korean_education
    
    # 리네임 대상 파일 매핑 (원본 -> 새이름)
    targets = {
        OUT_BASE: os.path.join(KE, f"korean_education_{voice}.mp4"),
        base_name + ".ko.srt": os.path.join(KE, f"korean_education_{voice}.ko.srt"),
        base_name + ".en.srt": os.path.join(KE, f"korean_education_{voice}.en.srt"),
        base_name + ".en.m4a": os.path.join(KE, f"korean_education_{voice}.en.m4a"),
        os.path.join(KE, "scene_0_thumbnail_korean.png"): os.path.join(KE, f"scene_0_thumbnail_korean_{voice}.png")
    }
    
    for src, dst in targets.items():
        if os.path.exists(src):
            if os.path.exists(dst):
                try: os.remove(dst)
                except Exception: pass
            os.rename(src, dst)
            print(f"  Renamed: {os.path.basename(src)} -> {os.path.basename(dst)}")
        else:
            print(f"  Missing (cannot rename): {os.path.basename(src)}")


def upload_to_drive(voice):
    """리네임된 목소리별 최종 결과물들을 구글 드라이브에 복사 및 무결성(사이즈) 검증."""
    print(f"[DRIVE] Uploading {voice} version to Google Drive...")
    os.makedirs(DRIVE, exist_ok=True)
    
    voice_files = [
        os.path.join(KE, f"korean_education_{voice}.mp4"),
        os.path.join(KE, f"korean_education_{voice}.ko.srt"),
        os.path.join(KE, f"korean_education_{voice}.en.srt"),
        os.path.join(KE, f"korean_education_{voice}.en.m4a"),
        os.path.join(KE, f"scene_0_thumbnail_korean_{voice}.png")
    ]
    
    for f in voice_files:
        if os.path.exists(f):
            d = os.path.join(DRIVE, os.path.basename(f))
            shutil.copy2(f, d)
            ok = os.path.getsize(f) == os.path.getsize(d)
            print(f"  {'OK' if ok else 'MISMATCH'} {os.path.basename(f)} ({os.path.getsize(d)} bytes)")
        else:
            print(f"  MISSING {os.path.basename(f)}")


def generate_thumbnail_korean(voice):
    """해례본 테마의 한국어 썸네일을 생성."""
    print(f"[3/4] 썸네일 생성 및 적용 (voice={voice})...", flush=True)
    try:
        from PIL import Image
        from make_video import generate_thumbnail
        bg = os.path.join(KE, "_thumb_bg_haerye.png")
        if not os.path.exists(bg):
            canvas = Image.new("RGBA", (1280, 720), (255, 255, 255, 255))
            scroll_img_path = os.path.join(ROOT, "assets/graphics/obj_haerye_scroll.png")
            if os.path.exists(scroll_img_path):
                scroll = Image.open(scroll_img_path).convert("RGBA")
                scale = max(1280.0 / scroll.width, 720.0 / scroll.height)
                w = int(scroll.width * scale)
                h = int(scroll.height * scale)
                scroll = scroll.resize((w, h), Image.Resampling.LANCZOS)
                r, g, b, a = scroll.split()
                a = a.point(lambda p: int(p * 0.5))
                scroll = Image.merge("RGBA", (r, g, b, a))
                offset_x = (1280 - w) // 2
                offset_y = (720 - h) // 2
                canvas.alpha_composite(scroll, (offset_x, offset_y))
            canvas.convert("RGB").save(bg)
            
        generate_thumbnail(bg, "한글 자음 모음 소리내기", "훈민정음",
                           os.path.join(KE, "scene_0_thumbnail_korean.png"))
        print("[3/4] 썸네일 완료", flush=True)
    except Exception as e:
        print(f"[3/4] 썸네일 생성 실패: {e}", flush=True)


def main():
    # 0. 초기 체크: 만약 기존에 돌고 있던 렌더링(sunhi로 예상)의 결과물(korean_education.mp4)이 있다면,
    # 우선 sunhi 결과물로 간주해 보존 리네임하고 드라이브에 복사한다.
    current_active_voice = None
    
    if os.path.exists(OUT_BASE) and os.path.getsize(OUT_BASE) > 100000000:
        print("[INIT] Detected already completed video in the workspace. Treating as 'sunhi' default version.")
        backup_and_rename_outputs("sunhi")
        upload_to_drive("sunhi")
        current_active_voice = "sunhi"
        # sunhi 오디오 캐시 백업
        swap_audio_cache("injoon", "sunhi")
        current_active_voice = "injoon"

    for voice in VOICES:
        # 이미 드라이브와 로컬에 파일이 모두 정상 복사되어 있다면 스킵
        final_mp4_local = os.path.join(KE, f"korean_education_{voice}.mp4")
        final_mp4_drive = os.path.join(DRIVE, f"korean_education_{voice}.mp4")
        if os.path.exists(final_mp4_local) and os.path.exists(final_mp4_drive):
            if os.path.getsize(final_mp4_local) == os.path.getsize(final_mp4_drive) and os.path.getsize(final_mp4_local) > 100000000:
                print(f"[SKIP] Voice version '{voice}' is already generated and uploaded. Skipping.")
                current_active_voice = voice
                continue

        print(f"\n========================================================")
        print(f" Starting compilation for voice: {voice.upper()}")
        print(f"========================================================")
        
        # 1. 오디오 캐시 스왑
        swap_audio_cache(voice, current_active_voice)
        current_active_voice = voice
        
        # 2. 프로세스 환경 변수 주입
        os.environ["EDGE_ACTIVE_VOICE"] = voice
        print(f"[ENV] Set EDGE_ACTIVE_VOICE = {voice}")
        
        # 3. make_video.py 실행 (한국어 렌더링)
        print("[1/4] 전체 재렌더 시작 (make_video.py)...", flush=True)
        rc = run(["python", "make_video.py",
                  "--scenario", "korean_education/scenario.txt", "--output", OUT_BASE,
                  "--profile", "assets/profiles/minimal_ink.json",
                  "--intro", "assets/intro.mp4", "--outro", "assets/outro.mp4",
                  "--outro-card", "assets/outro_template.png",
                  "--no-burn-subs", "--embed-subs"],
                 os.path.join(KE, f"_compile_{voice}.log"))
        
        if rc != 0 or not os.path.exists(OUT_BASE):
            print(f"[ERR] {voice} 버전 렌더 실패 (rc={rc})", flush=True)
            sys.exit(1)
        print("[1/4] 렌더 완료", flush=True)
        
        # 4. 영어 나레이션 추가
        print("[2/4] 영어 나레이션 추가 (add_en_narration.py)...", flush=True)
        shutil.rmtree(os.path.join(KE, "_en_tts"), ignore_errors=True)
        rc = run(["python", "add_en_narration.py", OUT_BASE], os.path.join(KE, f"_en_narr_{voice}.log"))
        print(f"[2/4] 영어 나레이션 추가 완료 (rc={rc})", flush=True)
        
        # 5. 썸네일 생성
        generate_thumbnail_korean(voice)
        
        # 6. 파일 리네임
        backup_and_rename_outputs(voice)
        
        # 7. 구글 드라이브 업로드
        upload_to_drive(voice)
        
        print(f"[SUCCESS] Completed all operations for voice: {voice.upper()}")

    print("\n[DONE] All voices (sunhi, injoon, hyunsu) have been processed successfully!")


if __name__ == "__main__":
    main()
