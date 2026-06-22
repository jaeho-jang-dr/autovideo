# 졸라 힙합 한글 쇼츠 — 제작 방법 (모션캡처 리타겟 파이프라인)

> 세로 9:16 쇼츠. 졸라맨·졸라걸이 **실제 댄서 모션**으로 춤추고, 그 위에 한글 자모(**힙합맨/힙합걸**)가
> 날아와 조립되며, 떨어진 받침 **ㄴ**을 졸라맨이 주워 제자리에 붙인다. 배경은 파스텔(중앙 밝게, 분홍·파랑).

## 핵심 아이디어
- Veo로 납작한 스틱맨을 애니메이트하면 동작이 얌전 → **한계**.
- 대신 **자유 라이선스 댄스 영상의 사람 모션을 포즈 추정으로 떠서(motion capture) 졸라 골격에 리타겟** →
  진짜 사람 댄서급 다이나믹/절도가 캐릭터에 그대로 반영된다.

## 소스 & 라이선스 (중요)
- 댄스 소스: **Pexels**(무료, 상업적 사용·수정 허용, 출처표기 불필요).
  - 졸라맨: `source/hiphop_2795746.mp4` (힙합 단독 댄서)
  - 졸라걸: `source/cand_6616343.mp4` (컨템포러리 단독 댄서)
- 음악: `make_music.py`로 **자작 인스트루멘탈(무가사)** — MusicGen.
- 안무는 특정 저작물을 복제하지 않음(리타겟+정규화로 오리지널 재구성). 남의 K-pop 안무 영상 복제 금지.

## 파이프라인 (순서)
1. **기본 이미지**: `base_zolla_pair_beige.png` — 원본 졸라맨/졸라걸 PNG를 PIL로 변형 없이 합성(불투명 베이지). *(Veo 안 씀)*
2. **포즈 추정 → 졸라 리타겟**: `mocap_to_zolla.py`
   - YOLOv8s-pose(COCO 17키포인트) 프레임별 추출 → 졸라 스틱맨(머리/헤어/사지) 렌더.
   - 옵션: `win`(시간축 스무딩=떨림↓), `speed`(<1 느리게), `snap`(N프레임 홀드=탁탁 절도), `style`(man/girl/skeleton).
   - 검출 실패 프레임은 직전 포즈 유지. 사용: `python mocap_to_zolla.py <src> <out> <style> <win> <speed> <snap>`
3. **듀오 합성**: `mocap_duo.py`
   - 남/녀 서로 다른 소스 → 각자 다른 동작. 중앙 hip 기준 **크기 정규화**(같은 비율) 후 좌(W*0.30)/우(W*0.70) 배치.
   - `size`(0.8=20%작게), `snap`, `speed`. → `_duo2.mp4`
4. **자모 조립**: `make_jamo_assembly.py`
   - 단어 "힙합맨"+"힙합걸"(자모 18개, 전 음절 받침). `hangeul_decomposer`로 [초성/중성/종성] 분해.
   - 단순 자모 글자가 **제각각 크기·색(자음 코랄/모음 청록/받침 앰버)으로 비정형 회전하며 날아와** 슬롯에 조립.
   - 배경=파스텔(중앙 흰/밝게, 좌 분홍·우 파랑). `draw_overlay(base,t,skip=...)`로 합성에서 재사용.
5. **최종 합성 + ㄴ 줍기**: `make_final.py`
   - 파스텔 배경 + `_duo2.mp4` 캐릭터(베이지 키잉→**50% 투명** 배경) + 자모 오버레이.
   - 받침 **ㄴ**(맨의 종성)만 따로 제어: 흔들흔들→띠우웅 낙하→졸라맨 **손목(`_man_norm.npy`) 추적해 주움**→제자리 복귀.
   - 가독성: 빈 자리 흐릿한 ㄴ 표시 + 줍는 동안 글로우·확대 + 느린 동선 + 도착 팝.
   - `_man_norm.npy`: `mocap_duo`의 extract/anchor/normalize로 졸라맨 정규화 관절 시퀀스 저장(줍기용).
6. **음악**: `make_music.py` → `bgm.wav`.
7. **마감**: ffmpeg로 H.264 변환 + bgm mux(+페이드) → `_final_music.mp4`. 브라우저(Edge) `file://`로 미리보기.

## 산출물
- 최종: `_final_music.mp4` (9:16, ~14초, 음악 포함)
- 중간: `_duo2.mp4`(춤), `_jamo_assembly.mp4`(자모), `_final.mp4`(무음 합성)

## 조절 파라미터 요약
| 효과 | 위치 |
|------|------|
| 떨림↓ | mocap `win`(스무딩 윈도우) ↑, 모델 yolov8s→m |
| 절도(탁탁) | `snap` ↑ (3~7) |
| 속도 | `speed` (<1 느리게) |
| 캐릭터 크기 | duo `size` |
| ㄴ 줍기 타이밍 | make_final 상단 `T_*` 상수 |
| 배경 톤 | make_jamo_assembly `make_bg()` |

## 의존성
opencv, ultralytics(YOLO-pose, torch+CUDA), moviepy/PIL, ffmpeg, transformers(MusicGen).
