@echo off
chcp 65001 > nul
echo ========================================================
echo [Google Flow 자동 제어 크롬 실행 스크립트]
echo ========================================================
echo.
echo * 안내: 기존의 모든 크롬 브라우저 창을 닫은 뒤 이 스크립트를 실행해 주세요.
echo.
echo * 설명: 사용자의 모니터 세션에 직접 디버깅 크롬 창을 띄워 올립니다.
echo         이후 AI 에이전트가 이 화면을 직접 제어하는 모습을 눈으로 보실 수 있습니다.
echo.
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="d:\Entertainments\DevEnvironment\autovideo\assets\chrome_profile" --start-maximized
pause
