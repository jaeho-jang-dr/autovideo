import os
import shutil
from gtts import gTTS
from moviepy import AudioFileClip
import moviepy.video.fx as fx

output_dir = r"d:\Entertainments\DevEnvironment\autovideo\scratch\vocab_assets\audio"
os.makedirs(output_dir, exist_ok=True)

def make_speedup_audio(text, output_path, speed=1.1):
    temp_path = output_path + ".temp.mp3"
    # Generate normal TTS via gTTS
    tts = gTTS(text=text, lang="ko")
    tts.save(temp_path)
    
    # Speed up to 1.1x using MoviePy AudioFileClip
    try:
        clip = AudioFileClip(temp_path)
        # Apply speed change (MultiplySpeed)
        clip_fast = clip.with_effects([fx.MultiplySpeed(speed)])
        clip_fast.write_audiofile(output_path, fps=44100, logger=None)
        clip.close()
        clip_fast.close()
        print(f"[Info] Generated accelerated audio: {output_path} for '{text}'")
    except Exception as e:
        print(f"[Warning] MoviePy speed change failed: {e}. Falling back to normal speed.")
        if os.path.exists(output_path):
            os.remove(output_path)
        shutil.copy2(temp_path, output_path)
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

def main():
    new_words = {
        "window": "창문",
        "fan": "선풍기",
        "chair": "의자",
        "bottle": "물병",
        "phone": "스마트폰"
    }
    
    for filename, text in new_words.items():
        out = os.path.join(output_dir, f"{filename}.mp3")
        make_speedup_audio(text, out, 1.1)

if __name__ == '__main__':
    main()
