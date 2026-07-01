import subprocess
import sys

# cp949 인코딩 오류 방지
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

prompt = """[프로젝트: autovideo, 스택: Python + Playwright (GUI 자동화 전용)]
[작업 목표]:
1. Google Flow를 통해 Scene 2, Scene 3, Scene 4에 대한 비디오 클립을 무중단 생성하고 성공적으로 다운로드 받으십시오.
   - 브라우저는 headless=False(보이는 모드)로 구동해야 합니다.
   - 대기 시간 규칙을 준수하십시오: 이미지 생성 시 40초, 비디오 생성 시 80초간 대기 후 다운로드를 확인해야 합니다.
   - Scene 2: 'python -u autoveo_flow.py --prompts korean_education/prompts_for_veo.txt --scene 2 --force' 를 실행하여 이미지 생성 및 애니메이션을 진행해 'prompts_for_veo/scene_2.mp4' 및 'scene_2.png'를 성공적으로 얻고, 이를 'korean_education/' 폴더로 이동/복사하십시오.
   - Scene 3: 'assets/images/scene_3.png'에 있는 세종대왕 포트레이트 이미지를 첫 프레임으로 삼아야 합니다. 'python -u flow_automator.py --scene 3 --auto --force --prompts korean_education/prompts_for_veo.txt --image-dir assets/images --video-dir korean_education' 명령어를 사용하여 이미지를 업로드하고 비디오를 생성하십시오. 최종 비디오가 'korean_education/scene_3.mp4'에 정상 저장되는지 확인하십시오.
   - Scene 4: 'python -u autoveo_flow.py --prompts korean_education/prompts_for_veo.txt --scene 4 --force' 를 실행하여 이미지 생성 및 애니메이션을 진행해 'prompts_for_veo/scene_4.mp4' 및 'scene_4.png'를 성공적으로 얻고, 이를 'korean_education/' 폴더로 이동/복사하십시오.
2. 모든 씬(Scene 1, 2, 3, 4)의 비디오가 'korean_education/' 아래에 올바르게 존재하는지 검증하십시오.
3. 'python korean_education/finalize.py'를 실행하여 비디오 컴파일 및 구글 드라이브 백업을 수행하십시오.
   - finalize.py 실행 시 썸네일도 새로 만들어져 구글 드라이브에 복사되는지 확인하십시오.

[필수 요구사항]:
- 쉘을 실행하여 각 명령어를 구동하고, 실행 과정에서 생성되는 디버그 스크린샷이나 에러 로그를 읽으며 필요 시 자가 수정하여 다운로드를 완수하십시오.
- 비디오 생성에는 수 분이 소요되므로, 렌더링 완료 및 다운로드가 완료될 때까지 참을성 있게 프로세스를 유지하며 대기하십시오.

[성공 기준]:
- 'korean_education/scene_2.mp4', 'korean_education/scene_3.mp4', 'korean_education/scene_4.mp4'가 정상 생성/저장됨.
- 'python korean_education/finalize.py'가 정상적으로 실행되어 비디오 컴파일 및 구글 드라이브 업로드가 완료됨.

[제약 조건 및 원칙]:
- 브라우저는 headless=False(보이는 모드)로 실행하십시오.
- UTF-8 인코딩 사용
- .harness/context/principles.md 파일의 개발 원칙 및 MoviePy 2.x 규칙 준수
"""

# 비대화형 모드로 기동하기 위해 -p 옵션을 붙입니다.
cmd = ["claude", "--dangerously-skip-permissions", "-p"]

print("Running Claude in non-interactive print mode with communicate...", flush=True)
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

# stdin을 통해 프롬프트를 전송하고 완료될 때까지 대기
stdout_data, _ = process.communicate(input=prompt)

print("--- Claude Output Start ---", flush=True)
sys.stdout.write(stdout_data)
sys.stdout.flush()
print("--- Claude Output End ---", flush=True)

print(f"\nClaude process finished with exit code {process.returncode}", flush=True)
sys.exit(process.returncode)
