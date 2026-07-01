import subprocess
import time

def main():
    print("="*60)
    print(" Launching CapCut PC via Windows Task Scheduler (Interactive)")
    print("="*60)
    
    task_name = "LaunchCapCutInteractive"
    # Target executable path
    exe_path = r"C:\Users\antigravity\AppData\Local\CapCut\Apps\8.7.0.3685\CapCut.exe"
    
    # Create the task
    # Note: We must escape the double quotes around the executable path
    cmd_create = [
        "schtasks", "/create", 
        "/tn", task_name, 
        "/tr", f'"{exe_path}"', 
        "/sc", "once", 
        "/sd", "2026/06/18", 
        "/st", "12:00", 
        "/it", 
        "/ru", "antigravity", 
        "/f"
    ]
    
    print(f"[Info] Creating task: {' '.join(cmd_create)}")
    res_create = subprocess.run(cmd_create, capture_output=True, text=True)
    print("Create stdout:", res_create.stdout)
    print("Create stderr:", res_create.stderr)
    
    if res_create.returncode != 0:
        print("[Error] Failed to create scheduled task.")
        return
        
    # Run the task
    cmd_run = ["schtasks", "/run", "/tn", task_name]
    print(f"[Info] Running task: {' '.join(cmd_run)}")
    res_run = subprocess.run(cmd_run, capture_output=True, text=True)
    print("Run stdout:", res_run.stdout)
    print("Run stderr:", res_run.stderr)
    
    # Wait a bit and delete
    time.sleep(3)
    cmd_delete = ["schtasks", "/delete", "/tn", task_name, "/f"]
    print(f"[Info] Deleting task: {' '.join(cmd_delete)}")
    subprocess.run(cmd_delete)
    
    print("[Success] Launch process complete.")
    print("="*60)

if __name__ == '__main__':
    main()
