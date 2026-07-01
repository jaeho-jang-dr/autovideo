import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

prompt = """[프로젝트: autovideo, 스택: Python + Playwright (GUI 자동화 전용)]
[작업 목표]:
1. 터미널을 사용하여 다음 명령어를 동기(Synchronous) 방식으로 직접 실행하고 끝까지 완료될 때까지 대기하십시오.
   명령어: python autoveo_flow.py --prompts korean_education/prompts_for_veo.txt --scene 2 --force
2. 절대 백그라운드로 실행하거나 백그라운드 셸로 넘기지 마십시오. 명령어 실행이 100% 완료되고 제어가 터미널로 돌아올 때까지 대기해야 합니다.
3. 실행 과정에서 브라우저가 보이는 상태(headless=False)로 뜹니다.
4. 생성이 완료되어 prompts_for_veo/scene_2.mp4 파일 다운로드가 완료될 때까지 기다리십시오. (비디오 생성 대기는 약 80~90초가 걸립니다.)
5. 성공적으로 완료되면 prompts_for_veo/scene_2.mp4를 korean_education/scene_2.mp4로 복사한 뒤, 최종 완료 및 검증 상태를 텍스트로 자세히 보고하십시오.
"""

cmd = ["claude", "--dangerously-skip-permissions", "-p"]

print("Starting Claude to run Scene 2 generation SYNCHRONOUSLY...", flush=True)
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
