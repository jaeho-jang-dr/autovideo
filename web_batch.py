# -*- coding: utf-8 -*-
"""전 게시영상·쇼츠 설명란에 drjayed.com 링크 일괄 추가(add_website_link.py 반복)."""
import subprocess, sys
# 게시(공개/일부공개)된 본편 3 + 쇼츠 8 (비공개 구버전 제외; DqJFWK0swds는 이미 완료)
IDS = [
    ("본편 세종",      "6lGedBJ5xx4"),
    ("본편 정주행",    "wJUAiZW5fW0"),
    ("본편 최면",      "JohmMBxizkg"),
    ("쇼츠 세종EN",    "FtBFZGTojfY"),
    ("쇼츠 세종KO",    "5YXdG4OIiMQ"),
    ("쇼츠 아이키KO",  "OAnDgIm3M_g"),
    ("쇼츠 아이키EN",  "y2kJBfPV1AY"),
    ("쇼츠 최면KO",    "qQscFq0nnAA"),
    ("쇼츠 최면EN",    "EiB8eNb1l7A"),
    ("쇼츠 정주행KO",  "9IlmG239m1M"),
    ("쇼츠 정주행EN",  "0xDd3tpR7R8"),
]
results = []
for name, vid in IDS:
    print(f"\n===== {name} {vid} =====", flush=True)
    try:
        r = subprocess.run([sys.executable, "add_website_link.py", vid], timeout=150)
        results.append((name, vid, r.returncode))
    except Exception as e:
        print(f"[에러] {vid}: {str(e)[:60]}", flush=True)
        results.append((name, vid, -1))
print("\n===== BATCH SUMMARY =====", flush=True)
for name, vid, rc in results:
    print(f"  {name} {vid}: {'OK' if rc == 0 else 'CHECK(rc=' + str(rc) + ')'}", flush=True)
print("BATCH_DONE", flush=True)
