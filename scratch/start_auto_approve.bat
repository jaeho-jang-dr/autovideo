@echo off
chcp 65001 >nul 2>&1
title Antigravity 자동 승인 매크로 v3
echo.
echo ======================================
echo   자동 승인 매크로를 시작합니다...
echo   이 창을 닫으면 매크로가 종료됩니다.
echo ======================================
echo.
d:
cd /d "d:\Entertainments\DevEnvironment\autovideo"
python scratch\auto_approve.py
pause
