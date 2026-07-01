# Flow 씬 생성 — 검증된 수동 레시피 (Claude Code CLI 재현용)

> 2026-06-13 binge_watching scene 1·2·3 으로 **엔드투엔드 검증**. autoveo_flow.py 자동화가
> 봇 감지/다운로드 타일 오인으로 막힐 때, 이 절차를 **그대로** 따르면 한 씬씩 확실히 만들 수 있다.
> 도구: `flow_driver.py` (라이브 브라우저를 띄워 둔 채 `debug/cmd/<n>.txt` 명령으로 한 단계씩 조작).
> 핵심 철학: **추측하지 말고 매 단계 스크린샷(`debug/_live.png`)·요소덤프(`debug/_live.json`)를 보고 좌표를 확인**한다.

---

## 명령 보내는 법
`flow_driver.py`는 `debug/cmd/1.txt, 2.txt, ...` 를 **순서대로** 읽어 실행하고, 매 명령 후
`debug/_live.png`(스크린샷) + `debug/_live.json`(요소 좌표) + `debug/_drv.log` 를 갱신한다.
- 한 번에 한 파일씩 쓰고 `debug/cmd/<n>.done` 이 생기면 다음으로.
- 명령: `clicktext|텍스트|ymin` · `clickxy|x|y` · `hover|x|y` · `fillprompt|텍스트` ·
  `key|Escape` · `wait|초` · `imgstatus` · `vidstatus` · `animate` · `newproject` · `goto|url` · `quit`
- 좌표는 **`debug/_live.json` 에서 실제 버튼을 찾아** 쓴다(아래 좌표는 2560×1249 기준 참고값; 해상도 다르면 반드시 재확인).

## 0. 시작 전 (충돌 방지)
```powershell
# chrome_profile 쓰는 chrome 전부 종료 + 락 삭제 (드라이버 동시 2개 금지)
Get-CimInstance Win32_Process -Filter "Name='chrome.exe'" | ?{ $_.CommandLine -like '*assets\chrome_profile*' } | %{ Stop-Process -Id $_.ProcessId -Force }
Remove-Item 'D:\Entertainments\DevEnvironment\autovideo\assets\chrome_profile\SingletonLock' -Force -ErrorAction SilentlyContinue
```
```bash
rm -f debug/_drv.log debug/_live.json; rm -rf debug/cmd; mkdir -p debug/cmd
python flow_driver.py > debug/flowdrv.log 2>&1 &   # READY 로그 나올 때까지 대기(자동으로 새 프로젝트 열림)
```

## A. 이미지 생성 (그 씬 이미지가 아직 없을 때)
1. **이미지 모드 맞추기.** `_live.png` 가 Agent 모드(하단에 `에이전트` 알약만, 모델칩 없음)면
   **에이전트 알약을 한 번** 클릭 → 모델칩 `🍌 Nano Banana 2 · 16:9 · 1x`(이미지 모드)가 자동으로 뜬다.
   - `clickxy|1065|1192` (에이전트 알약). **토글이라 짝수 번 누르면 원위치** — 누른 뒤 `_live.json` 으로
     모델칩이 떴는지 꼭 확인. (`clicktext|에이전트|540` 은 "에이전트 요청 사항" 등 다른 버튼을 잡을 수 있어 clickxy 권장)
   - 이미 모델칩이 `Nano Banana`(이미지)면 이 단계 생략.
2. `fillprompt|<이미지 프롬프트>`  (TED-Ed/채널 스타일 4레이어, `No watermark, no text...` 부정어 포함)
3. `clicktext|arrow_forward|540` → `wait|45` → `imgstatus`
4. **실패 시** (`_live.png` 에 "비정상적인 활동이 감지되었습니다" = 봇 일시 차단):
   타일 우하단 **`다시 시도`(refresh)** 버튼 클릭 → `wait|50` → `imgstatus`. 풀릴 때까지 1~2회 반복.
   - `_live.json` 에서 버튼 확인: `refresh 다시 시도`≈(687,453) · `undo 프롬프트 재사용`≈(727,453) · `삭제`≈(767,453)
   - **죽이지 말 것.** 봇 감지는 일시적이고 "다시 시도"로 풀린다.

## B. 영상화 (이미지 → 동영상)
5. `animate`  — 가장 큰 이미지 타일의 ⋮ → `애니메이션 적용`. 이미지가 **첫 프레임**으로 들어가고 `동영상·8s` 모드로 전환.
6. `fillprompt|<모션 프롬프트>`
7. `clicktext|arrow_forward|540` → `wait|110` → `vidstatus`  (DONE 나오면 완성)
8. 영상도 실패하면 A-4 와 동일하게 `다시 시도`.

## C. 다운로드 (★ 영상은 이미지의 "왼쪽" 타일)
9. 다운로드 직전 `ls debug/downloads/` 로 기존 파일 목록을 기록.
10. **왼쪽 영상 타일을 클릭** → 영상 플레이어가 열린다. 두 타일이 나란할 때 왼쪽 중심 ≈ `clickxy|436|276`.
    (오른쪽은 원본 이미지. `_live.json` 의 IMG 는 보통 오른쪽 이미지만 잡히고 영상은 `<video>` 라 안 잡힘)
11. 플레이어 우상단 **`다운로드` 버튼** 클릭 → `clickxy|2320|38`. (`_live.json` 에서 `download 다운로드` 확인)
    클릭하면 메뉴 없이 바로 받아진다.
12. 파일은 `debug/downloads/` 에 UUID 이름으로 떨어진다. **헤더가 `ftyp`(MP4)인지 검증**(JPEG=FFD8 면 영상 아님) 후
    `binge_watching/scene_<N>.mp4` 로 복사. ffprobe 로 8초·1280×720 확인.

## 좌표 빠른 참고 (2560×1249; 해상도 다르면 `_live.json`에서 재확인)
| 요소 | 좌표 |
|---|---|
| 에이전트 알약 | (1065,1192) |
| 모델칩(이미지/동영상) | (1458–1480,1192) |
| 모델칩 메뉴: 이미지 탭 | (1337,918) |
| 실패 타일: 다시 시도 / 프롬프트 재사용 / 삭제 | (687,453) / (727,453) / (767,453) |
| 왼쪽 영상 타일(클릭→플레이어) | (436,276) |
| 플레이어 다운로드 버튼 | (2320,38) |

## 함정 (반복 금지)
- **봇 감지("비정상적 활동")** → `다시 시도` 로 풀림. 프로세스/chrome **죽이지 말 것**(클라우드 저장이라 복구 가능, 화면만 날림).
- **영상 = 이미지의 왼쪽 타일.** 좌측 포스터를 무작정 받으면 렌더링 중엔 JPEG 포스터를 받는다 → 반드시 완성(`vidstatus` DONE) 후 왼쪽 타일 클릭→플레이어→다운로드.
- 좌표는 **매번 `_live.json` 으로 확인**(추측 클릭이 빗나가 컴포저를 망친다).
- 드라이버/크롬 **동시 2개 금지**, 실행 사이 `SingletonLock` 삭제.
