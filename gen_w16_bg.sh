#!/bin/bash
# W16 남이섬 배경 19종 — ★W15(gen_w15_bg.sh) 규격 그대로: 꽉 찬 장면 + 왼쪽아래만 큰사물 비움 + 굵은 외곽선.
#   (이전 실수: "왼쪽 1/3 비워라" → agy가 흰색으로 비워 배경이 잘려 보였음. 재발 금지.)
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
OUT='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\bg'
LOG=logs/gen_w16_bg.log; mkdir -p assets/graphics/bg logs; : > $LOG

COMMON="가로 16:9 (1280x720). 플랫 카툰 일러스트, 굵은 검정 외곽선, 부드러운 파스텔. 아름답고 충실하게 그려라(화면 전체를 배경으로 꽉 채운다). ⚠️화면 왼쪽~중앙 아래쪽은 캐릭터가 서므로 큰 사물 없이 비교적 비워둔다(단, 하늘·바닥·원경은 그대로 이어서 채운다. 흰색으로 비우지 마라). ⚠️⚠️그림 안에 글자·숫자·표지판 텍스트·간판을 단 하나도 넣지 마라. 사람은 배경에 아주 작은 실루엣으로만."

declare -A P
P[bg_w16_dock]="남이섬 나루터 선착장. 잔잔한 북한강, 나무 데크 잔교, 강 건너 나무숲, 원경에 작은 페리. $COMMON"
P[bg_w16_dock_sunset]="노을 지는 남이섬 나루터. 주황·분홍빛으로 물든 저녁 하늘과 강, 나무 데크와 페리 실루엣 원경, 서정적 분위기. $COMMON"
P[bg_w16_metasequoia]="남이섬 메타세쿼이아 가로수길. 곧게 뻗은 키 큰 메타세쿼이아 두 줄이 이루는 초록 터널, 흙길, 맑은 하늘. $COMMON"
P[bg_w16_ginkgo]="남이섬 은행나무 가로수길. 노랗게 물든 은행나무 두 줄의 노란 터널, 바닥에 은행잎, 맑은 하늘. $COMMON"
P[bg_w16_cherry_lane]="남이섬 봄 벚꽃길. 분홍 벚꽃이 만개한 벚나무 가로수길, 흩날리는 꽃잎, 연분홍빛 봄 하늘. $COMMON"
P[bg_w16_pine_forest]="남이섬 잣나무 숲길. 곧게 뻗은 키 큰 침엽수 사이로 난 산책로, 초록 그늘, 평화로운 숲. $COMMON"
P[bg_w16_bike_path]="남이섬 자전거 도로. 나무들 사이로 완만하게 뻗은 포장 자전거길, 옆으로 잔디와 나무, 넓은 하늘. $COMMON"
P[bg_w16_lawn]="남이섬 넓은 초록 잔디밭. 파란 하늘과 뭉게구름, 뒤로 나무숲, 소풍하기 좋은 탁 트인 잔디. $COMMON"
P[bg_w16_riverside]="북한강 강변 산책로. 잔잔한 강물, 갈대와 물풀, 강 건너 완만한 산과 나무, 맑은 하늘. $COMMON"
P[bg_w16_fishing_pier]="남이섬 강가 낚시터. 잔잔한 강 위로 뻗은 나무 데크 잔교, 갈대와 물풀, 강 건너 산 원경. $COMMON"
P[bg_w16_animal_zone]="남이섬 동물 방사장. 나무 울타리로 둘러싸인 넓은 잔디 구역, 뒤로 나무숲, 목가적이고 평화로운 분위기. $COMMON"
P[bg_w16_art_plaza]="남이섬 예술 광장. 야외 조각과 화단, 나무 벤치가 있는 넓고 정돈된 광장, 뒤로 나무와 갤러리 건물, 파란 하늘. $COMMON"
P[bg_w16_campsite]="남이섬 캠핑장. 넓은 잔디밭에 알록달록한 삼각 텐트 몇 개, 뒤로 나무숲, 낮의 맑은 하늘. $COMMON"
P[bg_w16_bench_rest]="남이섬 강변 산책로 쉼터. 큰 나무 그늘 아래 놓인 나무 벤치, 옆으로 잔잔한 강과 산책로, 여유로운 분위기. $COMMON"
P[bg_w16_autumn_tunnel]="남이섬 가을 단풍 나무 터널. 노랑·주황·빨강으로 물든 단풍나무가 아치를 이룬 길, 낙엽이 깔린 길, 따뜻한 가을빛. $COMMON"
P[bg_w16_winter_lane]="남이섬 겨울 눈길. 하얀 눈이 소복이 덮인 가로수와 길, 파란 겨울 하늘, 차분하고 낭만적인 설경. $COMMON"
P[bg_w16_zipwire]="남이섬 짚와이어 풍경. 높은 출발탑에서 강 위로 길게 뻗은 와이어 줄, 아래로 강과 초록 섬, 넓고 시원한 하늘. $COMMON"
P[bg_w16_home_living]="아늑한 거실 실내. 편안한 소파와 낮은 탁자, 러그, 창문과 화분, 따뜻한 파스텔 톤의 포근한 거실(화면을 실내로 꽉 채운다). $COMMON"
P[bg_w16_kitchen]="아늑한 부엌 실내. 조리대와 가스레인지, 상부장, 작은 창문, 밝고 깔끔한 파스텔 톤 부엌(화면을 실내로 꽉 채운다). $COMMON"

echo "=== W16 배경(재작성) $(date) ===" >> $LOG
MAX=4; i=0
for k in "${!P[@]}"; do
  echo "[gen] $k" >> $LOG
  agy -p "${P[$k]} 결과 PNG를 '${OUT}\\${k}.png' 로 저장하라." --dangerously-skip-permissions < /dev/null >> $LOG 2>&1 &
  i=$((i+1)); if (( i % MAX == 0 )); then wait; fi
done
wait
echo "=== 결과 ===" >> $LOG; ls -1 assets/graphics/bg/bg_w16_*.png 2>/dev/null | wc -l >> $LOG
echo "ALL_BG_DONE $(date)" >> $LOG
