#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
download_en_podcasts.py — 영어 팟캐스트(W1·W2) 생성 완료를 폴링 → 다운로드 → R2 업로드.

★ 핵심(교훈): NotebookLM 클라이언트의 download_audio 는 **async(코루틴)** 다.
  반드시 asyncio.run(...) 으로 await 해야 한다. 안 그러면 0바이트 무동작.

실행: python download_en_podcasts.py
완료 후 web/public/audio/podcasts/hangeul_week_{1,2}_podcast_en.m4a + R2(drjayed-media) 에 올라간다.
"""
import os
import sys
import time
import asyncio
import inspect

sys.path.insert(0, r"C:/Users/antigravity/.notebooklm/bin")
import nlm_common as N
import boto3

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
NB = "cc6092e5-3322-44e8-b65e-dc0e85c2e3ed"
JOBS = [(1, "fb575a24-63cc-49aa-8971-1f5859d1bacf"),
        (2, "dc3173d8-e056-4b1b-aa4a-d124f247550d")]
# web/public 에 두면 >25MB라 CF Pages 배포 실패 → 오프로드 백업 + R2 에만 저장
OUTDIR = os.path.join(ROOT, "scratch", "web_media_offloaded", "audio", "podcasts")
c = N.make_client("default")


def maybe_await(v):
    return asyncio.run(v) if inspect.iscoroutine(v) else v


def statuses():
    st = maybe_await(c.get_studio_status(NB))
    arts = st if isinstance(st, list) else st.get("artifacts", st)
    out = {}
    for a in (arts if isinstance(arts, list) else []):
        out[a.get("id") or a.get("artifact_id")] = a.get("status")
    return out


def r2_client():
    env = {}
    for ln in open(os.path.join(ROOT, "..", "parkgolftour", ".env"), encoding="utf-8"):
        if ln.startswith("CF_R2_"):
            k, _, v = ln.strip().partition("=")
            env[k] = v
    return boto3.client("s3", endpoint_url=env["CF_R2_ENDPOINT"], aws_access_key_id=env["CF_R2_ACCESS_KEY_ID"],
                        aws_secret_access_key=env["CF_R2_SECRET_ACCESS_KEY"], region_name="auto"), env


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    # 1) 폴링 (최대 ~35분)
    for _ in range(70):
        s = statuses()
        states = {wk: s.get(aid, "?") for wk, aid in JOBS}
        print("status:", states, flush=True)
        if all(states[wk] == "completed" for wk, _ in JOBS):
            break
        time.sleep(30)
    else:
        print("TIMEOUT: not all completed"); return

    # 2) 다운로드 (async!) + 3) R2 업로드
    s3, env = r2_client()
    for wk, aid in JOBS:
        out = os.path.join(OUTDIR, f"hangeul_week_{wk}_podcast_en.m4a")
        if os.path.exists(out):
            os.remove(out)
        asyncio.run(c.download_audio(NB, out, artifact_id=aid))
        sz = os.path.getsize(out) if os.path.exists(out) else 0
        if sz < 10000:
            print(f"FAIL wk{wk}: {sz} bytes"); continue
        key = f"audio/podcasts/hangeul_week_{wk}_podcast_en.m4a"
        s3.upload_file(out, "drjayed-media", key, ExtraArgs={"ContentType": "audio/mp4"})
        print(f"OK wk{wk}: {sz//1024//1024}MB -> local + R2:{key}", flush=True)
    print("DONE")


if __name__ == "__main__":
    main()
