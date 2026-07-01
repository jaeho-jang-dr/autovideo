"""Poll NotebookLM studio status for the sejong notebook until all artifacts
reach a terminal state (completed/failed), then exit. One-shot waiter."""
import json, subprocess, sys, time

NB = "sejong"
deadline = time.time() + 30 * 60  # 30 min cap
prev = None

def status():
    out = subprocess.run("nlm studio status %s --json" % NB, shell=True,
                         capture_output=True, text=True, timeout=90,
                         encoding="utf-8", errors="replace")
    return json.loads(out.stdout)

while time.time() < deadline:
    try:
        d = status()
    except Exception:
        time.sleep(40); continue
    summ = {}
    for a in d:
        k = "%s:%s" % (a["type"], a["status"])
        summ[k] = summ.get(k, 0) + 1
    key = tuple(sorted(summ.items()))
    if key != prev:
        print("STATUS " + "  ".join("%s x%d" % (k, v) for k, v in sorted(summ.items())), flush=True)
        prev = key
    pending = [a for a in d if a["status"] in ("in_progress", "pending", "unknown")]
    if not pending:
        print("ALL_TERMINAL " + " | ".join("%s=%s=%s" % (a["type"], a["status"], a["id"]) for a in d), flush=True)
        sys.exit(0)
    time.sleep(40)

print("POLL_TIMEOUT after 30min", flush=True)
sys.exit(2)
