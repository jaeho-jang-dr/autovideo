# -*- coding: utf-8 -*-
"""W11 약한 포즈 3개 재생성(동작 뚜렷하게)."""
import subprocess, os
from concurrent.futures import ThreadPoolExecutor, as_completed
ROOT = "D:/Entertainments/DevEnvironment/autovideo"
REF = f"{ROOT}/assets/characters/cutouts/madam_jay_base_front.png"
PD = f"{ROOT}/assets/graphics/poses"
MJ = ("레퍼런스 이미지 " + REF + " 의 캐릭터(마담제이)와 외형이 똑같아야 한다: 연한 코랄 V넥 선생님 조끼(왼가슴 펜주머니, 니트 밑단), "
      "흰 A라인 무릎 치마, 진갈색 탑번 쪽머리(양옆 웨이브 잔머리), 점 눈+작은 미소, 크림색 둥근 손, 크림색 슬립온, "
      "가는 스틱 팔다리, 굵은 검정 외곽선 플랫카툰, 머리 크고 몸 작은 비율. 이 외형 그대로 포즈만 바꿔 {path} 에 저장. "
      "순백색 배경, 전신, 캐릭터만(의자·테이블·그림자·글자 없음), 투명 컷아웃용, 몸은 오른쪽 향함. 포즈: {pose}")
FIX = [
 ("size_gesture", "의자 없이 무릎 굽혀 앉은 자세로 두 팔을 좌우로 활짝 크게 벌려 '양이 이만큼 많다'를 과장되게 표현, 눈 크게 뜨고 놀란 즐거운 표정, 오른쪽 향함"),
 ("stand_up", "의자에서 막 일어서는 순간의 동작 — 무릎을 반쯤 굽히고 상체를 앞으로 세우며 한 손으로 허벅지를 짚고 몸을 일으키는 중, 오른쪽 향함"),
 ("pat_belly", "서서 두 손으로 불룩한 배를 토닥토닥 두드리며 '배부르다' 만족 표정, 눈 감고 활짝 웃음, 오른쪽 향함"),
]
def run(j):
    name,pose=j; path=f"{PD}/madam_jay_w11_{name}.png"
    try:
        subprocess.run(["agy","-p",MJ.format(path=path,pose=pose),"--dangerously-skip-permissions"],
                       capture_output=True,text=True,timeout=420,encoding="utf-8",errors="ignore")
        return f"{'OK' if os.path.exists(path) else 'MISS'} {name}"
    except Exception as e: return f"ERR {name}: {str(e)[:30]}"
print("3개 재생성 시작",flush=True)
with ThreadPoolExecutor(max_workers=3) as ex:
    for f in as_completed({ex.submit(run,j):j for j in FIX}): print(f.result(),flush=True)
print("DONE",flush=True)
