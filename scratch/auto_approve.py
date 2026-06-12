# -*- coding: utf-8 -*-
"""
Antigravity 승인창 자동 클릭 스크립트 (Windows 전용)
====================================================
"Allow running this command?" 승인창이 뜨면
  1) 명령어를 읽어서 위험 명령인지 검사
  2) 안전하면 "Yes, allow this time" 클릭 → "Submit" 클릭
  3) 위험하면 건너뛰고 콘솔에 경고 출력

설치:
    pip install uiautomation

실행 (Antigravity가 켜진 상태에서):
    python antigravity_auto_approve.py

종료: Ctrl+C
"""

import time
import sys
import re

try:
    import uiautomation as auto
except ImportError:
    print("uiautomation 패키지가 필요합니다:  pip install uiautomation")
    sys.exit(1)

# ──────────────────────── 설정 ────────────────────────

# 검사 주기 (초)
POLL_INTERVAL = 1.0

# 이 패턴이 명령어에 포함되면 절대 자동 승인하지 않음 (직접 검토 필요)
DENY_PATTERNS = [
    r"\brm\b", r"\bdel\b", r"\brmdir\b", r"\bformat\b",
    r"Remove-Item", r"rd\s+/s",          # 삭제 계열
    r"\bgit\s+push\s+--force", r"git\s+reset\s+--hard",
    r"\bshutdown\b", r"\breg\s+(add|delete)\b",  # 시스템/레지스트리
    r"\bcurl\b.*\|\s*(sh|bash|powershell)",      # 원격 스크립트 실행
    r"\bmkfs\b", r"\bdd\b\s+if=",
]

# 선호 승인 옵션 (위에서부터 순서대로 찾음)
#   "Yes, and always allow ..." 를 먼저 두면 같은 명령은 다음부터 창이 안 뜸
PREFERRED_OPTIONS = [
    "Yes, and always allow",   # 프로젝트/전역 항상 허용 (있을 때만)
    "Yes, allow this time",    # 이번만 허용
]

DIALOG_MARKER = "Allow running this command?"
SUBMIT_LABEL = "Submit"

# ──────────────────────── 로직 ────────────────────────

deny_re = [re.compile(p, re.IGNORECASE) for p in DENY_PATTERNS]


def is_dangerous(cmd: str) -> bool:
    return any(r.search(cmd) for r in deny_re)


def find_antigravity_windows():
    """Antigravity 메인 창(들) 찾기 — Electron 앱은 Chrome_WidgetWin_1 클래스"""
    wins = []
    root = auto.GetRootControl()
    for w in root.GetChildren():
        try:
            if w.ClassName == "Chrome_WidgetWin_1" and "Antigravity" in (w.Name or ""):
                wins.append(w)
        except Exception:
            pass
    return wins


def walk(control, depth=0, max_depth=40):
    """UIA 트리 순회 (제너레이터)"""
    if depth > max_depth:
        return
    yield control
    try:
        for child in control.GetChildren():
            yield from walk(child, depth + 1, max_depth)
    except Exception:
        return


def handle_dialog(win) -> bool:
    """승인창을 찾아 처리. 처리했으면 True"""
    marker = None
    elements = list(walk(win))

    for el in elements:
        try:
            if DIALOG_MARKER in (el.Name or ""):
                marker = el
                break
        except Exception:
            continue
    if marker is None:
        return False

    # 승인창 발견 → 명령어 텍스트 추출 시도
    cmd_text = ""
    names = []
    for el in elements:
        try:
            n = el.Name or ""
        except Exception:
            continue
        if n:
            names.append(n)

    # 마커 다음에 나오는 짧은 텍스트 중 옵션/버튼이 아닌 것을 명령어로 간주
    try:
        idx = names.index(DIALOG_MARKER)
        for n in names[idx + 1: idx + 8]:
            if (not any(opt in n for opt in PREFERRED_OPTIONS)
                    and "No" != n.strip()[:2]
                    and SUBMIT_LABEL not in n and "Skip" not in n
                    and len(n) < 300):
                cmd_text = n
                break
    except ValueError:
        pass

    print(f"\n[감지] 승인창 발견  명령어: {cmd_text or '(추출 실패)'}")

    if cmd_text and is_dangerous(cmd_text):
        print("[차단] 위험 패턴 감지 → 자동 승인하지 않음. 직접 확인하세요!")
        # 같은 창을 계속 다시 처리하지 않도록 잠시 대기
        time.sleep(10)
        return True

    # 옵션 클릭
    clicked_option = False
    for pref in PREFERRED_OPTIONS:
        for el in elements:
            try:
                n = el.Name or ""
                if pref in n:
                    el.Click(simulateMove=False)
                    print(f"[클릭] 옵션: {n}")
                    clicked_option = True
                    break
            except Exception:
                continue
        if clicked_option:
            break

    if not clicked_option:
        print("[실패] 승인 옵션 버튼을 찾지 못함")
        return False

    time.sleep(0.3)

    # Submit 클릭 (트리 다시 읽기)
    for el in walk(win):
        try:
            n = el.Name or ""
            if n.strip().startswith(SUBMIT_LABEL):
                el.Click(simulateMove=False)
                print("[클릭] Submit  ✔ 자동 승인 완료")
                return True
        except Exception:
            continue

    # Submit 버튼을 못 찾으면 Enter 키로 대체
    try:
        win.SetActive()
        auto.SendKeys("{Enter}")
        print("[키입력] Enter  ✔ 자동 승인 완료(키보드)")
        return True
    except Exception:
        print("[실패] Submit 클릭/Enter 모두 실패")
        return False


def main():
    # Ensure stdout is unbuffered
    sys.stdout.reconfigure(line_buffering=True)
    print("=" * 50)
    print(" Antigravity UIA 자동 승인 스크립트 시작")
    print(" 종료: Ctrl+C")
    print("=" * 50)
    approved = 0
    while True:
        try:
            wins = find_antigravity_windows()
            if not wins:
                time.sleep(3)
                continue
            for w in wins:
                if handle_dialog(w):
                    approved += 1
                    print(f"[누적] 자동 처리 {approved}회")
                    time.sleep(1.0)
        except KeyboardInterrupt:
            print("\n종료합니다.")
            break
        except Exception as e:
            print(f"[오류] {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
