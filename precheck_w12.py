# -*- coding: utf-8 -*-
"""업로드 전 10가지 체크 (W12). 하나라도 ✗면 업로드 중단."""
import os, re, json, subprocess
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
PKG = "hangeul_birth_vowels/w12pkg"
VIDS = {"ko": "hangeul_birth_vowels/hangeul_w12_injun_np_ko.mp4",
        "en": "hangeul_birth_vowels/hangeul_w12_injun_np_en.mp4"}
THUMB = "hangeul_birth_vowels/thumb_w12_1280x720.jpg"
ok_all = True
def chk(name, ok, detail=""):
    global ok_all
    if not ok: ok_all = False
    print(f"  [{'✅' if ok else '✗ '}] {name}{(' — ' + detail) if detail else ''}")

def probe(f, args):
    return subprocess.run(["ffprobe", "-v", "error"] + args + [f],
                          capture_output=True, text=True).stdout.strip()

print("=== 업로드 전 10가지 체크 (W12) ===")

# 1. 영상 존재·4K·길이
for L, f in VIDS.items():
    if not os.path.exists(f):
        chk(f"{L} 영상", False, "없음"); continue
    wh = probe(f, ["-select_streams", "v", "-show_entries", "stream=width,height", "-of", "csv=p=0"])
    dur = float(probe(f, ["-show_entries", "format=duration", "-of", "csv=p=0"]) or 0)
    mb = os.path.getsize(f) // 1048576
    chk(f"1. {L} 영상 4K", wh.startswith("3840"), f"{wh} · {int(dur//60)}분{int(dur%60)}초 · {mb}MB")

# 2. 오디오 무음 아님
for L, f in VIDS.items():
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", f, "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"mean_volume: ([-\d.]+) dB", out)
    v = float(m.group(1)) if m else 0
    chk(f"2. {L} 오디오 정상", -30 < v < -10, f"mean {v} dB")

# 3. 소프트 자막 트랙(번인 금지)
for L, f in VIDS.items():
    langs = probe(f, ["-select_streams", "s", "-show_entries", "stream_tags=language", "-of", "csv=p=0"]).split()
    chk(f"3. {L} 소프트 자막", len(langs) >= 2, ",".join(langs))

# 4. 5개국어 자막 파일
for L in ("ko", "en"):
    files = [f"{PKG}/{L}_{c}.srt" for c in ("ko", "en", "ja", "zh", "es")]
    have = [os.path.basename(x) for x in files if os.path.exists(x) and os.path.getsize(x) > 100]
    chk(f"4. {L}판 자막 5개국어", len(have) == 5, f"{len(have)}/5")

# 5. 썸네일
if os.path.exists(THUMB):
    kb = os.path.getsize(THUMB) // 1024
    from PIL import Image
    w, h = Image.open(THUMB).size
    chk("5. 썸네일 1280x720 <2MB", (w, h) == (1280, 720) and kb < 2048, f"{w}x{h} {kb}KB")
else:
    chk("5. 썸네일", False, "없음")

# 6. 제목(100자 이내)
for L in ("ko", "en"):
    p = f"{PKG}/{L}_title.txt"
    t = open(p, encoding="utf-8").read().strip() if os.path.exists(p) else ""
    chk(f"6. {L} 제목", 0 < len(t) <= 100, f"{len(t)}자")

# 7. 설명 + AI 고지
for L in ("ko", "en"):
    p = f"{PKG}/{L}_desc.txt"
    d = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    has_ai = ("AI" in d) and ("Azure" in d or "Gemini" in d or "Veo" in d)
    chk(f"7. {L} 설명+AI고지", len(d) > 200 and has_ai, f"{len(d)}자, AI고지={'O' if has_ai else 'X'}")

# 8. 챕터
d = open(f"{PKG}/ko_desc.txt", encoding="utf-8").read() if os.path.exists(f"{PKG}/ko_desc.txt") else ""
ch = re.findall(r"^\d+:\d{2} ", d, re.M)
chk("8. 챕터(0:00 시작)", len(ch) >= 3 and "0:00 " in d, f"{len(ch)}개")

# 9. 태그 500자 이내
p = f"{PKG}/w12_tags.txt"
tg = [t.strip() for t in open(p, encoding="utf-8").read().split(",") if t.strip()] if os.path.exists(p) else []
total = sum(len(t) + 2 if " " in t else len(t) for t in tg) + max(0, len(tg) - 1)
chk("9. 태그 ≤500자", 0 < total <= 500, f"{len(tg)}개 / {total}자")

# 10. 다국어 제목·설명(ja/zh/es)
n = sum(1 for c in ("ja", "zh", "es")
        if os.path.exists(f"{PKG}/{c}_title.txt") and os.path.getsize(f"{PKG}/{c}_title.txt") > 5
        and os.path.exists(f"{PKG}/{c}_desc.txt") and os.path.getsize(f"{PKG}/{c}_desc.txt") > 200)
chk("10. 다국어 제목·설명(ja/zh/es)", n == 3, f"{n}/3")

# 매니페스트
mf = sum(1 for m in ("ko", "en") if os.path.exists(f"{PKG}/w12_{m}_manifest.json"))
chk("+ 매니페스트", mf == 2, f"{mf}/2")

print("\n" + ("=== ✅ 전부 통과 — 업로드 가능 ===" if ok_all else "=== ✗ 실패 항목 있음 — 업로드 중단 ==="))
raise SystemExit(0 if ok_all else 1)
