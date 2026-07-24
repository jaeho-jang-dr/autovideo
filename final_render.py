# -*- coding: utf-8 -*-
"""정식(라이선스) 렌더 래퍼: .env 로드 → Azure 선희/Emma + Azure DB클립(scratch/w11_jamo_azure) → compile_np.
   사용: python final_render.py <ko|en>"""
import os, sys, subprocess
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
os.environ["TTS_ENGINE"] = "azure"          # ★정식 라이선스 나레이션
os.environ["ELEVEN_API_KEY"] = ""           # ElevenLabs 끄기
os.environ["EDGE_ACTIVE_VOICE"] = "sunhi"   # KO=선희
os.environ["JAMO_DIR"] = os.path.join(ROOT, "scratch", "w11_jamo_azure")   # Azure DB클립
os.environ["PYTHONIOENCODING"] = "utf-8"
lang = sys.argv[1] if len(sys.argv) > 1 else "ko"
sys.exit(subprocess.run([sys.executable, "compile_np.py", "KO-W11", "hangeul_w11_madam", "review", lang],
                        cwd=ROOT, env=os.environ).returncode)
