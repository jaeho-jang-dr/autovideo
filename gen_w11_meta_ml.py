# -*- coding: utf-8 -*-
"""W11 다국어 제목·설명: ko/en 원본 제목·설명을 ja/zh/es 등으로 번역.
   KO영상: ko_en/ja/zh/es _title/_desc  |  EN영상: en_ko/ja/zh/es _title/_desc"""
import os
from deep_translator import GoogleTranslator
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
PKG = os.path.join(ROOT, "hangeul_birth_vowels", "w11pkg")
GCODE = {"en": "en", "ko": "ko", "ja": "ja", "zh": "zh-CN", "es": "es"}

def rd(n): return open(os.path.join(PKG, n), encoding="utf-8").read()
def wr(n, t): open(os.path.join(PKG, n), "w", encoding="utf-8").write(t)

def tr(text, src, tg):
    # 설명은 줄단위 번역(해시태그·URL·타임스탬프 보존)
    out = []
    for ln in text.split("\n"):
        s = ln.strip()
        if not s or s.startswith("#") or s.startswith("http") or s.startswith("🔗") \
           or __import__("re").match(r"^\d+:\d\d", s) or s[0] in "🎨":
            out.append(ln); continue
        try: out.append(GoogleTranslator(source=src, target=GCODE[tg]).translate(ln) or ln)
        except Exception: out.append(ln)
    return "\n".join(out)

if __name__ == "__main__":
    for base, cover in [("ko", ["en","ja","zh","es"]), ("en", ["ko","ja","zh","es"])]:
        title = rd(f"{base}_title.txt"); desc = rd(f"{base}_desc.txt")
        for tg in cover:
            tn = f"{base}_{tg}_title.txt"; dn = f"{base}_{tg}_desc.txt"
            if os.path.exists(os.path.join(PKG, tn)) and os.path.getsize(os.path.join(PKG, tn)) > 5:
                print("skip", tn); continue
            try:
                wr(tn, GoogleTranslator(source=base, target=GCODE[tg]).translate(title) or title)
                wr(dn, tr(desc, base, tg))
                print(f"  {base}→{tg} meta 완료")
            except Exception as e:
                print(f"  ERR {base}_{tg}: {str(e)[:60]}")
    print("다국어 제목·설명 완료")
