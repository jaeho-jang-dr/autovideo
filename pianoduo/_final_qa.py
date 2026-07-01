# -*- coding: utf-8 -*-
import os, cv2, numpy as np
PDIR=os.path.dirname(os.path.abspath(__file__))
p=os.path.join(PDIR,"pianoduo.mp4")
cap=cv2.VideoCapture(p); tot=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); fps=cap.get(cv2.CAP_PROP_FPS)
N=30; cells=[]
for k in range(N):
    fr_i=int(tot*k/N); cap.set(cv2.CAP_PROP_POS_FRAMES,fr_i); ok,fr=cap.read()
    if not ok: fr=np.full((180,320,3),40,np.uint8)
    else:
        h,w=fr.shape[:2]; fr=cv2.resize(fr,(320,int(h*320/w)))
    t=fr_i/fps
    cv2.rectangle(fr,(0,0),(78,24),(0,0,0),-1)
    cv2.putText(fr,f"{t:.1f}s",(4,18),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),1)
    cells.append(fr)
cap.release()
hm=max(c.shape[0] for c in cells); COLS=6
cells=[cv2.copyMakeBorder(c,0,hm-c.shape[0],0,0,cv2.BORDER_CONSTANT,value=(20,20,20)) for c in cells]
rows=[]
for r in range(0,N,COLS):
    row=cells[r:r+COLS]
    while len(row)<COLS: row.append(np.full((hm,320,3),20,np.uint8))
    rows.append(np.hstack(row))
out=os.path.join(PDIR,"_final_qa.png"); cv2.imwrite(out,np.vstack(rows)); print("[OK]",out)
