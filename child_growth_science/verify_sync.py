import os
import re
import sys
import cv2

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

TARGET_DIR = r"D:\Entertainments\DevEnvironment\autovideo\child_growth_science"
SCENARIO_PATH = r"D:\Entertainments\DevEnvironment\autovideo\child_growth_science\scenario.txt"
TOTAL_SCENES = 90

def is_real_mp4(path):
    try:
        with open(path, "rb") as f:
            head = f.read(16)
        return b"ftyp" in head
    except Exception:
        return False

def get_video_duration(path):
    try:
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            return 0.0
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        if fps > 0:
            return frame_count / fps
        return 0.0
    except Exception:
        return 0.0

def main():
    print("=" * 60)
    print("  child_growth_science 씬 매칭 상태 정밀 진단")
    print("=" * 60)
    
    if not os.path.exists(SCENARIO_PATH):
        print(f"[ERR] 대본 파일({SCENARIO_PATH})이 존재하지 않습니다.")
        sys.exit(1)
        
    with open(SCENARIO_PATH, "r", encoding="utf-8") as f:
        content = f.read()
        
    raw_blocks = re.split(r'\[Scene\s+(\d+)\]', content, flags=re.IGNORECASE)
    scenario_scenes = {}
    for i in range(1, len(raw_blocks), 2):
        scene_id = int(raw_blocks[i])
        block_text = raw_blocks[i+1]
        text_match = re.search(r'text:\s*(.*)', block_text, re.IGNORECASE)
        if text_match:
            scenario_scenes[scene_id] = text_match.group(1).strip()
            
    print(f"[정보] 대본에 정의된 총 씬 수: {len(scenario_scenes)}개")
    
    missing = []
    corrupted = []
    valid_count = 0
    
    print("\n비디오 클립 유효성 진단 (0 ~ 90):")
    for i in range(0, TOTAL_SCENES + 1):
        path = os.path.join(TARGET_DIR, f"scene_{i}.mp4")
        if not os.path.exists(path):
            missing.append(i)
            continue
            
        if os.path.getsize(path) == 0 or not is_real_mp4(path):
            corrupted.append(f"Scene {i} (이진 헤더 손상)")
            continue
            
        duration = get_video_duration(path)
        if duration <= 0.0:
            corrupted.append(f"Scene {i} (비디오 프레임 파싱 실패 - 재생불가)")
            continue
            
        valid_count += 1
        
    print(f"- 정상 파일 수: {valid_count} / {TOTAL_SCENES + 1}")
    if missing:
        print(f"- 미완성(누락) 씬 번호: {missing}")
    if corrupted:
        print(f"- 손상된 씬 번호 (재다운로드 필요): {corrupted}")
        
    matching_errors = []
    for i in range(0, TOTAL_SCENES + 1):
        if i not in scenario_scenes:
            matching_errors.append(f"Scene {i} 가 대본 파일에 정의되어 있지 않습니다.")
            
    if matching_errors:
        print("\n[❌] 대본 매칭 불일치 오류:")
        for err in matching_errors:
            print(f"  {err}")
    else:
        print("\n[✔] 대본과 비디오 인덱스 매칭 정상.")
        
    if not missing and not corrupted and not matching_errors:
        print("\n[✔] 모든 검증 통과! 비디오 클립과 대본이 100% 매칭되며 컴파일 준비가 완료되었습니다.")
    else:
        print("\n[!] 미완성된 씬 혹은 손상된 씬이 있어 컴파일을 실행할 수 없습니다.")
        
if __name__ == "__main__":
    main()
