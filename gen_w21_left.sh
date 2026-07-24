#!/usr/bin/env bash
# W21 좌향 방향성 포즈(좌향좌15° FL / 좌측면 L) 정식 생성 — flip 대신 진짜로 그려 '선생님' 글자 안 뒤집히게.
cd /d/Entertainments/DevEnvironment/autovideo || exit 1
PD="home_vocab/w21/poses_raw"; mkdir -p "$PD"
REF="D:/Entertainments/DevEnvironment/autovideo/assets/characters/madam_jay_base_front.png"
CHAR="첨부한 기준 이미지의 캐릭터(마담제이: 갈색 번머리, 코랄색 조끼에 '선생님' 글자, 흰 치마, 흰 신발, 점 눈에 작은 미소, 굵은 검정 외곽선, 납작한 파스텔 미니멀 동화풍)와 완전히 동일한 디자인·비율·색을 그대로 유지하되 포즈만 바꿔 다시 그린다. 조끼의 '선생님' 글자는 정상 방향으로 읽히게(뒤집지 말 것)."
PSTYLE="머리끝부터 발끝까지 전신이 다 보이게 세로로 여유있게, 순백색(#ffffff) 배경, 그림자 없음, 글자·워터마크·말풍선 없음. 나노바나나(제미나이 이미지)로 직접 생성하고 Google Flow는 절대 쓰지 말 것."

launch_pose(){ local key="$1"; shift; local desc="$*"
  printf '%s\n기준 이미지: %s (반드시 참고 이미지로 사용).\n포즈: %s\n%s\n결과 PNG 저장: D:/Entertainments/DevEnvironment/autovideo/%s/mj_w21_%s.png\n' \
    "$CHAR" "$REF" "$desc" "$PSTYLE" "$PD" "$key" > "$PD/prompt_$key.txt"
  nohup agy -p "$(cat "$PD/prompt_$key.txt")" --dangerously-skip-permissions > "$PD/log_$key.txt" 2>&1 &
}
waitfiles(){ for i in $(seq 1 60); do local ok=1; for f in "$@"; do [ -f "$f" ] || ok=0; done
  [ $ok -eq 1 ] && { echo "  batch ready"; return; }; sleep 5; done; echo "  batch TIMEOUT"; }

echo "### 메인 드라이버 완료 대기"
for i in $(seq 1 240); do grep -q "### 완료" home_vocab/w21/gen_driver.log 2>/dev/null && break; sleep 10; done
echo "### 좌향 포즈 생성 시작"

LEFT=(
"present_left|몸을 왼쪽으로 약 15도 튼 정면 자세에서, 왼팔을 펴 손바닥을 위로 하여 왼쪽 무언가를 정중히 가리켜 제시하는 전신."
"point_left|몸을 왼쪽으로 약 15도 튼 정면 자세에서, 왼팔을 뻗어 검지로 왼쪽 먼 곳을 가리키는 전신."
"explain_fl|몸을 왼쪽으로 약 15도 튼 정면에서, 왼손을 왼쪽으로 펴 차분히 설명하는 제스처의 전신."
"touch_hair_long_fl|몸을 왼쪽으로 약 15도 튼 정면에서, 왼손으로 긴 머리카락을 어깨 아래로 쓸어내리는 전신."
"look_up_fl|몸을 왼쪽으로 약 15도 튼 정면에서, 고개를 들어 위쪽을 올려다보는 전신."
"look_around_l|몸 전체가 왼쪽을 향한 완전한 좌측 측면(옆모습). 앞(왼쪽)을 바라보며 주변을 살피듯 서 있는 전신."
)
i=0; batch=()
for e in "${LEFT[@]}"; do k="${e%%|*}"; d="${e#*|}"; launch_pose "$k" "$d"; batch+=("$PD/mj_w21_$k.png"); echo "  pose: $k"
  i=$((i+1)); if [ $((i%4)) -eq 0 ]; then waitfiles "${batch[@]}"; batch=(); fi; done
[ ${#batch[@]} -gt 0 ] && waitfiles "${batch[@]}"
echo "### 좌향 완료. 총 포즈 $(ls $PD/mj_w21_*.png 2>/dev/null|wc -l)개"
