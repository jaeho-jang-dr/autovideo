#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ElevenLabs 및 gTTS 통합 TTS 매니저.
.env 설정에 따라 ElevenLabs API 또는 gTTS를 사용하여 오디오 파일을 생성한다.
"""
import os
import requests
from gtts import gTTS

def load_env():
    """프로젝트 루트의 .env 파일을 수동 파싱하여 os.environ에 주입 (외부 패키지 의존성 제거)"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    # 주석 제거 및 따옴표 제거
                    if "#" in val:
                        val = val.split("#", 1)[0].strip()
                    val = val.strip("'\"")
                    # 시스템 환경변수가 설정되어 있지 않은 경우에만 주입
                    if key and key not in os.environ:
                        os.environ[key] = val

# 모듈 로드 시 환경변수 로드
load_env()

def save_tts_gtts(text, output_path, lang='ko'):
    """gTTS를 사용하여 나레이션을 생성하고 저장하는 Fallback 함수"""
    print(f"[TTS] Fallback to gTTS (lang={lang})...")
    # gTTS는 기본적으로 한국어('ko') 및 영어('en') 등을 지원합니다.
    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)
    return True

def save_tts(text, output_path, lang='ko', voice_id=None):
    """
    ElevenLabs API를 호출하여 TTS 오디오 파일을 생성하고 저장한다.
    실패하거나 설정이 없을 경우 gTTS로 자동 Fallback한다.
    """
    api_key = os.environ.get("ELEVEN_API_KEY", "").strip()
    
    # API 키가 없으면 바로 gTTS 사용
    if not api_key:
        print("[TTS] ELEVEN_API_KEY not set. Using gTTS.")
        return save_tts_gtts(text, output_path, lang)
        
    # Voice ID 설정 파싱
    active_voice = os.environ.get("ELEVEN_ACTIVE_VOICE", "female").strip().lower()
    
    if not voice_id:
        if active_voice == "male":
            voice_id = os.environ.get("ELEVEN_VOICE_MALE", "oq1t7YrJg871G2HokpW9").strip()
        elif active_voice == "custom":
            voice_id = os.environ.get("ELEVEN_VOICE_CUSTOM", "").strip()
            if not voice_id:
                print("[TTS] ELEVEN_VOICE_CUSTOM is active but empty. Falling back to female.")
                voice_id = os.environ.get("ELEVEN_VOICE_FEMALE", "21m00Tcm4TlvDq8ikWAM").strip()
        else: # female
            voice_id = os.environ.get("ELEVEN_VOICE_FEMALE", "21m00Tcm4TlvDq8ikWAM").strip()

    model_id = os.environ.get("ELEVEN_MODEL", "eleven_multilingual_v2").strip()
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    
    print(f"[TTS] Requesting ElevenLabs (Voice: {voice_id}, Model: {model_id})...")
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=15)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"[TTS] Successfully generated: {output_path} via ElevenLabs")
            return True
        else:
            print(f"[TTS] ElevenLabs API error: {response.status_code} - {response.text}")
            return save_tts_gtts(text, output_path, lang)
    except Exception as e:
        print(f"[TTS] Connection to ElevenLabs failed: {e}")
        return save_tts_gtts(text, output_path, lang)

if __name__ == "__main__":
    # 간단한 테스트 실행
    print("Testing Env Loading...")
    print("Active Voice:", os.environ.get("ELEVEN_ACTIVE_VOICE"))
    print("Male Voice:", os.environ.get("ELEVEN_VOICE_MALE"))
    print("Female Voice:", os.environ.get("ELEVEN_VOICE_FEMALE"))
