# -*- coding: utf-8 -*-
"""5개 언어 gTTS 생성(ko/en 있으면 스킵) + 씬별 최대길이 타임라인 계산.
gTTS: zh->zh-CN, ja->ja, es->es. 출력: audio_free/{lang}_S##.mp3 + i18n/timeline.json"""
import os, json, subprocess
from gtts import gTTS
ROOT="D:/Entertainments/DevEnvironment/autovideo"
AUD=os.path.join(ROOT,"sejong_film","main","audio_free")
I18N=os.path.join(ROOT,"sejong_film","main","i18n")
os.makedirs(AUD,exist_ok=True)
data=json.load(open(os.path.join(I18N,"narration.json"),encoding="utf-8"))
GLANG={"ko":"ko","en":"en","zh":"zh-CN","ja":"ja","es":"es"}
LANGS=["ko","en","zh","ja","es"]

def dur(p):
    try: return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0","-show_entries","format=duration",p],capture_output=True,text=True,timeout=20).stdout.strip())
    except Exception: return 0.0
def clean(t): return t.replace("“","").replace("”","").replace("‘","'").replace("’","'")

# 1) gTTS 생성
for lang in LANGS:
    made=0
    for d in data:
        if d["music"] or not d.get(lang): continue
        out=os.path.join(AUD,f"{lang}_S{d['n']:02d}.mp3")
        if os.path.exists(out) and os.path.getsize(out)>800: continue
        try:
            gTTS(clean(d[lang]),lang=GLANG[lang]).save(out); made+=1
        except Exception as e:
            print(f"[ERR] {lang}_S{d['n']:02d}: {str(e)[:70]}")
    print(f"{lang}: 신규 {made}개 생성")

# 2) 씬별 언어별 길이 + 최대 슬롯 타임라인
XF=0.6; DISS=("디졸브","모프","페이드","입자와이프","슬라이드")
# 전환정보는 마스터에서
import re
trans={}
for line in open(os.path.join(ROOT,"sejong_film","sejong_master_shotscript_48.md"),encoding="utf-8"):
    m=re.match(r"^\*\*S(\d+)\s*·.*?(?:→(\S+))?\*\*",line)
    if m: trans[int(m.group(1))]=(m.group(2) or "컷")

rows=[]; totals={l:0.0 for l in LANGS}
for d in data:
    n=d["n"]; durs={}
    for lang in LANGS:
        p=os.path.join(AUD,f"{lang}_S{n:02d}.mp3")
        durs[lang]=dur(p) if os.path.exists(p) else 0.0
        totals[lang]+=durs[lang]
    if d["music"]:
        slot=2.6
    else:
        slot=max(durs.values())+0.55 if any(durs.values()) else 3.4
    rows.append({"n":n,"music":d["music"],"trans":trans.get(n,"컷"),"durs":{k:round(v,2) for k,v in durs.items()},"slot":round(slot,2)})

# 타임라인 총길이(전환 크로스페이드 반영)
t=0.0; prev="컷"
for r in rows:
    inxf=XF if prev in DISS else 0.0; st=max(0,t-inxf); r["start"]=round(st,2); t=st+r["slot"]; r["end"]=round(t,2); prev=r["trans"]
json.dump({"rows":rows,"total":round(t,2),"lang_totals":{k:round(v,1) for k,v in totals.items()}},
          open(os.path.join(I18N,"timeline.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=2)

print("\n=== 언어별 나레이션 총합(gTTS) ===")
for l in LANGS: print(f"  {l}: {totals[l]/60:.1f}분")
print(f"\n=== 최대슬롯 기반 영상 총길이: {t:.1f}s ({t/60:.2f}분) ===")
# 언어별로 슬롯 대비 초과하는 씬(잘릴 위험) 점검 — 최대슬롯이라 없어야 정상
over=[(r['n'],l,r['durs'][l],r['slot']) for r in rows for l in LANGS if not r['music'] and r['durs'][l]>r['slot']+0.01]
print("슬롯 초과(잘림위험):", over if over else "없음 ✓")
# 가장 긴 언어가 슬롯을 지배하는 비율
dom={l:0 for l in LANGS}
for r in rows:
    if r["music"]: continue
    mx=max(r["durs"],key=lambda k:r["durs"][k]); dom[mx]+=1
print("씬별 최장 언어 분포:",dom)
