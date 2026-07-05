# -*- coding: utf-8 -*-
"""남은 쇼츠 3개를 일부공개로 업로드+게시 (검증된 2단계: upload_hyp -> resume_draft).
- 각 쇼츠: (1) upload_hyp.py 로 파일+메타데이터 업로드(초안 생성/게시 시도)
           (2) resume_draft.py 로 초안 재개 -> 일부공개 -> 저장(게시), 실제 shorts ID 캡처
- 결과는 scratch/shorts_upload_results.json 에 기록.
사용: python finish_shorts_upload.py
주의: 브라우저 프로필(assets/chrome_profile) 공유 -> 반드시 순차 실행. 동시에 다른 크롬 실행 금지."""
import subprocess, sys, os, re, json, time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
TAG = "내가 만든 내 동영상"
RESULTS = "scratch/shorts_upload_results.json"

def free_profile():
    """assets/chrome_profile 점유 크롬 종료 (프로필 잠금 방지)."""
    ps = ("$p=Get-CimInstance Win32_Process -Filter \"Name='chrome.exe'\" -EA SilentlyContinue | "
          "Where-Object { $_.CommandLine -match 'chrome_profile' }; "
          "if($p){$p|ForEach-Object{Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue}}; "
          "$l='assets\\chrome_profile\\SingletonLock'; if(Test-Path $l){Remove-Item $l -Force -EA SilentlyContinue}")
    try: subprocess.run(["powershell", "-NoProfile", "-Command", ps], timeout=30)
    except Exception as e: print("free_profile 경고:", str(e)[:60], flush=True)
    time.sleep(2)

JOBS = [
    {"key": "binge_en",
     "video": "binge_watching/binge_short_veo_en.mp4",
     "desc":  "binge_watching/desc_short_en.txt",
     "title": "What Binge-Watching Does to Your Body 👀 #Shorts",
     "part":  "What Binge-Watching Does to Your Body"},
    {"key": "hyp_ko",
     "video": "hypnosis_science/hyp_short_veo_ko.mp4",
     "desc":  "hypnosis_science/desc_short_ko.txt",
     "title": "최면, 마술일까 과학일까? 🧠 #Shorts",
     "part":  "최면, 마술일까 과학일까"},
    {"key": "hyp_en",
     "video": "hypnosis_science/hyp_short_veo_en.mp4",
     "desc":  "hypnosis_science/desc_short_en.txt",
     "title": "Hypnosis: Magic or Science? 🧠 #Shorts",
     "part":  "Hypnosis: Magic or Science"},
]

def run(cmd, logpath, timeout=300):
    with open(logpath, "w", encoding="utf-8") as f:
        p = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, timeout=timeout)
    txt = open(logpath, encoding="utf-8").read()
    return p.returncode, txt

def vid_from(txt):
    m = re.search(r"VIDEO_ID=([A-Za-z0-9_-]{9,})", txt or "")
    return m.group(1) if m else ""

results = []
for j in JOBS:
    key = j["key"]; print(f"\n=== [{key}] {j['title']} ===", flush=True)
    free_profile()
    r = {"key": key, "title": j["title"], "video": j["video"], "vid": "", "published": False, "note": ""}
    # (1) 업로드
    up_log = f"scratch/up_{key}.log"
    try:
        rc, txt = run([PY, "upload_hyp.py", j["video"], j["desc"], j["title"], TAG, "none", "unlisted"], up_log, timeout=600)
        print(f"  upload rc={rc}", flush=True)
    except Exception as e:
        r["note"] += f"upload예외:{str(e)[:60]}; "; print("  upload 예외", str(e)[:80], flush=True)
    time.sleep(4)
    # (2) 초안 재개 -> 게시 (실제 ID 캡처)
    rs_log = f"scratch/resume_{key}.log"
    try:
        rc, txt = run([PY, "resume_draft.py", j["part"], "unlisted"], rs_log, timeout=300)
        v = vid_from(txt)
        if v: r["vid"] = v
        if "게시확인" in txt or "저장" in txt: r["published"] = True
        print(f"  resume rc={rc} vid={r['vid']} published={r['published']}", flush=True)
    except Exception as e:
        r["note"] += f"resume예외:{str(e)[:60]}; "; print("  resume 예외", str(e)[:80], flush=True)
    results.append(r)
    json.dump(results, open(RESULTS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    time.sleep(3)

print("\n=== 결과 요약 ===", flush=True)
for r in results:
    print(f" {r['key']}: vid={r['vid'] or '미확인'} published={r['published']} {r['note']}", flush=True)
print("RESULTS_JSON:", RESULTS, flush=True)
print("DRIVER_DONE", flush=True)
