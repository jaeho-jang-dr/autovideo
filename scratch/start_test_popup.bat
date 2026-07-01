@echo off
chcp 65001 >nul 2>&1
title 자동 승인 테스트 팝업
echo.
echo ======================================
echo   테스트 팝업을 띄웁니다...
echo   매크로가 작동하면 팝업이 자동으로 닫힙니다.
echo ======================================
echo.
d:
cd /d "d:\Entertainments\DevEnvironment\autovideo"
python scratch\test_gui_popup.py
pause
