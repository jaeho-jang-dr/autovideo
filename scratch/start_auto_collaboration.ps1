# start_auto_collaboration.ps1
# Claude-Gemini 양방향 협업 자동화 런처 스크립트 (Windows 전용)
# =======================================================================

$ErrorActionPreference = "Stop"

# 루트 디렉토리 및 로그 디렉토리 확인
$ScratchDir = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $ScratchDir

$ApproveLog = Join-Path $ScratchDir "auto_approve.log"
$ApproveErrLog = Join-Path $ScratchDir "auto_approve_err.log"
$RunnerLog = Join-Path $ScratchDir "agent_chain_runner.log"
$RunnerErrLog = Join-Path $ScratchDir "agent_chain_runner_err.log"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Claude-Gemini Auto-Collaboration Launcher" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# python 및 스크립트 절대 경로 획득
$PythonPath = (Get-Command python).Source
$ApproveScript = Join-Path $ScratchDir "auto_approve.py"
$RunnerScript = Join-Path $ScratchDir "agent_chain_runner.py"

# 1. auto_approve.py 백그라운드 실행
Write-Host "[1/2] 승인 매크로(auto_approve.py) 기동 중..." -NoNewline
$ApproveCmd = "`"$PythonPath`" `"$ApproveScript`""
$ApproveResult = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $ApproveCmd; CurrentDirectory = $ProjectRoot }

if ($ApproveResult.ReturnValue -eq 0) {
    Write-Host " [성공] (PID: $($ApproveResult.ProcessId))" -ForegroundColor Green
    Write-Host "       로그: $ApproveLog" -ForegroundColor Gray
} else {
    Write-Host " [실패] (오류코드: $($ApproveResult.ReturnValue))" -ForegroundColor Red
    exit 1
}

# 2. agent_chain_runner.py 백그라운드 실행
Write-Host "[2/2] 에이전트 연쇄 모니터(agent_chain_runner.py) 기동 중..." -NoNewline
$RunnerCmd = "`"$PythonPath`" -u `"$RunnerScript`""
$RunnerResult = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $RunnerCmd; CurrentDirectory = $ProjectRoot }

if ($RunnerResult.ReturnValue -eq 0) {
    Write-Host " [성공] (PID: $($RunnerResult.ProcessId))" -ForegroundColor Green
    Write-Host "       로그: $RunnerLog" -ForegroundColor Gray
} else {
    Write-Host " [실패] (오류코드: $($RunnerResult.ReturnValue))" -ForegroundColor Red
    # 승인 매크로 종료 시도
    Stop-Process -Id $ApproveResult.ProcessId -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "----------------------------------------------------------" -ForegroundColor Yellow
Write-Host "✔ 모든 프로세스가 백그라운드에서 정상 시작되었습니다!" -ForegroundColor Green
Write-Host "모니터링 방법:" -ForegroundColor Yellow
Write-Host "  * 체인 모니터 로그 실시간 확인:" -ForegroundColor White
Write-Host "    Get-Content -Path '$RunnerLog' -Wait" -ForegroundColor Gray
Write-Host "  * 승인 매크로 로그 실시간 확인:" -ForegroundColor White
Write-Host "    Get-Content -Path '$ApproveLog' -Wait" -ForegroundColor Gray
Write-Host "중단 방법:" -ForegroundColor Yellow
Write-Host "  * stop_auto_collaboration.ps1 스크립트를 실행하십시오." -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan
