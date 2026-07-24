#!/bin/bash
# W20 영어판 렌더 — 외부에서 죽어도 mp4 나올 때까지 자동 재시도(TTS 캐시 재사용으로 빠르게 따라잡음)
cd /d/Entertainments/DevEnvironment/autovideo
OUT="hangeul_birth_vowels/hangeul_w20_injun_np_en.mp4"
LOG="logs/render_w20_en.log"
: > "$LOG"
for attempt in $(seq 1 12); do
  if [ -f "$OUT" ]; then break; fi
  echo "=== RENDER ATTEMPT $attempt $(date) ===" >> "$LOG"
  SUB_LANGS=en WALK_STRIDE_SEC=1.08 EDGE_ACTIVE_VOICE=sunhi PYTHONUTF8=1 python compile_np.py KO-W20 hangeul_w20_injun review en >> "$LOG" 2>&1
  sleep 2
done
if [ -f "$OUT" ]; then
  echo "RENDER_COMPLETE $OUT $(ls -la "$OUT" | awk '{print $5}') bytes"
else
  echo "RENDER_FAILED after retries"
fi
