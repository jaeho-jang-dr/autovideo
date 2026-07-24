# -*- coding: utf-8 -*-
"""W11 교체용 신규 포즈 10 + 의자에 앉은 포즈 1 = 11개 (기존 재사용 대체, 스타일 통일)."""
import subprocess, os
from concurrent.futures import ThreadPoolExecutor, as_completed
ROOT="D:/Entertainments/DevEnvironment/autovideo"
REF=f"{ROOT}/assets/characters/cutouts/madam_jay_base_front.png"
PD=f"{ROOT}/assets/graphics/poses"
MJ=("레퍼런스 이미지 "+REF+" 의 캐릭터(마담제이)와 외형이 똑같아야 한다: 연한 코랄/살몬 V넥 선생님 조끼(왼가슴 작은 주머니에 펜, 조끼 아래 주름 니트 밑단, 흰 속옷), "
    "흰색 A라인 무릎 치마, 진갈색 위로 올린 탑번 쪽머리(가운데 가르마+양옆 웨이브 잔머리), 점 눈+작은 미소, 크림색 둥근 손, 크림색 슬립온, "
    "가는 스틱 팔다리, 굵은 검정 외곽선 플랫카툰, 머리 크고 몸 작은 비율. 이 외형 그대로 포즈만 바꿔 {path} 에 저장. "
    "순백색 배경, 전신, 캐릭터만({extra}그림자·글자 없음), 투명 컷아웃용. 포즈: {pose}")
ITEMS=[
 ("walk_left","걷는 동작, 왼쪽을 향해 한 발 앞으로 내딛으며 팔 자연스럽게 흔듦, 옆모습","의자·테이블·소품·"),
 ("walk_right","걷는 동작, 오른쪽을 향해 한 발 앞으로 내딛으며 팔 자연스럽게, 옆모습","의자·테이블·소품·"),
 ("point_left","서서 왼손 검지로 왼쪽 위를 가리키는, 몸은 왼쪽 향함, 미소","의자·테이블·소품·"),
 ("point_right","서서 오른손 검지로 오른쪽 위를 가리키는, 몸은 오른쪽 향함, 미소","의자·테이블·소품·"),
 ("presenting","서서 두 팔을 좌우로 벌려 무언가 소개하는 자세, 살짝 오른쪽 향함, 활짝 미소","의자·테이블·소품·"),
 ("raising_hand","서서 오른손을 위로 번쩍 든 자세(질문/부르기), 오른쪽 향함, 미소","의자·테이블·소품·"),
 ("greeting","서서 두 손을 앞으로 모으고 가볍게 고개 숙여 인사하는, 오른쪽 향함, 미소","의자·테이블·소품·"),
 ("cheering","두 손을 위로 들고 기뻐하는 만세 자세, 오른쪽 향함, 눈 감고 활짝 웃음","의자·테이블·소품·"),
 ("thinking","서서 오른손을 턱에 대고 고개 살짝 갸웃하며 생각하는, 오른쪽 향함","의자·테이블·소품·"),
 ("waving","서서 오른손을 들어 좌우로 흔드는 인사, 오른쪽 향함, 밝은 미소","의자·테이블·소품·"),
 # 의자에 앉은 포즈(의자 포함)
 ("sit_on_chair","소박한 나무 의자에 앉은 자세, 몸은 오른쪽을 향하고 두 손 무릎 위, 등 곧게, 미소. 나무 의자는 함께 그리되 테이블·음식은 그리지 말 것","테이블·소품·"),
]
def run(j):
    name,pose,extra=j; path=f"{PD}/madam_jay_w11_{name}.png"
    try:
        subprocess.run(["agy","-p",MJ.format(path=path,pose=pose,extra=extra),"--dangerously-skip-permissions"],
                       capture_output=True,text=True,timeout=420,encoding="utf-8",errors="ignore")
        return f"{'OK' if os.path.exists(path) else 'MISS'} {name}"
    except Exception as e: return f"ERR {name}: {str(e)[:30]}"
print(f"{len(ITEMS)}개 생성 시작(병렬4)",flush=True)
with ThreadPoolExecutor(max_workers=4) as ex:
    done=0
    for f in as_completed({ex.submit(run,j):j for j in ITEMS}):
        done+=1; print(f"[{done}/{len(ITEMS)}] {f.result()}",flush=True)
print("DONE",flush=True)
