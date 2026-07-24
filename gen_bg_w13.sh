#!/bin/bash
# W13 배경 20종 (agy) — 성산일출봉(제주) 길 찾기 여정. 2씬당 1개.
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
OUT='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\bg'
LOG="logs/gen_bg_w13.log"
mkdir -p assets/graphics/bg logs

COMMON="넓은 가로 16:9 구도. 플랫 카툰 일러스트, 굵은 검정 외곽선, 부드러운 파스텔(청록 바다·연둣빛 초원·베이지 현무암·하늘색). ⚠️화면에 어떤 글자·숫자·상표·간판 텍스트도 절대 넣지 마라(모든 표지판·간판은 빈칸, 픽토그램/화살표만 허용). 중앙과 왼쪽은 캐릭터가 걸어다닐 수 있게 넓게 비운다. 사람은 배경에 실루엣으로 적게."
JEJU="제주도 특유의 요소를 살려라: 검은 현무암 돌담, 야자수와 억새, 푸른 바다, 멀리 보이는 성산일출봉(바다에서 솟은 거대한 초록 분화구)."

declare -A P
P[bg_w13_coast]="제주 성산 해안도로. 오른쪽 멀리 바다에서 솟은 거대한 초록 분화구(성산일출봉)가 보이고, 왼쪽은 넓은 인도와 현무암 돌담. 청록 바다와 흰 파도. $JEJU $COMMON"
P[bg_w13_fork]="제주 시골 갈림길. 길이 두 갈래로 나뉘고 가운데에 나무 표지판 기둥(판은 완전히 빈칸, 화살표만). 주변에 현무암 돌담과 들풀. $JEJU $COMMON"
P[bg_w13_village]="제주 마을길. 낮은 검은 현무암 돌담이 길을 따라 이어지고, 담 너머 낮은 기와집. 길바닥은 흙길. $JEJU $COMMON"
P[bg_w13_village2]="제주 마을길 다른 각도. 담장 옆에 감귤나무(주황 열매), 돌하르방 석상 하나(글자 없음), 낮은 돌담. $JEJU $COMMON"
P[bg_w13_village3]="제주 마을 좁은 골목. 양옆으로 현무암 돌담이 높게 서 있고 끝에 바다가 보임. $JEJU $COMMON"
P[bg_w13_street]="곧게 뻗은 시골 아스팔트 도로. 끝없이 앞으로 이어지고 소실점에 초록 분화구(일출봉)가 보임. 양옆은 들판. $COMMON"
P[bg_w13_crossing]="제주 시골 마을의 횡단보도. 흰 줄무늬 횡단보도가 길을 가로지르고 옆에 작은 신호등 기둥. 뒤에 돌담과 바다. $COMMON"
P[bg_w13_corner]="현무암 돌담이 직각으로 꺾이는 길 모퉁이. 오른쪽으로 길이 돌아감. 담 위에 들꽃. $COMMON"
P[bg_w13_junction]="시골 사거리. 길이 네 갈래로 갈리고 가운데에 신호등과 화살표 표지판(글자 없음). 주변에 낮은 건물. $COMMON"
P[bg_w13_store]="제주 시골 작은 편의점 앞. 유리문과 차양, 간판은 완전히 빈 판(글자 없음), 앞에 음료 냉장고와 벤치. $COMMON"
P[bg_w13_field]="유채꽃이 노랗게 핀 넓은 들판길. 길이 들판 사이로 나 있고 멀리 초록 분화구(일출봉)와 바다. $COMMON"
P[bg_w13_field2]="억새가 은빛으로 물결치는 오름 능선길. 완만한 초록 언덕과 하늘. $COMMON"
P[bg_w13_ticket]="성산일출봉 매표소 입구. 작은 목조 매표 부스와 안내 기둥(전부 빈 판, 글자 없음), 뒤로 거대한 분화구 절벽이 솟아 있음. $COMMON"
P[bg_w13_entrance]="성산일출봉 입구 광장. 넓은 돌바닥, 벤치, 위로 이어지는 등산로 시작점, 뒤로 웅장한 분화구 절벽. $COMMON"
P[bg_w13_stairs]="성산일출봉 등산 계단. 아래에서 위로 이어지는 나무·돌 계단과 난간, 양옆은 초록 절벽 풀밭. $COMMON"
P[bg_w13_stairs2]="등산 계단 중턱. 계단 옆으로 탁 트인 바다와 성산 마을이 내려다보임. 난간과 전망 지점. $COMMON"
P[bg_w13_summit]="성산일출봉 정상. 눈앞에 거대한 사발 모양 초록 분화구(움푹 팬 화구)가 펼쳐지고 가장자리를 따라 산책로. $COMMON"
P[bg_w13_summit2]="성산일출봉 정상 전망대. 난간 너머로 푸른 바다와 성산 마을, 멀리 우도가 보임. 하늘엔 갈매기. $COMMON"
P[bg_w13_downhill]="성산일출봉 하산길. 아래로 이어지는 계단과 다리, 바다와 해안 마을이 보임. $COMMON"
P[bg_w13_sunrise]="성산일출봉 앞바다 일출. 수평선에서 붉은 해가 솟아오르고 바다가 주황·분홍으로 물듦, 실루엣으로 보이는 분화구. 따뜻한 파스텔 일출 톤. $COMMON"

echo "=== W13 bg gen start $(date) ===" >> "$LOG"
for k in "${!P[@]}"; do
  if [ -f "assets/graphics/bg/${k}.png" ]; then echo "[skip] $k" >> "$LOG"; continue; fi
  echo "[gen] $k" >> "$LOG"
  agy -p "${P[$k]} 결과 PNG를 '${OUT}\\${k}.png' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1
  sleep 4
done
echo "=== done $(date) ===" >> "$LOG"
ls -1 assets/graphics/bg/bg_w13_*.png 2>/dev/null | wc -l >> "$LOG"
