import os
import shutil
import sys
from gradio_client import Client

# Target path
target_dir = r"d:\Entertainments\DevEnvironment\autovideo\assets\audio"
target_path = os.path.join(target_dir, "kpop_song_1.mp3")

# Ensure directory exists
os.makedirs(target_dir, exist_ok=True)

print("Connecting to Hugging Face MusicGen Space...")
try:
    client = Client("facebook/MusicGen")
except Exception as e:
    print(f"Error connecting: {e}")
    sys.exit(1)

prompt = "90s K-Pop dance pop, retro synthwave, energetic beats, catchy hook, bright 808 bass, upbeat tempo 120bpm, educational fun, crisp production"

print(f"Submitting prompt: '{prompt}'...")
try:
    # Pass a valid audio file path instead of None
    dummy_melody = r"d:\Entertainments\DevEnvironment\autovideo\assets\intro_audio.wav"
    result = client.predict(
        texts=prompt,
        melodies=dummy_melody,
        api_name="/predict_batched"
    )
    print("Success!")
    print(f"Result file path: {result}")
    
    # Copy to target location
    if result and os.path.exists(result):
        # Even if it's a WAV, we can rename it to kpop_song_1.mp3 or save as kpop_song_1.wav and update the JS.
        # Let's save it as kpop_song_1.mp3 (most browsers will play WAV even with .mp3 extension, but let's check extension)
        ext = os.path.splitext(result)[1].lower()
        final_filename = f"kpop_song_1{ext}"
        final_dest = os.path.join(target_dir, final_filename)
        
        shutil.copy(result, final_dest)
        print(f"Copied audio file to: {final_dest}")
        
        # Write a status file for JS to read
        status_file = os.path.join(target_dir, "song_status.json")
        with open(status_file, "w", encoding="utf-8") as f:
            f.write(f'{{"status": "loaded", "filename": "{final_filename}"}}')
            
    else:
        print("Error: Generated file does not exist.")
        sys.exit(1)
        
except Exception as e:
    print(f"Error during generation: {e}")
    sys.exit(1)
