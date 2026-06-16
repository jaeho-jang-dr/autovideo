import os
import sys
import subprocess

TARGET_DIR = r"D:\Entertainments\DevEnvironment\autovideo\child_growth_science"
PROMPTS_FILE = r"child_growth_science\child_growth_prompts.txt"
SCENARIO_FILE = r"child_growth_science\scenario.txt"
OUTPUT_VIDEO = r"D:\Entertainments\DevEnvironment\autovideo\child_growth_science\child_growth.mp4"
TOTAL_SCENES = 90

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
    for i in range(0, TOTAL_SCENES + 1):
        path = os.path.join(TARGET_DIR, f"scene_{i}.mp4")
        if not os.path.exists(path) or os.path.getsize(path) == 0 or not is_real_mp4(path):
            missing.append(i)
    return missing

def main():
    print("=" * 60)
    print("  '우리 아이 키 얼마나 자랄까요?' 통합 복구 및 렌더링 파이프라인")
    print("=" * 60)
    
    missing = get_missing_scenes()
    if missing:
        print(f"\n[!] 현재 누락된 씬 감지 ({len(missing)}개): {missing}")
        print("    누락된 씬들에 대해 autoveo_flow.py를 순차적으로 구동하여 복구합니다...")
        
        for scene_num in missing:
            print(f"\n>>> 누락된 Scene {scene_num} 생성 및 다운로드 시작...")
            cmd = ["python", "autoveo_flow.py", "--prompts", PROMPTS_FILE, "--scene", str(scene_num)]
            try:
                res = subprocess.run(cmd, check=True)
                if res.returncode == 0:
                    # autoveo_flow.py가 child_growth_prompts.txt 기반이므로 child_growth/scene_X.mp4로 저장됨
                    # 이를 전용 폴더인 child_growth_science/로 이동/복사시킵니다.
                    src = os.path.join(r"D:\Entertainments\DevEnvironment\autovideo\child_growth", f"scene_{scene_num}.mp4")
                    dst = os.path.join(TARGET_DIR, f"scene_{scene_num}.mp4")
                    if os.path.exists(src):
                        import shutil
                        shutil.copy2(src, dst)
                        print(f"Scene {scene_num} 전용 폴더 복사 완료 ✔")
                    else:
                        print(f"[경고] 생성 완료되었으나 원본 파일 {src}을 찾을 수 없습니다.")
                else:
                    print(f"[오류] Scene {scene_num} 복구 중 비정상 종료 (exit code: {res.returncode})")
            except Exception as e:
                print(f"[에러] Scene {scene_num} 실행 중 오류 발생: {e}")
                
        missing_after = get_missing_scenes()
        if missing_after:
            print(f"\n[경고] 복구 시도 후에도 여전히 씬이 누락되었습니다: {missing_after}")
            print("한 번 더 실행하시거나, 구글 Flow 상에서 생성 에러가 반복되는지 직접 확인해주세요.")
            sys.exit(1)
            
    print("\n[✔] 축하합니다! 모든 0~90번 씬이 누락 없이 다운로드되었습니다.")
    print("    최종 비디오 컴파일 및 렌더링을 시작합니다...")
    
    compile_cmd = [
        "python", "make_video.py",
        "--scenario", SCENARIO_FILE,
        "--output", OUTPUT_VIDEO,
        "--intro", "assets/intro.mp4",
        "--outro", os.path.join(TARGET_DIR, "scene_0_thumbnail.png"),
        "--annotations", r"child_growth_science\annotations.json",
        # 표준: 영어/한글 자막은 굽지 않고 토글 가능한 CC(소프트 트랙)로 내장 (한글 박스는 유지)
        "--no-burn-subs", "--embed-subs"
    ]
    
    print(f"컴파일 명령어 실행: {' '.join(compile_cmd)}")
    try:
        subprocess.run(compile_cmd, check=True)
        print("\n" + "=" * 60)
        print("  🎉 최종 비디오 컴파일이 완료되었습니다!")
        print(f"  출력 경로: {OUTPUT_VIDEO}")
        print("=" * 60)
    except Exception as e:
        print(f"\n[에러] 비디오 컴파일(make_video.py) 도중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
