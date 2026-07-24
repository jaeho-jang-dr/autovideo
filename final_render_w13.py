# -*- coding: utf-8 -*-
"""W13 정식(라이선스) 최종 렌더: Azure 선희(KO)/Emma(EN) + 지은 발음클립(jamo, 여성) → compile_np 4K.
   사용: python final_render_w13.py <ko|en>   ※KO·EN 병렬 금지(순차)"""
import os, sys, subprocess
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
os.environ["TTS_ENGINE"] = "azure"            # ★정식 라이선스
os.environ["ELEVEN_API_KEY"] = ""
os.environ["EDGE_ACTIVE_VOICE"] = "sunhi"     # KO 나레이터 = 선희
# ★지은=여성 → 발음클립은 jamo(선희 여성)
os.environ["JAMO_DIR"] = os.path.join(ROOT, "web", "public", "audio", "jamo")
os.environ["PYTHONIOENCODING"] = "utf-8"
lang = sys.argv[1] if len(sys.argv) > 1 else "ko"
sys.exit(subprocess.run([sys.executable, "compile_np.py", "KO-W13", "hangeul_w13_jieun", "4K", lang],
                        cwd=ROOT, env=os.environ).returncode)
