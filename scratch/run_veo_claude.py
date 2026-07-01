import subprocess
import sys

# cp949 인코딩 오류 방지
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

prompt = """[프로젝트: autovideo, 스택: Python]
binge_watching_prompts.txt에 정의된 모든 씬(scene_1 ~ scene_96)을 autoveo_flow.py를 사용해 순차적으로 100% 다운로드 완료해줘.
이미 1~3번 씬은 다운로드되어 폴더에 있으므로 skip될 것입니다.

제약 사항:
- GUI가 보이는 상태(headless=False)로 크롬 브라우저가 실행되며 사용자 모니터에 노출되도록 하십시오.
- 딜레이 설정: 이미지 생성 시 최소 40초 이상 대기, 동영상은 최소 70초 대기 후 다운로드를 체크합니다 (이미 autoveo_flow.py에 반영됨).
- 다운로드 전략: 비디오 타일 영역을 클릭해 라이트박스(상세 모달)를 열고, 우측 상단에 노출되는 다운로드 아이콘 버튼을 눌러 원본 크기로 저장하고, 라이트박스는 Escape 키를 눌러 닫습니다 (이미 autoveo_flow.py에 반영됨).
- 클릭 재시도 및 스샷: 타일 클릭 후 라이트박스가 정상적으로 열리지 않는 경우, 해당 시점의 화면 스크린샷을 저장하고 좌표 정보를 로깅 및 기억하여 마우스 move 후 다시 강제 재클릭을 시도해 안정성을 보장합니다.
- 다운로드 프로세스 도중 팝업창 승인은 윈도우 우회 매크로(auto_approve.py)를 별도 백그라운드로 실행하여 자동 클릭되게 처리하십시오.
- 렌더링 과정이 끊기지 않고 완료될 때까지 터미널 세션을 유지(Wait)해서 완전히 끝내십시오.
"""

import threading

cmd = ["claude", "--dangerously-skip-permissions", "-p"]

print("Starting Claude Code with prompt for Binge Watching...", flush=True)
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
        for line in pipe:
            sys.stdout.write(line)
            sys.stdout.flush()
    except Exception as e:
        sys.stderr.write(f"Error reading pipe: {e}\n")
        sys.stderr.flush()

# Start output reader thread
t = threading.Thread(target=read_output, args=(process.stdout,))
t.daemon = True
t.start()

# Send prompt and close stdin to signal EOF
process.stdin.write(prompt + "\n")
process.stdin.flush()
process.stdin.close()

# Wait for process and thread to finish
process.wait()
t.join()

print(f"\nClaude process finished with exit code {process.returncode}", flush=True)
sys.exit(process.returncode)
