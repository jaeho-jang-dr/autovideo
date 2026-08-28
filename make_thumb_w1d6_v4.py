# -*- coding: utf-8 -*-
"""W1-6 최종 마스터 썸네일 v4 — 책 합성 정밀 보정(2026-08-28).
   ★사장님 지적(v3, 2026-08-28) — "책이 옷에 파묻혔네, 자연스럽지 못하다. 다시 만들어라."
   원인 진단(직접 확대 확인):
     1) v3의 책 도려내기 마스크가 "피부색도 셔츠 남색도 아니면 제거"라는 네거티브
        방식이어서, 책과 무관한 소매 안쪽 솔기선·옷깃 잉크선까지 bbox 안에 있다는
        이유만으로 함께 지워짐 → 새 책을 얹었을 때 어깨/소매에 점선 모양의 흰
        얼룩(핀홀)이 남아 "옷 속으로 파묻힌" 뭉개진 인상을 만들었다.
     2) 서양책(활짝 편 펼침 형태)과 새 고서(덮인 직사각 형태)의 실루엣이 달라
        구멍을 다 못 덮어 어깨 바로 위쪽에 살짝 틈(배경이 비치는 좁은 틈)이 있었다.
   수정(scratch/thumb_v3/step9~11 참조):
     - 마스크를 "책 색상 포지티브 매칭(밤색/금장/크림) + 그 근접(3px) 잉크선"으로
       바꿔 셔츠 솔기선·바지 허리단은 전혀 건드리지 않음(검증 완료).
     - 옛 책의 위쪽 펼친 페이지 흔적(칼라 근처 회백색 안티에일리어싱 유령선)만
       국소적으로(어깨 솔기선과 떨어진 좁은 구역, x<170) 추가 정리.
     - 새 고서를 격자 탐색(스케일/위치)으로 구멍을 화소 단위로 거의 완전히
       덮도록 배치(bw=290, bx=-15, by=138) → 배경이 비치는 틈 제거.
     - 구멍 경계 바로 바깥 옷/피부 픽셀에 옅은 그림자 링을 먹여(20~30% 어둡게)
       책이 옷 위에 얹혀 있는 입체감을 추가.
     - 손가락(원본 그대로 유지)이 항상 책보다 앞에 오도록 레이어 순서 유지.
   결과물: scratch/injun_book3q_korean_v2.png (확대 검증 완료 — 어깨/소매/허리단
   깨끗, 배경 틈 없음, 손가락-책 앞뒤관계 정상).
   배경: W1_6/bg/L1_andong_1k.png 그대로 유지(문구·레이아웃 v3와 동일, 포즈만 교체).
   규격: 1280x720 <2MB. KO/EN 각각 다른 파일 → _v4 로 저장(v3 파일 보존).
   사용: python make_thumb_w1d6_v4.py"""
import os
from PIL import Image, ImageDraw, ImageFont
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
W, H = 1280, 720
MALGUN = "C:/Windows/Fonts/malgunbd.ttf"
DONG = "assets/fonts/Cafe24Dongdong.ttf"
BG = "W1_6/bg/L1_andong_1k.png"
POSE = "W1_6/수동작업/인준_고서_좌측3q_투명.png"


def F(p, s): return ImageFont.truetype(p, s)


def outline(d, xy, txt, font, fill, oc=(26, 22, 18, 255), ow=6):
    x, y = xy
    for dx in range(-ow, ow + 1, 2):
        for dy in range(-ow, ow + 1, 2):
            d.text((x + dx, y + dy), txt, font=font, fill=oc)
    d.text((x, y), txt, font=font, fill=fill)


def cover(path, w, h):
    im = Image.open(path).convert("RGBA")
    r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r), int(im.height * r)))
    return im.crop(((im.width - w) // 2, (im.height - h) // 2,
                    (im.width - w) // 2 + w, (im.height - h) // 2 + h))


def build(lang):
    base = cover(BG, W, H)
    # 상단·하단 그라데이션 — 글자 대비 확보(배경 그림 자체는 최대한 보존)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d0 = ImageDraw.Draw(ov)
    for i in range(300):
        d0.rectangle([0, i, W, i + 1], fill=(18, 22, 30, int(150 * (1 - i / 300))))
    for i in range(190):
        d0.rectangle([0, H - 190 + i, W, H - 190 + i + 1], fill=(15, 14, 20, int(140 * i / 190)))
    base.alpha_composite(ov)

    # 인준(오른쪽, 반듯이 서서 왼쪽 3/4 자세로 우리 고서 '훈민정음'을 두 손으로 든 모습)
    pose = Image.open(POSE).convert("RGBA")
    ph = 640; pw = int(pose.width * ph / pose.height)
    pose = pose.resize((pw, ph), Image.Resampling.LANCZOS)
    px = W - pw - 110  # 우측 110px 안쪽 여백으로 몸/손/책 잘림 완전 방지
    py = H - ph - 20   # 바닥에서 20px 띄움
    base.alpha_composite(pose, (px, py))

    d = ImageDraw.Draw(base)
    if lang == "ko":
        outline(d, (46, 30), "훈민정음", F(MALGUN, 84), (255, 255, 255))
        outline(d, (46, 122), "한글날", F(MALGUN, 118), (255, 214, 90))
        outline(d, (50, 262), "지켜 낸 사람들", F(DONG, 44), (180, 235, 255), ow=4)
        outline(d, (50, 318), "그 이야기", F(DONG, 44), (180, 235, 255), ow=4)
    else:
        outline(d, (46, 34), "Hunminjeongeom", F(MALGUN, 62), (255, 255, 255))
        outline(d, (46, 118), "Hangeul Day", F(MALGUN, 92), (255, 214, 90))
        outline(d, (50, 244), "How Hangeul", F(DONG, 42), (180, 235, 255), ow=4)
        outline(d, (50, 298), "Was Saved", F(DONG, 42), (180, 235, 255), ow=4)
    tag = "안동 · W1-6" if lang == "ko" else "Andong · W1-6"
    tf = F(MALGUN, 30); tw = d.textlength(tag, font=tf)
    outline(d, (W - tw - 30, 24), tag, tf, (255, 255, 255), ow=4)
    out = f"hangeul_birth_vowels/thumb_w1d6_final_{lang}_v4_1280x720.jpg"
    base.convert("RGB").save(out, quality=92)
    print(f"{out}  ({os.path.getsize(out)//1024}KB)")


for lg in ("ko", "en"):
    build(lg)
