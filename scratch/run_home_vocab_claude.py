import subprocess
import sys
import os

# cp949 인코딩 오류 방지
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

prompt = """[프로젝트: autovideo, 스택: Python + Playwright + MoviePy]
[작업 목표]:
1. 'home_vocab/prompts_for_flow.txt'를 로드하여 'autoveo_flow.py'를 통해 Google Flow(Labs Omni)에서 23종의 2D 라인아트 이미지 에셋을 무중단 생성하고 성공적으로 다운로드 받으십시오.
   - **중요 절대 원칙**: 이미지와 영상 에셋은 타사 로컬 생성기나 API를 절대 사용하지 않으며, 반드시 **Google Flow 웹 에디터 상에서만 100% 생성 및 다운로드**받아야 합니다.
   - 브라우저는 headless=False(보이는 모드)로 구동해야 합니다.
   - 실행 중 Antigravity CLI의 승인 팝업 우회를 위해 백그라운드로 'python scratch/auto_approve.py' 매크로가 이미 돌고 있으니 안심하고 실행하십시오.
   - 실행 명령어 예시:
     `python autoveo_flow.py --prompts home_vocab/prompts_for_flow.txt`
   - 다운로드 완료 후 다운로드된 에셋들이 'home_vocab/' 폴더 밑에 'bed.png', 'blanket.png', 'clock.png' 등 알맞은 이름으로 매핑 및 존재해야 합니다.

2. 모든 에셋(인물 5종, 사물 18종)의 다운로드가 완료되면, 조감독이 미리 작성해 둔 전용 컴파일러 스크립트를 실행하십시오:
   - 실행 명령어:
     `python scratch/compile_home_vocab.py`
   - 이 컴파일러는 선희(SunHi) Neural 목소리를 강제하고 효과음 및 자막 elastic 모션을 동적 믹싱하여 다음 3개 결과물을 렌더링합니다:
     - `home_vocab/home_vocab_4k.mp4` (4K UHD 해상도 마스터 원본)
     - `home_vocab/home_vocab_sns_720p.mp4` (720p HD 해상도, SNS용 300MB 미만 사본)
     - `home_vocab/home_vocab_thumbnail.png` (한글 썸네일)
   - 인트로 및 아웃트로는 사용자의 지시에 따라 **제외**되어 있습니다.

3. 최종 빌드가 끝나면 3개 파일(4K 마스터, 720p SNS 사본, 썸네일)을 구글 드라이브 AutoVideo 경로로 업로드하십시오:
   - 복사 경로: `G:\\내 드라이브\\AutoVideo\\`
   - 복사 후 최종적으로 존재 여부와 바이트 크기를 확인하여 보고하십시오.

[필수 요구사항]:
- 쉘을 실행하여 각 명령어를 구동하고, 실행 과정에서 생성되는 디버그 스크린샷이나 에러 로그를 읽으며 필요 시 자가 수정하여 다운로드를 완수하십시오.
- 비디오/이미지 생성과 인코딩에는 많은 시간이 소요되므로, 최종 빌드가 완료될 때까지 터미널 세션을 종료하지 말고 참을성 있게 프로세스를 대기(Wait)하십시오.

[성공 기준]:
- 모든 23종의 png 에셋이 'home_vocab/' 폴더 내에 누락 없이 위치함.
- `home_vocab_4k.mp4`, `home_vocab_sns_720p.mp4`, `home_vocab_thumbnail.png` 파일이 정상 빌드되어 구글 드라이브 `G:\\내 드라이브\\AutoVideo\\` 경로에 성공적으로 업로드됨.
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
