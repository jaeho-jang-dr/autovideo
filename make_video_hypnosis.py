import os
import sys
from gtts import gTTS
from moviepy import AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, VideoFileClip
import moviepy.video.fx as fx

# Ensure output folders exist
os.makedirs("assets/audio", exist_ok=True)
os.makedirs("assets/videos", exist_ok=True)

# 16-scene configuration
SCENES = [
    {
        "id": 1,
        "text": "천천히 회전하는 회중시계를 바라봅니다. 최면술사의 부드러운 목소리를 따라가다 보면, 어느새 깊은 몰입 상태에 빠지게 됩니다.",
        "image": "assets/images/scene_1.png"
    },
    {
        "id": 2,
        "text": "많은 이들이 최면을 단순한 마술쇼나 타인을 마음대로 조종하는 기이한 눈속임으로 생각하곤 합니다.",
        "image": "assets/images/scene_2.png"
    },
    {
        "id": 3,
        "text": "하지만 과연 이 최면술은 대중의 인식처럼 실제로 우리 뇌와 몸에 효과가 있는 과학적 현상일까요?",
        "image": "assets/images/scene_3.png"
    },
    {
        "id": 4,
        "text": "최면의 기원은 18세기 오스트리아의 의사 프란츠 안톤 메스머의 황당한 주장으로 거슬러 올라갑니다.",
        "image": "assets/images/scene_4.png"
    },
    {
        "id": 5,
        "text": "그는 우주로부터 흐르는 눈에 보이지 않는 힘인 '동물 자기'를 조절해 만병을 고칠 수 있다고 선전했습니다.",
        "image": "assets/images/scene_5.png"
    },
    {
        "id": 6,
        "text": "하지만 그의 화려한 치료실과 신비주의 치료법은 곧 프랑스 왕실의 큰 의심을 사게 되었습니다.",
        "image": "assets/images/scene_6.png"
    },
    {
        "id": 7,
        "text": "이에 따라 프랑스 왕실은 벤자민 프랭클린을 필두로 당대 최고의 과학자들로 구성된 위원회를 소집했습니다.",
        "image": "assets/images/scene_7.png"
    },
    {
        "id": 8,
        "text": "그들은 과학사 최초로 환자의 눈을 가리고 진짜 자석인 척 속이는 '맹검 실험'을 최초로 시도했습니다.",
        "image": "assets/images/scene_8.png"
    },
    {
        "id": 9,
        "text": "실험 결과, 환자가 에너지가 흐른다고 착각했을 때만 몸이 반응했고, 동물 자기는 실체가 없는 사기로 판명났습니다.",
        "image": "assets/images/scene_9.png"
    },
    {
        "id": 10,
        "text": "비록 사기극으로 끝났지만, 이는 인간의 상상력과 기대가 몸에 반응을 일으키는 '플라시보 효과'의 시초가 되었습니다.",
        "image": "assets/images/scene_10.png"
    },
    {
        "id": 11,
        "text": "그 뒤 19세기 의사 제임스 브레이드가 나타나 최면을 마법이나 종교가 아닌 신경 생리학적 관점으로 재정의했습니다.",
        "image": "assets/images/scene_11.png"
    },
    {
        "id": 12,
        "text": "그는 특정 물체에 고도로 주의를 집중하면, 뇌가 일시적인 신경성 수면과 강한 몰입 상태에 빠진다는 사실을 밝혀냈습니다.",
        "image": "assets/images/scene_12.png"
    },
    {
        "id": 13,
        "text": "오늘날 현대 과학은 fMRI 장치를 이용해 최면 상태의 뇌를 들여다봄으로써 그 작동 기전을 완벽히 규명했습니다.",
        "image": "assets/images/scene_13.png"
    },
    {
        "id": 14,
        "text": "놀랍게도 최면 상태에서는 통증 신호를 인지하는 뇌의 전대상피질 부위 활성도가 극적으로 감소합니다.",
        "image": "assets/images/scene_14.png"
    },
    {
        "id": 15,
        "text": "덕분에 현대 의학에서는 약물 마취가 어려운 환자들의 무마취 수술이나 극심한 심리 치료에 최면을 직접 활용하고 있습니다.",
        "image": "assets/images/scene_15.png"
    },
    {
        "id": 16,
        "text": "최면은 초자연적 마법이 아닌, 인간의 상상력과 뇌 과학이 만들어내는 정교하고 강력한 우리 마음의 도구입니다.",
        "image": "assets/images/scene_16.png"
    }
]

# Text wrap helper
def wrap_text(text, max_chars=30):
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        if len(' '.join(current_line + [word])) <= max_chars:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return '\n'.join(lines)

# Pre-flight: every scene MUST have a Veo motion clip.
# Golden Rule P8 forbids substituting a static-image Ken Burns zoom, so we abort
# loudly here instead of silently degrading a missing clip to a still image.
missing = [s["id"] for s in SCENES
           if not os.path.exists(f"assets/videos/scene_{s['id']}.mp4")]
if missing:
    print("=" * 60)
    print("  [중단] 다음 씬의 Veo 비디오 클립이 없습니다:")
    for mid in missing:
        print(f"    - assets/videos/scene_{mid}.mp4")
    print("=" * 60)
    print("  골든룰 P8: 정적 이미지 줌(Ken Burns) 대체는 금지됩니다.")
    print("  먼저 클립을 생성/배치한 뒤(place_clips.py 참고) 다시 실행하세요.")
    sys.exit(1)

clips = []
print("Starting hypnosis video composition process...")

for idx, scene in enumerate(SCENES):
    audio_path = f"assets/audio/scene_{scene['id']}.mp3"
    
    # Always generate fresh TTS to prevent outdated cached script mismatch
    print(f"Generating fresh TTS for Scene {scene['id']}...")
    if os.path.exists(audio_path):
        try:
            os.remove(audio_path)
        except Exception as e:
            print(f"Warning: Could not remove old audio {audio_path}: {e}")
    tts = gTTS(text=scene['text'], lang='ko')
    tts.save(audio_path)
        
    # Read audio duration and speed up the narration by 10% (1.1x speed)
    audio_clip = AudioFileClip(audio_path)
    audio_clip = audio_clip.with_effects([fx.MultiplySpeed(1.1)])
    duration = audio_clip.duration
    
    # Load the Veo motion clip (guaranteed to exist by the pre-flight check above)
    video_path = f"assets/videos/scene_{scene['id']}.mp4"
    print(f"Loading video clip for Scene {scene['id']}...")
    base_clip = VideoFileClip(video_path)
    # Match video duration to TTS audio duration by scaling speed
    speed_factor = base_clip.duration / duration
    base_clip = base_clip.with_effects([fx.MultiplySpeed(speed_factor)]).with_audio(audio_clip)
    img_width, img_height = base_clip.size
    
    # Create wrapped subtitle
    wrapped_text = wrap_text(scene['text'], max_chars=35)
    
    # Subtitle text clip setup
    try:
        txt_clip = TextClip(
            text=wrapped_text,
            font=r'C:\Windows\Fonts\malgun.ttf',
            font_size=24,
            color='white',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(img_width - 100, 200)
        )
    except Exception as e:
        print(f"TextClip Error for Scene {scene['id']}: {e}. Falling back to default font.")
        txt_clip = TextClip(
            text=wrapped_text,
            font_size=24,
            color='white',
            stroke_color='black',
            stroke_width=2,
            method='caption',
            size=(img_width - 100, 200)
        )
        
    # Bottom centered position
    txt_clip = txt_clip.with_position(('center', img_height - 230)).with_duration(duration)
    
    # Combine base clip and subtitle
    video_scene = CompositeVideoClip([base_clip, txt_clip])
    
    # Apply fade transition for smooth blending
    video_scene = video_scene.with_effects([fx.CrossFadeIn(0.5)])
    
    clips.append(video_scene)
    print(f"Scene {scene['id']} prepared. Duration: {duration:.2f}s")

# Concatenate and write final video
print("Merging all scenes into final video...")
final_video = concatenate_videoclips(clips, method="compose")
final_video.write_videofile(
    "hypnosis_science.mp4",
    fps=24,
    codec="libx264",
    audio_codec="aac"
)
print("SUCCESS: hypnosis_science.mp4 has been rendered successfully!")
