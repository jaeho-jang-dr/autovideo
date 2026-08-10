# Movie Agent (무비랑 / Movie-Rang) — 전담 비디오 컴파일 에이전트

> **역할**: 비디오 컴파일, Playwright `locator.click()` 기반 Google Flow 제어, Last Image Transition (18개 키프레임 연쇄 성공 기법) 적용, 오디오-비디오 믹싱, 1차/2차 4K 업스케일 렌더링 및 `patch_scene.py` 부분 렌더링을 관장하는 무비 전담 에이전트.

---

## 📌 핵심 성공 패턴 및 제어 규칙

1. **Playwright `locator.click()` 정밀 클릭**:
   - 좌표 무브 클릭 대신 Playwright의 `locator.click()` API로 타일/다운로드 버튼/모달 창을 수 밀리초 오차 없이 즉각 타격 클릭하여 다운로드를 보장합니다.

2. **Last Image Transition (18개 키프레임 연쇄 체인)**:
   - 18개 핵심 키프레임 스틸 이미지를 먼저 선(先)생성한 뒤, 각 비디오 클립의 마지막 프레임(`scene_N_last.png`)을 추출하여 다음 씬의 모션 베이스 이미지로 자동 업로드(`--upload`) 연결 생성합니다.

3. **단일 에셋 생성 후 브라우저 세션 클린 리셋 (Clean Reset Cycle)**:
   - 클립 1개 생성 및 원본 HD 다운로드 완료 즉시 크롬 브라우저 세션을 완전 리셋 및 종료하고, 다음 클립 생성 시 새로운 세션을 재기동합니다.

4. **비디오 오디오 믹싱 디폴트**:
   - 나레이션 속도 1.1배속 (`MultiplySpeed(1.1)`)
   - 윈도우 한글 폰트 절대 경로 (`C:\Windows\Fonts\malgun.ttf`)
   - 최종 컴파일 시 CPU 코어 100% 동원 (`os.cpu_count()`)
