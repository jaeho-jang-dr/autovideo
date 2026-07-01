#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Place downloaded W1 backfill NotebookLM artifacts: slides->web docs, notes md->pdf, podcast->R2."""
import os
import sys
import glob
import shutil
sys.path.insert(0, "D:/Entertainments/DevEnvironment/autovideo")
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
import make_daily_media as m
from r2_guard import assert_r2_ok

STG = "D:/Entertainments/DevEnvironment/autovideo/scratch/nlm"
DOCS = "D:/Entertainments/DevEnvironment/autovideo/web/public/docs"
s3 = m.r2()
B = "drjayed-media"

bases = ["w1d2", "w1d3", "w1d4", "w1d5", "w1d7"]
placed = []
for base in bases:
    for sfx in ("", "_en"):
        sp = f"{STG}/dl_{base}_slides{sfx}.pdf"
        rp = f"{STG}/dl_{base}_notes{sfx}.md"
        ap = f"{STG}/dl_{base}_podcast{sfx}.m4a"
        row = f"{base}{sfx}:"
        # slides
        if os.path.exists(sp):
            shutil.copyfile(sp, f"{DOCS}/hangeul_{base}_slides{sfx}.pdf")
            row += " slides✓"
        else:
            row += " slides✗"
        # notes md -> pdf
        if os.path.exists(rp):
            md = open(rp, encoding="utf-8").read()
            m.make_pdf(m.md_to_html(md), f"{DOCS}/hangeul_{base}_guide{sfx}.pdf")
            row += " notes✓"
        else:
            row += " notes✗"
        # podcast -> R2 (guard)
        if os.path.exists(ap):
            try:
                assert_r2_ok(extra_gb=0.04)
                s3.upload_file(ap, B, f"audio/podcasts/hangeul_{base}_podcast{sfx}.m4a",
                               ExtraArgs={"ContentType": "audio/mp4"})
                row += " podcast✓"
            except Exception as e:
                row += f" podcast✗({str(e)[:40]})"
        else:
            row += " podcast✗"
        placed.append(row)
print("PLACEMENT:")
for r in placed:
    print("  " + r)
