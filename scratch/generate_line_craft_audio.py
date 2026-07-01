import os
from gtts import gTTS
from moviepy import AudioFileClip
import moviepy.video.fx as fx

def make_speedup_audio(text, output_path, speed=1.1):
    temp_path = output_path + ".temp.mp3"
    # 1. Generate normal TTS via gTTS
    tts = gTTS(text=text, lang="ko")
    tts.save(temp_path)
    
    # 2. Speed up to 1.1x using MoviePy AudioFileClip
    try:
        clip = AudioFileClip(temp_path)
        # Apply speed change (MultiplySpeed)
        clip_fast = clip.with_effects([fx.MultiplySpeed(speed)])
        clip_fast.write_audiofile(output_path, fps=44100, logger=None)
        clip.close()
        clip_fast.close()
        print(f"[Info] Generated accelerated audio: {output_path}")
    except Exception as e:
        print(f"[Warning] MoviePy speed change failed: {e}. Falling back to normal speed.")
        if os.path.exists(output_path):
            os.remove(output_path)
        shutil.copy2(temp_path, output_path)
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

def main():
    os.makedirs("scratch/line_craft_assets", exist_ok=True)
    
    tts_texts = [
        "미래의 자동차가 칠판 위에 한 땀 한 땀 아름다운 선으로 그려지고 있습니다.",
        "정밀한 기계 부품과 톱니바퀴들이 유기적으로 맞물려 움직이기 시작합니다."
    ]
    
    for i, txt in enumerate(tts_texts):
        out = os.path.abspath(f"scratch/line_craft_assets/tts_{i+1}.mp3")
        make_speedup_audio(txt, out, 1.1)

if __name__ == '__main__':
    import shutil
    main()
