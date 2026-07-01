# -*- coding: utf-8 -*-
import os, cv2, numpy as np, sys
PDIR = os.path.dirname(os.path.abspath(__file__))
def strip(n):
    p = os.path.join(PDIR, f"scene_{n}.mp4")
    cap = cv2.VideoCapture(p); tot = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    cells=[]
    for k,frac in enumerate([0.0,0.2,0.4,0.6,0.8,1.0]):
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0,min(tot-1,int(tot*frac))))
        ok,fr=cap.read()
        if not ok: fr=np.full((200,320,3),40,np.uint8)
        else:
            h,w=fr.shape[:2]; fr=cv2.resize(fr,(320,int(h*320/w)))
        cv2.rectangle(fr,(0,0),(70,26),(0,0,0),-1)
        cv2.putText(fr,f"{n}:{int(frac*100)}",(4,20),cv2.FONT_HERSHEY_SIMPLEX,0.55,(0,255,255),1)
        cells.append(fr)
    cap.release()
    hm=max(c.shape[0] for c in cells)
    cells=[cv2.copyMakeBorder(c,0,hm-c.shape[0],0,0,cv2.BORDER_CONSTANT,value=(20,20,20)) for c in cells]
    return np.hstack(cells)
rows=[strip(int(x)) for x in sys.argv[1:]]
out=os.path.join(PDIR,"_qa_strip.png"); cv2.imwrite(out,np.vstack(rows)); print("[OK]",out)
