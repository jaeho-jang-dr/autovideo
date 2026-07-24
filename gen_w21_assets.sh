#!/usr/bin/env bash
# W21 마담제이 나머지 포즈(23) + 배경(10) agy 나노바나나 직접 생성. 4개씩 배치·파일 대기.
cd /d/Entertainments/DevEnvironment/autovideo || exit 1
PD="home_vocab/w21/poses_raw"; BD="assets/graphics/bg"
mkdir -p "$PD" "$BD"
REF="D:/Entertainments/DevEnvironment/autovideo/assets/characters/madam_jay_base_front.png"
CHAR="첨부한 기준 이미지의 캐릭터(마담제이: 갈색 번머리, 코랄색 조끼에 '선생님' 글자, 흰 치마, 흰 신발, 점 눈에 작은 미소, 굵은 검정 외곽선, 납작한 파스텔 미니멀 동화풍)와 완전히 동일한 디자인·비율·색을 그대로 유지하되 포즈만 바꿔 다시 그린다."
PSTYLE="머리끝부터 발끝까지 전신이 다 보이게 세로로 여유있게, 순백색(#ffffff) 배경, 그림자 없음, 글자·워터마크·말풍선 없음. 나노바나나(제미나이 이미지)로 직접 생성하고 Google Flow는 절대 쓰지 말 것."
BSTYLE="파스텔 색연필 동화풍, 굵고 부드러운 검정 외곽선, 밝고 따뜻한 톤. 화면 전체를 꽉 채운 하나의 연속된 장면(흰 여백·빈칸 절대 없음). 사람·캐릭터·동물 없이 빈 배경만. 화면 하단 1/3은 바닥(길)이 가로 왼쪽 끝부터 오른쪽 끝까지 평평하게 이어져 어디로나 걸을 수 있게 하고 큰 전경 사물로 좌우를 막지 말 것. 건물·소품·장식은 중단과 상단, 뒤쪽에 배치. 글자·간판 텍스트·상표·숫자·워터마크 절대 없음. 16:9 가로 와이드 구도. 나노바나나(제미나이 이미지)로 직접 생성, Google Flow 금지."

launch_pose(){ local key="$1"; shift; local desc="$*"
  printf '%s\n기준 이미지: %s (반드시 참고 이미지로 사용).\n포즈: %s\n%s\n결과 PNG 저장: D:/Entertainments/DevEnvironment/autovideo/%s/mj_w21_%s.png\n' \
    "$CHAR" "$REF" "$desc" "$PSTYLE" "$PD" "$key" > "$PD/prompt_$key.txt"
  nohup agy -p "$(cat "$PD/prompt_$key.txt")" --dangerously-skip-permissions > "$PD/log_$key.txt" 2>&1 &
}
launch_bg(){ local key="$1"; shift; local desc="$*"
  printf '서울 성수동의 배경 그림: %s\n%s\n결과 PNG 저장: D:/Entertainments/DevEnvironment/autovideo/%s/bg_w21_%s.png\n' \
    "$desc" "$BSTYLE" "$BD" "$key" > "$BD/prompt_w21_$key.txt"
  nohup agy -p "$(cat "$BD/prompt_w21_$key.txt")" --dangerously-skip-permissions > "$BD/log_w21_$key.txt" 2>&1 &
}
waitfiles(){ # $@ = full paths ; 최대 300초 대기
  for i in $(seq 1 60); do local ok=1; for f in "$@"; do [ -f "$f" ] || ok=0; done
    [ $ok -eq 1 ] && { echo "  batch ready"; return; }; sleep 5; done
  echo "  batch TIMEOUT (일부 미완)"; }

# ===== 포즈 목록 (key|desc) =====
POSES=(
"count_two|정면, 한 손을 가슴 높이로 들어 검지와 중지로 숫자 2를 펴 보이며 웃는 전신."
"count_fingers|정면, 한 손으로 다른 손의 손가락을 하나씩 꼽으며 세는 전신."
"explain|정면, 양손을 가슴 앞에서 살짝 벌려 차분히 설명하는 제스처의 전신."
"crouch_low|정면, 무릎을 살짝 굽히고 한 손을 무릎 아래 높이로 낮춰 '작은 키'를 나타내는 전신."
"touch_hair_short|정면, 한 손으로 귀 옆 짧은 머리를 매만지는 전신."
"admire|정면, 두 손을 가슴 앞에 살짝 모으고 눈을 반짝이며 감탄하는 전신."
"hand_heart|정면, 두 손을 머리 옆에서 손가락 하트 모양으로 만드는 전신."
"thumbs_up|정면, 한 손 엄지를 척 세우고 밝게 웃는 전신."
"slim_gesture|정면, 두 손으로 허리 양옆에 곡선을 그리듯 '날씬한 몸매'를 나타내는 전신."
"push_glasses|정면, 검지로 콧등의 둥근 안경을 살짝 밀어 올리는 전신(안경 착용)."
"hands_together|정면, 두 손을 가슴 앞에 공손히 모으고 부드럽게 웃는 전신."
"nod|정면, 고개를 살짝 끄덕이며(약간 숙임) 미소 짓는 전신."
"laugh|정면, 한 손을 입가에 대고 크게 즐겁게 웃는 전신."
"clap|정면, 두 손을 가슴 앞에서 마주쳐 손뼉 치는 전신."
"finger_lips|정면, 검지를 입술에 대고 '쉿' 조용히 하는 전신."
"cheer_arms|정면, 두 팔을 머리 위로 번쩍 들고 응원하듯 기뻐하는 전신."
"hop|정면, 두 발을 모아 살짝 뛰어오른(공중에 살짝 뜬) 밝은 전신."
"point_head|정면, 검지로 자기 관자놀이를 톡톡 가리키며 '똑똑함'을 나타내는 전신."
"connect_hands|정면, 두 손의 손가락을 앞에서 서로 맞물려 '연결(잇기)'을 나타내는 전신."
"wave|정면, 한 손을 어깨 높이로 들어 좌우로 흔들며 작별 인사하는 전신."
"look_up_fr|몸을 오른쪽으로 15도 튼 정면에서, 고개를 들어 위쪽을 올려다보는 전신."
"touch_hair_long_fr|몸을 오른쪽으로 15도 튼 정면에서, 한 손으로 긴 머리카락을 어깨 아래로 쓸어내리는 전신."
"explain_fr|몸을 오른쪽으로 15도 튼 정면에서, 오른손을 오른쪽으로 펴 설명하는 제스처의 전신."
)
# ===== 배경 목록 (batch1 4개 제외한 나머지 10) =====
BGS=(
"cafe_interior|카페 내부. 원목 테이블과 의자, 큰 창으로 드는 햇살, 벽의 식물과 선반, 따뜻한 조명."
"popup_front|팝업스토어 외관. 트렌디하고 미니멀한 파사드, 큰 유리창, 세련된 거리."
"popup_inside|팝업스토어 내부. 미니멀한 전시대와 스포트라이트 조명, 감각적인 디스플레이 공간."
"forest_path|서울숲 산책로. 큰 나무들이 이룬 초록 터널, 벤치, 나뭇잎 사이 햇살."
"forest_pond|서울숲 연못. 잔잔한 물과 갈대, 물가의 나무와 징검다리."
"brick_factory|붉은 벽돌 공장을 개조한 복합문화공간. 큰 아치형 창과 철제 구조, 빈티지한 벽돌 외벽."
"understand_ave|언더스탠드에비뉴. 알록달록한 컨테이너 건물들이 늘어선 골목, 계단과 데크."
"print_alley|레트로 인쇄골목. 좁고 정겨운 골목, 낡은 벽돌과 셔터, 빈티지한 분위기."
"flower_cafe|플라워 카페 앞. 꽃과 초록 화분이 가득한 입구, 파스텔 차양."
"rooftop|루프탑에서 본 성수동 노을 스카이라인. 붉은 벽돌 건물들과 먼 도시, 따뜻한 주황빛 하늘."
)

echo "### 먼저 진행 중인 배경 배치1(4) 완료 대기"
waitfiles "$BD/bg_w21_alley_entrance.png" "$BD/bg_w21_brick_street.png" "$BD/bg_w21_shoe_street.png" "$BD/bg_w21_cafe_terrace.png"

echo "### 배경 나머지 10개 (4개씩)"
i=0; batch=()
for e in "${BGS[@]}"; do k="${e%%|*}"; d="${e#*|}"; launch_bg "$k" "$d"; batch+=("$BD/bg_w21_$k.png"); echo "  bg: $k"
  i=$((i+1)); if [ $((i%4)) -eq 0 ]; then waitfiles "${batch[@]}"; batch=(); fi; done
[ ${#batch[@]} -gt 0 ] && waitfiles "${batch[@]}"

echo "### 포즈 23개 (4개씩)"
i=0; batch=()
for e in "${POSES[@]}"; do k="${e%%|*}"; d="${e#*|}"; launch_pose "$k" "$d"; batch+=("$PD/mj_w21_$k.png"); echo "  pose: $k"
  i=$((i+1)); if [ $((i%4)) -eq 0 ]; then waitfiles "${batch[@]}"; batch=(); fi; done
[ ${#batch[@]} -gt 0 ] && waitfiles "${batch[@]}"

echo "### 완료. 포즈 $(ls $PD/mj_w21_*.png 2>/dev/null|wc -l)개 / 배경 $(ls $BD/bg_w21_*.png 2>/dev/null|wc -l)개"
