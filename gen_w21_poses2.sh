#!/usr/bin/env bash
# W21 마담제이 포즈 전면 재생성 — 살색·싱글라인. 기준=W21/madam_front_base_frame1.png. 정면 위주 + 창의적 오브젝트 포즈. 4개씩 배치.
cd /d/Entertainments/DevEnvironment/autovideo || exit 1
PD="home_vocab/w21/poses2_raw"; mkdir -p "$PD"
REF="D:/Entertainments/DevEnvironment/autovideo/W21/madam_front_base_frame1.png"
CHAR="마담제이: 진갈색 탑번 쪽머리(양옆 잔머리 한 가닥씩), 점 두 개 눈·작은 코·작은 미소, 코랄/살구색 V넥 선생님 조끼(가슴 왼쪽 작은 펜주머니·니트 밑단·아주 작은 '선생님' 글자), 흰색 A라인 무릎길이 치마, 흰색 둥근 벙어리장갑 손, 흰색 운동화, 굵은 검정 외곽선, 큰 머리·작은 몸통."
LINE="★★★가장 중요: 팔과 다리는 반드시 '폭도 속채움도 전혀 없는 단 하나의 얇은 검정 선(single stroke line)'으로만 그린다. 팔·다리를 두 줄(튜브)이나 살(피부)로 채우지 마라. 손목 끝에만 작은 흰 벙어리장갑, 발끝에만 흰 운동화. 기준 이미지의 싱글라인 그대로."
SKIN="얼굴과 목의 피부는 반드시 '따뜻한 크림빛 살색'(순백색 금지), 볼에 아주 연한 발그레."
STYLE="머리끝~발끝 전신, 순백색(#ffffff) 배경, 그림자·바닥선·글자·워터마크 없음. 나노바나나(제미나이 이미지)로 직접 생성, Google Flow 금지."

launch(){ local key="$1"; shift; local desc="$*"
  printf '기준 이미지: %s (반드시 참고 — 특히 팔다리 싱글라인·살색 얼굴을 그대로).\n%s\n%s\n%s\n포즈: %s\n%s\n결과 PNG 저장: D:/Entertainments/DevEnvironment/autovideo/%s/mj_w21_%s.png\n' \
    "$REF" "$CHAR" "$LINE" "$SKIN" "$desc" "$STYLE" "$PD" "$key" > "$PD/prompt_$key.txt"
  nohup agy -p "$(cat "$PD/prompt_$key.txt")" --dangerously-skip-permissions > "$PD/log_$key.txt" 2>&1 &
}
waitfiles(){ for i in $(seq 1 70); do local ok=1; for f in "$@"; do [ -f "$f" ] || ok=0; done
  [ $ok -eq 1 ] && { echo "  batch ready"; return; }; sleep 5; done; echo "  batch TIMEOUT"; }

POSES=(
"smile_bright|정면을 바라보고 활짝 웃으며 양손을 자연스럽게 내린 전신."
"explain|정면에서 양손을 가슴 앞에 살짝 벌려 차분히 설명하는 전신."
"present_right|정면 자세에서 오른팔을 펴 손바닥을 위로 하여 오른쪽을 정중히 제시(얼굴은 정면 유지)."
"present_left|정면 자세에서 왼팔을 펴 손바닥을 위로 하여 왼쪽을 정중히 제시(얼굴은 정면 유지)."
"point_right|정면 자세에서 오른팔을 뻗어 검지로 오른쪽을 가리킴(얼굴은 정면 유지)."
"point_left|정면 자세에서 왼팔을 뻗어 검지로 왼쪽을 가리킴(얼굴은 정면 유지)."
"point_up|정면에서 한 손 검지로 위를 가리키며 위쪽을 올려다보는 전신."
"count_two|정면에서 한 손을 들어 검지와 중지로 숫자 2를 펴 보이며 웃는 전신."
"count_fingers|정면에서 한 손으로 다른 손 손가락을 하나씩 꼽으며 세는 전신."
"hand_heart|정면에서 두 손을 머리 옆에서 손가락 하트로 만드는 전신."
"thumbs_up|정면에서 한 손 엄지를 척 세우고 밝게 웃는 전신."
"admire|정면에서 두 손을 가슴 앞에 모으고 눈을 반짝이며 감탄하는 전신."
"slim_gesture|정면에서 두 손으로 허리 양옆 곡선을 그리듯 날씬한 몸매를 표현하는 전신."
"push_glasses|정면에서 검지로 콧등의 둥근 안경을 살짝 밀어 올리는 전신(안경 착용)."
"hands_together|정면에서 두 손을 가슴 앞에 공손히 모으고 부드럽게 웃는 전신."
"nod|정면에서 고개를 살짝 끄덕이며 미소 짓는 전신."
"laugh|정면에서 한 손을 입가에 대고 크게 즐겁게 웃는 전신."
"clap|정면에서 두 손을 가슴 앞에서 마주쳐 손뼉 치는 전신."
"finger_lips|정면에서 검지를 입술에 대고 쉿 하는 전신."
"cheer_arms|정면에서 두 팔을 머리 위로 번쩍 들고 응원하듯 기뻐하는 전신."
"point_head|정면에서 검지로 자기 관자놀이를 톡톡 가리키며 똑똑함을 나타내는 전신."
"connect_hands|정면에서 두 손의 손가락을 앞에서 서로 맞물려 연결을 나타내는 전신."
"crouch_low|정면에서 무릎을 살짝 굽히고 한 손을 무릎 아래로 낮춰 작은 키를 나타내는 전신."
"think|정면에서 한 손을 턱에 대고 고개를 살짝 갸웃하며 생각하는 전신."
"wave|정면에서 한 손을 어깨 높이로 들어 좌우로 흔들며 작별 인사하는 전신."
"microscope_bend|정면에서 허리를 앞으로 살짝 굽히고 한 손은 책상 위 현미경을 잡고 한 눈을 대어 관찰하는 전신(현미경 포함)."
"telescope_look|정면에서 한 손에 작은 망원경을 눈에 대고 먼 곳을 바라보는 전신(망원경 포함)."
"notebook_write|정면에서 한 손에 작은 노트를 들고 다른 손 펜으로 무언가 적으며 말하는 전신(노트·펜 포함)."
"sit_explain|의자에 앉아(간단한 의자 포함) 정면을 보며 한 손으로 설명하는 전신."
"hold_book|정면에서 두 손으로 펼친 책 한 권을 들고 설명하는 전신(책 포함)."
"magnifier_look|정면에서 한 손에 큰 돋보기를 들고 그 너머를 자세히 살피는 전신(돋보기 포함)."
)
echo "### 포즈 ${#POSES[@]}개 생성 (4개씩)"
i=0; batch=()
for e in "${POSES[@]}"; do k="${e%%|*}"; d="${e#*|}"; launch "$k" "$d"; batch+=("$PD/mj_w21_$k.png"); echo "  pose: $k"
  i=$((i+1)); if [ $((i%4)) -eq 0 ]; then waitfiles "${batch[@]}"; batch=(); fi; done
[ ${#batch[@]} -gt 0 ] && waitfiles "${batch[@]}"
echo "### 완료. 생성 $(ls $PD/mj_w21_*.png 2>/dev/null|wc -l)개"
