# -*- coding: utf-8 -*-
"""W11 v4 정규화 — 사장님 지시: 머리높이 말고 **전체 키(머리끝~발끝) 딱 맞춤**.
   - 서기 12종: 키=STAND_H로 통일  /  앉기 8종: 키=SIT_H로 통일(좀 낮게, 앉은 것끼리)
   - sit_taste·sit_drink 는 왼쪽을 봐서 **좌우 리버스**해 오른쪽 향하게
   - 원본 raw(scratch/w11v3_orig)에서 다시 처리 → poses/mj_*.png 덮어씀. 증명시트 scratch/w11v4_uniformity.png
   머리끝 검출은 '행 픽셀수 >= 0.30*최대행'인 첫 행(가는 든 손/숟가락은 건너뜀)."""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
PD = os.path.join(ROOT, "assets", "graphics", "poses")
SRC = os.path.join(ROOT, "scratch", "w11v3_orig")
CANVAS_W, CANVAS_H = 560, 860
BOTTOM = CANVAS_H - 16                # 발/의자 바닥 기준선
STAND_H = 660                         # 서기 캐릭터 키(머리끝~발끝)
SIT_H   = 500                         # 앉기 캐릭터 키(좀 낮게, 앉은 것끼리 통일)
STAND = ["walk_right","look_around","greeting","wave","point_right","thinking","cheer","hungry",
         "presenting","pay_card","pay_cash","get_receipt"]
SIT   = ["sit_base","sit_menu","sit_point","sit_call","sit_eat","sit_taste","sit_drink","sit_receive"]
FLIP  = {"sit_taste","sit_drink"}     # 왼쪽 보는 것 → 리버스

def cutout(im):
    im = im.convert("RGBA"); a = np.array(im); rgb = a[:,:,:3].astype(int); al = a[:,:,3]
    white = (rgb[:,:,0]>238)&(rgb[:,:,1]>238)&(rgb[:,:,2]>238)&(al>10)
    lbl, n = ndimage.label(white)
    border = set(np.unique(np.concatenate([lbl[0,:],lbl[-1,:],lbl[:,0],lbl[:,-1]]))) - {0}
    a[np.isin(lbl, list(border)),3] = 0
    return a

def head_top(al):
    """가는 든 손/숟가락은 건너뛰고 머리(넓은 블록)의 첫 행."""
    rowc = (al>30).sum(axis=1)
    mx = rowc.max()
    thr = max(8, int(mx*0.30))
    for y in range(al.shape[0]):
        if rowc[y] >= thr: return y
    return int(np.argmax(rowc>0))

def process(name, target):
    p = os.path.join(SRC, f"mj_{name}.png")
    if not os.path.exists(p): return None
    a = cutout(Image.open(p))
    al = a[:,:,3]
    ys, xs = np.where(al > 20)
    if len(ys)==0: return None
    top,bot,left,right = ys.min(), ys.max(), xs.min(), xs.max()
    crop = a[top:bot+1, left:right+1]
    ht = head_top(crop[:,:,3])                 # 크롭 내 머리끝 행
    feet = crop.shape[0]-1                      # 크롭 맨 아래=발
    char_h = feet - ht                          # 실제 키(머리끝~발끝)
    scale = target / char_h
    cim = Image.fromarray(crop)
    if name in FLIP: cim = cim.transpose(Image.FLIP_LEFT_RIGHT)
    nw,nh = max(1,round(cim.width*scale)), max(1,round(cim.height*scale))
    cim = cim.resize((nw,nh), Image.LANCZOS)
    canvas = Image.new("RGBA",(CANVAS_W,CANVAS_H),(0,0,0,0))
    px = (CANVAS_W - nw)//2
    py = BOTTOM - nh
    canvas.alpha_composite(cim,(px,max(0,py)))
    canvas.save(os.path.join(PD, f"mj_{name}.png"))
    a2 = np.array(canvas)[:,:,3]
    ht2 = head_top(a2); yy=np.where(a2>20)[0]; feet2=yy.max() if len(yy) else 0
    return {"name":name,"char_h_src":int(char_h),"scale":round(scale,3),
            "height_after":int(feet2-ht2),"head_top":int(ht2),"feet":int(feet2),"flip":name in FLIP}

def sheet(rows):
    cols=5; rws=4; tw,th=280,440
    sh=Image.new("RGB",(cols*tw, rws*th+44),(250,248,244)); d=ImageDraw.Draw(sh)
    try: f=ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf",17); fb=ImageFont.truetype(r"C:\Windows\Fonts\malgun.ttf",22)
    except: f=fb=ImageFont.load_default()
    d.text((14,10),f"W11 v4 — 전체 키 통일(서기 {STAND_H} / 앉기 {SIT_H}px). 초록=머리끝 빨강=발. taste·drink 리버스됨",font=fb,fill=(30,30,30))
    for i,r in enumerate(rows):
        if r is None: continue
        cx=(i%cols)*tw; cy=(i//cols)*th+44
        im=Image.open(os.path.join(PD,f"mj_{r['name']}.png")).convert("RGBA")
        sc=min(tw/im.width,(th-30)/im.height); iw,ih=int(im.width*sc),int(im.height*sc)
        bgc=Image.new("RGBA",(tw,th),(255,255,255,255)); bgc.alpha_composite(im.resize((iw,ih),Image.LANCZOS),((tw-iw)//2,0))
        sh.paste(bgc.convert("RGB"),(cx,cy))
        gy=cy+int(r['head_top']*sc); fy=cy+int(r['feet']*sc)
        d.line((cx,gy,cx+tw,gy),fill=(0,175,0),width=2); d.line((cx,fy,cx+tw,fy),fill=(220,40,40),width=2)
        tag=f"{r['name']} H={r['height_after']}"+(" ↔" if r['flip'] else "")
        d.text((cx+6,cy+th-26),tag,font=f,fill=(20,20,20))
    out=os.path.join(ROOT,"scratch","w11v4_uniformity.png"); sh.save(out); return out

if __name__=="__main__":
    rows=[process(n,STAND_H) for n in STAND]+[process(n,SIT_H) for n in SIT]
    st=[r['height_after'] for r in rows if r and r['name'] in STAND]
    si=[r['height_after'] for r in rows if r and r['name'] in SIT]
    print(f"서기 키 after: min={min(st)} max={max(st)} (목표 {STAND_H})")
    print(f"앉기 키 after: min={min(si)} max={max(si)} (목표 {SIT_H})")
    print("리버스:", [r['name'] for r in rows if r and r['flip']])
    print("증명시트:", sheet(rows))
