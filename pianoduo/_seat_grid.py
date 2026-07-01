# -*- coding: utf-8 -*-
"""각 클립의 첫 프레임(0%)과 끝 프레임(100%)을 나란히 → 좌우 좌석/마주봄 추적용."""
import os, cv2, numpy as np
PDIR=os.path.dirname(os.path.abspath(__file__))
def f(n,frac):
    cap=cv2.VideoCapture(os.path.join(PDIR,f"scene_{n}.mp4")); t=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    cap.set(cv2.CAP_PROP_POS_FRAMES,max(0,min(t-1,int(t*frac)))); ok,fr=cap.read(); cap.release()
    if not ok: return np.full((180,300,3),40,np.uint8)
    h,w=fr.shape[:2]; return cv2.resize(fr,(300,int(h*300/w)))
def grid(frac,out):
    cells=[]
    for n in range(1,26):
        im=f(n,frac); cv2.rectangle(im,(0,0),(46,26),(0,0,0),-1)
        cv2.putText(im,str(n),(5,21),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,255,255),2)
        cells.append(im)
    hm=max(c.shape[0] for c in cells)
    cells=[cv2.copyMakeBorder(c,0,hm-c.shape[0],0,0,cv2.BORDER_CONSTANT,value=(20,20,20)) for c in cells]
    rows=[np.hstack((cells[r:r+5]+[np.full((hm,300,3),20,np.uint8)]*5)[:5]) for r in range(0,25,5)]
    cv2.imwrite(out,np.vstack(rows)); print("[OK]",out)
grid(0.02, os.path.join(PDIR,"_seat_first.png"))
grid(0.98, os.path.join(PDIR,"_seat_last.png"))
