import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

prompt = """[프로젝트: autovideo, 스택: Python + Playwright (GUI 자동화 전용)]
[작업 목표]:
1. 터미널을 사용하여 다음 명령어를 직접 실행하고 끝까지 완료될 때까지 대기하십시오.
   명령어: python autoveo_flow.py --prompts korean_education/prompts_for_veo.txt --scene 2 --force
2. 실행 시 브라우저가 보이는 상태(headless=False)로 뜹니다.
3. 생성 및 다운로드가 완료될 때까지 대기하며, 오류가 발생할 경우 터미널 로그를 확인하고 자동으로 자가 수정하여 재시도하십시오.
4. 생성이 완료되어 prompts_for_veo/scene_2.mp4가 저장되면, 이를 korean_education/scene_2.mp4로 복사하고 완료 메시지를 리턴하십시오.
"""

cmd = ["claude", "--dangerously-skip-permissions", "-p"]

print("Starting Claude to run Scene 2 generation...", flush=True)
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

stdout_data, _ = process.communicate(input=prompt)

print("--- Claude Output Start ---", flush=True)
sys.stdout.write(stdout_data)
sys.stdout.flush()
print("--- Claude Output End ---", flush=True)

sys.exit(process.returncode)
