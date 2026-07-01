import os
import sys
import time
import subprocess
import argparse

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        
    parser = argparse.ArgumentParser(description="Interactive Python Script Launcher via Windows Task Scheduler")
    parser.add_argument("--script", required=True, help="Python script to run (e.g. autoveo_flow.py)")
    parser.add_argument("--args", default="", help="Arguments for the script")
    parser.add_argument("--log", default="scratch/interactive_run.log", help="Log file path to redirect outputs")
    args = parser.parse_args()

    task_name = "RunPythonInteractive"
    script_path = os.path.abspath(args.script)
    log_path = os.path.abspath(args.log)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    # Clean up old log
    if os.path.exists(log_path):
        try:
            os.remove(log_path)
        except Exception:
            pass

    # Create temporary batch file to bypass schtasks 261-char path length limit
    bat_path = os.path.abspath("scratch/temp_interactive.bat")
    cwd = os.getcwd()
    bat_content = f'@echo off\ncd /d "{cwd}"\npython -u "{script_path}" {args.args} > "{log_path}" 2>&1\n'
    try:
        with open(bat_path, "w", encoding="cp949") as f:
            f.write(bat_content)
    except Exception as e:
        print(f"[Error] Failed to create temporary batch file: {e}")
        return

    # Task Scheduler command executes the batch file
    run_cmd = f'cmd.exe /c "{bat_path}"'
    
    # 1. Create the scheduled task
    cmd_create = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", run_cmd,
        "/sc", "once",
        "/sd", "2026/06/18",
        "/st", "12:00",
        "/it",
        "/ru", "antigravity",
        "/f"
    ]
    
    print(f"[Launcher] Creating scheduled task: {task_name}")
    res_create = subprocess.run(cmd_create, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res_create.returncode != 0:
        print(f"[Error] Failed to create scheduled task: {res_create.stderr}")
        return

    # 2. Run the task
    cmd_run = ["schtasks", "/run", "/tn", task_name]
    print(f"[Launcher] Running task: {task_name}")
    res_run = subprocess.run(cmd_run, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if res_run.returncode != 0:
        print(f"[Error] Failed to execute task: {res_run.stderr}")
        # Cleanup
        subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], stdout=subprocess.DEVNULL)
        return

    print(f"[Launcher] Monitoring log: {log_path}")
    print("="*60)

    # 3. Monitor the log file in real-time
    # We wait for the log file to be created first
    start_time = time.time()
    while not os.path.exists(log_path):
        if time.time() - start_time > 15: # 15s timeout
            print("[Error] Timeout waiting for log file to be created. Check if task scheduler is running.")
            subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], stdout=subprocess.DEVNULL)
            return
        time.sleep(0.5)

    # Open log and print line by line
    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
        # Keep reading as lines are appended
        task_finished = False
        empty_checks = 0
        
        while not task_finished:
            line = f.readline()
            if line:
                print(line.rstrip())
                empty_checks = 0
            else:
                # Check if task is still running using schtasks query
                # To minimize overhead, we check only when we hit EOF repeatedly
                empty_checks += 1
                if empty_checks > 10: # Check task status every ~1 second of idle
                    # Query task status
                    cmd_query = ["schtasks", "/query", "/tn", task_name, "/fo", "LIST"]
                    res_query = subprocess.run(cmd_query, capture_output=True, text=True, encoding="utf-8", errors="ignore")
                    stdout_str = res_query.stdout or ""
                    if "Running" not in stdout_str and "실행 중" not in stdout_str:
                        # Task finished! Let's read the remaining log one last time
                        time.sleep(0.5)
                        remaining = f.read()
                        if remaining:
                            print(remaining.rstrip())
                        task_finished = True
                    empty_checks = 0
                time.sleep(0.1)

    print("="*60)
    print("[Launcher] Task execution completed.")

    # 4. Clean up scheduled task and batch file
    cmd_delete = ["schtasks", "/delete", "/tn", task_name, "/f"]
    subprocess.run(cmd_delete, stdout=subprocess.DEVNULL)
    if os.path.exists(bat_path):
        try:
            os.remove(bat_path)
        except Exception:
            pass
    print("[Launcher] Cleaned up scheduled task and temporary files.")

if __name__ == '__main__':
    main()
