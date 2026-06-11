import os
import sys
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, VideoFileClip
import moviepy.video.fx as fx
from PIL import Image
import numpy as np

# Ensure output folders exist
os.makedirs("assets/audio", exist_ok=True)
os.makedirs("assets/videos", exist_ok=True)

# 1. Scripts list (Same as before...)
# ... (No changes here, keeping list from source)


# 1. Scripts list
SCENES = [
    {
        "id": 1,
        "text": "매일 쏟아지는 업무, 밀려오는 고지서, 그리고 미래에 대한 끊임없는 걱정. 우리는 늘 스트레스 속에서 살아갑니다. 보통은 기분 탓이거나 피곤해서 그렇다고 생각하죠. 하지만 이 스트레스가 단순히 기분의 문제를 넘어, 실제로 당신의 머릿속 뇌 크기를 줄이고 있다면 어떨까요?",
        "image": "assets/images/scene_1.png"
    },
    {
        "id": 2,
        "text": "우리가 위협을 느끼면 뇌의 시상하부에서 신호를 보내 HPA 축을 활성화합니다. 이 과정에서 아드레날린과 함께 '코르티솔'이라는 스트레스 호르몬이 온몸으로 분비됩니다.",
        "image": "assets/images/scene_2.png"
    },
    {
        "id": 3,
        "text": "단기적인 스트레스는 위험에서 벗어나도록 돕는 고마운 방어 기제입니다. 하지만 문제는 이 스트레스가 멈추지 않고 만성화될 때 발생합니다.",
        "image": "assets/images/scene_3.png"
    },
    {
        "id": 4,
        "text": "뇌 속에서 스트레스의 공격을 가장 먼저 받는 곳은 기억과 학습을 담당하는 '해마'입니다. 혈액을 타고 뇌로 흘러 들어간 고농도의 코르티솔은 해마의 신경 세포들을 연결하는 시냅스를 파괴하기 시작합니다.",
        "image": "assets/images/scene_4.png"
    },
    {
        "id": 5,
        "text": "새로운 뇌 세포가 태어나는 것마저 방해하죠. 결국 해마의 부피가 물리적으로 줄어들며, 우리는 자꾸만 기억을 깜빡하고 집중하기 어려워집니다.",
        "image": "assets/images/scene_5.png"
    },
    {
        "id": 6,
        "text": "스트레스의 칼날은 이성과 의사결정을 담당하는 '전두엽'도 향합니다. 전두엽의 신경 회로가 줄어들면서 계획을 세우거나 감정을 조절하는 능력이 약해집니다.",
        "image": "assets/images/scene_6.png"
    },
    {
        "id": 7,
        "text": "반면, 공포와 생존 본능을 담당하는 '편도체'는 코르티솔을 먹고 오히려 더 비대해집니다. 이 때문에 아주 작은 자극에도 쉽게 불안해하고 화를 내는 예민한 상태가 되어 버립니다. 뇌가 이성을 잃고 생존 모드로만 작동하는 것이죠.",
        "image": "assets/images/scene_7.png"
    },
    {
        "id": 8,
        "text": "결국 만성 스트레스는 뇌의 물리적인 구조를 바꾸고 크기를 쪼그라뜨립니다. 하지만 절망할 필요는 없습니다. 우리의 뇌는 경험에 따라 변화하는 '신경가소성'을 가지고 있기 때문입니다.",
        "image": "assets/images/scene_8.png"
    },
    {
        "id": 9,
        "text": "규칙적인 운동, 깊은 수면, 그리고 단 10분간의 명상만으로도 뇌는 코르티솔의 공격을 멈추고 스스로 회복을 시작합니다.",
        "image": "assets/images/scene_9.png"
    },
    {
        "id": 10,
        "text": "오늘 하루, 끊임없이 달리기만 했던 당신의 뇌에게 온전한 휴식을 선물해 보는 건 어떨까요?",
        "image": "assets/images/scene_10.png"
    },
    {
        "id": 11,
        "text": "구독과 좋아요를 통해 매주 유익한 과학 이야기를 만나보세요.",
        "image": "assets/images/scene_11.png"
    }
]

# 2. Text wrap helper
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

# 2.1. Ken Burns Zoom Effect Helper for static images
def make_zoom(clip, duration, zoom_ratio=0.03):
    def effect(get_frame, t):
        frame = get_frame(t)
        img = Image.fromarray(frame)
        width, height = img.size
        # Dynamic zoom multiplier over time (starts at 1.0, increases slowly)
        factor = 1.0 + (zoom_ratio * t)
        new_w, new_h = int(width / factor), int(height / factor)
        left = (width - new_w) // 2
        top = (height - new_h) // 2
        right = left + new_w
        bottom = top + new_h
        img_cropped = img.crop((left, top, right, bottom))
        img_resized = img_cropped.resize((width, height), Image.Resampling.LANCZOS)
        return np.array(img_resized)
    return clip.transform(effect)

# 3. Process scenes
clips = []
print("Starting video composition process...")

for idx, scene in enumerate(SCENES):
    audio_path = f"assets/audio/scene_{scene['id']}.mp3"
    
    # Generate TTS if not exists
    if not os.path.exists(audio_path):
        print(f"Generating TTS for Scene {scene['id']}...")
        tts = gTTS(text=scene['text'], lang='ko')
        tts.save(audio_path)
        
    # Read audio duration
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    
    # Check if video clip exists, otherwise fallback to static image
    video_path = f"assets/videos/scene_{scene['id']}.mp4"
    if os.path.exists(video_path):
        print(f"Loading video clip for Scene {scene['id']}...")
        base_clip = VideoFileClip(video_path)
        # Match video duration to TTS audio duration by scaling speed
        speed_factor = base_clip.duration / duration
        base_clip = base_clip.with_effects([fx.MultiplySpeed(speed_factor)]).with_audio(audio_clip)
        img_width, img_height = base_clip.size
    else:
        print(f"Fallback to static image for Scene {scene['id']}...")
        img = Image.open(scene['image'])
        img_width, img_height = img.size
        base_clip = ImageClip(scene['image']).with_duration(duration).with_audio(audio_clip)
        base_clip = make_zoom(base_clip, duration)
    
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
    except Exception:
        # Fallback to default
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
    
    # Apply fade transition for smooth blending when composed
    video_scene = video_scene.with_effects([fx.CrossFadeIn(0.5)])
    
    clips.append(video_scene)
    print(f"Scene {scene['id']} prepared. Duration: {duration:.2f}s")

# 4. Concatenate and write final video
print("Merging all scenes into final video...")
final_video = concatenate_videoclips(clips, method="compose")
final_video.write_videofile(
    "output.mp4",
    fps=24,
    codec="libx264",
    audio_codec="aac"
)
print("SUCCESS: output.mp4 has been rendered successfully!")
