# youtuberang 일일 댓글 응대 루틴 (매일 새벽 2시, Windows 작업 스케줄러가 호출)
# ① 디버그 크롬(9222) 확인/기동  ② claude 헤드리스로 댓글 스캔·분류·하트·답글·이메일
$ErrorActionPreference = 'Continue'
Set-Location "D:\Entertainments\DevEnvironment\autovideo"
if (-not (Test-Path 'logs')) { New-Item -ItemType Directory -Path 'logs' | Out-Null }
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$log = "logs\daily_comments_$stamp.log"

# 1) 디버그 크롬(9222) 살아있나 확인, 없으면 기동
$alive = $false
try {
    $r = Invoke-WebRequest -Uri 'http://localhost:9222/json/version' -TimeoutSec 5 -UseBasicParsing
    if ($r.StatusCode -eq 200) { $alive = $true }
} catch {}
if (-not $alive) {
    Start-Process -FilePath 'C:\Program Files\Google\Chrome\Application\chrome.exe' `
        -ArgumentList '--remote-debugging-port=9222',
                      '--user-data-dir=d:\Entertainments\DevEnvironment\autovideo\assets\chrome_profile',
                      '--start-maximized'
    Start-Sleep -Seconds 20
}

# 2) claude 헤드리스로 일일 댓글 루틴 실행
$prompt = @'
[유튜브랑 일일 댓글 응대 루틴 — 자동 실행]
1) Bash로 curl http://localhost:9222/json/version 확인(없으면 종료).
2) `PYTHONIOENCODING=utf-8 python survey_comments.py` 로 YouTube Studio 댓글 수신함(채널 UC6KCrgUSdSVUd97b7ltJK_g, 응답없음)을 스캔하고 scratch/yt/survey_inbox.png 스크린샷을 읽어 새 댓글 목록·작성자·언어를 파악한다.
3) 각 댓글을 분류한다. 아래는 하트도 답글도 하지 말고 그대로 둔다(사장님이 나중에 검토):
   - 내 고정댓글 / 내가 수동으로 답한 댓글(이미 답글 있음)
   - 지금 당장 연락·전화번호·연락처 요구·오프플랫폼 연락 유도
   - 갑자기 도와주겠다는 권유/제안류
   - 비밀번호·비밀·.env 등 보안 민감 정보 요구
   - 인신공격·성적인 말·욕설·나쁜말·기분 나쁜말
4) 위에 해당하지 않는 선량한 댓글에만 `PYTHONIOENCODING=utf-8 python reply_comment.py "<작성자핸들>" "<답글>"` 로 ❤️하트 + 그 댓글 언어로 2줄 이내·존댓말로 따뜻·친절·성실하게 답한다(아는 것은 답). 스크린샷으로 hearted/submitted 검증.
5) 처리결과(답한 댓글 / 보류한 댓글과 사유)를 정리해 drjang00@gmail.com 로 요약 이메일을 보낸다(Gmail 도구 사용). 이메일이 불가하면 요약을 logs\daily_comments_summary_당일날짜.md 로 저장한다. 새 댓글이 없거나 전부 보류면 아무 것도 게시하지 말고 조용히 종료.
원칙: 환자유도·의사권위 금지, 사적 연락처 약속 금지, 욕/반말 금지.
'@

# google-workspace MCP를 발송용으로 잠깐만 활성화 → 루틴 실행 → 끝나면 비활성화
& claude mcp add-json google-workspace '{"type":"stdio","command":"cmd","args":["/c","npx","-y","@presto-ai/google-workspace-mcp"],"env":{}}' --scope local *>> $log 2>&1
& claude -p $prompt --dangerously-skip-permissions *>> $log 2>&1
& claude mcp remove google-workspace --scope local *>> $log 2>&1
"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] 일일 댓글 루틴 종료 (alive=$alive, google-workspace 잠깐 켰다 끔)" | Out-File -FilePath $log -Append -Encoding utf8
