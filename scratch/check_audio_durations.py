from moviepy import AudioFileClip
a1 = AudioFileClip("scratch/line_craft_assets/tts_1.mp3")
a2 = AudioFileClip("scratch/line_craft_assets/tts_2.mp3")
print("tts_1 duration:", a1.duration)
print("tts_2 duration:", a2.duration)
a1.close()
a2.close()
