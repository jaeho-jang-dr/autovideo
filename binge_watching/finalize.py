import os
import sys
import subprocess

TARGET_DIR = r"D:\Entertainments\DevEnvironment\autovideo\binge_watching"
PROMPTS_FILE = r"binge_watching\prompts_for_veo.txt"
SCENARIO_FILE = r"binge_watching\scenario.txt"
OUTPUT_VIDEO = r"D:\Entertainments\DevEnvironment\autovideo\binge_watching\binge_watching.mp4"
TOTAL_SCENES = 96

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
    print("  '몰아보기는 정말 우리 몸에 나쁠까?' 통합 복구 및 렌더링 파이프라인")
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
                    print(f"Scene {scene_num} 생성 완료 ✔")
                else:
                    print(f"[오류] Scene {scene_num} 복구 중 비정상 종료 (exit code: {res.returncode})")
            except Exception as e:
                print(f"[에러] Scene {scene_num} 실행 중 오류 발생: {e}")
                
        missing_after = get_missing_scenes()
        if missing_after:
            print(f"\n[경고] 복구 시도 후에도 여전히 씬이 누락되었습니다: {missing_after}")
            sys.exit(1)
            
    print("\n[✔] 모든 0~96번 씬이 누락 없이 준비되었습니다.")
    print("    최종 비디오 컴파일 및 렌더링을 시작합니다...")
    
    compile_cmd = [
        "python", "make_video.py",
        "--scenario", SCENARIO_FILE,
        "--output", OUTPUT_VIDEO,
        "--intro", "assets/intro.mp4",
        "--outro", "assets/outro.mp4",
        "--annotations", r"binge_watching\annotations.json",
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
