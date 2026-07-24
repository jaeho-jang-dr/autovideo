#!/bin/bash
# ★W14 앉기 씬 배경 재작업 — 사장님 원칙(C안): 캐릭터 크기 고정(앉기=서기의 60%), 배경을 사람에 맞춘다.
#   앉은 캐릭터 렌더 실측(1280x720): x[354,585] y[441,700], 폭231 높이259
#   ★eat_sit/study_book 등 컷아웃엔 '의자+책상 일부'가 이미 포함 → 배경엔 그 자리에 가구를 그리지 않는다.
#     배경의 가구(식탁·책상·카운터)는 캐릭터 오른쪽/뒤에 두고, 상판 높이를 y=583 선에 맞춘다.
#   ★agy 4개 병렬
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
OUT='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\bg'
REF='D:\Entertainments\DevEnvironment\autovideo\scratch\w14_sit_reference.png'
LOG="logs/gen_bg_w14_sitfit.log"
mkdir -p logs
: > "$LOG"

FIT="⚠️★가장 중요★ 참조 이미지 '${REF}' 를 반드시 보라. 초록 사각형 안의 '앉아 있는 여성'이 이 배경 위에 그대로 합성된다(크기·위치 고정, 폭231·높이259, 화면 1280x720 기준). 배경을 그 사람 크기에 정확히 맞춰라:
 (1) 사람이 앉을 자리(화면 왼쪽 중앙, x 350~590 / y 440~700)는 **완전히 비워라**. 그 자리에 의자·식탁·책상을 그리지 마라(캐릭터 그림에 의자와 책상 일부가 이미 포함되어 있다).
 (2) 배경에 그리는 가구(식탁·책상·카운터·테이블)는 **사람의 오른쪽(x 620 이상) 또는 뒤쪽**에 배치하고, 상판 높이를 **빨간 바닥선 y=700, 파란 상판선 y=583**에 맞춰 사람과 눈높이가 자연스럽게 이어지게 하라.
 (3) 원근·크기가 사람과 어긋나지 않게(사람 어깨높이가 상판보다 조금 위). 가구가 사람보다 지나치게 크거나 작으면 안 된다."

COMMON="넓은 가로 16:9(1280x720) 구도. 플랫 카툰 일러스트, 굵은 검정 외곽선, 부드러운 파스텔. ⚠️화면에 어떤 글자·숫자·상표·간판 텍스트도 절대 넣지 마라(표지판·시계 문자판·라벨은 빈칸). 사람은 배경에 실루엣으로 아주 적게. 화면 상단 왼쪽~중앙은 자막·글자가 올라가므로 비교적 단순하게."

declare -A P
P[bg_w14_kitchen]="제주 해변 숙소의 작은 주방·아침 식탁. 창밖에 에메랄드 바다. 아침 햇살. ${FIT} ${COMMON}"
P[bg_w14_kitchen2]="주방 카운터와 커피 코너. 커피포트와 컵, 과일 바구니, 아침 햇살, 창밖 바다. ${FIT} ${COMMON}"
P[bg_w14_cafe_fit]="해변 카페 내부. 창가 자리, 창밖으로 에메랄드 바다와 야자수, 따뜻한 나무 인테리어. ${FIT} ${COMMON}"
P[bg_w14_desk_fit]="공부방 책상 코너. 책꽂이와 스탠드, 창으로 들어오는 한낮의 밝은 빛, 창밖 바다. ${FIT} ${COMMON}"
P[bg_w14_beachtable_fit]="해변 야외 테라스 카페. 파라솔 아래, 앞은 흰 백사장과 에메랄드 바다, 비양도. ${FIT} ${COMMON}"
P[bg_w14_dinner]="해변 식당의 저녁. 따뜻한 조명, 창밖은 노을 지는 바다. ${FIT} ${COMMON}"
P[bg_w14_nightdesk_fit]="밤의 책상 코너. 스탠드 불빛, 창밖에 별과 어두운 바다, 아늑한 방. ${FIT} ${COMMON}"
P[bg_w14_bedroom]="해변 숙소 침실 아침. 침대와 이불, 협탁과 스탠드, 커튼 사이 아침 햇살, 창밖에 바다. ⚠️캐릭터(침대 가장자리에 앉아 기지개 켜는 사람)는 화면 왼쪽 중앙(x350~590, y440~700)에 합성되니 그 자리는 비우고, **침대는 사람의 오른쪽**에 두어 사람이 침대 가장자리에 걸터앉은 것처럼 보이게 하라. ${COMMON}"

echo "=== W14 앉기배경 재작업 $(date) ===" >> "$LOG"
MAX=4; i=0
for k in "${!P[@]}"; do
  rm -f "/d/Entertainments/DevEnvironment/autovideo/assets/graphics/bg/${k}.png"
  echo "[gen] $k" >> "$LOG"
  agy -p "${P[$k]} 결과 PNG를 '${OUT}\\${k}.png' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1 &
  i=$((i+1)); if (( i % MAX == 0 )); then wait; fi
done
wait
echo "=== done $(date) ===" >> "$LOG"
ls -la assets/graphics/bg/bg_w14_{kitchen,kitchen2,cafe_fit,desk_fit,beachtable_fit,dinner,nightdesk_fit,bedroom}.png 2>&1 >> "$LOG"
