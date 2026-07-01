import sys
sys.path.append('.')
from tts_manager import save_tts
import os

test_out = "scratch/temp_poc_tts.mp3"
if os.path.exists(test_out):
    os.remove(test_out)
if os.path.exists(test_out + ".txt"):
    os.remove(test_out + ".txt")

text = "안녕하세요! 이쁜 여자 목소리로 말하는 한국어 테스트입니다."
print("Testing save_tts...")
success = save_tts(text, test_out, lang='ko')
print("Success:", success)
if success and os.path.exists(test_out):
    print("TTS generated successfully at:", os.path.abspath(test_out))
