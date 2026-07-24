# Google Flow 다중 계정 연동 명세서 (Multi-Account Spec)

본 문서는 추가 요금(Pay-as-you-go API 요금) 없이 구글 Flow의 무료 구독 쿼터를 최대한 활용하여 하루 50개 이상의 비디오 클립을 안정적으로 생성하기 위해 구축된 **6개 구글 다중 계정 순환 빌더**의 연동 현황 및 관리 가이드라인을 정의합니다.

---

## 1. 👥 계정 및 프로필 매핑 테이블

구글의 계정 로그인 세션(쿠키)은 아래의 격리된 크롬 사용자 프로필 디렉토리에 각각 독립적으로 안전하게 저장되어 있습니다.

| 인덱스 | 타겟 프로필 폴더 | 연동된 구글 계정 이메일 | 연동 상태 | 비고 |
| :---: | :--- | :--- | :---: | :--- |
| **0** | `assets/chrome_profile_0` | `drjang00@gmail.com` | **SUCCESS** | 정상 연동 확인 완료 |
| **1** | `assets/chrome_profile_1` | `drjang000@gmail.com` | **SUCCESS** | 정상 연동 확인 완료 |
| **2** | `assets/chrome_profile_2` | `drjang001@gmail.com` | **SUCCESS** | 정상 연동 확인 완료 |
| **3** | `assets/chrome_profile_3` | `drjang002@gmail.com` | **SUCCESS** | 정상 연동 확인 완료 |
| **4** | `assets/chrome_profile_4` | `drjang003@gmail.com` | **SUCCESS** | 정상 연동 확인 완료 |
| **5** | `assets/chrome_profile_5` | `drjang004@gmail.com` | **SUCCESS** | 정상 연동 확인 완료 |

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
