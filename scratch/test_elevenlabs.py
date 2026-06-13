#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ElevenLabs 및 gTTS 동작 확인용 테스트 스크립트.
"""
import os
import sys

# 프로젝트 루트를 Python path에 추가
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
sys.path.append(PARENT)

from tts_manager import save_tts

def test():
    test_dir = os.path.join(PARENT, "assets", "audio")
    os.makedirs(test_dir, exist_ok=True)
    
    test_file_ko = os.path.join(test_dir, "test_narration_ko.mp3")
    test_file_en = os.path.join(test_dir, "test_narration_en.mp3")
    
    text_ko = "안녕하세요. 의사의 메스로 세상을 해부하고, 만화가의 상상력으로 꿰매는 닥터 제이 에드입니다."
    text_en = "Hello. This is Dr. Jay Ed, dissecting the world with a scalpel and stitching it back with imagination."
    
    # 1. 한국어 테스트
    print("--- Testing Korean TTS ---")
    success_ko = save_tts(text_ko, test_file_ko, lang="ko")
    if success_ko and os.path.exists(test_file_ko):
        print(f"SUCCESS: Korean audio generated at {test_file_ko} (Size: {os.path.getsize(test_file_ko)} bytes)")
    else:
        print("FAILED: Korean audio generation.")
        
    # 2. 영어 테스트
    print("\n--- Testing English TTS ---")
    success_en = save_tts(text_en, test_file_en, lang="en")
    if success_en and os.path.exists(test_file_en):
        print(f"SUCCESS: English audio generated at {test_file_en} (Size: {os.path.getsize(test_file_en)} bytes)")
    else:
        print("FAILED: English audio generation.")

if __name__ == "__main__":
    test()
