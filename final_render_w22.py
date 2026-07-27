# -*- coding: utf-8 -*-
"""W22 정식(라이선스) 최종 렌더: Azure 선희(KO)/Emma(EN) + 지은 발음클립(jamo, 여성) → compile_np 4K.
   사용: python final_render_w22.py <ko|en>   ※KO·EN 병렬 금지(순차)
   ★TTS 캐시 함정: 캐시키에 엔진명이 포함되므로 edge 음성이 재사용되지 않는다.
     그래도 렌더 로그에 Azure 호출이 실제로 찍히는지 확인할 것(0건이면 캐시 재사용 의심).
   ★자막은 그 판의 언어 하나만 소프트로 넣는다(SUB_LANGS) — 이중자막 금지(W20 v2 지시).
   ★걷기 보폭 WALK_STRIDE_SEC=1.08 (W22 빌드 기준)."""
import os, sys, subprocess
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
os.environ["TTS_ENGINE"] = "azure"            # ★정식 라이선스(유튜브 게시용)
os.environ["ELEVEN_API_KEY"] = ""
os.environ["EDGE_ACTIVE_VOICE"] = "sunhi"     # KO 나레이터 = 선희 / EN = Emma
os.environ["JAMO_DIR"] = os.path.join(ROOT, "web", "public", "audio", "jamo")  # 지은=여성 발음클립
os.environ["WALK_STRIDE_SEC"] = "1.08"
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
lang = sys.argv[1] if len(sys.argv) > 1 else "ko"
os.environ["SUB_LANGS"] = lang                # ko판=한글자막 / en판=영어자막
sys.exit(subprocess.run([sys.executable, "compile_np.py", "KO-W22", "hangeul_w22_jieun", "4K", lang],
                        cwd=ROOT, env=os.environ).returncode)
