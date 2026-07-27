#!/usr/bin/env bash
# W22 클립 소스 13개: 배경 스틸 6 + 지은(봄 원피스) 동작 7. agy 나노바나나, 기준이미지와 100% 동일(비틀림 없이).
cd /d/Entertainments/DevEnvironment/autovideo || exit 1
BD="W22/bg"; CD="W22/clips"; mkdir -p "$BD" "$CD"
FRONT="D:/Entertainments/DevEnvironment/autovideo/W22/jieun_spring_front.png"
SIDE="D:/Entertainments/DevEnvironment/autovideo/W22/jieun_spring_side_right.png"
CHAR="지은(봄 원피스): 길고 부드러운 웨이브의 연한 갈색 긴 머리, 점 두 개 눈·작은 코·작은 미소, 하늘색(라이트블루) 민소매 원피스 위에 연분홍 카디건, 흰색 운동화, 크림색 피부, 굵고 부드러운 검정 외곽선의 납작한 카툰."
STRICT="★★★절대 규칙: 기준 이미지의 지은과 머리 모양·색, 얼굴, 옷(원피스+카디건), 색, 신발, 몸 비율을 100% 똑같이 유지한다. 캐릭터를 비틀거나 변형·재해석하지 말고, 오직 포즈/방향만 바꾼다. 머리끝~발끝 전신, 순백색(#ffffff) 배경, 그림자·바닥선·글자·워터마크 없음. 나노바나나(제미나이 이미지)로 직접 생성, Google Flow 금지."
BSTYLE="파스텔 색연필 동화풍, 굵고 부드러운 검정 외곽선, 밝고 따뜻한 톤, 화면 전체를 꽉 채운 하나의 장면(빈칸·흰여백 없음), 사람·캐릭터 없이 빈 배경만, 하단은 바닥/난간이 가로로 이어짐, 글자·간판·상표·숫자·워터마크 절대 없음, 16:9 가로 와이드. 나노바나나로 직접 생성, Google Flow 금지."

launch_char(){ local key="$1"; local ref="$2"; shift 2; local desc="$*"
  printf '기준 이미지: %s (반드시 참고 이미지로 사용).\n%s\n%s\n포즈/방향: %s\n결과 PNG 저장: D:/Entertainments/DevEnvironment/autovideo/%s/jieun_%s.png\n' \
    "$ref" "$CHAR" "$STRICT" "$desc" "$CD" "$key" > "$CD/prompt_$key.txt"
  nohup agy -p "$(cat "$CD/prompt_$key.txt")" --dangerously-skip-permissions > "$CD/log_$key.txt" 2>&1 &
}
launch_bg(){ local key="$1"; shift; local desc="$*"
  printf '높은 하늘 전망대의 배경 그림: %s\n%s\n결과 PNG 저장: D:/Entertainments/DevEnvironment/autovideo/%s/bg_w22_%s.png\n' \
    "$desc" "$BSTYLE" "$BD" "$key" > "$BD/prompt_$key.txt"
  nohup agy -p "$(cat "$BD/prompt_$key.txt")" --dangerously-skip-permissions > "$BD/log_$key.txt" 2>&1 &
}
waitfiles(){ for i in $(seq 1 80); do local ok=1; for f in "$@"; do [ -f "$f" ] || ok=0; done
  [ $ok -eq 1 ] && { echo "  batch ready"; return; }; sleep 5; done; echo "  batch TIMEOUT"; }

# ===== 배경 6 (정지 스틸 = 동영상이 멈춘 프레임) =====
BGS=(
"elevator_up|유리 전망 엘리베이터가 하늘 높이 올라가 멈춘 순간의 밝은 실내. 유리벽 너머로 저 아래 도시와 흰 구름이 보이는 밝은 낮."
"sky_window|전망대의 거대한 파노라마 유리창. 창밖으로 흰 구름이 걸린 파란 낮 하늘과 저 멀리 펼쳐진 도시 전경. 실내엔 낮은 난간."
"deck_interior|전망대 실내 라운지. 원목 벤치와 화분, 둥근 조명, 큰 유리창으로 드는 부드러운 햇살. 차분하고 아늑함."
"sunset_city|전망대 유리창 밖 노을 절정. 하늘이 주황·분홍·보라로 물들고 먼 도시에 불빛이 하나둘 켜지기 시작."
"glass_floor|전망대 유리 바닥. 발아래로 까마득한 도시의 반짝이는 밤 야경이 내려다보임. 짜릿한 고소감."
"night_stars|밤 전망대. 별이 총총한 짙푸른 밤하늘과 저 멀리 반짝이는 도시 불빛, 따뜻한 실내 조명."
)
# ===== 지은 동작 7 (front/side 가이드 기준) =====
# key ref desc
echo "### 배경 6 (4개씩)"
i=0; batch=()
for e in "${BGS[@]}"; do k="${e%%|*}"; d="${e#*|}"; launch_bg "$k" "$d"; batch+=("$BD/bg_w22_$k.png"); echo "  bg:$k"
  i=$((i+1)); [ $((i%4)) -eq 0 ] && { waitfiles "${batch[@]}"; batch=(); }; done
[ ${#batch[@]} -gt 0 ] && waitfiles "${batch[@]}"

echo "### 지은 동작 7 (4개씩)"
launch_char walk_side   "$SIDE"  "오른쪽 측면으로, 오른발을 앞으로 내디딘 자연스러운 걷기 스트라이드 순간. 팔은 걷는 리듬으로 스윙."
launch_char look_out    "$SIDE"  "오른쪽 측면으로 창가에 서서, 한 손을 유리에 살짝 대고 먼 밖을 바라보는 자세."
launch_char point_far   "$FRONT" "정면에서 몸을 살짝 오른쪽으로 틀고 오른팔을 뻗어 저 먼 곳을 손가락으로 가리키는 자세('저기 가 봤어요' 느낌)."
launch_char dream_gaze  "$FRONT" "정면에서 한 손을 턱 근처에 살짝 대고 고개를 들어 위/먼 곳을 올려다보며 꿈꾸듯 미소 짓는 자세."
waitfiles "$CD/jieun_walk_side.png" "$CD/jieun_look_out.png" "$CD/jieun_point_far.png" "$CD/jieun_dream_gaze.png"
launch_char open_arms   "$FRONT" "정면에서 두 팔을 옆으로 활짝 벌려 눈앞의 전경에 감탄하는 밝은 자세."
launch_char count_trips "$FRONT" "정면에서 한 손으로 다른 손의 손가락을 하나씩 꼽으며 횟수를 세는 자세."
launch_char wave        "$FRONT" "정면에서 한 손을 어깨 높이로 들어 좌우로 흔들며 밝게 인사하는 자세."
waitfiles "$CD/jieun_open_arms.png" "$CD/jieun_count_trips.png" "$CD/jieun_wave.png"
echo "### 완료. 배경 $(ls $BD/bg_w22_*.png 2>/dev/null|wc -l)/6 · 동작 $(ls $CD/jieun_*.png 2>/dev/null|wc -l)/7"
