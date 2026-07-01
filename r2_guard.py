#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2_guard.py — R2(drjayed-media) 용량 안전장치.

규칙(사용자 2026-06-29): R2 사용량이 위험 한도의 90% 이상이면 업로드를 멈추고 알린다.
- R2 무료 한도 = 10 GB(스토리지). 위험 한도 = 10 GB. 90% = 9 GB.
- 업로드 직전 `assert_r2_ok()` 호출 → 9GB 이상이면 RuntimeError로 중단(호출부가 잡아 사용자에게 보고).

사용:
  python r2_guard.py            # 현재 사용량 출력
  from r2_guard import r2_usage, assert_r2_ok
"""
import sys

LIMIT_GB = 10.0          # R2 free-tier storage limit
DANGER_FRAC = 0.90       # 90% danger line → stop uploads
BUCKET = "drjayed-media"


def r2_usage(bucket=BUCKET):
    """(used_gb, pct, n_objects) 반환."""
    from make_daily_media import r2
    s3 = r2()
    total = 0
    n = 0
    tok = None
    while True:
        kw = {"Bucket": bucket, "MaxKeys": 1000}
        if tok:
            kw["ContinuationToken"] = tok
        resp = s3.list_objects_v2(**kw)
        for o in resp.get("Contents", []):
            total += o["Size"]
            n += 1
        if resp.get("IsTruncated"):
            tok = resp["NextContinuationToken"]
        else:
            break
    gb = total / 1e9
    return gb, gb / LIMIT_GB * 100.0, n


def assert_r2_ok(bucket=BUCKET, extra_gb=0.0):
    """90% 이상이면 RuntimeError. extra_gb=업로드 예정 용량(예측 포함)."""
    gb, pct, n = r2_usage(bucket)
    proj = gb + extra_gb
    if proj >= LIMIT_GB * DANGER_FRAC:
        raise RuntimeError(
            f"[R2-STOP] 사용량 {gb:.2f}GB(+예정 {extra_gb:.2f}) = {proj:.2f}GB ≥ "
            f"위험 90% 한도({LIMIT_GB*DANGER_FRAC:.1f}GB). 업로드 중단 — 사용자에게 보고 필요.")
    return gb, pct, n


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    gb, pct, n = r2_usage()
    line = LIMIT_GB * DANGER_FRAC
    status = "OK" if gb < line else "STOP-UPLOADS (≥90%)"
    print(f"R2 {BUCKET}: {n} objects, {gb:.3f} GB / {LIMIT_GB} GB ({pct:.1f}%) — 90% line={line:.1f}GB → {status}")
