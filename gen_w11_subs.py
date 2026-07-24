# -*- coding: utf-8 -*-
"""W11 5개국 자막: 렌더 srt(ko/en)를 deep_translator(Google)로 ja/zh/es 등 번역.
   KO영상: ko(원본)+en+ja+zh+es / EN영상: en(원본)+ko+ja+zh+es. 타임스탬프 유지.
   출력: hangeul_birth_vowels/w11pkg/ko_<lang>.srt, en_<lang>.srt"""
import os, re, time
from deep_translator import GoogleTranslator
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
PKG = os.path.join(ROOT, "hangeul_birth_vowels", "w11pkg")
SRT_KO = os.path.join(ROOT, "hangeul_birth_vowels", "hangeul_w11_madam_np.ko.srt")
SRT_EN = os.path.join(ROOT, "hangeul_birth_vowels", "hangeul_w11_madam_np.en.srt")
GCODE = {"en": "en", "ko": "ko", "ja": "ja", "zh": "zh-CN", "es": "es"}   # Google 코드

def parse_srt(p):
    blocks = open(p, encoding="utf-8").read().strip().split("\n\n")
    out = []
    for b in blocks:
        L = b.strip().split("\n")
        if len(L) < 3: continue
        out.append((L[0], L[1], " ".join(L[2:])))
    return out

def write_srt(path, cues, texts):
    with open(path, "w", encoding="utf-8") as f:
        for (idx, tm, _), tx in zip(cues, texts):
            f.write(f"{idx}\n{tm}\n{tx}\n\n")

def translate_all(cues, src, tgt):
    tr = GoogleTranslator(source=src, target=GCODE[tgt])
    texts = [c[2] for c in cues]
    try:
        res = tr.translate_batch(texts)
    except Exception:
        res = []
        for t in texts:
            try: res.append(tr.translate(t) or t)
            except Exception: res.append(t)
            time.sleep(0.1)
    return [r if r else texts[i] for i, r in enumerate(res)]

def done(name):
    p = os.path.join(PKG, name)
    return os.path.exists(p) and os.path.getsize(p) > 100

if __name__ == "__main__":
    ko = parse_srt(SRT_KO); en = parse_srt(SRT_EN)
    print(f"KO {len(ko)}큐, EN {len(en)}큐", flush=True)
    jobs = [("ko", ko, "ko"), ("ko", ko, "en"), ("ko", ko, "ja"), ("ko", ko, "zh"), ("ko", ko, "es"),
            ("en", en, "en"), ("en", en, "ko"), ("en", en, "ja"), ("en", en, "zh"), ("en", en, "es")]
    for src, cues, tg in jobs:
        name = f"{src}_{tg}.srt"
        if done(name):
            print(f"  skip {name}", flush=True); continue
        try:
            texts = [c[2] for c in cues] if tg == src else translate_all(cues, src, tg)
            write_srt(os.path.join(PKG, name), cues, texts)
            print(f"  {src}→{tg} 완료", flush=True)
        except Exception as e:
            print(f"  ERR {name}: {str(e)[:80]}", flush=True)
    print("자막 생성 종료 →", PKG, flush=True)
