#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Poll + download the 2-1(w2d1) NotebookLM artifacts already queued (ko/en notebooks)."""
import sys, os, time, asyncio
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
from notebooklm_tools.mcp.tools._utils import get_client
from notebooklm_tools.services import studio, downloads

NBS = {"ko": "a1c24ccf-6736-4029-b782-f68a1977f285",
       "en": "7fbca34c-fb0d-433f-821d-33ef194d9e86"}
TARGETS = {"audio", "slide_deck", "report"}
OUT = "scratch/nlm"
base = "w2d1"
client = get_client()

for lang, nb in NBS.items():
    deadline = time.time() + 1500
    comp = set()
    while time.time() < deadline:
        st = studio.get_studio_status(client, nb)
        arts = st["artifacts"] if isinstance(st, dict) else st.artifacts
        comp = {a.get("type") for a in arts if a.get("status") == "completed"}
        if TARGETS <= comp:
            print(f"[{lang}] all 3 completed", flush=True)
            break
        print(f"[{lang}] waiting... completed={sorted(comp)}", flush=True)
        time.sleep(25)
    sfx = "" if lang == "ko" else "_en"
    ap = f"{OUT}/dl_{base}_podcast{sfx}.m4a"
    sp = f"{OUT}/dl_{base}_slides{sfx}.pdf"
    rp = f"{OUT}/dl_{base}_notes{sfx}.md"
    try:
        asyncio.run(downloads.download_async(client, nb, "audio", ap)); print(f"[{lang}] podcast OK", flush=True)
    except Exception as e:
        print(f"[{lang}] podcast FAIL {e}", flush=True)
    try:
        asyncio.run(downloads.download_async(client, nb, "slide_deck", sp, slide_deck_format="pdf")); print(f"[{lang}] slides OK", flush=True)
    except Exception as e:
        print(f"[{lang}] slides FAIL {e}", flush=True)
    try:
        downloads.download_sync(client, nb, "report", rp); print(f"[{lang}] notes OK", flush=True)
    except Exception as e:
        print(f"[{lang}] notes FAIL {e}", flush=True)
print("RESUME_W2D1_DONE", flush=True)
