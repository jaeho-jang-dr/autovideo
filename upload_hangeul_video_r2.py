#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""upload_hangeul_video_r2.py — 한글교육 주차 스틱맨 영상(ko/en)을 R2(drjayed-media) docs/ 에 업로드.

웹(web/src/components/CurriculumView.astro)이 주차번호로
  https://pub-a8312324e7b445f8a1985f759cddeff7.r2.dev/docs/hangeul_w{N}_stickman_{ko,en}.mp4
를 동적 재생한다 → R2에 올리면 즉시 반영(웹 재배포 불필요).

사용: python upload_hangeul_video_r2.py 3
"""
import os
import sys

import boto3

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
BUCKET = "drjayed-media"
PUBLIC = "https://pub-a8312324e7b445f8a1985f759cddeff7.r2.dev"


def r2():
    env = {}
    for ln in open(os.path.join(ROOT, "..", "parkgolftour", ".env"), encoding="utf-8"):
        if ln.startswith("CF_R2_"):
            k, _, v = ln.strip().partition("=")
            env[k] = v
    return boto3.client("s3", endpoint_url=env["CF_R2_ENDPOINT"],
                        aws_access_key_id=env["CF_R2_ACCESS_KEY_ID"],
                        aws_secret_access_key=env["CF_R2_SECRET_ACCESS_KEY"], region_name="auto")


def main():
    wk = sys.argv[1] if len(sys.argv) > 1 else "3"
    s3 = r2()
    for lang in ("ko", "en"):
        f = os.path.join(ROOT, "hangeul_birth_vowels", f"hangeul_w{wk}_stickman_{lang}.mp4")
        if not os.path.exists(f):
            print(f"  MISS {f}")
            continue
        key = f"docs/hangeul_w{wk}_stickman_{lang}.mp4"
        s3.upload_file(f, BUCKET, key, ExtraArgs={"ContentType": "video/mp4"})
        print(f"  OK {os.path.getsize(f) // 1024 // 1024}MB -> {PUBLIC}/{key}")
    print("DONE")


if __name__ == "__main__":
    main()
