import subprocess
import sys
import threading
import os

# Set output encoding to UTF-8
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

def main():
    task_file = "scratch/gemini_task.md"
    if not os.path.exists(task_file):
        print(f"Task file {task_file} does not exist!")
        sys.exit(1)
        
    with open(task_file, "r", encoding="utf-8") as f:
        prompt = f.read()
        
    # Append instructions to report diff and errors clearly
    directive_prompt = f"""[Assistant Director Directive]
Please execute the tasks defined in the markdown content below. Make sure to complete them, verify, and write a summary report at the end to `scratch/gemini_report.md`.

---
{prompt}
"""
    
    cmd = ["claude", "--dangerously-skip-permissions", "-p"]
    
    print("Launching Claude Code with Pipe wrapper for Hangeul Curriculum integration...", flush=True)
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
        shell=True
    )
    
    def read_output(pipe):
        try:
            while True:
                char = pipe.read(1)
                if not char:
                    break
                sys.stdout.write(char)
                sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error reading pipe: {e}\n")
            sys.stderr.flush()
            
    # Start output reader thread
    t = threading.Thread(target=read_output, args=(process.stdout,))
    t.daemon = True
    t.start()
    
    # Send prompt and close stdin to signal EOF
    process.stdin.write(directive_prompt + "\n")
    process.stdin.flush()
    process.stdin.close()
    
    # Wait for process and thread to finish
    process.wait()
    t.join()
    
    print(f"\nClaude process finished with exit code {process.returncode}", flush=True)
    sys.exit(process.returncode)

if __name__ == '__main__':
    main()
