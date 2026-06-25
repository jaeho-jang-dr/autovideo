import subprocess
import sys

# cp949 encoding error prevention
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

prompt = """[프로젝트: autovideo, 스택: Python + MoviePy 2.2.1 + gTTS + Playwright]
[작업 목표: /goal 초급 1주차 "한글의 탄생과 단모음" 한영 2개 버전 4K 비디오 100% 제작 및 컴파일 완료]

[세부 실행 지침]:
1. 'd:/Entertainments/DevEnvironment/autovideo/hangeul_birth_vowels/scenario_draft.txt'를 참고하여 최종 영상 제작 시나리오 파일인 'scenario.txt'를 'hangeul_birth_vowels/' 디렉토리 안에 생성/감수하십시오.
   - 각 씬마다 [Scene X] 블록으로 설정하고, Script (KO)와 Script (EN)를 매칭하십시오.
   - 각 씬에 쓰일 Zolla/Jieun 캐릭터 레이어 오버레이 속성(cx, cy, scale, opacity 등) 및 텍스트 카드 매핑 값을 scenario.txt에 완전 기술하십시오.
2. 각 씬별 Google Flow 비디오 생성을 위한 프롬프트 리스트를 추출하고 'autoveo_flow.py' 또는 'flow_automator.py'를 구동하여 14개 모든 씬(Scene 0 ~ Scene 13)의 비디오 클립(.mp4)을 다운로드 받으십시오.
   - 브라우저는 headless=False(보이는 모드)로 구동합니다. (사용자 프로필: assets/chrome_profile)
   - 생성 및 다운로드 대기 룰 준수: 이미지 40초, 비디오 80초간 대기 후 체크.
   - 실패 시 즉시 해당 타일 삭제 후 재생성 시도. 3회 연속 실패 시 크롬 브라우저 Reboot 적용.
   - 진행 상황은 'hangeul_birth_vowels/progress_scenes.json'에 증분식으로 기록하여, 중단 시에도 이어서 기동하도록 구성하십시오.
3. 100% CPU 동원 렌더링 규칙을 적용하여 'make_video.py' 또는 'finalize.py' 컴파일러를 구동, 한국어 버전('hangeul_birth_vowels_ko.mp4') 및 영어 버전('hangeul_birth_vowels_en.mp4') 4K(3840x2160) 해상도 비디오를 빌드하십시오.
   - 각 언어에 맞춰 gTTS 음성(여성음, 1.1배속 'MultiplySpeed(1.1)')을 생성하여 매칭하십시오.
   - 자막 트랙('.ko.srt', '.en.srt')을 생성하여 자막 바(dynamic padding) 오버레이를 적용하십시오.
   - 우측 하단에 채널 로고 배지('assets/drjay_ed_logo_circle.png', 45x45 픽셀 크기)를 알파 블렌딩 적용하십시오.
   - 아웃트로 종료 후 'assets/outro_template.png' 10초 정지 카드를 무음 영상으로 합성하여 결합하십시오.
   - 인트로(Scene 0) 감지 시 자동으로 'hangeul_birth_vowels/scene_0_thumbnail_korean.png' 썸네일(한국어 텍스트와 sprout green 상자 디자인)을 빌드하십시오.
4. 최종 렌더링이 완료된 영상 및 자막 파일, 썸네일을 Google Drive 백업 폴더로 업로드하십시오.

[제약 조건 및 규칙]:
- MoviePy 2.x API 표준 준수
- 한글 자막 폰트 경로: 'C:\\Windows\\Fonts\\malgun.ttf'
- CLI 실행 시 조기 종료를 방지하기 위해 렌더링 완료 및 파일 추출까지 셸 프로세스를 대기(Wait)하여 유지할 것.
"""

# Run Claude in non-interactive print mode
cmd = ["claude", "--dangerously-skip-permissions", "-p"]

print("Starting Claude Code pipeline to generate Hangeul Birth & Vowels video...", flush=True)
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

print(f"\nClaude process finished with exit code {process.returncode}", flush=True)
sys.exit(process.returncode)
