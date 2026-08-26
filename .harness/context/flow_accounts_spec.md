# Google Flow 다중 계정 연동 명세서 (Multi-Account Spec)

본 문서는 추가 요금(Pay-as-you-go API 요금) 없이 구글 Flow의 무료 구독 쿼터를 최대한 활용하여 하루 50개 이상의 비디오 클립을 안정적으로 생성하기 위해 구축된 **6개 구글 다중 계정 순환 빌더**의 연동 현황 및 관리 가이드라인을 정의합니다.

---

## 1. 👥 계정 및 프로필 매핑 테이블

구글의 계정 로그인 세션(쿠키)은 아래의 격리된 크롬 사용자 프로필 디렉토리에 각각 독립적으로 안전하게 저장되어 있습니다.

| 인덱스 | 타겟 프로필 폴더 | 연동된 구글 계정 이메일 | 연동 상태 | 비고 |
| :---: | :--- | :--- | :---: | :--- |
| **0** | `assets/chrome_profile_0` | `drjang00@gmail.com` | **SUCCESS** | ✅ 2026-08-23 실측 확인 (아바타1·입력칸1) |
| **1** | `assets/chrome_profile_1` | `drjang000@gmail.com` | **SUCCESS** | ✅ 2026-08-23 사용 중 (무비랑 / 포트 9333) |
| **2** | `assets/chrome_profile_2` | `drjang001@gmail.com` | (사용 안 함) | ⚠️ **에이전트형 새 UI라 길이(8초) 설정이 없다.** 동영상 생성에 쓰지 마라 |
| **3** | `assets/chrome_profile_3` | `drjang002@gmail.com` | **FAIL** | ❌ 2026-08-23 실측 **로그아웃** (아바타0·입력칸0·'Get started' 노출) |
| **4** | `assets/chrome_profile_4` | `drjang003@gmail.com` | **FAIL** | ❌ 2026-08-23 실측 **로그아웃** (아바타0·입력칸0) |
| **5** | `assets/chrome_profile_5` | `drjang004@gmail.com` | **FAIL** | ❌ 2026-08-23 실측 **로그아웃** (아바타0·입력칸0) |

> ### ⚠️ 2026-08-23 갱신 기록 (캐릭터랑 실측)
> 이 표는 오래도록 **6개 전부 SUCCESS** 로 적혀 있었으나, 실제로는 **3·4·5 세션이 만료**돼
> 있었다. 그것을 모르고 `chrome_profile_3` 으로 Flow 를 돌려 첫 클립이 통째로 실패했다
> (편집기가 아니라 **로그인 안 된 영문 홍보 페이지**가 떴다).
>
> **판정은 짐작하지 말고 화면을 읽어라** — 아래 두 값이면 충분하다.
> * `googleusercontent` 계정 아바타 이미지 수 → **0 이면 로그아웃**
> * `div[role='textbox'][contenteditable='true']` 개수 → **1 이상이면 편집기 안착**
>
> 점검 스크립트: 프로필 하나를 내 포트로 띄워 위 둘을 읽고 바로 닫는다.
> ★점검할 때도 **무비랑(9333/profile_1)과 사장님 창(프로필 `User`)은 건드리지 않는다.**
> `taskkill /IM chrome` 은 절대 쓰지 말고, `--remote-debugging-port` 로 PID 를 골라 닫아라.

---

## 2. 🛡️ 세션 만료 시 로그인 재등록 가이드 (원격 디버깅 포트 우회)

구글 보안 봇 탐지 정책으로 인해 Playwright 자동화 모드 브라우저에서는 로그인이 차단될 수 있습니다. 세션이 만료되었거나 비밀번호 변경 등으로 재로그인이 필요한 경우, 아래의 **원격 디버깅 모드(CDP)**를 사용하여 실제 정식 구글 크롬으로 로그인 세션을 획득하십시오.

### 💡 로그인 명령어 (윈도우 CMD 전용)

열려 있는 모든 크롬 창을 완전히 종료한 후, **윈도우 명령 프롬프트(CMD) 창**에서 원하는 프로필 번호의 명령어를 복사하여 실행합니다:

```cmd
# 0번 계정 (drjang00@gmail.com)
start chrome --remote-debugging-port=9222 --user-data-dir="D:\Entertainments\DevEnvironment\autovideo\assets\chrome_profile_0"

# 1번 계정 (drjang000@gmail.com)
start chrome --remote-debugging-port=9222 --user-data-dir="D:\Entertainments\DevEnvironment\autovideo\assets\chrome_profile_1"

# 2번 계정 (drjang001@gmail.com)
start chrome --remote-debugging-port=9222 --user-data-dir="D:\Entertainments\DevEnvironment\autovideo\assets\chrome_profile_2"

# 3번 계정 (drjang002@gmail.com)
start chrome --remote-debugging-port=9222 --user-data-dir="D:\Entertainments\DevEnvironment\autovideo\assets\chrome_profile_3"

# 4번 계정 (drjang003@gmail.com)
start chrome --remote-debugging-port=9222 --user-data-dir="D:\Entertainments\DevEnvironment\autovideo\assets\chrome_profile_4"

# 5번 계정 (drjang004@gmail.com)
start chrome --remote-debugging-port=9222 --user-data-dir="D:\Entertainments\DevEnvironment\autovideo\assets\chrome_profile_5"
```
* **동작**: 크롬 창이 뜨면 구글 Flow(`https://labs.google/fx/tools/flow`)로 접속해 로그인을 정상 완료한 뒤, **해당 크롬 창을 완전히 닫아주시면** 세션이 해당 폴더에 안전하게 반영 저장됩니다.

---

## 3. 🤖 순환 가동 스케줄러 사용법

비디오 클립 대량 생성 시, 명령줄 끝에 `--profiles-count 6` 인자를 부여하여 실행합니다.

```powershell
python autoveo_flow.py --prompts prompts_for_veo.txt --profiles-count 6
```
* **동작 원리**: 씬 인덱스 번호를 기반으로 라운드 로빈 순환 모드로 크롬이 켜집니다. (`scene_n` 은 `n % 6` 번 프로필 계정을 활용해 빌드). 
* **이점**: 하나의 계정에 할당되는 요청 빈도가 최소화되어 구글 서버의 어뷰징 차단(Rate Limit)을 완벽하게 회피합니다.

---

## 🩺 4. 계정 세션 상태 자가 검증 방법

언제든지 6개 프로필의 로그인 세션 상태를 검사하고 싶다면 아래의 스크립트를 기동하십시오:

```powershell
# 프로젝트 루트 폴더에서 실행
python C:\Users\antigravity\.gemini\antigravity\brain\0f6238c4-5d7b-4f6a-a0d5-eb739122bc2d\scratch\verify_profiles.py
```
* **판독 기준**:
  * `SUCCESS`: 로그인 세션이 정상적으로 유효하여 Flow 본체 화면에 안착함.
  * `FAIL`: 로그인 세션이 만료되었거나 구글 로그인 로그인 폼으로 리다이렉트되어 튕겨나감 (재로그인 필요).
