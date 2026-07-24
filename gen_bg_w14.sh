#!/bin/bash
# W14 배경 23종 — 협재해수욕장(제주) 하루 일과. ★2씬당 1개, 시간 흐름을 빛으로.
# ★agy 4개 병렬
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
OUT='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\bg'
LOG="logs/gen_bg_w14.log"
mkdir -p assets/graphics/bg logs

COMMON="넓은 가로 16:9 구도. 플랫 카툰 일러스트, 굵은 검정 외곽선, 부드러운 파스텔. ⚠️화면에 어떤 글자·숫자·상표·간판 텍스트도 절대 넣지 마라(모든 표지판·시계 문자판·라벨은 빈칸). 중앙과 왼쪽은 캐릭터가 서거나 앉을 수 있게 넓게 비운다. 사람은 배경에 실루엣으로 아주 적게."
HJ="제주 협재해수욕장 특징을 살려라: 에메랄드빛 얕은 바다, 흰 백사장, 앞바다에 작은 섬(비양도), 야자수."

declare -A P
# 1막 새벽·아침
P[bg_w14_dawn]="협재 해변의 여명. 보랏빛·분홍빛 새벽 하늘, 잔잔한 에메랄드 바다에 비친 빛, 실루엣의 비양도와 야자수. $COMMON"
P[bg_w14_bedroom]="해변 숙소 침실 아침. 침대와 이불, 협탁과 스탠드, 커튼 사이로 들어오는 아침 햇살, 창밖에 바다가 살짝 보임. $COMMON"
P[bg_w14_bedside]="침대 옆에서 본 방. 침대 가장자리, 슬리퍼, 옷걸이, 바닥의 햇빛 조각. $COMMON"
P[bg_w14_window]="숙소 창가. 활짝 열린 창문 너머로 에메랄드 바다와 비양도, 야자수, 눈부신 아침 햇살. $HJ $COMMON"
# 2막 아침 준비
P[bg_w14_bath]="밝은 아침 욕실. 세면대와 거울, 수건, 칫솔컵, 창으로 들어오는 빛. $COMMON"
P[bg_w14_room]="숙소 방. 옷걸이에 걸린 옷, 열린 여행가방, 의자, 창밖 바다. $COMMON"
P[bg_w14_kitchen]="작은 주방과 아침 식탁. 식탁과 의자, 빵·과일·컵이 놓인 접시, 창밖 바다. $COMMON"
P[bg_w14_kitchen2]="주방 카운터 클로즈업. 커피포트와 컵, 과일 바구니, 아침 햇살. $COMMON"
P[bg_w14_door]="숙소 현관. 열린 문 밖으로 이어지는 해변 오솔길과 야자수, 밝은 아침. $COMMON"
# 3막 낮 카페·책상
P[bg_w14_cafe]="해변 카페 내부. 나무 책상과 의자, 창가 자리, 책과 노트북을 놓을 수 있는 넓은 책상, 창밖으로 에메랄드 바다. $COMMON"
P[bg_w14_cafe2]="카페 창가 책상 클로즈업. 나무 책상, 의자, 스탠드, 화분, 창밖 바다와 야자수. $COMMON"
P[bg_w14_desk]="공부용 책상 정면. 넓은 책상과 의자, 책꽂이, 창으로 들어오는 한낮의 밝은 빛. $COMMON"
P[bg_w14_beach_cafe]="해변 야외 테라스 카페. 파라솔 아래 테이블과 의자, 점심 접시, 앞은 흰 백사장과 에메랄드 바다. $HJ $COMMON"
# 4막 오후 해변
P[bg_w14_beach]="한낮 협재 백사장. 파라솔과 비치체어, 흰 모래, 에메랄드 얕은 바다, 비양도. $HJ $COMMON"
P[bg_w14_beach_walk]="해변 산책로. 야자수가 늘어선 모래길, 오른쪽에 바다, 오후의 긴 그림자. $HJ $COMMON"
P[bg_w14_sea]="에메랄드빛 얕은 바다. 무릎 깊이의 맑은 물, 잔물결, 가까이 보이는 비양도, 눈부신 햇살. $HJ $COMMON"
P[bg_w14_sea2]="바다에서 본 해변. 백사장과 야자수, 파라솔들이 멀리 보이고 앞은 맑은 물. $COMMON"
P[bg_w14_sunset_beach]="늦은 오후 해변. 주황빛으로 물들기 시작한 하늘, 길어진 그림자, 잔잔한 바다. $COMMON"
# 5막 저녁
P[bg_w14_dinner]="해변 식당의 저녁 식탁. 테이블과 의자, 접시와 컵, 따뜻한 조명, 창밖은 노을. $COMMON"
P[bg_w14_terrace]="숙소 테라스. 나무 의자와 작은 탁자, 난간 너머로 노을 지는 바다와 비양도. $COMMON"
P[bg_w14_sunset]="협재 노을. 수평선으로 지는 붉은 해, 주황·분홍으로 물든 바다와 하늘, 비양도 실루엣, 야자수 실루엣. $COMMON"
# 6막 밤
P[bg_w14_bath_night]="밤 욕실. 따뜻한 노란 조명, 세면대와 거울, 수건, 창밖은 어두운 밤. $COMMON"
P[bg_w14_bed_night]="밤 침실. 스탠드 불빛, 침대와 이불, 협탁 위 책과 노트, 창밖에 별과 어두운 바다. $COMMON"
P[bg_w14_night_sky]="협재 밤바다. 별이 가득한 밤하늘, 달빛이 비친 잔잔한 바다, 비양도 실루엣, 야자수. $COMMON"

echo "=== W14 bg gen start $(date) ===" >> "$LOG"
MAX=4
i=0
for k in "${!P[@]}"; do
  [ -f "assets/graphics/bg/${k}.png" ] && { echo "[skip] $k" >> "$LOG"; continue; }
  echo "[gen] $k" >> "$LOG"
  agy -p "${P[$k]} 결과 PNG를 '${OUT}\\${k}.png' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1 &
  i=$((i+1))
  if (( i % MAX == 0 )); then wait; fi     # ★4개 병렬
done
wait
echo "=== done $(date) ===" >> "$LOG"
ls -1 assets/graphics/bg/bg_w14_*.png 2>/dev/null | wc -l >> "$LOG"
