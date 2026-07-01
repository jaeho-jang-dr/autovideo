# -*- coding: utf-8 -*-
"""pianoduo 클립 QA — 각 클립에서 프레임 2장(50%,85%) 추출해 컨택트시트 PNG 생성.
육안 검사용: 마주봄/손뗌/3명/뭉개짐 탐지. 출력: pianoduo/_qa_mid.png, _qa_late.png"""
import os, cv2, numpy as np
PDIR = os.path.dirname(os.path.abspath(__file__))
COLS, THUMB_W = 5, 360

def grab(path, frac):
    cap = cv2.VideoCapture(path)
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
    cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, min(n-1, int(n*frac))))
    ok, fr = cap.read(); cap.release()
    return fr if ok else None

def sheet(frac, out):
    thumbs = []
    for i in range(1, 26):
        p = os.path.join(PDIR, f"scene_{i}.mp4")
        fr = grab(p, frac) if os.path.exists(p) else None
        if fr is None:
            fr = np.full((202, THUMB_W, 3), 40, np.uint8)
        else:
            h, w = fr.shape[:2]
            fr = cv2.resize(fr, (THUMB_W, int(h*THUMB_W/w)))
        cv2.rectangle(fr, (0,0), (52,30), (0,0,0), -1)
        cv2.putText(fr, str(i), (6,23), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
        thumbs.append(fr)
    hmax = max(t.shape[0] for t in thumbs)
    thumbs = [cv2.copyMakeBorder(t, 0, hmax-t.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(20,20,20)) for t in thumbs]
    rows = []
    for r in range(0, 25, COLS):
        row = thumbs[r:r+COLS]
        while len(row) < COLS:
            row.append(np.full((hmax, THUMB_W, 3), 20, np.uint8))
        rows.append(np.hstack(row))
    cv2.imwrite(out, np.vstack(rows))
    print(f"[OK] {out}")

sheet(0.50, os.path.join(PDIR, "_qa_mid.png"))
sheet(0.85, os.path.join(PDIR, "_qa_late.png"))
