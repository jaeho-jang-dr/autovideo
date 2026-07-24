# -*- coding: utf-8 -*-
"""W16 최종 업로드 패키지를 한 곳에 모은다(사장님 업로드용).
W16_package/한글판/ · 영어판/ 에 영상·썸네일·제목설명태그·자막5개를 배치."""
import os, shutil, json
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
HB = "hangeul_birth_vowels"; PKG = f"{HB}/w16pkg"; OUT = "W16_package"

EDITIONS = [
    ("한글판", "ko", f"{HB}/hangeul_w16_stickman_np_ko.mp4", f"{HB}/thumb_w16_ko_1280x720.jpg",
     "subs_upload/W16_1_한글판", "W16_취미와빈도_한글판.mp4"),
    ("영어판", "en", f"{HB}/hangeul_w16_stickman_np_en.mp4", f"{HB}/thumb_w16_en_1280x720.jpg",
     "subs_upload/W16_2_영어판", "W16_Hobbies_Frequency_영어판.mp4"),
]
SUBS5 = ["한국어.srt", "영어.srt", "일본어.srt", "중국어(중국).srt", "스페인어.srt"]

def rd(p):
    return open(p, encoding="utf-8").read().strip() if os.path.exists(p) else ""

for name, code, vid, thumb, subdir, vname in EDITIONS:
    d = os.path.join(OUT, name); os.makedirs(os.path.join(d, "자막"), exist_ok=True)
    shutil.copy(vid, os.path.join(d, vname))
    shutil.copy(thumb, os.path.join(d, "썸네일.jpg"))
    for s in SUBS5:
        src = os.path.join(subdir, s)
        if os.path.exists(src): shutil.copy(src, os.path.join(d, "자막", s))
    title = rd(f"{PKG}/{code}_title.txt")
    desc = rd(f"{PKG}/{code}_desc.txt")
    tags = rd(f"{PKG}/w16_tags.txt")
    comment = rd(f"{PKG}/{code}_comment.txt")
    vlang = "한국어" if code == "ko" else "영어(English)"
    with open(os.path.join(d, "0_제목설명태그.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"[제목]\n{title}\n\n[설명]\n{desc}\n\n[태그]\n{tags}\n\n")
        f.write(f"[동영상 언어] {vlang}  [카테고리] 교육  [AI 변경콘텐츠] 예(Yes)  [아동용] 아니요\n")
        f.write(f"[해상도] 3840x2160(4K)  [길이] 6:59\n\n")
        f.write(f"[고정댓글용]\n{comment}\n")
    print(f"[{name}] 완성: 영상+썸네일+제목설명태그+자막5")

print(f"\n=== 패키지: {os.path.abspath(OUT)} ===")
# 다국어 제목/설명(ja/zh/es)도 함께 넣어 사장님이 다국어 제목설명 참고
mdir = os.path.join(OUT, "다국어_제목설명"); os.makedirs(mdir, exist_ok=True)
for c in ("ja", "zh", "es"):
    with open(os.path.join(mdir, f"{c}.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"[{c} 제목]\n{rd(f'{PKG}/{c}_title.txt')}\n\n[{c} 설명]\n{rd(f'{PKG}/{c}_desc.txt')}\n")
print("다국어 제목설명(ja/zh/es)도 포함")
