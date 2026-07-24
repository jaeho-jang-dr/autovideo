# -*- coding: utf-8 -*-
"""W12 정식(라이선스) 최종 렌더: .env → Azure 선희(KO)/Emma(EN) 나레이션 + 인준 Azure DB클립 → compile_np 4K.
   사용: python final_render_w12.py <ko|en>
   ※ KO·EN 병렬 금지(공유 tts_cache 레이스) — 순차로 실행할 것."""
import os, sys, subprocess
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
os.environ["TTS_ENGINE"] = "azure"            # ★정식 라이선스 나레이션(선희/Emma)
os.environ["ELEVEN_API_KEY"] = ""             # ElevenLabs 끄기
os.environ["EDGE_ACTIVE_VOICE"] = "sunhi"     # KO 나레이터 = 선희(여행 가이드)
# ★DB 발음클립 = 인준(남) — gen_db_azure.py 로 Azure 생성해 둔 jamo_m
os.environ["JAMO_DIR"] = os.path.join(ROOT, "web", "public", "audio", "jamo_m")
os.environ["PYTHONIOENCODING"] = "utf-8"
lang = sys.argv[1] if len(sys.argv) > 1 else "ko"
sys.exit(subprocess.run([sys.executable, "compile_np.py", "KO-W12", "hangeul_w12_injun", "4K", lang],
                        cwd=ROOT, env=os.environ).returncode)
