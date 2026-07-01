cd "D:/Entertainments/DevEnvironment/autovideo"
: > scratch/nlm/backfill_trigger.log
for base in w1d2 w1d3 w1d4 w1d5 w1d7; do
  for lang in ko en; do
    LANGNAME=$([ "$lang" = ko ] && echo Korean || echo English)
    SRC="scratch/nlm/src_${base}_${lang}.txt"
    PROMPT="Use notebooklm-mcp. 1) notebook_create name 'drjayed ${base} ${lang}'. 2) Read the local file ${SRC} and source_add its full text (type text, title '${base} ${lang}'). 3) studio_create audio (${LANGNAME}), slide_deck (${LANGNAME}), report (${LANGNAME}). Print ONE final line exactly: TRIG ${base} ${lang} notebook=<id> audio=<id> slides=<id> report=<id>"
    echo "$PROMPT" | gemini -m gemini-2.5-flash --yolo 2>/dev/null | grep -E "^TRIG " | tail -1 >> scratch/nlm/backfill_trigger.log
    echo "done ${base} ${lang}"
  done
done
echo "BACKFILL_TRIGGER_DONE" >> scratch/nlm/backfill_trigger.log
