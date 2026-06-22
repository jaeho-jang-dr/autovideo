# -*- coding: utf-8 -*-
"""졸라 듀오 모션캡처 합성 — 졸라맨(소스A) + 졸라걸(소스B)을 각자 다른 동작으로,
같은 크기로 정규화해 한 화면 좌/우에 배치. 스냅(절도)·속도 조절. 배경=베이지(나중에 무대톤 교체).
사용: python zolla_dynamite_veo/mocap_duo.py <manSrc> <girlSrc> <out> [win=7] [speed=0.8] [snap=5]
※ 소스는 권리 있는 클립(CC/로열티프리/직접촬영)만.
"""
import os, sys
import numpy as np, cv2
from ultralytics import YOLO
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mocap_to_zolla import draw_zolla, smooth_seq

BEIGE=(212,230,240)  # BGR
W,H=1080,1920

def extract(model, src, win):
    cap=cv2.VideoCapture(src); fps=cap.get(cv2.CAP_PROP_FPS) or 25
    sw=int(cap.get(3)); sh=int(cap.get(4))
    kps=[]; cfs=[]; last=None; lastcf=np.zeros(17)
    while True:
        ok,fr=cap.read()
        if not ok: break
        r=model.predict(fr,verbose=False,imgsz=640)[0]
        got=None; gotcf=None
        if r.keypoints is not None and len(r.keypoints)>0:
            kxy=r.keypoints.xy.cpu().numpy(); kcf=r.keypoints.conf
            kcf=kcf.cpu().numpy() if kcf is not None else np.ones((kxy.shape[0],17))
            areas=[(k[:,0].max()-k[:,0].min())*(k[:,1].max()-k[:,1].min()) if k.size else 0 for k in kxy]
            i=int(np.argmax(areas))
            if areas[i]>sw*sh*0.01: got=kxy[i].astype(float); gotcf=kcf[i]
        if got is None: got=last if last is not None else np.zeros((17,2)); gotcf=lastcf
        last=got; lastcf=gotcf; kps.append(got); cfs.append(gotcf)
    cap.release()
    if kps: kps=smooth_seq(kps,cfs,win=win)
    return kps, cfs, fps

def anchor(kps, cfs, thr=0.3):
    hips=[]; heights=[]
    for kp,cf in zip(kps,cfs):
        v=cf>thr
        if v.sum()<4: continue
        ys=kp[v,1]; heights.append(ys.max()-ys.min())
        if cf[11]>thr and cf[12]>thr: hips.append((kp[11]+kp[12])/2)
        elif cf[11]>thr: hips.append(kp[11])
        elif cf[12]>thr: hips.append(kp[12])
    hipc=np.median(np.stack(hips),axis=0) if hips else np.array([W/2.,H/2.])
    medh=float(np.median(heights)) if heights else H*0.5
    return hipc, max(1.0,medh)

def normalize(kps, hipc, medh, tcx, tcy, th):
    s=th/medh; out=[]
    for kp in kps:
        o=kp.astype(float).copy()
        o[:,0]=(kp[:,0]-hipc[0])*s+tcx
        o[:,1]=(kp[:,1]-hipc[1])*s+tcy
        out.append(o)
    return out

def main():
    manSrc=sys.argv[1]; girlSrc=sys.argv[2]; out=sys.argv[3]
    win=int(sys.argv[4]) if len(sys.argv)>4 else 7
    speed=float(sys.argv[5]) if len(sys.argv)>5 else 0.8
    snap=int(sys.argv[6]) if len(sys.argv)>6 else 5
    size=float(sys.argv[7]) if len(sys.argv)>7 else 1.0   # 캐릭터 크기 배수(0.8=20%작게)
    model=YOLO("yolov8s-pose.pt")
    print("[A] 졸라맨 소스 추출..."); kA,cA,fA=extract(model,manSrc,win)
    print("[B] 졸라걸 소스 추출..."); kB,cB,fB=extract(model,girlSrc,win)
    if not kA or not kB: print("[FAIL] 포즈 미검출"); return
    hipA,hA=anchor(kA,cA); hipB,hB=anchor(kB,cB)
    th=H*0.50*size; tcy=H*0.54
    nA=normalize(kA,hipA,hA, W*0.30, tcy, th)
    nB=normalize(kB,hipB,hB, W*0.70, tcy, th)
    N=min(len(nA),len(nB))
    out_fps=max(8.0,(fA or 25)*speed)
    vw=cv2.VideoWriter(out,cv2.VideoWriter_fourcc(*"mp4v"),out_fps,(W,H))
    hi=0
    for i in range(N):
        if i%snap==0: hi=i
        canvas=np.full((H,W,3),BEIGE,np.uint8)
        draw_zolla(canvas,nA[hi],cA[hi],style="man")
        draw_zolla(canvas,nB[hi],cB[hi],style="girl")
        vw.write(canvas)
    vw.release()
    print(f"[OK] {out}  ({N} frames, out {out_fps:.0f}fps, snap={snap}, speed={speed}, win={win})")

if __name__=="__main__":
    main()
