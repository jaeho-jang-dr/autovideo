# -*- coding: utf-8 -*-
"""운동손상 쇼츠 업로드 패키지 생성 (거북목과 동일 구조)."""
import os, shutil
os.chdir(r"D:\Entertainments\DevEnvironment\autovideo")
OUT = "shorts_package/workout_injury"
LANGS = [("ko","한국어"),("en","영어"),("ja","일본어"),("zh","중국어(중국)"),("es","스페인어")]
MAIN = "https://youtu.be/qytcAZOiEsQ"

def ts(t):
    h=int(t//3600); m=int((t%3600)//60); s=t%60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".",",")

TL_EN=[(0,5.0),(5.0,9.0),(9.0,13.5),(13.5,17.5),(17.5,22.5)]
TL_KO=[(0,5.6),(5.6,10.8),(10.8,15.6),(15.6,20.2),(20.2,26.0)]

SUBS = {
 "ko":["헬스 부상의 69%는 무리한 고중량 욕심 때문이에요.","가장 많이 다치는 어깨, 충돌증후군을 조심하세요.","데드리프트에 허리가 말리면 요추 디스크가 눌려요.","무릎이 안으로 모이면 반월상 연골이 찢어져요.","다쳤다면 RICE 응급처치와 휴식을, 회복이 곧 성장이에요."],
 "en":["Nearly 69% of gym injuries come from ego lifting too heavy.","The shoulder gets hurt the most - watch for impingement.","Rounding your back on deadlifts crushes your lumbar discs.","Knees caving inward tear the meniscus in your knee.","Injured? Use RICE and rest - recovery is where you grow."],
 "ja":["ジムの怪我の69%は無理な高重量欲が原因です。","最も多く傷めるのは肩、インピンジメントに注意。","デッドリフトで腰が丸まると腰椎の椎間板が潰れます。","膝が内に入ると半月板が損傷します。","怪我したらRICE応急処置と休息を、回復こそ成長です。"],
 "zh":["近69%的健身伤源于逞强举过重的重量。","最常受伤的是肩膀，当心肩峰撞击。","硬拉时含腰会压垮腰椎间盘。","膝盖内扣会撕裂半月板。","受伤了就用RICE急救并休息，恢复才是成长。"],
 "es":["Casi el 69% de las lesiones vienen de levantar demasiado por ego.","El hombro es el más lesionado - cuidado con el pinzamiento.","Redondear la espalda en peso muerto aplasta los discos lumbares.","Si las rodillas se meten hacia dentro, se rompe el menisco.","¿Lesionado? Usa RICE y descansa - la recuperación es crecimiento."],
}
TITLE = {
 "ko":"헬스 부상 68.9%는 이것 때문! 💪 부상 없이 운동하는 법 #Shorts",
 "en":"69% of gym injuries come from THIS 💪 Lift smarter #Shorts",
 "ja":"ジムの怪我69%はコレが原因！💪 怪我しない筋トレ #Shorts",
 "zh":"69%的健身伤都因为这个！💪 无伤训练法 #Shorts",
 "es":"¡El 69% de las lesiones vienen de ESTO! 💪 Entrena mejor #Shorts",
}
DESC = {
 "ko":f"웨이트 부상의 무려 69%는 '무리한 고중량 욕심'에서 시작됩니다. 어깨·허리·무릎 부상과 올바른 응급처치(RICE)까지, 부상 없이 운동하는 법을 알려드려요. 💪\n\n📌 자세한 내용은 본편: {MAIN}\n\n※ 본 영상은 생성형 AI(Google Veo/Flow)로 제작·연출되었습니다.\n※ 교육 목적이며 통증이 지속되면 전문의와 상담하세요.\n\n#운동손상 #웨이트부상 #헬스 #부상방지 #RICE #Shorts",
 "en":f"A shocking 69% of weightlifting injuries come from ego lifting. Shoulders, back, knees, and proper RICE first aid - train injury-free. 💪\n\n📌 Full video: {MAIN}\n\n※ Created and directed with generative AI (Google Veo/Flow).\n※ Educational only - see a specialist if pain persists.\n\n#gyminjury #weightlifting #fitness #injuryprevention #Shorts",
 "ja":f"ウエイトの怪我の69%は無理な高重量欲から。肩・腰・膝の怪我とRICE応急処置まで。💪\n\n📌 本編: {MAIN}\n\n※ 生成AI(Google Veo/Flow)で制作。\n※ 教育目的、痛みが続く場合は専門医へ。\n\n#筋トレ #ジム #怪我予防 #Shorts",
 "zh":f"高达69%的举重伤源于逞强举重。肩、腰、膝伤与RICE急救。💪\n\n📌 完整视频: {MAIN}\n\n※ 由生成式AI(Google Veo/Flow)制作。\n※ 仅供教育，疼痛持续请就医。\n\n#健身受伤 #力量训练 #预防受伤 #Shorts",
 "es":f"El 69% de las lesiones con pesas vienen del ego. Hombro, espalda, rodilla y primeros auxilios RICE. 💪\n\n📌 Video completo: {MAIN}\n\n※ Creado con IA generativa (Google Veo/Flow).\n※ Solo educativo, consulta a un especialista si el dolor persiste.\n\n#lesiones #pesas #fitness #Shorts",
}
TAGS = "운동 손상, 웨이트 부상, 헬스, 부상 방지, 어깨충돌증후군, 힙힌지, 데드리프트, 스쿼트, 반월상연골, RICE, 근력 운동, 재활, 스포츠 의학, 부상 예방, 통증 관리, 물리치료, 스트레칭, 건강, gym injury, workout injury, weightlifting, injury prevention, shoulder impingement, hip hinge, meniscus, fitness, shorts, 쇼츠, 헬스쇼츠, drjay"

def write_edition(edname, video_src, thumb_src, tl):
    d = os.path.join(OUT, edname); os.makedirs(d, exist_ok=True)
    shutil.copy(video_src, os.path.join(d, f"운동손상쇼츠_{edname}.mp4"))
    shutil.copy(thumb_src, os.path.join(d, "썸네일.png"))
    vlang = "ko" if "한글" in edname else "en"
    with open(os.path.join(d, "0_영상_제목설명태그.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"[제목]\n{TITLE[vlang]}\n\n[설명]\n{DESC[vlang]}\n\n[태그]\n{TAGS}\n\n[동영상 언어] {vlang}  [카테고리] 교육  [AI 변경콘텐츠] 예  [아동용] 아니요\n[본편 연결] {MAIN}\n")
    subdir = os.path.join(d, "자막"); os.makedirs(subdir, exist_ok=True)
    for code, label in LANGS:
        with open(os.path.join(subdir, f"{label}.srt"), "w", encoding="utf-8", newline="\n") as f:
            for i,((t0,t1),txt) in enumerate(zip(tl, SUBS[code]),1):
                f.write(f"{i}\n{ts(t0)} --> {ts(t1)}\n{txt}\n\n")
        with open(os.path.join(subdir, f"{label}_제목설명.txt"), "w", encoding="utf-8", newline="\n") as f:
            f.write(f"[{label} 제목]\n{TITLE[code]}\n\n[{label} 설명]\n{DESC[code]}\n")
    print(f"[{edname}] 완성")

write_edition("한글판", "scratch/shorts_v2/workout_short_KO.mp4", "scratch/shorts_v2/wi_thumb_ko.png", TL_KO)
write_edition("영어판", "scratch/shorts_v2/workout_short_EN.mp4", "scratch/shorts_v2/wi_thumb_en.png", TL_EN)
print("=== 패키지:", os.path.abspath(OUT), "===")
