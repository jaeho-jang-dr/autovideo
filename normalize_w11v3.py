# -*- coding: utf-8 -*-
"""W11 v3 포즈 20개 컷아웃 + 사이즈 정규화(coral 넥라인 기준 머리높이 통일) + 균일성 증명 시트.
   - 흰 배경 → 투명 컷아웃(테두리 연결 흰색만; 옷/신발 내부 흰색 보존)
   - coral V넥 조끼 넥라인 검출 → 머리높이(head_top~neck)=TARGET로 스케일 → 캐릭터 크기 항상 동일
   - 모든 포즈 같은 캔버스, 발/바닥 정렬 → center-anchor paste 시 크기·위치 균일
   출력: 원본은 scratch/w11v3_orig/ 백업, poses/mj_*.png 덮어씀. 증명시트 scratch/w11v3_uniformity.png"""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
PD = os.path.join(ROOT, "assets", "graphics", "poses")
BK = os.path.join(ROOT, "scratch", "w11v3_orig"); os.makedirs(BK, exist_ok=True)
CANVAS_W, CANVAS_H = 560, 840
TARGET_HEAD = 150      # 머리끝~coral넥라인 픽셀높이(모든 포즈 동일)
FLOOR_MARGIN = 18      # 캐릭터 발/바닥이 캔버스 하단에서 이만큼 위
POSES = ["walk_right","look_around","greeting","wave","point_right","thinking","cheer","hungry",
         "presenting","pay_card","pay_cash","get_receipt",
         "sit_base","sit_menu","sit_point","sit_call","sit_eat","sit_taste","sit_drink","sit_receive"]

def cutout(im):
    """테두리에 연결된 흰색만 투명. 내부 흰색(치마·신발·속옷) 보존."""
    im = im.convert("RGBA"); a = np.array(im); rgb = a[:,:,:3].astype(int); al = a[:,:,3]
    white = (rgb[:,:,0]>238)&(rgb[:,:,1]>238)&(rgb[:,:,2]>238)&(al>10)
    lbl, n = ndimage.label(white)
    border = set(np.unique(np.concatenate([lbl[0,:],lbl[-1,:],lbl[:,0],lbl[:,-1]]))) - {0}
    mask = np.isin(lbl, list(border))
    a[mask,3] = 0
    return Image.fromarray(a,"RGBA")

def neckline(a):
    """coral/salmon 조끼가 처음 나타나는 행(넥라인). 없으면 None."""
    rgb = a[:,:,:3].astype(int); al = a[:,:,3]
    r,g,b = rgb[:,:,0],rgb[:,:,1],rgb[:,:,2]
    coral = (r>200)&(g>95)&(g<195)&(b>85)&(b<180)&((r-b)>45)&((r-g)>25)&(al>128)
    rows = coral.sum(axis=1)
    thr = max(6, int(coral.shape[1]*0.012))
    for y in range(coral.shape[0]):
        if rows[y] >= thr: return y
    return None

def process(name):
    p = os.path.join(PD, f"mj_{name}.png")
    if not os.path.exists(p): return None
    im = Image.open(p)
    im.convert("RGBA").save(os.path.join(BK, f"mj_{name}.png"))   # 백업
    im = cutout(im)
    a = np.array(im); al = a[:,:,3]
    ys, xs = np.where(al > 20)
    if len(ys)==0: return None
    top,bot,left,right = ys.min(), ys.max(), xs.min(), xs.max()
    crop = a[top:bot+1, left:right+1]
    nk = neckline(crop)
    if nk is None or nk < 12:
        # 폴백: 전신높이의 30%를 머리로 가정
        nk = int((bot-top+1)*0.30)
    head_h = nk
    scale = TARGET_HEAD / head_h
    cim = Image.fromarray(crop,"RGBA")
    nw,nh = max(1,int(cim.width*scale)), max(1,int(cim.height*scale))
    cim = cim.resize((nw,nh), Image.LANCZOS)
    canvas = Image.new("RGBA",(CANVAS_W,CANVAS_H),(0,0,0,0))
    px = (CANVAS_W - nw)//2
    py = CANVAS_H - FLOOR_MARGIN - nh
    if py < 0: py = 0
    canvas.alpha_composite(cim,(px,py))
    canvas.save(p)
    # 정규화 후 실제 머리높이 재측정(검증)
    a2 = np.array(canvas); nk2 = neckline(a2)
    yy = np.where(a2[:,:,3]>20)[0]; realtop = yy.min() if len(yy) else 0
    measured = (nk2-realtop) if nk2 is not None else -1
    return {"name":name,"head_h_src":head_h,"scale":round(scale,3),"head_after":measured,"neck_row":nk2,"top":realtop,"foot":CANVAS_H-FLOOR_MARGIN}

def sheet(rows):
    cols=5; rws=4; tw,th=280,420
    sh=Image.new("RGB",(cols*tw, rws*th+40),(250,248,244)); d=ImageDraw.Draw(sh)
    try: f=ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf",18); fb=ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf",22)
    except: f=fb=ImageFont.load_default()
    d.text((14,8),f"W11 v3 포즈 균일성 검증 — 머리높이 목표 {TARGET_HEAD}px, 초록선=넥라인 / 빨간선=바닥",font=fb,fill=(30,30,30))
    for i,r in enumerate(rows):
        if r is None: continue
        cx=(i%cols)*tw; cy=(i//cols)*th+40
        im=Image.open(os.path.join(PD,f"mj_{r['name']}.png")).convert("RGBA")
        sc=min(tw/im.width,(th-30)/im.height); iw,ih=int(im.width*sc),int(im.height*sc)
        im2=im.resize((iw,ih),Image.LANCZOS); bgc=Image.new("RGBA",(tw,th),(255,255,255,255))
        bgc.alpha_composite(im2,((tw-iw)//2,0)); sh.paste(bgc.convert("RGB"),(cx,cy))
        # 넥라인/바닥 가이드(스케일 반영)
        if r['neck_row'] is not None:
            gy=cy+int(r['neck_row']*sc); d.line((cx,gy,cx+tw,gy),fill=(0,180,0),width=2)
        fy=cy+int(r['foot']*sc); d.line((cx,fy,cx+tw,fy),fill=(220,40,40),width=2)
        d.text((cx+6,cy+th-26),f"{r['name']} h={r['head_after']}",font=f,fill=(20,20,20))
    out=os.path.join(ROOT,"scratch","w11v3_uniformity.png"); sh.save(out); return out

if __name__=="__main__":
    rows=[process(n) for n in POSES]
    ok=[r for r in rows if r]
    hs=[r['head_after'] for r in ok if r['head_after']>0]
    print(f"처리 {len(ok)}/20. 머리높이 after: min={min(hs)} max={max(hs)} 평균={sum(hs)//len(hs)} (목표 {TARGET_HEAD})")
    miss=[n for n,r in zip(POSES,rows) if r is None]
    if miss: print("누락:", miss)
    print("증명시트:", sheet(rows))
