#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
finalize.py — '한글의 탄생과 단모음' (초급 1주차) 통합 복구 + 한/영 4K 렌더 파이프라인.

흐름:
  1) hangeul_birth_vowels/scene_0..12.mp4 누락 감지
  2) 누락분은 autoveo_flow.py 로 (Google Flow) 생성·다운로드 (증분 progress 기록)
  3) make_video.py 를 두 번 호출:
       --lang ko -> hangeul_birth_vowels_ko.mp4 (한국어 나레이션 + 한글 자막바)
       --lang en -> hangeul_birth_vowels_en.mp4 (영어   나레이션 + 영어 자막바)
     · 4K(3840x2160) 업스케일, 채널 로고 배지(워터마크 가림), 10초 정지 아웃트로 카드
     · .ko.srt / .en.srt 사이드카 자막, Scene 0 한국어 썸네일 자동 생성
  4) G:\\내 드라이브\\AutoVideo\\hangeul_birth_vowels 로 백업(연결돼 있을 때)

사용:
  python hangeul_birth_vowels/finalize.py                 # 누락 생성 후 한/영 렌더
  python hangeul_birth_vowels/finalize.py --render-only   # 생성 건너뛰고 렌더만
  python hangeul_birth_vowels/finalize.py --lang ko       # 한 언어만 렌더
"""
import os
import sys
import argparse
import subprocess

TARGET_DIR = os.path.dirname(os.path.abspath(__file__))      # hangeul_birth_vowels/
ROOT_DIR = os.path.dirname(TARGET_DIR)                        # autovideo/

# autoveo_flow.py 는 프롬프트 파일명에서 OUT_DIR 를 유도한다:
#   hangeul_birth_vowels_prompts.txt -> 'hangeul_birth_vowels' -> 클립이 곧장 이 폴더로 떨어짐.
PROMPTS_FILE = os.path.join(ROOT_DIR, "hangeul_birth_vowels_prompts.txt")
SCENARIO_FILE = os.path.join(TARGET_DIR, "scenario.txt")

LOGO = "assets/drjay_ed_logo_circle.png"
OUTRO_CARD = "assets/outro_template.png"
SUB_PROFILE = "assets/profiles/black_box_sub.json"   # 반투명 검정 자막 바 + 흰 글자

TOTAL_SCENES = 13   # Scene 0 ~ 12 (Scene 13 = 정지 아웃트로 카드는 --outro-card 로 처리)

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def is_real_mp4(path):
    try:
        with open(path, "rb") as f:
            return b"ftyp" in f.read(16)
    except Exception:
        return False


def get_missing_scenes():
    missing = []
    for i in range(TOTAL_SCENES):
        p = os.path.join(TARGET_DIR, f"scene_{i}.mp4")
        if not os.path.exists(p) or os.path.getsize(p) == 0 or not is_real_mp4(p):
            missing.append(i)
    return missing


def generate_missing():
    missing = get_missing_scenes()
    if not missing:
        print("[OK] 0~12 씬이 모두 준비되어 있습니다. 생성 단계 건너뜀.")
        return True

    print(f"[!] 누락 씬 {len(missing)}개 감지: {missing}")
    print("    autoveo_flow.py (Google Flow) 로 생성을 시작합니다. (단일 세션, 증분 기록)")
    rel_prompts = os.path.relpath(PROMPTS_FILE, ROOT_DIR)

    # autoveo_flow.py 는 자체적으로 누락분만 처리(progress.json + 파일존재 SKIP)하므로
    # 전체 프롬프트로 한 번만 호출한다 — 한 브라우저 세션에서 순차 복구.
    cmd = ["python", "autoveo_flow.py", "--prompts", rel_prompts]
    try:
        subprocess.run(cmd, check=False, cwd=ROOT_DIR)
    except Exception as e:
        print(f"[에러] autoveo_flow 실행 오류: {e}")

    still = get_missing_scenes()
    if still:
        print(f"[경고] 생성 후에도 누락 씬 잔존: {still}")
        print("       다시 실행하거나 Flow 화면에서 반복 에러 여부를 확인하세요.")
        return False
    print("[OK] 모든 씬 클립 준비 완료.")
    return True


def render(lang):
    """make_video.py 를 해당 언어로 호출해 <project>_<lang>.mp4 (4K)를 빌드한다."""
    out_name = f"hangeul_birth_vowels_{lang}.mp4"
    output = os.path.join(TARGET_DIR, out_name)
    srt_flag = "--srt-ko" if lang == "ko" else "--srt-en"
    srt_path = os.path.join(TARGET_DIR, f"hangeul_birth_vowels.{lang}.srt")

    cmd = [
        "python", os.path.join(ROOT_DIR, "make_video.py"),
        "--scenario", SCENARIO_FILE,
        "--output", output,
        "--lang", lang,
        "--profile", SUB_PROFILE,            # 자막 바(dynamic padding) 스타일
        "--logo-path", LOGO,
        "--outro", "",                       # 일반 outro.mp4 생략 (Scene 12 가 아웃트로)
        "--outro-card", OUTRO_CARD,
        "--outro-card-duration", "10",
        srt_flag, srt_path,                  # .ko.srt / .en.srt 사이드카
    ]
    print(f"\n=== [{lang.upper()}] 렌더링 시작 ===\n{' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=ROOT_DIR)
    print(f"[OK] {out_name} 렌더 완료")
    return output


def backup_to_drive(files):
    gdrive_dir = r"G:\내 드라이브\AutoVideo\hangeul_birth_vowels"
    drive_root = "G:\\"
    if not os.path.exists(drive_root):
        print(f"\n[건너뜀] 구글 드라이브(G:) 가 연결돼 있지 않아 백업을 생략합니다.")
        print(f"          나중에 수동 백업 대상: {gdrive_dir}")
        return
    import shutil
    try:
        os.makedirs(gdrive_dir, exist_ok=True)
        print(f"\n[구글 드라이브 백업] -> {gdrive_dir}")
        for f in files:
            if f and os.path.exists(f):
                shutil.copy2(f, os.path.join(gdrive_dir, os.path.basename(f)))
                print(f"  -> {os.path.basename(f)} ✔")
            else:
                print(f"  -> [없음] {f}")
        print("[OK] 백업 완료.")
    except Exception as e:
        print(f"[경고] 백업 중 오류: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--render-only", action="store_true", help="클립 생성 단계 건너뛰고 렌더만")
    ap.add_argument("--lang", choices=["ko", "en", "both"], default="both")
    args = ap.parse_args()

    print("=" * 64)
    print("  한글의 탄생과 단모음 — 한/영 4K 통합 렌더 파이프라인 (Scene 0~12)")
    print("=" * 64)

    if not args.render_only:
        if not generate_missing():
            print("[중단] 클립이 모두 준비되지 않아 렌더를 중단합니다. (--render-only 로 강제 가능)")
            sys.exit(1)
    else:
        missing = get_missing_scenes()
        if missing:
            print(f"[경고] --render-only 인데 누락 씬 존재: {missing} (해당 씬은 정적 이미지 폴백)")

    langs = ["ko", "en"] if args.lang == "both" else [args.lang]
    outputs = []
    for lang in langs:
        outputs.append(render(lang))

    # 백업 대상: mp4 + 자막 + 썸네일
    backup_files = list(outputs)
    backup_files += [os.path.join(TARGET_DIR, "hangeul_birth_vowels.ko.srt"),
                     os.path.join(TARGET_DIR, "hangeul_birth_vowels.en.srt"),
                     os.path.join(TARGET_DIR, "scene_0_thumbnail_korean.png")]

    # 로컬 웹 public/docs/ 폴더로 복사 (Astro UI 제공용)
    web_docs_dir = os.path.join(ROOT_DIR, "web", "public", "docs")
    if os.path.exists(web_docs_dir):
        print(f"\n[로컬 웹 자산 복사] -> {web_docs_dir}")
        import shutil
        os.makedirs(web_docs_dir, exist_ok=True)
        for f in backup_files:
            if f and os.path.exists(f):
                shutil.copy2(f, os.path.join(web_docs_dir, os.path.basename(f)))
                print(f"  -> web/public/docs/{os.path.basename(f)} ✔")

    backup_to_drive(backup_files)

    print("\n" + "=" * 64)
    print("  🎉 완료")
    for o in outputs:
        print(f"   - {o}")
    print("=" * 64)


if __name__ == "__main__":
    main()
