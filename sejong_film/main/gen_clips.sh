#!/bin/bash
# 48 키프레임 → Veo 모션 클립. 누락분만 반복 패스(레이트리밋 트립 자동 재시도) + 페이싱.
# 출력: sejong_main_kf/scene_<n>.mp4
cd "D:/Entertainments/DevEnvironment/autovideo" || exit 1
KF=sejong_film/main/keyframes
OUTD=sejong_main_kf
mkdir -p "$OUTD"
PACE=${PACE:-20}        # 클립 사이 페이싱(초) — 영상은 자체로 ~2분 걸려 자연 페이싱됨
COOLDOWN=${COOLDOWN:-240}
MAXPASS=${MAXPASS:-8}
INITIAL_WAIT=${INITIAL_WAIT:-0}

declare -A MOT
while IFS=$'\t' read -r key motion; do MOT[$key]="$motion"; done < sejong_film/main/kf_motions.tsv

exists_ok(){ [ -f "$1" ] && [ "$(stat -c%s "$1" 2>/dev/null)" -gt 10000 ]; }

# 프로필 크롬 좀비 종료 + 락 제거 (다음 클립이 프로필을 못 띄우는 문제 방지)
kill_profile_chrome(){
  powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | Where-Object { \$_.CommandLine -like '*assets\chrome_profile*' } | ForEach-Object { try { Stop-Process -Id \$_.ProcessId -Force -ErrorAction Stop } catch {} }" >/dev/null 2>&1
  sleep 2
  for lf in SingletonLock SingletonCookie SingletonSocket lockfile; do rm -f "assets/chrome_profile/$lf" 2>/dev/null; done
}

[ "$INITIAL_WAIT" -gt 0 ] && { echo "시작 전 ${INITIAL_WAIT}s 쿨다운..."; sleep "$INITIAL_WAIT"; }

for pass in $(seq 1 $MAXPASS); do
  cnt=$(ls "$OUTD"/*.mp4 2>/dev/null | wc -l)
  echo "===== CLIP PASS $pass 시작 ($cnt/48) ====="
  [ "$cnt" -ge 48 ] && break
  did=0
  for n in $(seq 1 48); do
    key=$(printf "S%02d" "$n")
    img="$KF/$key.png"; out="$OUTD/scene_$n.mp4"
    exists_ok "$out" && continue
    [ -f "$img" ] || { echo "NO_KF $key"; continue; }
    did=1
    kill_profile_chrome          # ★ 매 클립 전 좀비 크롬 종료(프로필 잠금 해제)
    echo "---- CLIP $n ($key) pass $pass ----"
    PYTHONIOENCODING=utf-8 python autoveo_flow.py --prompts sejong_main_kf_prompts.txt --scene "$n" \
      --upload "$img" --motion "${MOT[$key]}" 2>&1 | grep -E "다운로드 성공|\[OK\]|\[FAIL\]|REBOOT|비정상" | tail -2
    if exists_ok "$out"; then echo "OK_$n ($(ls $OUTD/*.mp4 2>/dev/null|wc -l)/48)"; else echo "MISS_$n (다음 패스 재시도)"; fi
    sleep "$PACE"
  done
  cnt=$(ls "$OUTD"/*.mp4 2>/dev/null | wc -l)
  echo "===== CLIP PASS $pass 완료 ($cnt/48) ====="
  [ "$cnt" -ge 48 ] && break
  [ "$did" -eq 0 ] && break
  echo "(패스 사이 쿨다운 ${COOLDOWN}s)"; sleep "$COOLDOWN"
done
echo "남은 누락: $(for n in $(seq 1 48); do f="$OUTD/scene_$n.mp4"; exists_ok "$f" || printf 'scene_%s ' "$n"; done)"
echo "ALL_CLIPS_DONE"
