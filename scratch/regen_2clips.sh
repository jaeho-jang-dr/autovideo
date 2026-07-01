#!/bin/bash
cd "D:/Entertainments/DevEnvironment/autovideo" || exit 1
KF=sejong_film/main/keyframes
OUTD=sejong_main_kf
declare -A MOT
while IFS=$'\t' read -r key motion; do MOT[$key]="$motion"; done < sejong_film/main/kf_motions.tsv
exists_ok(){ [ -f "$1" ] && [ "$(stat -c%s "$1" 2>/dev/null)" -gt 50000 ]; }
kill_profile_chrome(){
  powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | Where-Object { \$_.CommandLine -like '*assets\chrome_profile*' } | ForEach-Object { try { Stop-Process -Id \$_.ProcessId -Force -ErrorAction Stop } catch {} }" >/dev/null 2>&1
  sleep 2
  for lf in SingletonLock SingletonCookie SingletonSocket lockfile; do rm -f "assets/chrome_profile/$lf" 2>/dev/null; done
}
for pass in 1 2 3 4 5; do
  did=0
  for n in 2 22; do
    key=$(printf "S%02d" "$n"); img="$KF/$key.png"; out="$OUTD/scene_$n.mp4"
    exists_ok "$out" && continue
    did=1
    kill_profile_chrome
    echo "---- REGEN CLIP $n ($key) pass $pass ----"
    timeout 330 env PYTHONIOENCODING=utf-8 python autoveo_flow.py --prompts sejong_main_kf_prompts.txt --scene "$n" \
      --upload "$img" --motion "${MOT[$key]}" --force 2>&1 | grep -E "다운로드 성공|\[OK\]|\[FAIL\]|REBOOT|비정상|수요가 많" | tail -3
    rc=${PIPESTATUS[0]}
    [ "$rc" = "124" ] && echo "(TIMEOUT 330s — 다음 패스 재시도)"
    kill_profile_chrome
    if exists_ok "$out"; then echo "OK_$n"; else echo "MISS_$n"; fi
    sleep 8
  done
  if exists_ok "$OUTD/scene_2.mp4" && exists_ok "$OUTD/scene_22.mp4"; then echo "BOTH_DONE"; break; fi
  [ "$did" -eq 0 ] && break
  echo "(pass 사이 쿨다운 150s)"; sleep 150
done
echo "RESULT scene_2=$(exists_ok "$OUTD/scene_2.mp4" && echo OK || echo MISS) scene_22=$(exists_ok "$OUTD/scene_22.mp4" && echo OK || echo MISS)"
echo "REGEN_DONE"
