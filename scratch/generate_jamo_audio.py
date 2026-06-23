# -*- coding: utf-8 -*-
import os
import sys
import subprocess

# gTTS 라이브러리가 없을 경우 자동 설치
try:
    from gtts import gTTS
except ImportError:
    print("gTTS 라이브러리를 찾을 수 없어 설치를 진행합니다...")
    subprocess.run([sys.executable, "-m", "pip", "install", "gTTS"], check=True)
    from gtts import gTTS

# 오디오 파일이 저장될 출력 디렉토리
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web", "public", "audio", "jamo"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 생성할 텍스트 목록 정의
# 1. 자음 단독 발음
consonants = {
    'ㄱ': '기역', 'ㄲ': '쌍기역', 'ㄴ': '니은',
    'ㄷ': '디귿', 'ㄸ': '쌍디귿', 'ㄹ': '리을',
    'ㅁ': '미음', 'ㅂ': '비읍', 'ㅃ': '쌍비읍',
    'ㅅ': '시옷', 'ㅆ': '쌍시옷', 'ㅇ': '이응',
    'ㅈ': '지읒', 'ㅉ': '쌍지읒', 'ㅊ': '치읓',
    'ㅋ': '키읔', 'ㅌ': '티읔', 'ㅍ': '피읔',
    'ㅎ': '히읗'
}

# 2. 모음 단독 발음
vowels = ['아', '야', '어', '여', '오', '요', '우', '유', '으', '이', '의', '애', '에', '얘', '예', '와', '왜', '외', '워', '웨', '위']

# 3. 초성 5개(ㄱ, ㄴ, ㅁ, ㅅ, ㅇ)와 모음의 조합으로 생성될 주요 1글자
syllables = []

# 한글 유니코드 계산을 위한 도구
CHO_LIST = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
JUNG_LIST = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
JONG_LIST = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㅈ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

# 1단계: 기존에 이미 생성된 5개 초성(ㄱ,ㄴ,ㅁ,ㅅ,ㅇ) 기반 주요 조합 추가
choseongs_base = ['ㄱ', 'ㄴ', 'ㅁ', 'ㅅ', 'ㅇ']
jungseongs = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
jongseongs_base = ['', 'ㄱ', 'ㄴ', 'ㅁ', 'ㅅ', 'ㅇ']

for cho in choseongs_base:
    for jung in jungseongs:
        for jong in jongseongs_base:
            ci = CHO_LIST.index(cho)
            ji = JUNG_LIST.index(jung)
            jo_i = JONG_LIST.index(jong)
            
            char = chr(0xAC00 + (ci * 21 + ji) * 28 + jo_i)
            syllables.append(char)

# 2단계: 19개 전체 자음(초성) * 12개 모음 * 받침 없는 조합 추가
for cho in CHO_LIST:
    for jung in jungseongs:
        ci = CHO_LIST.index(cho)
        ji = JUNG_LIST.index(jung)
        
        char = chr(0xAC00 + (ci * 21 + ji) * 28 + 0) # 받침 없음
        if char not in syllables:
            syllables.append(char)

# 3단계: 상황 표현 및 퀴즈용 필수 상용 음절 강제 추가 (받침이 들어간 단어 구제)
extra_syllables = ['물', '주', '세', '요', '밥', '맛', '있', '어', '화', '장', '실', '디', '에', '휴', '지', '여', '권', '기', '비', '행', '표', '차', '없', '닭', '앉', '않', '읽', '잃', '짧', '넓', '밟', '맑', '젊', '읊', '끓', '굶', '값', '몫', '넋', '삯', '핥', '흙']
for char in extra_syllables:
    if char not in syllables:
        syllables.append(char)

# 전체 타겟 에셋 목록 빌드 (텍스트: 파일명)
target_assets = {}

# 자음 매칭 (예: '기역' 텍스트 -> '기역.mp3' 파일명)
for key, value in consonants.items():
    target_assets[value] = value

# 모음 매칭 (예: '아' -> '아.mp3', 천지인 '아래아' 추가)
for v in vowels:
    target_assets[v] = v
target_assets['아래아'] = '아래아'

# 조합 글자 매칭
for s in syllables:
    target_assets[s] = s  # '가.mp3', '간.mp3' 등

print(f"총 {len(target_assets)}개의 한글 고품질 발음 에셋 생성을 시작합니다...")

success_count = 0
for text, filename in target_assets.items():
    # 파일 경로 설정 (윈도우 환경 파일명 오류 방지)
    safe_filename = f"{filename}.mp3"
    filepath = os.path.join(OUTPUT_DIR, safe_filename)
    
    # 이미 존재하는 파일은 스킵 (캐시 유지)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        success_count += 1
        continue
        
    try:
        # 한국어(ko) 발음 성우 렌더링
        tts = gTTS(text=text, lang='ko', slow=False)
        tts.save(filepath)
        success_count += 1
        if success_count % 20 == 0:
            print(f"진행 상황: {success_count}/{len(target_assets)} 개 에셋 생성 완료...")
    except Exception as e:
        print(f"에러 발생 ({text} -> {safe_filename}): {e}")

print(f"\n[OK] 성공적으로 {success_count}개의 고품질 발음 에셋이 {OUTPUT_DIR} 에 적재되었습니다!")
