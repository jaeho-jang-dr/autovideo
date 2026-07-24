# 3D 캐릭터 애니메이션 파이프라인 — 제미나이 인수 문서

> **목표**: 무료 3D "원형 캐릭터"를 Blender(bpy) 파이썬만으로 렌더하고,
> drjayed 캐릭터(마담제이 등) 외형을 입혀, 장소 배경(광장시장 등)에 합성한다.
> Adobe/Mixamo 불필요. 모든 게 로컬 파이썬으로 자동화됨.
>
> 작성: Claude(감독). 실행/개선: 제미나이(조감독). 최종 검증: 사장님.

---

## 0. 핵심 요약 (한 줄)
`bpy`(Blender 5.1.2 파이썬 모듈, 이미 설치됨) → Quaternius CC0 캐릭터 GLB 임포트 →
동작 45종 중 선택 → 부위별 재질로 마담제이 외형 입힘 → 투명배경 렌더 → PIL로 장소 배경에 발 앵커 합성 → mp4.

---

## 1. 준비물 (이미 다 있음)

| 항목 | 위치 / 값 | 비고 |
|------|-----------|------|
| 렌더 엔진 | `python -c "import bpy"` → **5.1.2** | pip 설치 완료. 헤드리스 EEVEE 렌더 됨 |
| 베이스 캐릭터 | `scratch/mocap/quaternius_char.glb` (2.2MB) | Quaternius "Animated Base Character" |
| 캐릭터 출처 | https://static.poly.pizza/0b65e14d-a349-44cc-836c-efdeb6933d48.glb | Poly Pizza, **CC-BY 3.0**(Quaternius). 재다운로드 시 이 URL |
| 리그 | Rigify식 `DEF-*` 본 (hips/spine.001~003/neck/head/shoulder/upper_arm/forearm/hand/thigh/shin/foot/toe + 손가락) | 부위별 웨이트로 재질 분리 가능 |
| 메시 | `Mannequin` (재질 M_Main, M_Joints) + `Icosphere`(효과, **렌더 숨김**) | |
| 배경 | `assets/graphics/bg/bg_w8_01.png` (광장시장) 등 | 다른 장소도 동일 방식 |
| 마담제이 2D 레퍼런스 | `assets/characters/madam_jay_base_front.png` | 갈색 윗묶음·밝은 피부·산호 조끼(선생님)·흰 치마·흰 신발·점눈·작은코·미소 |

### ⚠️ 반드시 알아야 할 함정 (GLB 100배 스케일)
GLB 임포트 시 armature/mesh의 `matrix_world` **스케일이 100배**다.
- 머리 부착물(머리번·눈)을 본에 `parent_set`하면 1/100로 쪼그라들어 **안 보인다**.
- **해결**: 부착물을 월드좌표로 만든 뒤 **`bpy.ops.object.join()`으로 메시에 합치고**(월드→로컬 변환 자동), 새 정점을 `DEF-head` 버텍스그룹에 weight 1.0으로 넣어 머리 따라가게 함. (스크립트에 구현됨)

### 좌표계
- **정면 = +Y** (얼굴이 +Y). 카메라는 +Y쪽에서 -Y 바라봄. `cam.location = (cx, cy + dist, cz)`, `dist = 캐릭터높이 * 2.4`.

---

## 2. 동작 45종 (액션 이름)
```
Dance_Loop ← 가장 화려/재밌음      Idle_Talking_Loop ← 선생님 설명
Walk_Loop, Walk_Formal_Loop, Jog_Fwd_Loop, Sprint_Loop
Idle_Loop, Sitting_Idle_Loop, Sitting_Talking_Loop, Sitting_Enter/Exit
Jump_Start/Loop/Land, Crouch_Fwd/Idle, Push_Loop, Roll, Swim_Fwd/Idle
Punch_Cross/Jab/Enter, Sword_Attack/Idle, Spell_Simple_Enter/Idle/Shoot/Exit
Pistol_*, Driving_Loop, PickUp_Table, Fixing_Kneeling, Interact, Hit_Chest/Head, Death01
```
선생님 캐릭터 추천: **Idle_Talking_Loop, Sitting_Talking_Loop, Walk_Loop, Dance_Loop**.

---

## 3. 스크립트 (완성, 그대로 실행)

### A. 베이스 캐릭터 렌더 — `scratch/render_glb.py`
```bash
python scratch/render_glb.py dance      # 원하는 동작 이름 일부(walk/idle_talking/sitting_talking/dance...)
```
- GLB 임포트 → 동작 선택 → 투명배경 1280×720 EEVEE 렌더 → `scratch/glb_frames/f*.png`
- 카메라 자동 프레이밍(정면 +Y), 3점 조명.

### B. 마담제이 외형 입혀 렌더 — `scratch/render_madam.py`
```bash
python scratch/render_madam.py dance
```
- **부위별 재질**(핵심): 정점 지배 본으로 얼굴 나눠 material_index 지정
  | 부위(본) | 재질 |
  |---|---|
  | `DEF-spine*`, `shoulder` | 산호 조끼 (0.94,0.46,0.40) |
  | `DEF-hips`, `thigh`, `foot`, `toe` | 흰색 (치마·신발) |
  | 나머지(head/neck/arm/hand/shin) | 피부 (0.98,0.89,0.83) |
- **머리번(윗묶음)·눈·코·입**: 구体 만들어 `join` → `DEF-head` 웨이트 (100배 함정 회피)
- 투명배경 렌더 → `scratch/madam_frames/f*.png`

### C. 장소 배경 합성 (PIL) — 아래 스니펫 (render 뒤 실행)
```python
from PIL import Image
import os, glob, imageio_ffmpeg, subprocess
bg = Image.open('assets/graphics/bg/bg_w8_01.png').convert('RGBA')
s = max(1280/bg.width, 720/bg.height); bg = bg.resize((int(bg.width*s), int(bg.height*s)), Image.LANCZOS)
bg = bg.crop(((bg.width-1280)//2,(bg.height-720)//2,(bg.width-1280)//2+1280,(bg.height-720)//2+720))
os.makedirs('scratch/comp_frames', exist_ok=True)
frames = sorted(glob.glob('scratch/madam_frames/*.png'))
ref = Image.open(frames[0]).convert('RGBA'); rb = ref.getbbox()
SCALE = 470/(rb[3]-rb[1]); FX, FY = 540, 668          # 캐릭터 목표 높이/발 위치(광장시장 바닥)
for i, fp in enumerate(frames):
    ch = Image.open(fp).convert('RGBA'); ch = ch.resize((int(ch.width*SCALE), int(ch.height*SCALE)), Image.LANCZOS)
    bb = ch.getbbox()                                 # 발=알파 bbox 하단, 중심=가로중앙 → 지터 없음
    out = bg.copy(); out.alpha_composite(ch, (FX-(bb[0]+bb[2])//2, FY-bb[3]))
    out.convert('RGB').save(f'scratch/comp_frames/c{i:04d}.png')
FF = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([FF,'-y','-framerate','24','-pattern_type','glob','-i','scratch/comp_frames/*.png',
                '-c:v','libx264','-pix_fmt','yuv420p','-crf','20','scratch/madam_market_dance.mp4'])
```
- **발 앵커**: 매 프레임 알파 bbox 하단을 바닥 `FY`에, 가로중심을 `FX`에 맞춤 → 공중부양·지터 방지.
- 고정 SCALE(첫 프레임 높이 기준)로 크기 일정.

---

## 4. 지금까지 결과 / 남은 개선점 (제미나이 TODO)

**됨**: 3D 렌더·동작 45종·부위별 재질(산호조끼·흰치마·흰신발)·머리번·눈코입·광장시장 합성·발앵커·mp4.

**개선 필요**:
1. **회색빛/창백함** — 정면 조명 넣었지만 아직 살짝 뜬다. 키라이트 세기·피부 채도(`SKIN` 값) 튜닝. EEVEE `film_transparent` + 배경합성 특성상 앰비언트 밸런스 조정.
2. **얼굴 디테일** — 눈코입이 구体라 거칠다. (a)위치·크기 미세조정, 또는 (b)**얼굴 텍스처/데칼**(2D 마담제이 얼굴 PNG를 머리 앞면 평면에 붙이기)로 교체하면 훨씬 깔끔.
3. **머리 윗묶음** — 더 단정하게(캡 매끈·번 위치). 사장님 지적사항.
4. **키·비율 변형** — 전체 스케일=키, 부위 스케일=비율(머리 크게=더 만화). 요청 시 조절.
5. **다른 캐릭터** — 같은 베이스에 인준/지은/닥터제이 재질만 바꿔 재사용(원형의 목적).
6. **장소별 발 위치(FX,FY)·SCALE** 배경마다 조정 필요.

---

## 5. 제미나이 실행 순서 (권장)
1. `python scratch/render_madam.py idle_talking` (선생님 설명 동작) 렌더 확인
2. 위 3-C 합성 스니펫으로 광장시장(또는 다른 장소) 배경 합성 → mp4
3. 사장님께 mp4 띄워 보여드리고 피드백 받기
4. 피드백대로 `render_madam.py`의 재질색/머리/얼굴/조명, 합성의 FX·FY·SCALE 수정
5. 확정되면 인준/지은/닥터제이용으로 재질 매핑만 바꿔 복제

**소통 규약**: `GEMINI.md` 및 듀얼-AI 인계 프로토콜 따름. 큰 변경(렌더 대량·업로드)은 사장님 확인 후.
