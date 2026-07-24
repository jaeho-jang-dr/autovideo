# -*- coding: utf-8 -*-
"""W18 정식(라이선스) 최종 렌더: Azure 선희(KO)/Emma(EN) → compile_np 4K.
   사용: python final_render_w18.py <ko|en>   ※KO·EN 병렬 금지(순차)
   ★나레이션 목소리는 승인 초안과 동일(선희/Emma), 엔진만 Azure(정식 라이선스=유튜브 게시용).
   ★TTS 캐시 함정: 캐시키에 엔진명 포함 → edge 음성 재사용 안 됨. 로그에 [TTS] Azure 실제로 찍히는지 확인(0건이면 캐시 재사용 의심).
   ★KO판 오디오 = 순수 한국어(선희 러닝 + 선희 DB클립). 괄호 영어뜻은 compile_np가 KO 오디오에서 strip(Emma 미독). 자막엔 유지."""
import os, sys, subprocess
ROOT = r"D:\Entertainments\DevEnvironment\autovideo"
for line in open(os.path.join(ROOT, ".env"), encoding="utf-8"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
os.environ["TTS_ENGINE"] = "azure"            # ★정식 라이선스(유튜브 게시용)
os.environ["ELEVEN_API_KEY"] = ""
os.environ["EDGE_ACTIVE_VOICE"] = "sunhi"     # KO=선희(여, 승인본과 동일) / EN=Emma
os.environ["JAMO_DIR"] = os.path.join(ROOT, "web", "public", "audio", "jamo")
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"
lang = sys.argv[1] if len(sys.argv) > 1 else "ko"
sys.exit(subprocess.run([sys.executable, "compile_np.py", "KO-W18", "hangeul_w18_madamjay", "4K", lang],
                        cwd=ROOT, env=os.environ).returncode)
