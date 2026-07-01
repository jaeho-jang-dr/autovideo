#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
비디오 마지막 프레임 추출기 (Extract Last Frame)

동영상(MP4)의 가장 마지막 프레임을 고화질 PNG 이미지로 추출하여,
다음 씬(Scene)의 구글 Flow 모션 베이스 이미지로 사용할 수 있도록 준비해 줍니다.
이로써 8초 이상의 연속 애니메이션/롱테이크 연출의 일관성을 보장합니다.

사용 예:
  python scratch/extract_last_frame.py --video binge_watching/scene_94.mp4 --output binge_watching/scene_95_base.png
"""

import os
import sys
import argparse

# cp949 인코딩 오류 방지
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

def extract_last_frame(video_path, output_path):
    video_path = os.path.abspath(video_path)
    output_path = os.path.abspath(output_path)
    
    if not os.path.exists(video_path):
        print(f"[ERR] 비디오 파일이 존재하지 않습니다: {video_path}")
        return False
        
    print(f"[정보] 비디오 로드 중: {video_path}")
    
    # OpenCV 지연 임포트
    try:
        import cv2
    except ImportError:
        print("[ERR] opencv-python 라이브러리가 설치되어 있지 않습니다.")
        print("      설치 명령: pip install opencv-python")
        return False
        
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERR] 비디오 파일을 열 수 없습니다: {video_path}")
        return False
        
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0.0
    
    print(f"       - 해상도: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    print(f"       - FPS: {fps:.2f} | 총 프레임 수: {frame_count} | 재생 시간: {duration:.2f}초")
    
    # 마지막 프레임 찾기 (간혹 마지막 프레임이 손상되었거나 읽을 수 없는 경우를 대비해 역순으로 스캔)
    success = False
    frame = None
    target_idx = frame_count - 1
    
    while target_idx >= 0 and not success:
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_idx)
        ret, temp_frame = cap.read()
        if ret and temp_frame is not None:
            frame = temp_frame
            success = True
            break
        target_idx -= 1
        
    cap.release()
    
    if not success or frame is None:
        print("[ERR] 비디오에서 유효한 마지막 프레임을 읽어오지 못했습니다.")
        return False
        
    # 출력 디렉토리 생성
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 고화질 PNG로 저장
    try:
        cv2.imwrite(output_path, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 1])
        print(f"[✔] 마지막 프레임(인덱스: {target_idx}) 추출 완료!")
        print(f"    출력 경로: {output_path} ({os.path.getsize(output_path) / 1024:.1f} KB)")
        return True
    except Exception as e:
        print(f"[ERR] 이미지 저장 중 오류 발생: {e}")
        return False

def main():
    ap = argparse.ArgumentParser(description="비디오 클립의 마지막 프레임을 PNG로 추출합니다.")
    ap.add_argument("--video", required=True, help="입력 비디오 파일 (.mp4) 경로")
    ap.add_argument("--output", required=True, help="출력 이미지 파일 (.png) 경로")
    args = ap.parse_args()
    
    success = extract_last_frame(args.video, args.output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
