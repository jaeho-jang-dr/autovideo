# -*- coding: utf-8 -*-
"""모션캡처 → 졸라 리타겟.
자유 라이선스 댄스 영상(Pexels 등)에서 사람 포즈(YOLO-pose, COCO 17키포인트)를 프레임별 추출하고,
그 관절 움직임을 졸라맨/졸라걸 스틱맨 골격에 입혀 '사람처럼 춤추는 졸라' 클립을 렌더한다.
※ 소스 영상은 반드시 사용 권리가 있는 것(직접 촬영/CC/로열티프리)만 사용.
사용: python zolla_dynamite_veo/mocap_to_zolla.py <input.mp4> <output.mp4> [man|girl]
"""
import os, sys
import numpy as np, cv2
from ultralytics import YOLO

# COCO-17 keypoint index
NOSE,LEYE,REYE,LEAR,REAR,LSH,RSH,LEL,REL,LWR,RWR,LHIP,RHIP,LKN,RKN,LAN,RAN = range(17)
INK=(40,40,45)          # 검은 잉크
BEIGE=(212,230,240)     # BGR 베이지(#F0E6D4)
HAIR_BLACK=(40,40,45)
HAIR_ORANGE=(40,140,235)  # BGR 주황

def ema(prev, cur, a=0.5):
    if prev is None: return cur
    return a*cur + (1-a)*prev

# COCO 스켈레톤 연결(어깨-팔-다리-몸통)
SK_EDGES = [(5,7),(7,9),(6,8),(8,10),(5,6),(5,11),(6,12),(11,12),
            (11,13),(13,15),(12,14),(14,16)]

def smooth_seq(kps, cfs, win=5):
    """키포인트 시퀀스를 시간축 이동평균으로 스무딩(지터 제거). win=홀수."""
    n=len(kps)
    if n==0: return kps
    arr=np.stack(kps)            # (n,17,2)
    out=arr.copy(); h=win//2
    for t in range(n):
        a=max(0,t-h); b=min(n,t+h+1)
        out[t]=arr[a:b].mean(axis=0)
    return [out[t] for t in range(n)]

def draw_skeleton(canvas, kp, cf, thr=0.3):
    """졸라 변환 전 raw 포즈 스켈레톤(뼈=청록 굵은선, 관절=빨강점, 머리=원)."""
    def P(i): return (int(kp[i,0]),int(kp[i,1])) if cf[i]>thr else None
    sh_l,sh_r=P(5),P(6)
    shw=80.0
    if sh_l and sh_r: shw=max(20.0,np.hypot(sh_l[0]-sh_r[0],sh_l[1]-sh_r[1]))
    T=max(5,int(shw*0.14))
    for a,b in SK_EDGES:
        A,B=P(a),P(b)
        if A and B: cv2.line(canvas,A,B,(196,205,78),T,cv2.LINE_AA)   # 청록(BGR)
    for i in range(17):
        Pi=P(i)
        if Pi: cv2.circle(canvas,Pi,max(4,T//2),(60,60,255),-1,cv2.LINE_AA)  # 빨강 관절
    # 머리 원
    pts=[P(i) for i in (0,1,2,3,4) if P(i)]
    if pts:
        hc=(int(np.mean([p[0] for p in pts])),int(np.mean([p[1] for p in pts])))
        cv2.circle(canvas,hc,int(shw*0.4),(196,205,78),T,cv2.LINE_AA)

def draw_zolla(canvas, kp, cf, style="man", thr=0.3):
    h,w = canvas.shape[:2]
    def P(i): return (int(kp[i,0]),int(kp[i,1])) if cf[i]>thr else None
    sh_l,sh_r = P(LSH),P(RSH)
    if sh_l and sh_r:
        shw = max(20.0, np.hypot(sh_l[0]-sh_r[0], sh_l[1]-sh_r[1]))
        sh_mid = ((sh_l[0]+sh_r[0])//2,(sh_l[1]+sh_r[1])//2)
    elif sh_l or sh_r:
        s=sh_l or sh_r; shw=60.0; sh_mid=s
    else:
        return
    T=max(5,int(shw*0.13))                    # 선 두께
    def limb(a,b,t=None):
        A,B=P(a),P(b)
        if A and B:
            cv2.line(canvas,A,B,INK,t or T,cv2.LINE_AA)
            cv2.circle(canvas,A,(t or T)//2,INK,-1,cv2.LINE_AA)
            cv2.circle(canvas,B,(t or T)//2,INK,-1,cv2.LINE_AA)
    hip_l,hip_r=P(LHIP),P(RHIP)
    hip_mid=None
    if hip_l and hip_r: hip_mid=((hip_l[0]+hip_r[0])//2,(hip_l[1]+hip_r[1])//2)
    elif hip_l or hip_r: hip_mid=hip_l or hip_r
    # 몸통/척추
    if hip_mid: cv2.line(canvas,sh_mid,hip_mid,INK,T,cv2.LINE_AA)
    cv2.line(canvas,sh_l or sh_mid, sh_r or sh_mid, INK, T, cv2.LINE_AA)
    if hip_l and hip_r: cv2.line(canvas,hip_l,hip_r,INK,T,cv2.LINE_AA)
    # 팔/다리
    limb(LSH,LEL); limb(LEL,LWR); limb(RSH,REL); limb(REL,RWR)
    limb(LHIP,LKN); limb(LKN,LAN); limb(RHIP,RKN); limb(RKN,RAN)
    # 손/발
    for wj in (LWR,RWR):
        Wp=P(wj)
        if Wp: cv2.ellipse(canvas,Wp,(int(T*0.9),int(T*0.7)),0,0,360,INK,max(2,T//3),cv2.LINE_AA)
    for aj in (LAN,RAN):
        Ap=P(aj)
        if Ap: cv2.ellipse(canvas,(Ap[0],Ap[1]+T),(int(T*1.3),int(T*0.7)),0,0,360,INK,max(2,T//3),cv2.LINE_AA)
    # 머리(눈/이/코 평균) + 헤어
    pts=[P(i) for i in (NOSE,LEYE,REYE,LEAR,REAR) if P(i)]
    if pts:
        hc=(int(np.mean([p[0] for p in pts])),int(np.mean([p[1] for p in pts])))
    else:
        hc=(sh_mid[0], int(sh_mid[1]-shw*0.7))
    hr=int(shw*0.42)
    # 목
    cv2.line(canvas,sh_mid,(hc[0],hc[1]+hr),INK,T,cv2.LINE_AA)
    cv2.circle(canvas,hc,hr,(255,255,255),-1,cv2.LINE_AA)
    cv2.circle(canvas,hc,hr,INK,max(3,T//2),cv2.LINE_AA)
    # 눈 + 미소
    ey=int(hr*0.18)
    cv2.circle(canvas,(hc[0]-hr//3,hc[1]-ey),max(2,hr//8),INK,-1,cv2.LINE_AA)
    cv2.circle(canvas,(hc[0]+hr//3,hc[1]-ey),max(2,hr//8),INK,-1,cv2.LINE_AA)
    cv2.ellipse(canvas,(hc[0],hc[1]+hr//6),(hr//2,hr//3),0,15,165,INK,max(2,hr//10),cv2.LINE_AA)
    # 헤어
    if style=="girl":
        bun=(hc[0],hc[1]-hr-int(hr*0.5))
        cv2.circle(canvas,bun,int(hr*0.5),HAIR_ORANGE,-1,cv2.LINE_AA)
        cv2.circle(canvas,bun,int(hr*0.5),INK,max(2,T//3),cv2.LINE_AA)
        cv2.ellipse(canvas,(hc[0],hc[1]-int(hr*0.6)),(hr,int(hr*0.7)),0,180,360,HAIR_ORANGE,-1,cv2.LINE_AA)
    else:
        cv2.ellipse(canvas,(hc[0],hc[1]-int(hr*0.55)),(int(hr*1.05),int(hr*0.85)),0,178,362,HAIR_BLACK,-1,cv2.LINE_AA)
        for dx in (-0.5,0,0.5):
            cv2.line(canvas,(hc[0]+int(dx*hr),hc[1]-int(hr*0.5)),(hc[0]+int(dx*hr*1.3),hc[1]-int(hr*1.1)),HAIR_BLACK,max(3,T//2),cv2.LINE_AA)

def main():
    src=sys.argv[1] if len(sys.argv)>1 else "zolla_dynamite_veo/source/dance_src.mp4"
    out=sys.argv[2] if len(sys.argv)>2 else "zolla_dynamite_veo/_mocap_proto.mp4"
    style=sys.argv[3] if len(sys.argv)>3 else "man"   # man | girl | skeleton
    win=int(sys.argv[4]) if len(sys.argv)>4 else 7    # 스무딩 윈도우(클수록 떨림↓·둔해짐)
    speed=float(sys.argv[5]) if len(sys.argv)>5 else 1.0  # <1 느리게(절도감)
    model=YOLO("yolov8s-pose.pt")                     # n→s: 더 정확·덜 떨림
    cap=cv2.VideoCapture(src); fps=cap.get(cv2.CAP_PROP_FPS) or 25
    W=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # 1) 패스: 키포인트 추출(검출 실패 시 직전 유지)
    kps=[]; cfs=[]; last=None; lastcf=np.zeros(17)
    while True:
        ok,fr=cap.read()
        if not ok: break
        res=model.predict(fr,verbose=False,imgsz=640)[0]
        got=None; gotcf=None
        if res.keypoints is not None and len(res.keypoints)>0:
            kxy=res.keypoints.xy.cpu().numpy(); kcf=res.keypoints.conf
            kcf=kcf.cpu().numpy() if kcf is not None else np.ones((kxy.shape[0],17))
            areas=[(k[:,0].max()-k[:,0].min())*(k[:,1].max()-k[:,1].min()) if k.size else 0 for k in kxy]
            i=int(np.argmax(areas))
            if areas[i] > (W*H*0.01): got=kxy[i].astype(float); gotcf=kcf[i]
        if got is None: got=last if last is not None else np.zeros((17,2)); gotcf=lastcf
        last=got; lastcf=gotcf; kps.append(got); cfs.append(gotcf)
    cap.release()
    if not kps: print("[FAIL] 포즈 미검출"); return
    # 2) 시간축 스무딩(지터 제거)
    kps=smooth_seq(kps,cfs,win=win)
    # 3) 렌더 (speed<1이면 출력 fps 낮춰 느리게)
    snap=int(sys.argv[6]) if len(sys.argv)>6 else 1   # 포즈 홀드 프레임수(>1이면 탁탁 절도감)
    out_fps=max(8.0, fps*speed)
    vw=cv2.VideoWriter(out,cv2.VideoWriter_fourcc(*"mp4v"),out_fps,(W,H))
    drawer=draw_skeleton if style=="skeleton" else (lambda c,k,cf: draw_zolla(c,k,cf,style=style))
    held_kp, held_cf = kps[0], cfs[0]
    for i,(kp,cf) in enumerate(zip(kps,cfs)):
        if i % snap == 0:            # snap 프레임마다 포즈 갱신, 사이엔 정지(탁→홀드→탁)
            held_kp, held_cf = kp, cf
        canvas=np.full((H,W,3),BEIGE,np.uint8)
        drawer(canvas,held_kp,held_cf)
        vw.write(canvas)
    vw.release()
    print(f"[OK] {out}  ({len(kps)} frames, src {fps:.0f}→out {out_fps:.0f}fps, style={style}, win={win}, speed={speed}, snap={snap})")

if __name__=="__main__":
    main()
