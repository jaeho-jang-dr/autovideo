# -*- coding: utf-8 -*-
"""
scripts/bridge.py — Claude Code(감독) 및 Antigravity Gemini(조감독) 초고속 협업 브릿지

기능:
1. 태스크 전달: python scripts/bridge.py send --title "..." --body "..." [--files "a.py,b.py"]
2. 상태 확인: python scripts/bridge.py status
3. 작업 완료 보고: python scripts/bridge.py report --status COMPLETED --summary "..." [--urls "http://localhost:8930"]
4. 작업 완료 대기: python scripts/bridge.py wait [--timeout 300]
5. 교정앱 포트 등록: python scripts/bridge.py app --port 8930 --label "피란길 v12" --status RUNNING
6. 최신 태스크 읽기: python scripts/bridge.py get-task
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path

# UTF-8 출력 보장
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = Path(__file__).resolve().parent.parent
BRIDGE_DIR = BASE_DIR / "scratch" / "bridge"
BRIDGE_DIR.mkdir(parents=True, exist_ok=True)

TASK_FILE = BRIDGE_DIR / "active_task.json"
STATE_FILE = BRIDGE_DIR / "shared_state.json"
EVENTS_FILE = BRIDGE_DIR / "events.jsonl"
LEGACY_TASK_MD = BASE_DIR / "scratch" / "gemini_task.md"
LEGACY_REPORT_MD = BASE_DIR / "scratch" / "gemini_report.md"

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_event(sender, event_type, data):
    event = {
        "timestamp": get_timestamp(),
        "sender": sender,
        "type": event_type,
        "data": data
    }
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def read_json(path, default=None):
    if not path.exists():
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def cmd_send(args):
    """감독(Claude) -> 조감독(Gemini) 태스크 발송"""
    task = {
        "id": f"task_{int(time.time())}",
        "created_at": get_timestamp(),
        "sender": args.sender or "Claude (Director)",
        "recipient": "Gemini (Assistant Director)",
        "status": "PENDING",
        "title": args.title,
        "body": args.body or "",
        "target_files": [f.strip() for f in args.files.split(",")] if args.files else [],
        "priority": args.priority or "NORMAL",
        "report": None
    }
    write_json(TASK_FILE, task)
    log_event(task["sender"], "TASK_SENT", task)

    # gemini_task.md 동기화 (기존 워크플로우 호환)
    target_f_str = ', '.join(task['target_files']) if task['target_files'] else '지정 없음'
    md_content = f"""# [브릿지 지시] {task['title']}
> 발신: {task['sender']} · 수신: {task['recipient']} · 일시: {task['created_at']} · 상태: PENDING
> 우선순위: {task['priority']} · 대상파일: {target_f_str}

## 지시 내용
{task['body']}

---
*이 태스크는 scripts/bridge.py를 통해 실시간 동기화 중입니다.*
"""
    with open(LEGACY_TASK_MD, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"🚀 [BRIDGE] 태스크 발송 완료! ID: {task['id']}")
    print(f"   - 제목: {task['title']}")
    print(f"   - 상태: PENDING")
    print(f"   - 조감독 호출 키워드: 제작자님, 제미나이에게 '브릿지 진행' 또는 '지시 수신' 한마디만 전달하세요!")

def cmd_report(args):
    """조감독(Gemini) -> 감독(Claude) 완료/진행 보고"""
    task = read_json(TASK_FILE)
    if not task:
        task = {
            "id": f"ad_hoc_{int(time.time())}",
            "created_at": get_timestamp(),
            "sender": "Gemini (Assistant Director)",
            "title": "자율 작업 보고"
        }
    
    report_data = {
        "reported_at": get_timestamp(),
        "sender": args.sender or "Gemini (Assistant Director)",
        "status": args.status,
        "summary": args.summary,
        "urls": [u.strip() for u in args.urls.split(",")] if args.urls else [],
        "details": args.details or ""
    }
    
    task["status"] = args.status
    task["report"] = report_data
    write_json(TASK_FILE, task)
    log_event(report_data["sender"], "TASK_REPORTED", report_data)

    # gemini_report.md 동기화
    url_str = ', '.join(report_data['urls']) if report_data['urls'] else '없음'
    report_entry = f"""
## [{report_data['reported_at']}] {args.status}: {args.summary}
- 발신: {report_data['sender']}
- 관련 URL/포트: {url_str}
- 세부 내용:
{report_data['details']}
"""
    with open(LEGACY_REPORT_MD, "a", encoding="utf-8") as f:
        f.write(report_entry)

    print(f"✅ [BRIDGE] 보고 등록 완료! 상태: {args.status}")
    print(f"   - 요약: {args.summary}")
    if report_data['urls']:
        print(f"   - 앱 URL: {url_str}")

def cmd_status(args):
    """현재 브릿지 종합 상태 출력"""
    task = read_json(TASK_FILE)
    state = read_json(STATE_FILE)
    
    print("=" * 60)
    print(" 📡 AUTOVIDEO CLAUDE-GEMINI BRIDGE STATUS")
    print("=" * 60)
    
    if not task:
        print(" [활성 태스크] 현재 진행 중인 태스크 없음 (IDLE)")
    else:
        status_icon = "⏳" if task.get("status") == "PENDING" else ("🔄" if task.get("status") == "IN_PROGRESS" else "✅")
        print(f" [활성 태스크] {status_icon} [{task.get('status', 'UNKNOWN')}] {task.get('title', '제목 없음')}")
        print(f"   - 발신/수신: {task.get('sender')} -> {task.get('recipient')}")
        print(f"   - 생성일시: {task.get('created_at')}")
        if task.get("target_files"):
            print(f"   - 대상 파일: {', '.join(task['target_files'])}")
        
        report = task.get("report")
        if report:
            print(f"   - 최근 보고 ({report.get('reported_at')}): {report.get('summary')}")
            if report.get("urls"):
                print(f"   - 확인 URL: {', '.join(report.get('urls'))}")

    apps = state.get("apps", {})
    if apps:
        print("\n [구동 중인 교정앱 / 서비스]")
        for port, app_info in apps.items():
            print(f"   * http://localhost:{port}/ -> {app_info.get('label')} [{app_info.get('status')}]")
    
    print("=" * 60)

def cmd_wait(args):
    """감독이 조감독의 완료를 기다림"""
    timeout = args.timeout or 300
    poll_interval = 2
    start_time = time.time()
    
    print(f"⏳ [BRIDGE] 조감독(Gemini) 작업 완료 대기 중... (최대 {timeout}초)")
    while time.time() - start_time < timeout:
        task = read_json(TASK_FILE)
        status = task.get("status")
        if status in ["COMPLETED", "DONE", "FINISHED"]:
            report = task.get("report", {})
            print(f"\n🎉 [BRIDGE] 조감독 작업 완료 감지!")
            print(f"   - 상태: {status}")
            print(f"   - 요약: {report.get('summary')}")
            if report.get("urls"):
                print(f"   - 링크: {', '.join(report.get('urls'))}")
            return 0
        elif status == "FAILED":
            report = task.get("report", {})
            print(f"\n❌ [BRIDGE] 조감독 작업 실패 보고!")
            print(f"   - 사유: {report.get('summary')}")
            return 1
        
        time.sleep(poll_interval)
        print(".", end="", flush=True)
    
    print(f"\n⏰ [BRIDGE] 대기 시간 초과 ({timeout}초)")
    return 2

def cmd_app(args):
    """교정앱 등 서버 상태 등록/갱신"""
    state = read_json(STATE_FILE)
    if "apps" not in state:
        state["apps"] = {}
    
    state["apps"][str(args.port)] = {
        "port": args.port,
        "label": args.label or f"App-{args.port}",
        "status": args.status or "RUNNING",
        "updated_at": get_timestamp()
    }
    write_json(STATE_FILE, state)
    print(f"🌐 [BRIDGE] 앱 등록 완료: http://localhost:{args.port}/ ({args.label})")

def cmd_get_task(args):
    """조감독이 최신 태스크를 원클릭으로 읽기"""
    task = read_json(TASK_FILE)
    if not task:
        print(json.dumps({"status": "NO_TASK"}, ensure_ascii=False, indent=2))
        return
    print(json.dumps(task, ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser(description="Claude-Gemini Bridge CLI")
    subparsers = parser.add_subparsers(dest="command")

    # send
    p_send = subparsers.add_parser("send", help="태스크 발송 (Claude -> Gemini)")
    p_send.add_argument("--title", required=True, help="태스크 제목")
    p_send.add_argument("--body", default="", help="태스크 세부 내용")
    p_send.add_argument("--files", default="", help="수정 대상 파일들 (쉼표 구분)")
    p_send.add_argument("--priority", default="NORMAL", choices=["LOW", "NORMAL", "HIGH", "URGENT"])
    p_send.add_argument("--sender", default="Claude (Director)")

    # report
    p_rep = subparsers.add_parser("report", help="보고 등록 (Gemini -> Claude)")
    p_rep.add_argument("--status", required=True, choices=["IN_PROGRESS", "COMPLETED", "FAILED", "BLOCKED"])
    p_rep.add_argument("--summary", required=True, help="작업 요약")
    p_rep.add_argument("--urls", default="", help="관련 URL / 교정앱 링크 (쉼표 구분)")
    p_rep.add_argument("--details", default="", help="세부 사항")
    p_rep.add_argument("--sender", default="Gemini (Assistant Director)")

    # status
    p_stat = subparsers.add_parser("status", help="상태 조회")

    # wait
    p_wait = subparsers.add_parser("wait", help="작업 완료 대기")
    p_wait.add_argument("--timeout", type=int, default=300, help="대기 제한 시간(초)")

    # app
    p_app = subparsers.add_parser("app", help="교정앱 상태 등록")
    p_app.add_argument("--port", type=int, required=True, help="포트 번호")
    p_app.add_argument("--label", default="", help="앱 라벨/설명")
    p_app.add_argument("--status", default="RUNNING", help="앱 상태 (RUNNING/STOPPED)")

    # get-task
    p_get = subparsers.add_parser("get-task", help="최신 활성 태스크 조회 (JSON)")

    args = parser.parse_args()

    if args.command == "send":
        cmd_send(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "wait":
        sys.exit(cmd_wait(args))
    elif args.command == "app":
        cmd_app(args)
    elif args.command == "get-task":
        cmd_get_task(args)
    else:
        cmd_status(args)

if __name__ == "__main__":
    main()
