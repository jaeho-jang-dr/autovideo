import os
import sys
import shutil
import subprocess

TARGET_DIR = os.path.dirname(os.path.abspath(__file__))   # korean_education/
ROOT_DIR = os.path.dirname(TARGET_DIR)                     # autovideo/

PROMPTS_FILE = os.path.join(TARGET_DIR, "prompts_for_veo.txt")
SCENARIO_FILE = os.path.join(TARGET_DIR, "scenario.txt")
OUTPUT_VIDEO = os.path.join(TARGET_DIR, "korean_education.mp4")
PROFILE = os.path.join(ROOT_DIR, "assets", "profiles", "minimal_ink.json")

TOTAL_SCENES = 90  # Scene 0 ~ 89

# autoveo_flow.py derives its output folder from the prompts file basename
# ("prompts_for_veo.txt" -> "prompts_for_veo"), so generated clips land there.
# We copy them back into korean_education/ for compilation.
AUTOVEO_OUT_DIR = os.path.join(ROOT_DIR, "prompts_for_veo")

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass


def is_real_mp4(path):
    try:
        with open(path, "rb") as f:
            head = f.read(16)
        return b"ftyp" in head
    except Exception:
        return False


def get_missing_scenes():
    missing = []
    for i in range(0, TOTAL_SCENES):  # 0 .. 89
        path = os.path.join(TARGET_DIR, f"scene_{i}.mp4")
        if not os.path.exists(path) or os.path.getsize(path) == 0 or not is_real_mp4(path):
            missing.append(i)
    return missing


def main():
    print("=" * 60)
    print("  '한글의 특성과 자음 모음의 발음 방법' 통합 복구 및 렌더링 파이프라인 (90씬)")
    print("=" * 60)

    missing = get_missing_scenes()
    if missing:
        print(f"\n[!] 현재 누락된 씬 감지 ({len(missing)}개): {missing}")
        print("    누락된 씬들에 대해 autoveo_flow.py를 순차적으로 구동하여 복구합니다...")

        # autoveo_flow.py 는 루트(ROOT_DIR) 기준 상대경로/프로필로 동작하므로 cwd=ROOT_DIR 로 실행한다.
        rel_prompts = os.path.relpath(PROMPTS_FILE, ROOT_DIR)

        for scene_num in missing:
            print(f"\n>>> 누락된 Scene {scene_num} 생성 및 다운로드 시작...")
            cmd = ["python", "autoveo_flow.py", "--prompts", rel_prompts, "--scene", str(scene_num)]
            try:
                res = subprocess.run(cmd, check=True, cwd=ROOT_DIR)
                if res.returncode == 0:
                    # autoveo_flow.py 가 prompts_for_veo/scene_X.mp4 로 저장하므로 korean_education/ 로 복사한다.
                    src = os.path.join(AUTOVEO_OUT_DIR, f"scene_{scene_num}.mp4")
                    dst = os.path.join(TARGET_DIR, f"scene_{scene_num}.mp4")
                    if os.path.exists(src) and os.path.abspath(src) != os.path.abspath(dst):
                        shutil.copy2(src, dst)
                        print(f"Scene {scene_num} 전용 폴더 복사 완료 ✔")
                    elif os.path.exists(dst):
                        print(f"Scene {scene_num} 이미 전용 폴더에 존재 ✔")
                    else:
                        print(f"[경고] 생성 완료되었으나 원본 파일 {src} 을 찾을 수 없습니다.")
                else:
                    print(f"[오류] Scene {scene_num} 복구 중 비정상 종료 (exit code: {res.returncode})")
            except Exception as e:
                print(f"[에러] Scene {scene_num} 실행 중 오류 발생: {e}")

        missing_after = get_missing_scenes()
        if missing_after:
            print(f"\n[경고] 복구 시도 후에도 여전히 씬이 누락되었습니다: {missing_after}")
            print("한 번 더 실행하시거나, 구글 Flow 상에서 생성 에러가 반복되는지 직접 확인해주세요.")
            sys.exit(1)

    print("\n[✔] 축하합니다! 0~89번 90개 씬이 누락 없이 모두 준비되었습니다.")
    print("    최종 비디오 컴파일 및 렌더링을 시작합니다...")

    # make_video.py 는 assets/* 등 루트 기준 상대경로를 사용하므로 cwd=ROOT_DIR 로 실행한다.
    compile_cmd = [
        "python", os.path.join(ROOT_DIR, "make_video.py"),
        "--scenario", SCENARIO_FILE,
        "--output", OUTPUT_VIDEO,
        "--profile", PROFILE,
        "--intro", "assets/intro.mp4",
        "--outro", "assets/outro.mp4",
        "--outro-card", "assets/outro_template.png",
        # 표준: 영어/한글 자막은 굽지 않고 토글 가능한 CC(소프트 트랙)로 내장한다.
        "--no-burn-subs", "--embed-subs",
    ]

    print(f"컴파일 명령어 실행: {' '.join(compile_cmd)}")
    try:
        subprocess.run(compile_cmd, check=True, cwd=ROOT_DIR)
        print("\n" + "=" * 60)
        print("  🎉 최종 비디오 컴파일이 완료되었습니다!")
        print(f"  출력 경로: {OUTPUT_VIDEO}")
        print("=" * 60)

        # 구글 드라이브 백업 자동화
        gdrive_dir = r"G:\내 드라이브\AutoVideo\korean_education"
        try:
            os.makedirs(gdrive_dir, exist_ok=True)
            files_to_copy = [
                (OUTPUT_VIDEO, "korean_education.mp4"),
                (OUTPUT_VIDEO.replace(".mp4", ".ko.srt"), "korean_education.ko.srt"),
                (OUTPUT_VIDEO.replace(".mp4", ".en.srt"), "korean_education.en.srt"),
                (os.path.join(TARGET_DIR, "scene_0_thumbnail_korean.png"), "scene_0_thumbnail_korean.png")
            ]
            print("\n[구글 드라이브 백업 시작...]")
            for src_file, name in files_to_copy:
                if os.path.exists(src_file):
                    dst_file = os.path.join(gdrive_dir, name)
                    shutil.copy2(src_file, dst_file)
                    print(f"  -> {name} 복사 완료 ✔")
                else:
                    print(f"  -> [건너뜀] {name} 파일이 존재하지 않습니다.")
            print("[✔] 구글 드라이브 백업이 성공적으로 끝났습니다.")
        except Exception as ge:
            print(f"[경고] 구글 드라이브 백업 중 오류 발생 (G드라이브 연결 여부 확인 필요): {ge}")
    except subprocess.CalledProcessError as e:
        print(f"\n[에러] 비디오 컴파일(make_video.py) 도중 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
