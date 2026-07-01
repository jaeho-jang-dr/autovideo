import subprocess

def main():
    exe_path = r"C:\Users\antigravity\AppData\Local\CapCut\Apps\8.7.0.3685\CapCut.exe"
    print(f"Diagnosing launch of: {exe_path}")
    try:
        p = subprocess.run([exe_path], capture_output=True, text=True, timeout=5)
        print("Exit code:", p.returncode)
        print("STDOUT:", p.stdout)
        print("STDERR:", p.stderr)
    except subprocess.TimeoutExpired:
        print("Process started and timed out successfully (normal for GUI).")
    except Exception as e:
        print("Error during execution:", e)

if __name__ == '__main__':
    main()
