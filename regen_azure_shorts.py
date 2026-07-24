# -*- coding: utf-8 -*-
"""쇼츠 4개 나레이션을 공식 Azure TTS(상업 라이선스)로 재생성.
- 음성: KO=선희(SunHi), EN=Emma  (edge-tts와 동일 음성모델, 합법)
- 원본 나레이션 텍스트는 각 narr 폴더의 <mp3>.txt 캐시에서 그대로 사용
- 씬 길이(assemble 고정값)에 맞춰 미세 템포조정 → 나레이션 잘림 방지 + 타임라인 보존
"""
import os, sys, subprocess
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
from dotenv import load_dotenv
load_dotenv()  # AZURE_SPEECH_KEY / AZURE_SPEECH_REGION
os.environ["EDGE_ACTIVE_VOICE"] = "sunhi"   # KO 여성(선희). EN은 save_tts_azure가 Emma 강제
os.environ["TTS_ENGINE"] = "azure"
sys.path.insert(0, os.getcwd())
from tts_manager import save_tts_azure

# (라벨, narr폴더, lang, [씬별 목표길이])  ← assemble 스크립트의 dur과 일치
JOBS = [
    ("turtle_EN",  "scratch/shorts_v2/narr",    "en", [3.5, 6.0, 6.6, 6.6, 4.6]),
    ("turtle_KO",  "scratch/shorts_v2/narr_ko", "ko", [4.0, 5.2, 7.2, 6.3, 4.6]),
    ("workout_EN", "scratch/wi/narr_en",        "en", [5.0, 4.0, 4.5, 4.0, 5.0]),
    ("workout_KO", "scratch/wi/narr_ko",        "ko", [5.6, 5.2, 4.8, 4.6, 5.8]),
]
TAIL = 0.12   # 씬 끝 여유(무음) — 마지막 음절 잘림 방지

def dur(p):
    return float(subprocess.run(["ffprobe","-v","quiet","-of","csv=p=0",
        "-show_entries","format=duration",p], capture_output=True, text=True).stdout.strip() or 0)

problems = []
for label, folder, lang, targets in JOBS:
    print(f"\n===== {label}  ({folder}, {lang}) =====", flush=True)
    for i, tgt in enumerate(targets, 1):
        final = os.path.join(folder, f"s{i}.mp3")
        txtc = final + ".txt"
        if not os.path.exists(txtc):
            problems.append(f"{label} s{i}: 원본 텍스트 캐시 없음 {txtc}")
            print(f"  ! s{i}: txt 캐시 없음 → 건너뜀"); continue
        text = open(txtc, encoding="utf-8").read().strip()
        raw = os.path.join(folder, f"s{i}.azraw.mp3")
        # 1) Azure 원본 생성 (여기서 [TTS] Azure ... 로그가 찍혀야 함)
        save_tts_azure(text, raw, lang=lang)
        d = dur(raw)
        fit = tgt - TAIL
        factor = 1.0 if d <= fit else round(d / fit, 4)
        factor = min(factor, 1.6)
        # 2) 씬 길이에 맞춰 템포조정(피치 보존) → 최종 narr 경로 덮어쓰기
        subprocess.run(["ffmpeg","-y","-v","error","-i",raw,
            "-filter:a", f"atempo={factor}", "-ar","24000","-ac","1",
            "-c:a","libmp3lame","-b:a","96k", final], check=True)
        nd = dur(final)
        open(txtc, "w", encoding="utf-8").write(text)  # 캐시 유지
        flag = "" if nd <= tgt + 0.01 else "  <<< 초과!"
        print(f"  s{i}: Azure {d:.2f}s → x{factor} → {nd:.2f}s / 씬 {tgt}s{flag}", flush=True)
        if nd > tgt + 0.05:
            problems.append(f"{label} s{i}: {nd:.2f}s > 씬 {tgt}s")
        os.remove(raw)

print("\n===== 결과 =====")
if problems:
    print("문제:", *problems, sep="\n  ")
else:
    print("OK — 20클립 전부 Azure 재생성, 씬 길이 내로 맞춤(잘림 없음).")
print("REGEN_AZURE_DONE")
