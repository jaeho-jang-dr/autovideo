# -*- coding: utf-8 -*-
"""W11 v2 — 마담제이 포즈 전면 재생성(한 배치, 같은 옷·머리·색상). 앉기=30°돌아 의자포함, 걷기 좌우, 지급 등."""
import subprocess, os
from concurrent.futures import ThreadPoolExecutor, as_completed
ROOT="D:/Entertainments/DevEnvironment/autovideo"
REF=f"{ROOT}/assets/characters/cutouts/madam_jay_base_front.png"
PD=f"{ROOT}/assets/graphics/poses"
# 똑같은 옷·머리·색상(원래 마담제이) 고정 스크립트
LOOK=("레퍼런스 이미지 "+REF+" 의 캐릭터(마담제이)와 옷·머리·색상이 똑같아야 한다: "
      "연한 코랄/살몬 V넥 조끼(왼가슴 작은 주머니에 펜 꽂힘, 조끼 아래 주름 니트 밴드 밑단, 흰 속옷), "
      "흰색 A라인 무릎길이 치마, 진갈색 위로 올린 탑번 쪽머리(가운데 가르마+얼굴 양옆 웨이브 잔머리), "
      "점 눈 두 개+작은 미소, 크림색 둥근 손, 크림색 슬립온 신발, 가는 스틱 팔다리, 굵고 부드러운 검정 외곽선 플랫 카툰, "
      "머리 크고 몸 작은 비율. ")
FRAME="순백색 배경, ★전신 전체(머리끝~발끝) 다 보이게, 캐릭터가 프레임 세로로 비슷하게 꽉 차게(머리 위 여백 조금), 그림자·글자 없음, 투명 컷아웃용. "
def P(name, extra, pose):
    path=f"{PD}/mj_{name}.png"
    return (name, LOOK + FRAME.replace("그림자·글자 없음", extra+"그림자·글자 없음") + "포즈: " + pose + f" → 이 그림을 {path} 에 저장해줘.", path)

STAND=[
 ("walk_right","의자·","오른쪽을 향해 걷는 옆모습, 한 발 앞으로 내딛고 팔 자연스럽게 흔듦"),
 ("walk_left","의자·","왼쪽을 향해 걷는 옆모습, 한 발 앞으로 내딛고 팔 자연스럽게"),
 ("look_around","의자·","서서 오른쪽을 둘러보는, 한 손 이마에 살짝 얹고 호기심 표정"),
 ("greeting","의자·","서서 두 손을 앞에 모으고 살짝 고개 숙여 인사, 미소, 오른쪽 살짝 향함"),
 ("wave","의자·","서서 오른손을 들어 좌우로 흔드는 인사, 밝은 미소"),
 ("point_right","의자·","서서 오른손 검지로 오른쪽을 가리키는, 미소"),
 ("thinking","의자·","서서 오른손을 턱에 대고 고개 살짝 갸웃하며 생각하는"),
 ("cheer","의자·","두 손을 위로 들고 기뻐하는 만세, 눈 감고 활짝 웃음"),
 ("hungry","의자·","서서 두 손으로 배를 만지며 배고픈 아쉬운 표정, 오른쪽 향함"),
 ("presenting","의자·","서서 두 팔을 좌우로 벌려 무언가 소개하는, 활짝 미소"),
 ("pay_card","의자·","서서 오른손으로 카드를 앞(오른쪽)으로 내미는 카드 지급 동작, 미소"),
 ("pay_cash","의자·","서서 오른손으로 지폐(현금)를 앞(오른쪽)으로 내미는 현금 지급 동작"),
 ("get_receipt","의자·","서서 두 손으로 작은 영수증 종이를 받는, 오른쪽 향함"),
]
# 앉기: 오른쪽 30도 돌아 앉음 + 소박한 나무 의자 함께(자연스럽게, 엉거주춤 금지)
SIT=[
 ("sit_base","","소박한 나무 의자에 오른쪽으로 30도 돌아 자연스럽게 앉은 자세, 두 손 무릎 위, 등 곧게, 미소"),
 ("sit_menu","","나무 의자에 오른쪽 30도 돌아 앉아 두 손으로 메뉴판을 들고 내려다보는"),
 ("sit_point","","나무 의자에 오른쪽 30도 돌아 앉아 오른손 검지로 앞을 가리켜 고르는"),
 ("sit_call","","나무 의자에 오른쪽 30도 돌아 앉아 오른손을 위로 들어 점원을 부르는"),
 ("sit_eat","","나무 의자에 오른쪽 30도 돌아 앉아 오른손에 젓가락을 들고 먹는 동작"),
 ("sit_taste","","나무 의자에 오른쪽 30도 돌아 앉아 숟가락을 입에 가져가 맛보며 음미하는"),
 ("sit_drink","","나무 의자에 오른쪽 30도 돌아 앉아 물컵을 들어 마시는"),
 ("sit_receive","","나무 의자에 오른쪽 30도 돌아 앉아 두 손을 앞으로 내밀어 받는"),
]
jobs=[P(n,e,p) for n,e,p in STAND]+[P(n,"",p) for n,e2,p in SIT for e in [""]]
# SIT은 의자 포함이라 extra 비움
jobs=[P(n,e,p) for n,e,p in STAND]
for n,_,p in SIT:
    path=f"{PD}/mj_{n}.png"
    jobs.append((n, LOOK+"순백색 배경, ★전신(의자 포함) 다 보이게, 캐릭터가 프레임 세로로 비슷하게 꽉 차게, 그림자·글자 없음, 투명 컷아웃용. 포즈: "+p+f". 나무 의자는 함께 그리되 테이블·음식은 그리지 말 것. → {path} 에 저장.", path))

def run(j):
    name,prompt,path=j
    try:
        subprocess.run(["agy","-p",prompt,"--dangerously-skip-permissions"],capture_output=True,text=True,timeout=440,encoding="utf-8",errors="ignore")
        return f"{'OK' if os.path.exists(path) else 'MISS'} {name}"
    except Exception as e: return f"ERR {name}: {str(e)[:30]}"
print(f"총 {len(jobs)}개 포즈 생성(병렬4)",flush=True)
with ThreadPoolExecutor(max_workers=4) as ex:
    d=0
    for f in as_completed({ex.submit(run,j):j for j in jobs}):
        d+=1; print(f"[{d}/{len(jobs)}] {f.result()}",flush=True)
print("DONE",flush=True)
