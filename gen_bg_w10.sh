#!/bin/bash
# W10 배경 4종 생성 (agy, 16:9, 광안리+객체, 글자 없이, 중앙 열림)
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
OUT='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\bg'
LOG="logs/gen_bg_w10.log"
mkdir -p assets/graphics/bg logs
COMMON="넓은 가로 16:9 구도. 플랫 카툰 일러스트, 굵은 검정 외곽선, 부드러운 파스텔(남색·베이지·하늘색). ⚠️화면에 어떤 글자·숫자·상표·간판 텍스트도 절대 넣지 마라(모든 간판·라벨은 빈칸). 중앙과 왼쪽은 캐릭터가 걸어다니며 상호작용하도록 넓게 비운다."
declare -A P
P[bg_w10_beach]="부산 광안리 해변 전경. 뒤에 광안대교(길게 이어진 현수교)와 파란 바다·하늘, 야자수, 나무 데크와 모래사장, 작은 벤치. $COMMON"
P[bg_w10_shop]="부산 광안리 해변가 작은 상점 진열대 장면. 뒤에 광안대교와 바다. 오른쪽에 알록달록한 상품(과자봉지·음료병·기념품·조개)이 놓인 나무 선반과 진열대, 파라솔. $COMMON"
P[bg_w10_counter]="부산 광안리 상점의 계산대(나무 카운터) 장면. 카운터 위에 카드 단말기·계산기·작은 바구니·동전접시. 창밖으로 광안대교와 바다. $COMMON"
P[bg_w10_sale]="부산 광안리 상점의 세일 코너. 빨간 세일 태그와 가격표 모양(숫자·글자 없는 빈 태그), 할인 상품이 쌓인 진열대, 풍선 장식. 뒤에 광안대교. $COMMON"
echo "=== bg gen start $(date) ===" >> "$LOG"
for k in bg_w10_beach bg_w10_shop bg_w10_counter bg_w10_sale; do
  echo "[gen] $k" >> "$LOG"
  agy -p "${P[$k]} 결과 PNG를 '${OUT}\\${k}.png' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1
  sleep 5
done
echo "=== bg gen done $(date) ===" >> "$LOG"
ls -1 assets/graphics/bg/bg_w10_*.png >> "$LOG"
