# Cascadeur 셋업 & 워크플로우 — 애니 캐릭터 동작 제작

> **목적**: 사람 관절 물리(가동범위·균형)를 아는 엔진으로 **커스텀 티칭 동작을 제대로 제작**한다.
> Claude(감독)가 뼈에 임의 각도 넣는 방식 폐기 → Cascadeur의 물리+AI가 생체역학을 보장.

---

## 0. 왜 Cascadeur인가
- **물리 기반 + AI 오토포징**: 제어점 몇 개만 옮기면 AI가 나머지 몸을 **자연스럽게(관절 한계·균형 지켜서)** 배치. 손으로 각도 넣어 뭉개지던 문제 해결.
- **동작을 "만드는" 툴** (가져오기만 아님). 기성 모션 클린업·편집도 가능.
- FBX·glTF 입출력 → 우리 애니 캐릭터 그대로 사용.

## 1. 이 PC 사양 (확인 완료 — 충분)
| 요구 | 이 PC | 판정 |
|---|---|---|
| NVIDIA GTX950+ | **RTX 5070** | ✅ 상회 |
| RAM 16GB | **127GB** | ✅ |
| i5/Ryzen5+ | **Ryzen 7 7800X3D** | ✅ |
| Win10 64bit | Win11 | ✅ |

## 2. 다운로드 & 설치
1. https://cascadeur.com/download 접속
2. **Windows** 버전 다운 (약 373MB, 현재 v2026.1.3)
3. 설치 실행 → 계정 가입(무료) → 로그인

## 3. 라이선스 선택 ⚠️ 중요
| 티어 | 조건 | FBX 내보내기 | 상업 |
|---|---|---|---|
| **Free** | 비상업 | ❌ (.casc 전용) | ❌ |
| **Indie** | 매출 <$100k/년, 3명까지 | ✅ | ✅ |
| Pro | $399/년 | ✅ | ✅ |

- **우리는 Indie 필요**: (a) 상업(drjayed 영상) (b) **FBX로 내보내야** 우리 렌더 파이프라인에서 씀. **Free는 .casc만** 나와서 우리 파이프라인에 못 넘김.
- 먼저 **Free로 배우고**, 실제 상업 제작 시작할 때 **Indie($99/년)** 로 전환 권장.

## 4. 워크플로우 (동작 1개 만드는 순서)
1. **캐릭터 임포트**: Cascadeur에서 `File > Import` → 우리 캐릭터 FBX
   - 준비됨: `scratch/mocap/shino_for_mixamo.fbx` (2.4MB, 애니 소녀, T포즈)
2. **리깅 매핑** (`Quick Rigging Tool`): 캐릭터 뼈(J_Bip_*)를 Cascadeur 리그(골반·발·손 등)에 매핑 → AutoPosing/AutoPhysics 활성화
3. **동작 제작** (여기가 핵심 = 관절 아는 엔진):
   - **AutoPosing**: 손·발 제어점만 원하는 위치로 → AI가 팔·다리·척추를 생체역학적으로 자동 배치
   - **타임라인 키프레임**: 시작→중간→끝 포즈 찍기 (예: 인사=허리 숙였다 편다)
   - **AutoPhysics**: 무게중심·균형 자동 보정 (안 넘어지게, 자연스럽게)
   - **AI Inbetweening**: 키 사이 자동 채움
4. **내보내기**: `File > Export > FBX` (애니 포함) → `scratch/mocap/anim_<이름>.fbx`

## 5. 우리 파이프라인 연결
- Cascadeur에서 만든 FBX를 주시면 → **Claude가 bpy로 렌더 + 배경 합성 + 스튜디오/뷰어 등록**.
- 즉 **동작 제작 = Cascadeur(물리 엔진)**, **렌더·합성·조립 = Claude**.

## 6. 역할 분담
- **사장님(또는 애니메이터)**: Cascadeur GUI에서 동작 제작 (AI가 도와주니 초보도 가능).
- **Claude**: 캐릭터 FBX 준비(완료), Cascadeur 결과 FBX 렌더·합성, 뷰어 관리.
- ⚠️ Cascadeur는 GUI 툴이라 Claude가 직접 조작 불가 — 동작 제작은 사람이, 나머지는 Claude가.

## 7. 배우기 (무료 자료)
- 공식 튜토리얼: https://cascadeur.com/help
- Cascadeur 유튜브 채널 (Quick Start, AutoPosing 강좌)
- 첫 목표: 애니 캐릭터로 **인사 → 가리키기 → 설명** 3동작 만들어 FBX 내보내기

## 8. 대안 (동작 제작 다른 엔진)
- **DeepMotion SayMotion**: 텍스트로 동작 생성("teacher pointing at board") → FBX. 웹 기반, 초간단.
- **Mixamo**: 기성 프로 모션 라이브러리(걷기·가리키기 등 바로 가져오기). FBX 업로드+다운로드.
- 조합 권장: **기성=Mixamo, 커스텀=Cascadeur/SayMotion, 조립·렌더=Claude**.
