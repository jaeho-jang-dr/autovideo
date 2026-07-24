#!/bin/bash
# W12 배경 22종 생성 (agy, 16:9, 인천공항→강남역 여정, 글자 없이, 왼쪽/중앙 열림)
cd /d/Entertainments/DevEnvironment/autovideo
export PATH="$PATH:/c/Users/antigravity/AppData/Local/agy/bin"
OUT='D:\Entertainments\DevEnvironment\autovideo\assets\graphics\bg'
LOG="logs/gen_bg_w12.log"
mkdir -p assets/graphics/bg logs
COMMON="넓은 가로 16:9 구도. 플랫 카툰 일러스트, 굵은 검정 외곽선, 부드러운 파스텔(하늘색·베이지·연회색·민트). ⚠️화면에 어떤 글자·숫자·상표·간판 텍스트도 절대 넣지 마라(모든 표지판·안내판·라벨은 빈칸으로, 픽토그램/화살표/색선만 허용). 중앙과 왼쪽은 캐릭터가 걸어다니며 상호작용하도록 넓게 비운다. 사람은 배경에 실루엣으로 적게."
declare -A P
# 1막 공항
P[bg_w12_arrival]="인천공항 입국장. 높은 천장, 유리벽, 수하물 카트와 여행 캐리어 몇 개, 바닥은 반질한 타일. 안내 표지판은 빈 화면(글자 없음). $COMMON"
P[bg_w12_hall]="공항 중앙홀. 거대한 유리 천장으로 햇빛, 에스컬레이터, 화분, 대기 의자. 천장에 매달린 안내판은 빈칸. $COMMON"
P[bg_w12_signboard]="공항 교통 안내판 앞. 큰 안내 기둥에 버스·지하철·택시 픽토그램(그림 아이콘만, 글자 절대 없음)과 화살표. 옆에 여행 캐리어. $COMMON"
# 2막 버스
P[bg_w12_busstop]="인천공항 공항버스(리무진) 정류장. 큰 파란 리무진 버스가 옆으로 서 있고 아래 짐칸이 열려 있다. 정류장 지붕과 벤치, 버스 번호판은 빈칸(숫자 없음). $COMMON"
# 3막 교통카드
P[bg_w12_ticket]="지하철역 교통카드 자동판매기. 큰 기계 화면(빈 화면), 카드 투입구, 동전 반환구. 옆에 안내 기둥. $COMMON"
P[bg_w12_charge]="교통카드 충전기 클로즈업. 기계 화면은 빈 회색, 카드를 올리는 납작한 단말기 패드, 지폐 투입구. 배경 흐릿한 역 통로. $COMMON"
P[bg_w12_counter]="역 안 작은 편의점 계산대. 나무 카운터 위 카드 단말기와 동전접시, 뒤 선반에 라벨 없는 상품들. $COMMON"
P[bg_w12_gate]="지하철 개찰구. 여러 개의 스피드게이트와 카드 태그 단말기(둥근 패드), 위에 화살표 픽토그램. $COMMON"
# 4막 공항철도
P[bg_w12_platform]="공항철도 승강장. 유리 스크린도어, 매끈한 바닥, 천장 조명, 대기선. 전광판은 빈 화면. $COMMON"
P[bg_w12_platform2]="지하철 승강장의 행선지 표시대 앞. 기둥에 매달린 전광판·방향 화살표(글자 숫자 절대 없음), 반대편 선로. $COMMON"
P[bg_w12_boarding]="열차 문이 열린 탑승 순간. 승강장에서 열차 안으로 이어지는 열린 출입문, 발밑 틈, 문 옆 손잡이 기둥. $COMMON"
P[bg_w12_train]="지하철 열차 내부. 긴 좌석, 천장에 손잡이(둥근 고리)가 줄지어 매달림, 창밖은 어두운 터널. 노선도는 빈 그림. $COMMON"
# 5막 서울역 환승
P[bg_w12_seoulstn]="서울역 지하철 도착 승강장. 넓고 밝은 승강장, 기둥, 벤치, 스크린도어. 표지판 빈칸. $COMMON"
P[bg_w12_transfer]="지하철 환승통로. 길게 이어진 복도, 천장에 방향 화살표 표지판(그림·화살표만, 글자 없음), 타일 벽. $COMMON"
P[bg_w12_transfer2]="환승 계단과 에스컬레이터. 위로 올라가는 계단, 옆에 에스컬레이터, 손잡이 난간, 벽 타일. $COMMON"
P[bg_w12_map]="지하철 노선도가 걸린 벽. 커다란 액자 안에 여러 색(초록·파랑·주황) 노선이 교차하는 선과 동그란 역 표시만 있고 글자·숫자는 절대 없음. $COMMON"
P[bg_w12_map2]="지하철 노선도 클로즈업. 초록색 순환선(둥근 고리 모양)이 크게 보이고 다른 색 선이 지나감. 역은 흰 동그라미. 글자·숫자 절대 없음. $COMMON"
P[bg_w12_sign_transfer]="환승 표지판이 이어지는 복도. 천장에 큰 화살표 표지판이 연속으로 매달려 방향을 가리킴(픽토그램·화살표만). $COMMON"
P[bg_w12_platform_line2]="2호선 지하철 승강장. 초록색 톤의 기둥과 띠, 스크린도어, 벤치. 전광판 빈 화면. $COMMON"
# 6막 강남
P[bg_w12_train2]="지하철 열차 내부, 창밖으로 서울 도심 빌딩이 지나감(지상 구간). 손잡이, 좌석, 밝은 낮 햇살. $COMMON"
P[bg_w12_gangnam_exit]="강남역 지하 출구 계단. 위로 올라가는 넓은 계단, 난간, 계단 위쪽에서 들어오는 밝은 햇빛, 출구 표지판은 빈칸(번호 없음). $COMMON"
P[bg_w12_gangnam_street]="서울 강남대로 지상 거리. 유리 고층빌딩들, 넓은 인도, 가로수, 버스 정류장 표지와 벤치, 지나가는 버스. 간판은 전부 빈칸(글자 없음). $COMMON"
P[bg_w12_gangnam_night]="서울 강남대로 밤 풍경. 고층빌딩 창문 불빛, 가로등, 은은한 네온 빛(글자 없는 색 판), 인도와 가로수. 따뜻한 야경 파스텔. $COMMON"

echo "=== W12 bg gen start $(date) ===" >> "$LOG"
for k in "${!P[@]}"; do
  if [ -f "assets/graphics/bg/${k}.png" ]; then echo "[skip] $k (있음)" >> "$LOG"; continue; fi
  echo "[gen] $k" >> "$LOG"
  agy -p "${P[$k]} 결과 PNG를 '${OUT}\\${k}.png' 로 저장하라." --dangerously-skip-permissions < /dev/null >> "$LOG" 2>&1
  sleep 4
done
echo "=== W12 bg gen done $(date) ===" >> "$LOG"
ls -1 assets/graphics/bg/bg_w12_*.png 2>/dev/null | wc -l >> "$LOG"
