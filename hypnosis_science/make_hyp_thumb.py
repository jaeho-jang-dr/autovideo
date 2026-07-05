# -*- coding: utf-8 -*-
"""최면 썸네일 (한/영): 회중시계 이미지 + 캐치 제목 + 로고. 1280x720 jpg <2MB.
사용: python hypnosis_science/make_hyp_thumb.py"""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
ROOT="D:/Entertainments/DevEnvironment/autovideo"; HS=os.path.join(ROOT,"hypnosis_science")
S=3                    # 3x → 3840x2160(4K) 고해상도 (대형 TV 대비, 텍스트·로고 크리스프)
W,H=1280*S,720*S
MALGUN=r"C:\Windows\Fonts\malgunbd.ttf"; ARIALBD=r"C:\Windows\Fonts\arialbd.ttf"

# 배경: 회중시계(씬1) 클린 프레임
bgsrc=os.path.join(ROOT,"scratch","hyp","s1.png")
if not os.path.exists(bgsrc):
    subprocess.run(["ffmpeg","-y","-v","error","-ss","1","-i",os.path.join(HS,"scene_1.mp4"),"-frames:v","1",bgsrc])

def make(lang, title, sub):
    bg=Image.open(bgsrc).convert("RGB").resize((W,H),Image.LANCZOS)
    # 좌측 어둡게(텍스트 대비) — 좌→우 그라디언트 오버레이
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); od=ImageDraw.Draw(ov)
    for x in range(W):
        a=int(180*max(0,(1-x/(W*0.72))))
        od.line([(x,0),(x,H)],fill=(8,6,20,a))
    im=Image.alpha_composite(bg.convert("RGBA"),ov)
    d=ImageDraw.Draw(im)
    font=MALGUN if lang=="ko" else ARIALBD
    # 제목 (큰 글씨, 좌측) — 전부 S배 스케일
    tf=ImageFont.truetype(font, (96 if lang=="ko" else 88)*S)
    lines=title.split("\n"); y=140*S
    for ln in lines:
        d.text((70*S,y), ln, font=tf, fill=(255,240,150), stroke_width=8*S, stroke_fill=(10,6,20))
        y+=int(tf.size*1.15)
    # 서브 태그라인
    sf=ImageFont.truetype(font, 44*S)
    d.text((72*S,y+18*S), sub, font=sf, fill=(235,235,245), stroke_width=5*S, stroke_fill=(10,6,20))
    # 로고 (우하단, 워터마크 커버 겸)
    try:
        lg=Image.open(os.path.join(ROOT,"assets","drjay_ed_logo_circle.png")).convert("RGBA").resize((120*S,120*S),Image.LANCZOS)
        im.alpha_composite(lg,(W-140*S,H-140*S))
    except Exception: pass
    out=os.path.join(HS,f"thumb_{lang}.jpg")
    q=90
    im.convert("RGB").save(out,"JPEG",quality=q)
    while os.path.getsize(out)>2*1024*1024 and q>70:   # 유튜브 2MB 제한
        q-=5; im.convert("RGB").save(out,"JPEG",quality=q)
    sz=os.path.getsize(out)/1024
    print(f"{lang}: {out} ({sz:.0f}KB, {W}x{H}, q{q})")

make("ko","최면, 진짜\n과학일까?","마술인가, 뇌과학인가")
make("en","Is Hypnosis\nReal Science?","Magic, or brain science?")
print("DONE")
