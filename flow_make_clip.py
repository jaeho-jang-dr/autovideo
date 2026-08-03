# -*- coding: utf-8 -*-
"""★W23 캐릭터 동영상 1개 생성 — 사장님 절차를 그대로 고정한 스크립트 (2026-07-27).

두 번째부터 딴 길로 새는 이유 = 좌표를 매번 새로 찍었기 때문. 그래서 **성공한 순서를 여기 박아둔다.**
좌표는 하드코딩하지 않고 **매 단계 화면 덤프에서 찾아** 누른다(창 크기 달라져도 같게 동작).

사장님 확정 절차 (이대로만):
 1. 리셋 — 크롬 전부 kill → flow_driver 새로 기동 → 새 프로젝트(새 세션)
 2. 우상단 '+' 미디어 추가 → 이미지 업로드(파일 주입)
 3. 30초 대기 — 이미지 타일이 뜬다
 4. ★타일 본체를 클릭/더블클릭하면 **나노 바나나(이미지 편집기)로 빠진다 — 절대 금지.**
    타일에 hover → **우상단 점 세 개(더 생성하기)** → **'프롬프트에 추가'**
 5. 동영상 메뉴를 누르면 이미 9:16 · 1개 · Veo 3.1 Lite · 8s 로 되어 있다(확인만)
 6. 프롬프트 붙여넣기 → 우측 화살표(만들기) 실행
 7. 90초 대기 → 왼편에 두 번째 타일(동영상) 생성
 8. 그 타일 클릭 → 우상단 아래화살표(다운로드) → 저장 → 컷랑에 전달

사용:
  python flow_make_clip.py <키>            예) python flow_make_clip.py windmill_up
  python flow_make_clip.py <키> --no-reset  (이미 드라이버가 떠 있을 때)
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
CMD = "debug/cmd"
LIVE = "debug/_live.json"
DL = "debug/downloads"
CLIPS = "W23/clips"
LOG = "scratch/flow_make_clip.log"
_n = [0]


def log(m):
    print(m, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(m + "\n")


def cmd(line, wait=5):
    """명령을 던지고 **드라이버가 <n>.done 을 쓸 때까지만** 기다린다.

    ★예전엔 wait 초를 무조건 sleep 했다 — 드라이버가 5초에 끝내도 25초를 버리는 구조였다.
      이제 wait 는 '고정 대기'가 아니라 **상한(timeout)** 이다. 실제로 끝나면 즉시 다음 단계로 간다.
    """
    _n[0] += 1
    n = _n[0]
    done = f"{CMD}/{n}.done"
    # --no-reset 로 이어 붙일 때 지난 회차의 .done 이 남아 있으면 즉시 통과해버린다 → 먼저 지운다
    if os.path.exists(done):
        os.remove(done)
    with open(f"{CMD}/{n}.txt", "w", encoding="utf-8") as f:
        f.write(line)
    t0 = time.time()
    while time.time() - t0 < wait:
        if os.path.exists(done):
            time.sleep(0.2)          # 드라이버의 후처리(shot/dump) 마무리 여유
            return True
        time.sleep(0.2)
    return False


def dump():
    try:
        return json.load(open(LIVE, encoding="utf-8"))[0]
    except Exception:
        return {"url": "", "els": []}


def shot(wait=4):
    cmd("shot", wait)
    return dump()


def vidstatus_done():
    """드라이버가 남긴 vidstatus 판정을 읽는다.

    ★Flow는 완성 클립을 <video> 없이 **포스터 이미지 타일**로만 보여주는 경우가 있다.
      그때 dump 에서 VIDEO 태그를 찾으면 영원히 못 찾는다(2026-07-27 실측 실패).
      드라이버의 vidstatus(play_circle + 포스터 판정)를 정답으로 쓴다.
    """
    try:
        lines = open("debug/_drv.log", encoding="utf-8", errors="ignore").read().splitlines()
    except Exception:
        return False
    for ln in reversed(lines[-60:]):
        if "vidstatus:" in ln:
            return "DONE" in ln
    return False


def find(pred):
    for e in dump().get("els", []):
        if pred(e):
            return e
    return None


def by_text(sub, role=None, ymin=None):
    def p(e):
        t = (e.get("text") or "")
        if sub not in t:
            return False
        if role and e.get("role") != role:
            return False
        if ymin is not None and e.get("y", 0) < ymin:
            return False
        return True
    return find(p)


def reset_and_start():
    log("[1] 리셋 — 크롬 전부 kill")
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
                    "Where-Object { $_.CommandLine -match 'flow_driver' } | "
                    "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"],
                   capture_output=True)
    time.sleep(4)
    shutil.rmtree(CMD, ignore_errors=True)
    os.makedirs(CMD, exist_ok=True)
    _n[0] = 0            # ★새 드라이버는 1.txt 부터 기다린다 — 재시도 때 카운터를 안 되돌리면 영원히 못 만난다
    log("[1] flow_driver 기동 → 새 프로젝트")
    env = dict(os.environ)
    if os.environ.get("FLOW_PROFILE"):
        log(f"     프로필: {os.environ['FLOW_PROFILE']}")
    subprocess.Popen([sys.executable, "flow_driver.py"], cwd=ROOT, env=env,
                     stdout=open("scratch/flow_driver_auto.log", "w", encoding="utf-8"),
                     stderr=subprocess.STDOUT)
    for _ in range(20):
        time.sleep(5)
        u = dump().get("url", "")
        if "/project/" in u:
            log("     새 세션 준비됨"); return True
        if u:
            break
    # ★지난 동영상/프로젝트가 점유하고 있으면: 좌상단 날짜 옆 ← 로 나갔다가 '새 프로젝트' 로 들어간다
    log("     프로젝트 진입 안 됨 → 뒤로(←) 후 '새 프로젝트' 재시도")
    for _ in range(3):
        cmd("clicktext|돌아가기", 6)
        cmd("clicktext|새 프로젝트", 10)
        if "/project/" in dump().get("url", ""):
            log("     새 세션 준비됨(재시도)"); return True
        cmd("newproject", 8)
        if "/project/" in dump().get("url", ""):
            log("     새 세션 준비됨(newproject)"); return True
    log("     ★새 프로젝트 진입 실패"); return False


def run(key, do_reset=True):
    prompt_file = f"W23/prompts/{key}.txt"
    out = f"{CLIPS}/injun_w23_{key}.mp4"
    if not os.path.exists(prompt_file):
        raise SystemExit(f"프롬프트 없음: {prompt_file} (gen_w23_assets.py 가 만든다)")
    prompt = open(prompt_file, encoding="utf-8").read().replace("\n", " ").strip()
    guide = "W23/guides/upload/injun_w23_guide_front.png"
    src = open("gen_w23_assets.py", encoding="utf-8").read()
    import re
    m = re.search(rf'\("{key}",\s*(GUIDE_\w+)', src)
    if m:
        guide = {"GUIDE_FRONT": "W23/guides/upload/injun_w23_guide_front.png",
                 "GUIDE_3Q": "W23/guides/upload/injun_w23_guide_3q.png",
                 "GUIDE_SIDE": "W23/guides/upload/injun_w23_guide_side.png"}[m.group(1)]
    os.makedirs(CLIPS, exist_ok=True)

    if do_reset and not reset_and_start():
        return False

    # ★아래 숫자는 '고정 대기'가 아니라 **상한**이다(cmd 가 .done 을 보고 즉시 넘어간다).
    #   그래서 상한은 넉넉히 두되 실제 소요는 짧다.
    log(f"[2] 업로드 {guide}")
    cmd(f"upload|{guide}", 40)
    log("[3] 이미지 타일 대기(최대 30초)")
    cmd("wait|30", 60)
    # ★반드시 shot 으로 화면을 갱신한 뒤 찾는다(갱신 없이 찾으면 옛 덤프를 보고 놓친다)
    tile = None
    for i in range(6):
        shot(10)
        tile = find(lambda e: e.get("tag") == "IMG" and e.get("w", 0) > 100)
        if tile:
            log(f"     타일 확인 ({tile['x']},{tile['y']}) {tile['w']}x{tile['h']}"); break
        cmd("wait|10", 25)
    if not tile:
        log("★업로드 타일 없음"); return False
    tx, ty = tile["x"] + tile["w"] // 2, tile["y"] + tile["h"] // 2

    log("[4~6] ★makeclip — 프롬프트에 추가 + 9:16 설정확인 + 페이스트 + 실행을 한 번에")
    cmd(f"makeclip|{prompt}", 45)

    # ★사장님 확정 규칙(2026-07-27): **되는 생성은 90초면 끝난다.** 90초 뒤 왼편 타일에
    #   완성 동영상(재생 아이콘)이 있으면 성공, 없으면 실패 → 리셋하고 다시 만든다(--tries).
    log("[7] 동영상 생성 대기(90초)")
    cmd("wait|90", 140)
    for i in range(3):                       # 90초 + 최대 45초 여유만 본다
        cmd("vidstatus", 15)
        if find(lambda e: e.get("tag") == "VIDEO" and e.get("w", 0) > 100) or vidstatus_done():
            log("     완성 동영상 타일 확인"); break
        cmd("wait|15", 35)
    else:
        log("★동영상 타일 안 뜸 — 생성 실패"); return False

    log("[8] ★grabvideo — 왼편 타일 클릭 + 다운로드 + 저장")
    t_dl = time.time()
    cmd(f"grabvideo|{os.path.abspath(out)}", 90)
    log(f"     다운로드 구간 {time.time()-t_dl:.1f}s")
    if os.path.exists(out) and os.path.getsize(out) > 100000:
        log(f"✅ 저장: {out} ({os.path.getsize(out)//1024}KB)")
        return True
    log("★다운로드 실패")
    return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("key")
    ap.add_argument("--no-reset", action="store_true")
    ap.add_argument("--tries", type=int, default=2,
                    help="실패(90초 뒤 다운로드 버튼 안 뜸) 시 리셋하고 다시 만드는 횟수")
    a = ap.parse_args()
    ok = False
    for t in range(1, a.tries + 1):
        if t > 1:
            log(f"\n===== 재시도 {t}/{a.tries} — 리셋하고 처음부터 다시 만든다 =====")
        ok = run(a.key, do_reset=(not a.no_reset) or t > 1)
        if ok:
            break
    sys.exit(0 if ok else 1)
