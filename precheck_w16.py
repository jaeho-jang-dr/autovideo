# -*- coding: utf-8 -*-
"""업로드 전 10가지 체크 (W16). 하나라도 ✗면 업로드 중단.
   ★자막은 API 매니페스트(subs 5개)로 올린다 → 체크4는 subs_upload/W16_*에 5개씩 준비됐는지 본다.
   (precheck_w15.py 복제 — 경로만 W16으로 치환)"""
import os, re, subprocess
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
PKG = "hangeul_birth_vowels/w16pkg"
# ★compile_np 4K 모드는 접미사 없이 같은 파일명에 3840x2160으로 저장한다
VIDS = {"ko": "hangeul_birth_vowels/hangeul_w16_stickman_np_ko.mp4",
        "en": "hangeul_birth_vowels/hangeul_w16_stickman_np_en.mp4"}
THUMBS = {"ko": "hangeul_birth_vowels/thumb_w16_ko_1280x720.jpg",
          "en": "hangeul_birth_vowels/thumb_w16_en_1280x720.jpg"}
SUBS_DIR = {"ko": "subs_upload/W16_1_한글판", "en": "subs_upload/W16_2_영어판"}
YT5 = ["한국어.srt", "영어.srt", "일본어.srt", "중국어(중국).srt", "스페인어.srt"]

ok_all = True


def chk(name, ok, detail=""):
    global ok_all
    if not ok:
        ok_all = False
    print(f"  [{'OK' if ok else '✗ '}] {name}{(' — ' + detail) if detail else ''}")


def probe(f, args):
    return subprocess.run(["ffprobe", "-v", "error"] + args + [f],
                          capture_output=True, text=True).stdout.strip()


print("=== 업로드 전 10가지 체크 (W16) ===")

# 1. 영상 4K
for L, f in VIDS.items():
    if not os.path.exists(f):
        chk(f"1. {L} 영상 4K", False, "없음")
        continue
    wh = probe(f, ["-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0"])
    dur = float(probe(f, ["-show_entries", "format=duration", "-of", "csv=p=0"]) or 0)
    mb = os.path.getsize(f) // 1048576
    chk(f"1. {L} 영상 4K", wh.startswith("3840"), f"{wh} · {int(dur//60)}분{int(dur%60)}초 · {mb}MB")

# 2. 오디오 정상(무음 아님)
for L, f in VIDS.items():
    if not os.path.exists(f):
        chk(f"2. {L} 오디오", False, "영상 없음"); continue
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"mean_volume: ([-\d.]+) dB", out)
    v = float(m.group(1)) if m else 0
    chk(f"2. {L} 오디오 정상", -32 < v < -8, f"mean {v} dB")

# 3. 나레이션 = Azure(정식 라이선스) — tts_cache에 azure 세그먼트가 있는지
naz = len([f for f in os.listdir("hangeul_birth_vowels/tts_cache") if "_azure_" in f]) \
    if os.path.isdir("hangeul_birth_vowels/tts_cache") else 0
chk("3. Azure TTS(선희/Emma) 사용", naz > 50, f"azure 세그먼트 {naz}개")

# 4. 자막 5개국어 준비(매니페스트 subs API 업로드용)
for L, d in SUBS_DIR.items():
    have = [s for s in YT5 if os.path.exists(f"{d}/{s}") and os.path.getsize(f"{d}/{s}") > 100]
    chk(f"4. {L}판 자막 5개 준비", len(have) == 5, f"{len(have)}/5 in {d}")

# 5. 썸네일
for L, t in THUMBS.items():
    if not os.path.exists(t):
        chk(f"5. {L} 썸네일", False, "없음"); continue
    from PIL import Image
    w, h = Image.open(t).size
    kb = os.path.getsize(t) // 1024
    chk(f"5. {L} 썸네일 1280x720 <2MB", (w, h) == (1280, 720) and kb < 2048, f"{w}x{h} {kb}KB")

# 6. 제목 100자 이내 (5개 언어)
for c in ("ko", "en", "ja", "zh", "es"):
    p = f"{PKG}/{c}_title.txt"
    t = open(p, encoding="utf-8").read().strip() if os.path.exists(p) else ""
    chk(f"6. {c} 제목 ≤100자", 0 < len(t) <= 100, f"{len(t)}자")

# 7. 설명 + AI 고지
for c in ("ko", "en", "ja", "zh", "es"):
    p = f"{PKG}/{c}_desc.txt"
    d = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    has_ai = ("Gemini" in d or "AI" in d) and "Azure" in d
    chk(f"7. {c} 설명+AI고지", len(d) > 200 and has_ai, f"{len(d)}자, AI고지={'O' if has_ai else 'X'}")

# 8. 챕터(0:00 시작, 3개 이상)
d = open(f"{PKG}/ko_desc.txt", encoding="utf-8").read() if os.path.exists(f"{PKG}/ko_desc.txt") else ""
ch = re.findall(r"^\d+:\d{2} ", d, re.M)
chk("8. 챕터(0:00 시작)", len(ch) >= 3 and "0:00 " in d, f"{len(ch)}개")

# 9. 태그 500자 이내
p = f"{PKG}/w16_tags.txt"
tg = [t.strip() for t in open(p, encoding="utf-8").read().split(",") if t.strip()] if os.path.exists(p) else []
total = sum(len(t) + 2 if " " in t else len(t) for t in tg) + max(0, len(tg) - 1)
chk("9. 태그 ≤500자", 0 < total <= 500, f"{len(tg)}개 / {total}자")

# 10. 매니페스트 2개 + 자막 5개국어 채워짐(★API 업로드)
import json
n = 0
for L in ("ko", "en"):
    p = f"{PKG}/w16_{L}_manifest.json"
    if not os.path.exists(p):
        continue
    mf = json.load(open(p, encoding="utf-8"))
    if len(mf.get("subs", {})) == 5 and len(mf.get("localizations", {})) == 5:
        n += 1
chk("10. 매니페스트(자막 5개·5개국어 메타)", n == 2, f"{n}/2")

print("\n" + ("=== ✅ 전부 통과 — 업로드 가능 ===" if ok_all else "=== ✗ 실패 항목 있음 — 업로드 중단 ==="))
raise SystemExit(0 if ok_all else 1)
