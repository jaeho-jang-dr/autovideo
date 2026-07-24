# -*- coding: utf-8 -*-
"""yt_localize.py — 영상 하나의 다국어 현지화를 한 번에 오케스트레이션.
검증된 스크립트(set_video_lang.py / tx_sub.py / tx_meta.py)를 순서대로 호출 + 매번 크롬 종료(K).
사용: python yt_localize.py <VID> <manifest.json> [--subs-only|--meta-only]
manifest.json 예:
{
  "video_lang": "영어",                # (선택) 본영상 언어 설정 (set_video_lang)
  "langs": [
    {"row":"한국어 (동영상 언어)", "srt":"a.ko.srt", "add":false, "do":["sub"]},
    {"row":"일본어", "srt":"ja.srt", "title":"ja_title.txt", "desc":"ja_desc.txt", "add":true}
  ]
}
원칙: 언어당 자막·제목설명 중 하나라도 넣어 언어 persist. 2패스 재실행으로 빈 것만 채움.
"""
import sys, os, json, subprocess, time
VID = sys.argv[1]
MAN = json.load(open(sys.argv[2], encoding="utf-8"))
ONLY = sys.argv[3] if len(sys.argv) > 3 else ""

def K():
    subprocess.run(["powershell", "-c", "Get-Process chrome -EA SilentlyContinue | Stop-Process -Force -EA SilentlyContinue"],
                   capture_output=True)
    time.sleep(4)

def run(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=200)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return f"[timeout/err] {e}"

results = []
if MAN.get("video_lang") and ONLY != "--meta-only" and ONLY != "--subs-only":
    K(); run(["python", "set_video_lang.py", VID, MAN["video_lang"]]); print(f"[본언어] {MAN['video_lang']} 설정", flush=True)

for L in MAN["langs"]:
    row = L["row"]; do = L.get("do", ["sub", "meta"])
    sub_ok = meta_ok = None
    if "sub" in do and L.get("srt") and ONLY != "--meta-only":
        K()
        cmd = ["python", "tx_sub.py", VID, row, L["srt"]] + (["add"] if L.get("add") else [])
        out = run(cmd)
        sub_ok = ("publish=True" in out) or ("게시=OK" in out)
        print(f"[자막] {row}: {'OK' if sub_ok else 'FAIL'}", flush=True)
    if "meta" in do and L.get("title") and L.get("desc") and ONLY != "--subs-only":
        K()
        title = open(L["title"], encoding="utf-8").read().strip()
        out = run(["python", "tx_meta.py", VID, row, title, L["desc"]])
        meta_ok = "게시=OK" in out
        print(f"[제목설명] {row}: {'OK' if meta_ok else 'FAIL'}", flush=True)
    results.append((row, sub_ok, meta_ok))

def mark(x): return "✓" if x is True else ("-" if x is None else "✗")
print("\n=== 요약 (VID=" + VID + ") ===", flush=True)
allok = True
for row, s, m in results:
    if s is False or m is False: allok = False
    print(f"  {row:22} 자막={mark(s)}  제목설명={mark(m)}", flush=True)
print("=== " + ("전부 성공" if allok else "일부 실패 → 스크린샷으로 빈칸 확인 후 그 언어만 재실행") + " ===", flush=True)
