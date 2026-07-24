#!/bin/bash
# W20 최종: Azure TTS(선희 KO/Emma EN/DB선희) + 4K. KO편(ko자막)·EN편(en자막) 각각 재시도.
cd /d/Entertainments/DevEnvironment/autovideo
for LANG in ko en; do
  OUT="hangeul_birth_vowels/hangeul_w20_injun_np_${LANG}.mp4"
  LOG="logs/render_w20_azure_${LANG}.log"
  SUB="$LANG"
  rm -f "$OUT" "hangeul_birth_vowels/hangeul_w20_injun_np_${LANG}_silent.mp4"
  : > "$LOG"
  for attempt in $(seq 1 6); do
    if [ -f "$OUT" ]; then break; fi
    echo "=== AZURE4K $LANG ATTEMPT $attempt $(date) ===" >> "$LOG"
    SUB_LANGS="$SUB" TTS_ENGINE=azure EDGE_ACTIVE_VOICE=sunhi WALK_STRIDE_SEC=1.08 PYTHONUTF8=1 \
      python compile_np.py KO-W20 hangeul_w20_injun 4K "$LANG" >> "$LOG" 2>&1
    sleep 2
  done
  if [ -f "$OUT" ]; then echo "AZURE4K_${LANG}_DONE $(stat -c%s "$OUT") bytes"; else echo "AZURE4K_${LANG}_FAILED"; fi
done
echo "AZURE4K_ALL_DONE"
