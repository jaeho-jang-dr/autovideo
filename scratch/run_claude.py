import subprocess
import sys

# cp949 인코딩 오류 방지
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

prompt = """[프로젝트: autovideo, 스택: Python + MoviePy + gTTS, Astro]
[작업 목표]:
1. 'channel/export_web.py'를 수정하여 에피소드 밑에 scenes 리스트(seq, script_kr, script_en, duration_sec)가 중첩되도록 쿼리를 보강하고 'web/src/data/content.json'으로 익스포트하도록 수정 및 실행하십시오.
2. 'web/' 디렉토리에 Astro 5.x 정적 웹사이트를 구축하십시오. 'npx -y create-astro@latest ./web --yes --no-git --install' 명령어로 프로젝트를 초기화하십시오.
3. 'astro.config.mjs'에 다국어(i18n) 설정을 구성하십시오. (defaultLocale: 'ko', locales: ['ko', 'en'], routing: { prefixDefaultLocale: false }).
   라우팅은 한국어 홈('/', '/ko'), 영어 홈('/en'), 카테고리별 목록('/category/[category]', '/en/category/[category]'), 에피소드 상세('/lesson/[code]', '/en/lesson/[code]')로 구현하십시오.
4. 'src/styles/global.css'에 변수 기반 색상(딥블랙/딥네이비 HSL배경, 네온 바이올렛/블루 그라디언트 테두리 발광, 글래스모피즘 효과 카드)을 세팅하고 Inter, Outfit, Noto Sans KR 웹폰트를 연동하십시오.
5. 상세 화면에 YouTube 임베드 iframe 뷰어(없을 경우 대체 썸네일) 및 하단에 좌우 2컬럼(Side-by-Side) 형태의 한/영 대본 대조 학습 뷰어를 구현하십시오.
6. 'npm run build'가 에러 없이 작동하여 빌드가 통과하는지 확인하십시오.
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
