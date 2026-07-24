# -*- coding: utf-8 -*-
"""거북목 쇼츠 업로드 패키지 생성. 영어판/한글판 각 폴더에:
영상 + 썸네일 + 제목설명태그.txt + 5개국어 자막 + 각 자막 제목설명."""
import os, shutil
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
OUT = "shorts_package/turtle_neck"
LANGS = [("ko","한국어"),("en","영어"),("ja","일본어"),("zh","중국어(중국)"),("es","스페인어")]

def ts(t):
    h=int(t//3600); m=int((t%3600)//60); s=t%60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".",",")

# 씬 타임라인 (영어판 / 한글판)
TL_EN=[(0,3.5),(3.5,9.5),(9.5,16.1),(16.1,22.7),(22.7,27.3)]
TL_KO=[(0,4.0),(4.0,9.2),(9.2,16.4),(16.4,22.7),(22.7,27.3)]

# 씬별 5개국어 자막 (한글은 모든 언어에 한글 원문 유지 안 함 — 과학쇼츠라 완전 번역)
SUBS = {
 "ko":["지금 스마트폰을 내려다보고 계신가요?","고개를 15도만 숙여도 목엔 12kg이 실려요.","60도로 숙이면 무려 27kg! 목에 아이를 얹은 셈이죠.","자세를 리셋하세요. 등과 뒤통수를 벽에 붙이고 서요.","매일 친턱 운동으로 목을 바르게 펴 주세요."],
 "en":["Are you looking down at your phone right now?","Tilt your head just 15 degrees and your neck holds 12kg.","At 60 degrees it hits 27kg - like a child on your neck!","Reset your posture - back and head flat against a wall.","Do chin-tucks every day to straighten your neck."],
 "ja":["今スマホを見下ろしていませんか？","たった15度うつむくだけで首に12kgかかります。","60度でなんと27kg！首に子どもを乗せたのと同じです。","姿勢をリセット。背中と後頭部を壁につけて立ちます。","毎日チンタック運動で首をまっすぐ伸ばしましょう。"],
 "zh":["你现在正低头看手机吗？","仅仅低头15度，颈部就承受12公斤。","低到60度竟达27公斤！等于脖子上坐着一个孩子。","重置姿势：后背和后脑贴墙站立。","每天做收下巴运动，让颈椎回正。"],
 "es":["¿Estás mirando el móvil con la cabeza agachada?","Inclina la cabeza solo 15 grados y el cuello soporta 12 kg.","A 60 grados llega a 27 kg, como un niño sobre el cuello.","Reinicia tu postura: espalda y cabeza contra la pared.","Haz retracciones de cuello cada día para enderezarlo."],
}

# 제목/설명/태그 (5개국어 자막 제목설명 + 영상 언어용)
TITLE = {
 "ko":"거북목이면 목에 27kg?! 🐢 3초 자가 교정법 #Shorts",
 "en":"Text Neck = 27kg on your neck?! 🐢 Fix it fast #Shorts",
 "ja":"スマホ首で首に27kg？！🐢 今すぐできる矯正法 #Shorts",
 "zh":"乌龟颈让脖子承受27公斤？！🐢 快速自我矫正 #Shorts",
 "es":"¿Cuello de tortuga = 27 kg en el cuello? 🐢 Corrígelo ya #Shorts",
}
DESC = {
 "ko":"고개를 60도 숙이면 목엔 무려 27kg! 스마트폰이 만든 거북목, 3초 친턱 운동으로 바로잡는 법을 알려드려요. 🐢\n\n📌 자세한 내용은 본편: https://youtu.be/KI_LvmiTWtE\n\n※ 본 영상은 생성형 AI(Google Veo/Flow)로 제작·연출되었습니다.\n※ 교육 목적이며 통증이 지속되면 전문의와 상담하세요.\n\n#거북목 #일자목 #목통증 #자세교정 #친턱운동 #Shorts",
 "en":"Tilt your head 60 degrees and your neck bears 27kg! Learn how a 3-second chin-tuck fixes smartphone text neck. 🐢\n\n📌 Full video: https://youtu.be/KI_LvmiTWtE\n\n※ Created and directed with generative AI (Google Veo/Flow).\n※ Educational only - see a specialist if pain persists.\n\n#textneck #posture #neckpain #chintuck #Shorts",
 "ja":"60度うつむくと首に27kg！スマホ首を3秒のチンタックで直す方法。🐢\n\n📌 本編: https://youtu.be/KI_LvmiTWtE\n\n※ 生成AI(Google Veo/Flow)で制作・演出。\n※ 教育目的です。痛みが続く場合は専門医へ。\n\n#スマホ首 #ストレートネック #姿勢改善 #Shorts",
 "zh":"低头60度，颈部承受27公斤！用3秒收下巴运动矫正乌龟颈。🐢\n\n📌 完整视频: https://youtu.be/KI_LvmiTWtE\n\n※ 由生成式AI(Google Veo/Flow)制作。\n※ 仅供教育，疼痛持续请就医。\n\n#乌龟颈 #颈椎 #姿势矫正 #Shorts",
 "es":"¡Inclina la cabeza 60 grados y el cuello soporta 27 kg! Corrige el cuello de tortuga con una retracción de 3 segundos. 🐢\n\n📌 Video completo: https://youtu.be/KI_LvmiTWtE\n\n※ Creado con IA generativa (Google Veo/Flow).\n※ Solo educativo, consulta a un especialista si el dolor persiste.\n\n#cuellodetortuga #postura #Shorts",
}
TAGS = "거북목, 일자목, 목통증, 자세교정, 친턱운동, 스마트폰 자세, 목디스크, 경추, 목건강, 스트레칭, 건강, 과학, 의학, 물리치료, text neck, turtle neck, forward head posture, posture correction, chin tuck, neck pain, neck health, health, shorts, 쇼츠, 건강쇼츠, drjay"

def write_edition(edname, video_src, thumb_src, tl):
    d = os.path.join(OUT, edname)
    os.makedirs(d, exist_ok=True)
    shutil.copy(video_src, os.path.join(d, f"거북목쇼츠_{edname}.mp4"))
    shutil.copy(thumb_src, os.path.join(d, "썸네일.png"))
    # 영상 언어용 제목설명태그 (한글판=ko, 영어판=en)
    vlang = "ko" if "한글" in edname else "en"
    with open(os.path.join(d, "0_영상_제목설명태그.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"[제목]\n{TITLE[vlang]}\n\n[설명]\n{DESC[vlang]}\n\n[태그]\n{TAGS}\n\n[동영상 언어] {vlang}  [카테고리] 교육  [AI 변경콘텐츠] 예  [아동용] 아니요\n[본편 연결] https://youtu.be/KI_LvmiTWtE\n")
    # 5개국어 자막 + 각 제목설명
    subdir = os.path.join(d, "자막")
    os.makedirs(subdir, exist_ok=True)
    for code, label in LANGS:
        srt = os.path.join(subdir, f"{label}.srt")
        with open(srt, "w", encoding="utf-8", newline="\n") as f:
            for i,((t0,t1),txt) in enumerate(zip(tl, SUBS[code]),1):
                f.write(f"{i}\n{ts(t0)} --> {ts(t1)}\n{txt}\n\n")
        with open(os.path.join(subdir, f"{label}_제목설명.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(f"[{label} 제목]\n{TITLE[code]}\n\n[{label} 설명]\n{DESC[code]}\n")
    print(f"[{edname}] 완성: 영상+썸네일+제목설명태그 + 자막 5개국어(+제목설명)")

write_edition("한글판", "scratch/shorts_v2/turtle_short_KO.mp4", "scratch/shorts_v2/thumb_ko.png", TL_KO)
write_edition("영어판", "scratch/shorts_v2/turtle_short_FINAL.mp4", "scratch/shorts_v2/thumb_en.png", TL_EN)
print("=== 패키지 위치:", os.path.abspath(OUT), "===")
