# stop_auto_collaboration.ps1
# Claude-Gemini 양방향 협업 자동화 프로세스 중단 스크립트 (Windows 전용)
# =======================================================================

$TargetScripts = @("auto_approve.py", "agent_chain_runner.py")

Write-Host "==========================================================" -ForegroundColor Yellow
Write-Host " Claude-Gemini Auto-Collaboration Terminator" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Yellow

foreach ($script in $TargetScripts) {
    # CommandLine을 매칭하여 정확히 관련 python 프로세스만 타겟팅
    $processes = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like "*$script*" }
    
    if ($processes) {
        foreach ($proc in $processes) {
            Write-Host "발견: $script (PID: $($proc.ProcessId)) 종료 시도..." -NoNewline
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
            Write-Host " [종료 완료]" -ForegroundColor Green
        }
    } else {
        Write-Host "알림: 실행 중인 $script 프로세스가 없습니다." -ForegroundColor Gray
    }
}

Write-Host "==========================================================" -ForegroundColor Yellow
