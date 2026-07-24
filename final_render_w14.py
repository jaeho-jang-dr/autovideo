# -*- coding: utf-8 -*-
"""W14 정식(라이선스) 최종 렌더: Azure 선희(KO)/Emma(EN) + 마담제이 발음클립(jamo, 여성) → compile_np 4K.
   사용: python final_render_w14.py <ko|en>   ※KO·EN 병렬 금지(순차)
   ★TTS 캐시 함정: 캐시키에 엔진명이 포함되므로 edge 음성이 재사용되지 않는다.
     그래도 렌더 로그에 Azure 호출이 실제로 찍히는지 확인할 것(0건이면 캐시 재사용 의심)."""
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
# ★마담제이=여성 → 발음클립은 jamo(선희 여성)
os.environ["JAMO_DIR"] = os.path.join(ROOT, "web", "public", "audio", "jamo")
os.environ["PYTHONIOENCODING"] = "utf-8"
lang = sys.argv[1] if len(sys.argv) > 1 else "ko"
sys.exit(subprocess.run([sys.executable, "compile_np.py", "KO-W14", "hangeul_w14_madam", "4K", lang],
                        cwd=ROOT, env=os.environ).returncode)
