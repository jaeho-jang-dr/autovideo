# -*- coding: utf-8 -*-
"""greeting·cheer 를 확실한 오른쪽 옆모습으로 재생성(정면이라 미달)."""
import subprocess, os
from concurrent.futures import ThreadPoolExecutor, as_completed
ROOT="D:/Entertainments/DevEnvironment/autovideo"
REF=f"{ROOT}/assets/characters/cutouts/madam_jay_base_front.png"
PD=f"{ROOT}/assets/graphics/poses"
LOOK=("레퍼런스 이미지 "+REF+" 의 캐릭터(마담제이)와 옷·머리·색상·모양이 똑같아야 한다: "
      "연한 코랄/살몬 V넥 조끼(왼가슴 작은 주머니에 펜, 조끼 아래 주름 니트 밴드 밑단, 흰 속옷), "
      "흰색 A라인 무릎길이 치마, 진갈색 위로 올린 탑번 쪽머리(가운데 가르마+얼굴 양옆 웨이브 잔머리), "
      "점 눈 두 개+작은 미소, 크림색 둥근 손, 크림색 슬립온 신발, 가는 스틱 팔다리, 굵고 부드러운 검정 외곽선 플랫 카툰, 머리 크고 몸 작은 비율. ")
RIGHT="★★몸통·얼굴·시선 모두 완전히 오른쪽을 향한 오른쪽 옆모습(right side profile). 정면 금지, 왼쪽 금지. 코와 시선이 화면 오른쪽을 본다. "
FRAME="순백색 배경, 전신(머리끝~발끝) 다 보이게, 그림자·글자 없음, 투명 컷아웃용. "
JOBS=[
 ("greeting","서서 오른쪽을 향해 두 손을 앞(오른쪽)에 공손히 모으고 허리를 살짝 숙여 인사하는, 미소"),
 ("cheer","서서 오른쪽을 향해 두 손을 위로 들고 기뻐하는, 얼굴은 오른쪽 위를 보며 활짝 웃음"),
]
def run(j):
    name,pose=j; path=f"{PD}/mj_{name}.png"
    prompt=LOOK+RIGHT+FRAME+"포즈: "+pose+f". → {path} 에 저장."
    try:
        subprocess.run(["agy","-p",prompt,"--dangerously-skip-permissions"],capture_output=True,text=True,timeout=440,encoding="utf-8",errors="ignore")
        return f"{'OK' if os.path.exists(path) else 'MISS'} {name}"
    except Exception as e: return f"ERR {name}: {str(e)[:30]}"
print(f"{len(JOBS)}개 오른쪽 재생성",flush=True)
with ThreadPoolExecutor(max_workers=2) as ex:
    for f in as_completed({ex.submit(run,j):j for j in JOBS}): print(f.result(),flush=True)
print("DONE",flush=True)
