# -*- coding: utf-8 -*-
"""W11 v3 — 마담제이 포즈 전부 새로. ★모두 오른쪽 향함(앉기·말·인사·계산·메뉴). 같은 옷·색·모양. 사이즈는 후처리 정규화로 통일."""
import subprocess, os
from concurrent.futures import ThreadPoolExecutor, as_completed
ROOT="D:/Entertainments/DevEnvironment/autovideo"
REF=f"{ROOT}/assets/characters/cutouts/madam_jay_base_front.png"
PD=f"{ROOT}/assets/graphics/poses"
LOOK=("레퍼런스 이미지 "+REF+" 의 캐릭터(마담제이)와 옷·머리·색상·모양이 똑같아야 한다: "
      "연한 코랄/살몬 V넥 조끼(왼가슴 작은 주머니에 펜, 조끼 아래 주름 니트 밴드 밑단, 흰 속옷), "
      "흰색 A라인 무릎길이 치마, 진갈색 위로 올린 탑번 쪽머리(가운데 가르마+얼굴 양옆 웨이브 잔머리), "
      "점 눈 두 개+작은 미소, 크림색 둥근 손, 크림색 슬립온 신발, 가는 스틱 팔다리, 굵고 부드러운 검정 외곽선 플랫 카툰, 머리 크고 몸 작은 비율. ")
RIGHT="★몸통·얼굴·시선 모두 오른쪽을 향한다(오른쪽 3/4 또는 옆모습). 왼쪽을 향하면 안 된다. "
FRAME="순백색 배경, 전신(머리끝~발끝) 다 보이게, 그림자·글자 없음, 투명 컷아웃용. "
STAND=[
 ("walk_right","오른쪽으로 걷는 옆모습, 한 발 앞으로 내딛고 팔 자연스럽게"),
 ("look_around","서서 오른쪽을 둘러보는, 한 손 이마에 살짝, 호기심"),
 ("greeting","서서 오른쪽을 향해 두 손 모으고 살짝 고개 숙여 인사, 미소"),
 ("wave","서서 오른쪽을 향해 오른손 들어 흔드는 인사, 밝은 미소"),
 ("point_right","서서 오른손 검지로 오른쪽을 가리키는, 미소"),
 ("thinking","서서 오른쪽 향해 오른손 턱에 대고 고개 갸웃 생각"),
 ("cheer","서서 오른쪽 향해 두 손 위로 들고 기뻐하는, 활짝 웃음"),
 ("hungry","서서 오른쪽 향해 두 손으로 배 만지며 배고픈 표정"),
 ("presenting","서서 오른쪽을 향해 두 손을 펼쳐 무언가 소개하는, 미소"),
 ("pay_card","서서 오른쪽을 향해 오른손으로 카드를 내미는 카드 지급, 미소"),
 ("pay_cash","서서 오른쪽을 향해 오른손으로 지폐(현금)를 내미는 현금 지급"),
 ("get_receipt","서서 오른쪽을 향해 두 손으로 영수증 종이를 받는"),
]
SIT=[
 ("sit_base","나무 의자에 앉아 오른쪽(30도)을 향해 자연스럽게 앉은 자세, 두 손 무릎, 미소"),
 ("sit_menu","나무 의자에 오른쪽 향해 앉아 두 손으로 메뉴판을 들고 보는"),
 ("sit_point","나무 의자에 오른쪽 향해 앉아 오른손 검지로 앞(오른쪽)을 가리키는"),
 ("sit_call","나무 의자에 오른쪽 향해 앉아 오른손을 위로 들어 점원을 부르는"),
 ("sit_eat","나무 의자에 오른쪽 향해 앉아 오른손 젓가락으로 먹는"),
 ("sit_taste","나무 의자에 오른쪽 향해 앉아 숟가락을 입에 가져가 맛보는"),
 ("sit_drink","나무 의자에 오른쪽 향해 앉아 물컵을 들어 마시는"),
 ("sit_receive","나무 의자에 오른쪽 향해 앉아 두 손을 앞으로 내밀어 받는"),
]
jobs=[]
for n,p in STAND:
    path=f"{PD}/mj_{n}.png"
    jobs.append((n, LOOK+RIGHT+FRAME+"포즈: "+p+f". → {path} 에 저장.", path))
for n,p in SIT:
    path=f"{PD}/mj_{n}.png"
    jobs.append((n, LOOK+RIGHT+"순백색 배경, 전신(의자 포함) 다 보이게, 그림자·글자 없음, 투명 컷아웃용. 포즈: "+p+f". 나무 의자는 함께 그리되 테이블·음식은 그리지 말 것. → {path} 에 저장.", path))
def run(j):
    name,prompt,path=j
    try:
        subprocess.run(["agy","-p",prompt,"--dangerously-skip-permissions"],capture_output=True,text=True,timeout=440,encoding="utf-8",errors="ignore")
        return f"{'OK' if os.path.exists(path) else 'MISS'} {name}"
    except Exception as e: return f"ERR {name}: {str(e)[:30]}"
print(f"총 {len(jobs)}개(전부 오른쪽 향함)",flush=True)
with ThreadPoolExecutor(max_workers=4) as ex:
    d=0
    for f in as_completed({ex.submit(run,j):j for j in jobs}):
        d+=1; print(f"[{d}/{len(jobs)}] {f.result()}",flush=True)
print("DONE",flush=True)
