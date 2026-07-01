import asyncio
import edge_tts
import os

async def generate_narration():
    # Use Emma neural voice for English host and SunHi neural voice for Korean words
    text_en = "Hello! Today we are learning Hangeul. Look at this letter."
    text_ko = "기역! 기역은 혀뿌리가 목구멍을 막는 소리입니다."
    
    # Ensure scratch directory exists
    os.makedirs("scratch", exist_ok=True)
    
    # Generate English part
    communicate_en = edge_tts.Communicate(text_en, "en-US-EmmaMultilingualNeural")
    await communicate_en.save("scratch/test_edge_en.mp3")
    print("English TTS saved to scratch/test_edge_en.mp3")
    
    # Generate Korean part
    communicate_ko = edge_tts.Communicate(text_ko, "ko-KR-SunHiNeural")
    await communicate_ko.save("scratch/test_edge_ko.mp3")
    print("Korean TTS saved to scratch/test_edge_ko.mp3")

if __name__ == "__main__":
    asyncio.run(generate_narration())
