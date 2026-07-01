import os
import sys
import subprocess
import time

TARGET_DIR = r"D:\Entertainments\DevEnvironment\autovideo\binge_watching"
PROMPTS_FILE = "binge_watching_prompts.txt"
SCENARIO_FILE = "scenario.txt"
OUTPUT_VIDEO = r"D:\Entertainments\DevEnvironment\autovideo\binge_watching\binge_watching.mp4"
TOTAL_SCENES = 96

# cp949 인코딩 오류 방지
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
    print("  AsapSCIENCE 'Binge Watching' 통합 복구 및 렌더링 파이프라인")
    print("=" * 60)
    
    missing = get_missing_scenes()
    if missing:
        print(f"\n[!] 현재 누락된 씬 감지 ({len(missing)}개): {missing}")
        print("    누락된 씬들에 대해 autoveo_flow.py를 순차적으로 구동하여 복구합니다...")
        
        for scene_num in missing:
            print(f"\n>>> 누락된 Scene {scene_num} 생성 및 다운로드 시작...")
            # autoveo_flow.py를 해당 scene 번호만 타겟하여 실행
            cmd = ["python", "autoveo_flow.py", "--prompts", PROMPTS_FILE, "--scene", str(scene_num)]
            try:
                # 사용자의 데스크톱 크롬 세션이 필요하므로 서브프로세스로 실행
                res = subprocess.run(cmd, check=True)
                if res.returncode == 0:
                    print(f"Scene {scene_num} 복구 완료 ✔")
                else:
                    print(f"[오류] Scene {scene_num} 복구 중 비정상 종료 (exit code: {res.returncode})")
            except Exception as e:
                print(f"[에러] Scene {scene_num} 실행 중 오류 발생: {e}")
                
        # 복구 완료 후 누락 재점검
        missing_after = get_missing_scenes()
        if missing_after:
            print(f"\n[경고] 복구 시도 후에도 여전히 씬이 누락되었습니다: {missing_after}")
            print("한 번 더 실행하시거나, 구글 Flow 상에서 생성 에러가 반복되는지 직접 확인해주세요.")
            sys.exit(1)
            
    print("\n[✔] 축하합니다! 모든 0~96번 씬이 누락 없이 다운로드되었습니다.")
    print("    최종 비디오 컴파일 및 렌더링을 시작합니다...")
    
    # make_video.py 실행하여 최종 합본 제작
    # --scenario scenario.txt --output binge_watching/binge_watching.mp4 --intro assets/intro.mp4 --outro assets/outro.mp4
    compile_cmd = [
        "python", "make_video.py",
        "--scenario", SCENARIO_FILE,
        "--output", OUTPUT_VIDEO,
        "--intro", "assets/intro.mp4",
        "--outro", ""
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
