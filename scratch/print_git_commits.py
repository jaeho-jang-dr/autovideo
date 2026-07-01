import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    try:
        out = subprocess.check_output(
            ["git", "log", "-n", "10", "--pretty=format:Commit: %h%nAuthor: %an <%ae>%nDate:   %ad%nSubject: %s%n%b%n--------------------------------------------------"],
            text=True,
            encoding='utf-8'
        )
        print(out)
    except Exception as e:
        print(f"Error running git log: {e}")

if __name__ == "__main__":
    main()
