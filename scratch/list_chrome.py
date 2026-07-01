import subprocess
import sys

def main():
    try:
        out = subprocess.check_output('wmic process where "name=\'chrome.exe\'" get processid,commandline', shell=True)
        lines = out.decode('utf-8', errors='ignore').splitlines()
        for line in lines:
            if not line.strip():
                continue
            if '--type=' in line:
                continue
            print(line)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
