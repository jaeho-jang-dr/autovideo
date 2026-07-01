#!/bin/bash
cd "D:/Entertainments/DevEnvironment/autovideo" || exit 1
TSV=sejong_film/main/kf_shots.tsv
OUT=sejong_film/main/keyframes
TMP=scratch/_kf_one.txt
TARGETS="S28 S39 S40"
kill_profile_chrome(){
  powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" | Where-Object { \$_.CommandLine -like '*assets\chrome_profile*' } | ForEach-Object { try { Stop-Process -Id \$_.ProcessId -Force -ErrorAction Stop } catch {} }" >/dev/null 2>&1
  sleep 2
  for lf in SingletonLock SingletonCookie SingletonSocket lockfile; do rm -f "assets/chrome_profile/$lf" 2>/dev/null; done
}
get_prompt(){ grep -P "^$1\t" "$TSV" | head -1 | cut -f3; }
fresh(){ # 새로 생성됐는지(백업과 다른 크기/존재) — 단순히 mtime 최근 확인 대신 마킹 파일 사용
  [ -f "$OUT/$1.png" ]; }
for pass in 1 2 3 4; do
  did=0
  for key in $TARGETS; do
    # 이번 런에서 이미 새로 만들었으면 스킵
    [ -f "scratch/_kf_done_$key" ] && continue
    did=1
    prompt=$(get_prompt "$key")
    kill_profile_chrome
    echo "---- KF $key (pass $pass) ----"
    printf '%s: %s\n' "$key" "$prompt" > "$TMP"
    before=$(stat -c%s "$OUT/$key.png" 2>/dev/null || echo 0)
    timeout 200 env PYTHONIOENCODING=utf-8 python gen_assets_flow.py --prompts "$TMP" --outdir "$OUT" --no-transparent --yes --force 2>&1 | grep -E "\[OK\]|실패|비정상|REBOOT|수요가 많|다운로드 성공" | tail -3
    rc=${PIPESTATUS[0]}
    [ "$rc" = "124" ] && echo "(TIMEOUT 200s)"
    kill_profile_chrome
    after=$(stat -c%s "$OUT/$key.png" 2>/dev/null || echo 0)
    if [ "$after" -gt 10000 ] && [ "$after" != "$before" ]; then echo "OK_$key"; touch "scratch/_kf_done_$key"; else echo "MISS_$key"; fi
    sleep 8
  done
  done_all=1; for key in $TARGETS; do [ -f "scratch/_kf_done_$key" ] || done_all=0; done
  [ "$done_all" = "1" ] && { echo "ALL_KF_DONE"; break; }
  [ "$did" -eq 0 ] && break
  echo "(pass 쿨다운 120s)"; sleep 120
done
echo "RESULT: $(for k in $TARGETS; do [ -f scratch/_kf_done_$k ] && echo -n "$k=OK " || echo -n "$k=MISS "; done)"
echo "KF_REGEN_DONE"
