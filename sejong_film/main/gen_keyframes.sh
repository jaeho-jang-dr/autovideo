#!/bin/bash
# 48 키프레임 생성 — 누락분만 반복 패스(봇 트립으로 빠진 샷 자동 재시도) + 페이싱.
cd "D:/Entertainments/DevEnvironment/autovideo" || exit 1
TSV=sejong_film/main/kf_shots.tsv
OUT=sejong_film/main/keyframes
TMP=scratch/_kf_tmp.txt
mkdir -p "$OUT"
PACE=40          # 샷 사이 페이싱(초) — 봇 신호 완화(보수적)
COOLDOWN=240     # 패스 사이 쿨다운(초)
MAXPASS=8
INITIAL_WAIT=${INITIAL_WAIT:-240}   # 시작 전 봇 플래그 식히기

echo "시작 전 ${INITIAL_WAIT}s 쿨다운(봇 플래그 식힘)..."; sleep "$INITIAL_WAIT"

for pass in $(seq 1 $MAXPASS); do
  cnt=$(ls "$OUT"/*.png 2>/dev/null | wc -l)
  echo "===== PASS $pass 시작 (현재 $cnt/48) ====="
  [ "$cnt" -ge 48 ] && break
  did=0
  while IFS=$'\t' read -r key ref prompt; do
    [ -z "$key" ] && continue
    [ -f "$OUT/$key.png" ] && continue
    did=1
    rm -f assets/chrome_profile/SingletonLock 2>/dev/null
    echo "---- $key 생성 (pass $pass) ----"
    if [ "$ref" = "NONE" ]; then
      printf '%s: %s\n' "$key" "$prompt" > "$TMP"
      PYTHONIOENCODING=utf-8 python gen_assets_flow.py --prompts "$TMP" --outdir "$OUT" --no-transparent --yes --force 2>&1 | grep -E "\[OK\]|실패|비정상|REBOOT" | tail -2
    else
      printf '%s | %s | %s\n' "$key" "$ref" "$prompt" > "$TMP"
      PYTHONIOENCODING=utf-8 python gen_assets_flow.py --ref-jobs "$TMP" --outdir "$OUT" --no-transparent --yes --force 2>&1 | grep -E "\[OK\]|실패|비정상|REBOOT" | tail -2
    fi
    if [ -f "$OUT/$key.png" ]; then echo "OK_$key ($(ls $OUT/*.png 2>/dev/null|wc -l)/48)"; else echo "MISS_$key (다음 패스 재시도)"; fi
    sleep "$PACE"
  done < "$TSV"
  cnt=$(ls "$OUT"/*.png 2>/dev/null | wc -l)
  echo "===== PASS $pass 완료 ($cnt/48) ====="
  [ "$cnt" -ge 48 ] && break
  [ "$did" -eq 0 ] && break
  echo "(패스 사이 쿨다운 ${COOLDOWN}s — 봇 플래그 식힘)"; sleep "$COOLDOWN"
done
echo "남은 누락: $(for n in $(seq 1 48); do k=$(printf S%02d $n); [ -f "$OUT/$k.png" ] || printf '%s ' "$k"; done)"
echo "ALL_KEYFRAMES_DONE2"
