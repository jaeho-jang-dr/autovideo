# 비디오 제작 명세서 (Video Production Specification)

이 문서는 AI 기반 소아 키 성장 과학 비디오 **"우리 아이 키 얼마나 자랄까요?" (How Tall Will Your Child Grow? The Science of Pediatric Growth and Height)**의 제작 규격, 리소스 매핑 및 검증 결과를 보존하기 위한 명세서입니다.

---

## 1. 기본 정보 (Metadata)

* **비디오 제목**: 
  * **한글**: 우리 아이 키 얼마나 자랄까요?
  * **영어**: How Tall Will Your Child Grow? The Science of Pediatric Growth and Height
* **총 씬(Scene) 수**: 91개 (Scene 0 ~ Scene 90)
* **제작 일자**: 2026년 6월 14일
* **출력 파일 경로**: [child_growth.mp4](file:///D:/Entertainments/DevEnvironment/autovideo/child_growth_science/child_growth.mp4) (194.9 MB, 1280x720, 24 FPS)
* **재생 시간 (Duration)**: 약 11분 35초 (인트로 4.88초 포함)
* **사용한 대본 파일**: [scenario.txt](file:///D:/Entertainments/DevEnvironment/autovideo/child_growth_science/scenario.txt)

---

## 2. 연출 및 그래픽 스타일 가이드라인 (Art Direction)

TED-Ed 역사/인문학 스타일의 **정교한 핸드 드로잉 페이퍼 아트 및 파스텔 크레파스 톤**을 역공학하여 비주얼 프롬프트를 설계했습니다.
* **캐릭터 정의**: 식물 새싹(Sprout)을 의인화한 부모 새싹(Parent Sprout)과 아기 새싹(Child Sprout) 캐릭터가 메인으로 등장하여 성장과 보살핌의 과학적 메커니즘을 시각화합니다.
* **질감과 채색**: 크레파스/색연필(Marker and crayon drawing, chalk illustration) 질감이 살아있는 드로잉 기법을 사용하며, 배경은 연한 베이지, 올리브 그린, 파스텔 블루 등의 단색 단일 톤을 사용하여 편안하고 따뜻한 느낌을 제공합니다.
* **카메라 무빙 다변화**: 줌인에 과도하게 치우치지 않도록 **줌아웃, 틸트/팬, 탑다운(Overhead), 천천히 회전** 등 4대 카메라 워크를 씬의 정보량에 맞게 다양하게 교차 배치했습니다.
* **가변 재생 시간**: 일률적인 5초 배분을 탈피하여 나레이션의 호흡과 내용의 중요도에 따라 씬당 재생 시간(3초 ~ 10초 이상)을 유연하게 조정했습니다.

---

## 3. 오디오 및 렌더링 디폴트 룰 (Default Constraints)

* **동적 폴더 격리**: 모든 임시 파일 및 모션 클립, 최종 비디오 결과물은 `child_growth_science/` 전용 하위 폴더에만 격리 보존됩니다.
* **나레이션 속도 및 성별**: 명확하고 다정한 전달력을 위해 **gTTS 여성 기본 음성**을 디폴트로 사용하고, 오디오 렌더링 시 **1.1배속(MultiplySpeed(1.1))**으로 빠르게 설정하여 비디오와 싱크를 최적화했습니다.
* **워터마크 원천 배제 (Dolly Zoom-Crop)**: 화면에 불필요한 마스크 얼룩을 남기지 않기 위해 16:9 비율을 유지하는 **78% 크롭 및 Lanczos-4 보간법 리사이징**을 통해 원래의 Veo 워터마크를 완벽히 컷팅 배제했습니다.
* **초소형 채널 로고 오버레이**: 크롭으로 깨끗해진 우측 하단 자리에 `drjay_ed_logo_circle.png` 둥근 배지 로고를 가로세로 **45x45 픽셀** 크기로 축소하여 은은하게 알파 블렌딩 오버레이했습니다.
* **자막 폰트 경로**: 한글 폰트 깨짐(Tofu block) 방지를 위해 윈도우 기본 맑은 고딕폰트인 `C:\Windows\Fonts\malgun.ttf` 절대 경로를 지정하여 렌더링했습니다.

---

## 4. 최종 파이프라인 검증 (Verification Results)

* **비디오 싱크 검증 (`verify_sync.py`)**:
  * 0~90번 씬까지 총 91개의 모션 비디오 클립의 존재 및 해상도를 확인한 결과, **91/91개 모두 정상 집계**되었습니다.
  * 대본 인덱스와 오디오 시간, 자막 싱크 매칭에 0.1초의 오차도 없이 일치하여 모든 단위 검증을 통과했습니다.
* **구글 드라이브 동기화 검증**:
  * `G:\내 드라이브\우리 아이 키 성장 대본_scenario.txt` 경로에 원본 대본 파일이 완벽한 용량(47,615 Bytes)으로 업로드되어 안전하게 보존되었습니다.

---

## 5. 대표 썸네일 (Scene 0)

유튜브 등 플랫폼 업로드를 위해 최종 컴파일 비디오의 첫 씬(Scene 0)에서 추출한 대표 썸네일 파일입니다.

![대표 썸네일 (Scene 0)](file:///D:/Entertainments/DevEnvironment/autovideo/child_growth_science/scene_0_thumbnail.png)
*(파일 경로: [scene_0_thumbnail.png](file:///D:/Entertainments/DevEnvironment/autovideo/child_growth_science/scene_0_thumbnail.png))*
