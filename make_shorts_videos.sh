#!/bin/bash
# 정주행 쇼츠 세로 비디오 3개 생성 (이미지 업로드 방식 = 이미지생성 단계 스킵, 안정적)
# 전제: shorts_src/scene_0.png, scene_2.png, scene_20.png 준비됨
# 실행: bash make_shorts_videos.sh
cd "D:/Entertainments/DevEnvironment/autovideo"

# 이미지 존재 확인
missing=""
for n in 0 2 20; do
  [ -f "shorts_src/scene_${n}.png" ] || [ -f "shorts_src/scene_${n}.jpg" ] || missing="$missing $n"
done
if [ -n "$missing" ]; then
  echo "[중단] 이미지 없음: shorts_src/scene_{$missing}.png — 먼저 3장 저장하세요."; exit 1
fi

for n in 0 2 20; do
  IMG="shorts_src/scene_${n}.png"; [ -f "$IMG" ] || IMG="shorts_src/scene_${n}.jpg"
  echo "===== 씬 ${n} 세로 비디오 생성 (업로드: $IMG) ====="
  # 프로필 크롬/좀비 정리 (프로필만)
  powershell -NoProfile -Command "@(Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" -ErrorAction SilentlyContinue | Where-Object { \$_.CommandLine -like '*assets\chrome_profile*' }) | ForEach-Object { try { Stop-Process -Id \$_.ProcessId -Force } catch {} }; @(Get-CimInstance Win32_Process -Filter \"Name='node.exe'\" -ErrorAction SilentlyContinue | Where-Object { \$_.CommandLine -like '*playwright*' }) | ForEach-Object { try { Stop-Process -Id \$_.ProcessId -Force } catch {} }; Start-Sleep 4; Get-ChildItem 'assets\chrome_profile' -Filter 'Singleton*' -Force -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue" >/dev/null 2>&1
  # 업로드 방식 비디오 생성 (timeout 340초 캡, 무한루프 방지)
  timeout 340 env PYTHONIOENCODING=utf-8 python autoveo_flow.py --prompts shorts_src_prompts.txt --scene ${n} --upload "$IMG" --aspect 9:16 --force > "scratch/veo_short_${n}.log" 2>&1
  if [ -f "shorts_src/scene_${n}.mp4" ]; then
    echo "  ✓ 완료: shorts_src/scene_${n}.mp4"
  else
    echo "  ✗ 실패 (로그: scratch/veo_short_${n}.log 확인)"
  fi
  sleep 5
done
echo "===== 전체 결과 ====="
for n in 0 2 20; do
  [ -f "shorts_src/scene_${n}.mp4" ] && echo "  scene_${n}.mp4 OK" || echo "  scene_${n}.mp4 없음"
done
echo "SHORTS_VIDEOS_DONE"
