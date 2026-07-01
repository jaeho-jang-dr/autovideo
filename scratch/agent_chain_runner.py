import os
import sys
import time
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASK_FILE = os.path.join(ROOT, "scratch", "gemini_task.md")
REPORT_FILE = os.path.join(ROOT, "scratch", "gemini_report.md")

def setup_file_logging():
    log_file_path = os.path.join(ROOT, "scratch", "agent_chain_runner.log")
    try:
        # 즉시 기록을 위해 buffering=1 (Line buffering) 설정
        log_file = open(log_file_path, "w", encoding="utf-8", buffering=1)
        sys.stdout = log_file
        sys.stderr = log_file
    except Exception as e:
        print(f"Failed to setup file logging: {e}")

def get_mtime(p):
    if os.path.exists(p):
        return os.path.getmtime(p)
    return 0

def check_stop_signal(p):
    """파일 내용 중에 STOP 또는 DONE 시그널이 있으면 에이전트 기동을 차단하여 무한루프를 방지합니다."""
    if not os.path.exists(p):
        return False
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if "[STATUS] STOP" in content or "[STATUS] DONE" in content or "status: done" in content or "status: stop" in content:
                return True
    except Exception:
        pass
    return False

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def run_cmd(args):
    # Windows 환경인 경우, powershell.exe를 사용해 Function/Script 호환성 보장
    if os.name == 'nt':
        ps_args = []
        for arg in args:
            # 공백이나 특수 문자가 들어 있으면 백틱과 큰따옴표로 이스케이프
            if any(char in arg for char in [" ", "'", '"', "$", "&", "(", ")", ";"]):
                escaped = arg.replace('"', '`"')
                ps_args.append(f'"{escaped}"')
            else:
                ps_args.append(arg)
        cmd_str = " ".join(ps_args)
        full_cmd = ["powershell.exe", "-Command", cmd_str]
    else:
        full_cmd = args

    log(f"Executing: {' '.join(full_cmd)}")
    try:
        proc = subprocess.Popen(
            full_cmd,
            shell=True if os.name != 'nt' else False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        for line in proc.stdout:
            sys.stdout.write(f"  [RUNNER] {line}")
            sys.stdout.flush()
        proc.wait()
        log(f"Process finished with exit code {proc.returncode}")
        return proc.returncode
    except Exception as e:
        log(f"Execution failed: {e}")
        return -1

def main():
    # 백그라운드 구동 시 로그 파일 자동 연동
    setup_file_logging()
    
    # Ensure stdout is unbuffered
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(line_buffering=True)
        except Exception:
            pass
    log("=== Agent Auto Chain Runner Started ===")
    log(f"Monitoring:\n  Task: {TASK_FILE}\n  Report: {REPORT_FILE}")
    
    last_task_time = get_mtime(TASK_FILE)
    last_report_time = get_mtime(REPORT_FILE)
    
    while True:
        try:
            # 1. gemini_task.md 감시 (클로드가 지시한 경우)
            current_task_time = get_mtime(TASK_FILE)
            if current_task_time > last_task_time:
                if check_stop_signal(TASK_FILE):
                    log("gemini_task.md contains STOP/DONE signal. Skipping trigger.")
                    last_task_time = current_task_time
                else:
                    log("Detected update in gemini_task.md! Triggering Gemini Assistant (agy)...")
                    time.sleep(1)
                    cmd = ["agy", "--dangerously-skip-permissions", "--continue", "--print", "scratch/gemini_task.md를 읽고 지시사항을 즉시 수행하십시오."]
                    run_cmd(cmd)
                    last_task_time = get_mtime(TASK_FILE)
                    last_report_time = get_mtime(REPORT_FILE)
                time.sleep(2)
                continue
                
            # 2. gemini_report.md 감시 (제미나이가 완료 보고서를 쓴 경우)
            current_report_time = get_mtime(REPORT_FILE)
            if current_report_time > last_report_time:
                if check_stop_signal(REPORT_FILE):
                    log("gemini_report.md contains STOP/DONE signal. Skipping trigger.")
                    last_report_time = current_report_time
                else:
                    log("Detected update in gemini_report.md! Triggering Claude Director...")
                    time.sleep(1)
                    cmd = ["claude", "--dangerously-skip-permissions", "-p", "scratch/gemini_report.md의 결과 보고서를 확인하고 검수 결과를 보고하십시오."]
                    run_cmd(cmd)
                    last_report_time = get_mtime(REPORT_FILE)
                    last_task_time = get_mtime(TASK_FILE)
                time.sleep(2)
                continue
                
        except KeyboardInterrupt:
            log("Runner stopped by user.")
            break
        except Exception as e:
            log(f"Runner error: {e}")
            
        time.sleep(3)

if __name__ == "__main__":
    main()
