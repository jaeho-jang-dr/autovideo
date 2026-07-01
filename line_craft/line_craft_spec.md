# 2D Animation Line Craft Video Integration Test Specification

> **2D Line Craft 비디오 생성 및 CapCut PC / MoviePy 2.x 최종 렌더링 통합 테스트 명세서 (오브젝트 레이어 합성 버전)**
> 
> *본 명세서는 2026-06-18 일 진행된 라인 크라프트 기법의 씬 2종 연동 테스트에 대한 2차 파이프라인 분석과 명세를 담고 있습니다.*

---

## 1. 프로젝트 요약
- **목적**: 2D Animation Line Craft 스타일 비디오 본편 2개(총 12.28초)를 대상으로, 전체 화면의 왜곡이나 깜빡임(흔들기, 돌리기, 번쩍이기) 없이 **개별 오브젝트(레이어) 단위의 2D 종이인형 모션 연출** 및 **한국어 자막 하드번(Text Bounce)**을 통합 구현하여 검증.
- **파이프라인 단계**: 
  1. 프롬프트 정의 (`scratch/line_craft_prompts.txt`)
  2. Flow 비디오 자동 생성 및 로컬 다운로드 (`line_craft/scene_1.mp4`, `scene_2.mp4`)
  3. MoviePy 2.x API 기반 1.1배 가속 TTS 오디오 합성 (`scratch/generate_line_craft_audio.py`)
  4. 커스텀 2D 모션 그래픽 레이어 주입 및 한국어 자막 하드번 렌더링 (`make_video.py` 실행)
     - 인트로/아웃트로 및 정지 카드를 완전히 배제하고 오직 씬 본편만 컴파일.

---

## 2. 씬별 상세 명세 (Scenario Specifications)

### [Scene 1] (duration: 6.26s)
- **나레이션 대본**: 미래의 자동차가 칠판 위에 한 땀 한 땀 아름다운 선으로 그려지고 있습니다.
- **영어 자막**: A futuristic car is being drawn step by step with beautiful lines on a chalkboard.
- **비디오 소스**: [scene_1.mp4](file:///D:/Entertainments/DevEnvironment/autovideo/line_craft/scene_1.mp4) (8초 원본 -> 1.1배속 오디오 싱크 가속 적용)
- **자막 렌더링**: 한국어 자막 하드번(Text Bounce 적용, 맑은 고딕 Bold 24pt, 테두리 8px 검은색)
- **추가 이펙트 레이어 [오브젝트 무브먼트]**:
  - **빨간색 강조 화살표 슈팅**: 2.5초 시점에 화면 내 안전지대 우상단(1100, 150)에서 출발해 비행 자동차 본체 방향(880, 350)으로 0.7초 동안 미끄러지듯 날아가(fly-in) 꽂힌 뒤 고정 유지됨.
- **어노테이션 라벨**: 좌상단 Sprout Green 박스 ("비행 자동차 구조 설계도") 오버레이 합성.

### [Scene 2] (duration: 6.05s)
- **나레이션 대본**: 정밀한 기계 부품과 톱니바퀴들이 유기적으로 맞물려 움직이기 시작합니다.
- **영어 자막**: Precise mechanical parts and gears start to move dynamically together.
- **비디오 소스**: [scene_2.mp4](file:///D:/Entertainments/DevEnvironment/autovideo/line_craft/scene_2.mp4) (8초 원본 -> 1.1배속 오디오 싱크 가속 적용)
- **자막 렌더링**: 한국어 자막 하드번(Text Bounce 적용, 맑은 고딕 Bold 24pt, 테두리 8px 검은색)
- **추가 이펙트 레이어 [오브젝트 무브먼트]**:
  - **회전 기어 타겟 하이라이트**: 3.0초 시점에 기어 장치 중심부(780, 360)에 노란색 점선 타겟 링 및 "ACTIVE" 라벨이 페이드인되어 나타나며, 40deg/sec 속도로 제자리 회전 연출.
- **어노테이션 라벨**: 좌상단 Sprout Green 박스 ("로봇 손 관절 기어 메커니즘") 오버레이 합성.

---

## 3. 오디오 및 비주얼 이펙트 매핑 (Effects Map)
- **나레이션 가속**: gTTS 1.1배속 가속 및 AAC 인코딩 결합.
- **트랜지션 효과음**: 씬 전환 경계점인 **7.5초 ~ 8.1초** 구간에 `assets/audio/whoosh.wav` (0.6초, 볼륨 0.45 증폭) 믹싱.
- **자막 튕기기 효과**: MoviePy 상에서 첫 0.3초 동안 스케일을 0 -> 1.1 -> 1.0으로 애니메이션 처리 (`apply_text_bounce`).
- **채널 로고 오버레이**: 78% 크롭된 우측 하단 자리에 `assets/drjay_ed_logo_circle.png` 원형 로고 배지를 25% 축소 크기인 **가로세로 45x45 픽셀**로 알파 블렌딩 오버레이.
- **배경음악**: 로컬 `kpop_song_1.wav` 파일을 BGM(`lofi_bgm.mp3` 경로 지정)으로 활용하여 볼륨 0.15로 믹싱.

---

## 4. 최종 출력물 사양
- **비디오 파일**: [line_craft_final.mp4](file:///D:/Entertainments/DevEnvironment/autovideo/line_craft/line_craft_final.mp4)
- **해상도**: 3840x2160 (4K UHD, ffmpeg Lanczos upscale 적용)
- **파일 크기**: 25.30 MB (인트로/아웃트로 제외된 본편 12.28초 분량)
- **프레임 레이트**: 24 fps (libx264 비디오 코덱 + aac 오디오 코덱 재인코딩 적용)
- **자막 (Soft CC)**: 한국어(kor) 및 영어(eng) srt 자막 트랙 내장 (VLC/YouTube CC 대응, 디폴트 OFF)
  - [한국어 SRT](file:///D:/Entertainments/DevEnvironment/autovideo/line_craft/line_craft_final.ko.srt)
  - [영어 SRT](file:///D:/Entertainments/DevEnvironment/autovideo/line_craft/line_craft_final.en.srt)
