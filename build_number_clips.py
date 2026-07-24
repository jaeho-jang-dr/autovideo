# -*- coding: utf-8 -*-
"""119/112 DB클립을 '일·일·구·죠' 처럼 음절 사이 0.1초 띄워 또박또박 재생성(선희).
   음절별 edge-tts(선희) + 0.1초 무음 → ffmpeg concat. 파일명=따옴표 텍스트(숫자), 오디오=한글 발음."""
import os, subprocess, tempfile
os.environ["EDGE_ACTIVE_VOICE"] = "sunhi"
from tts_manager import save_tts

JD = "web/public/audio/jamo"
GAP = 0.10   # 음절 사이 0.1초
TMP = tempfile.mkdtemp(prefix="numclip_")

_TRIM = ("silenceremove=start_periods=1:start_duration=0:start_threshold=-45dB:detection=peak,"
         "areverse,"
         "silenceremove=start_periods=1:start_duration=0:start_threshold=-45dB:detection=peak,"
         "areverse")

def tts(text, name):
    """선희 TTS 후 앞뒤 무음 제거(edge-tts가 붙이는 패딩 제거 → 음절이 붙지 않게)."""
    raw = os.path.join(TMP, name + "_raw.mp3")
    save_tts(text, raw, lang="ko")
    p = os.path.join(TMP, name + ".mp3")
    subprocess.run(["ffmpeg", "-y", "-i", raw, "-af", _TRIM, p],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return p

# 음절/꼬리 조각
il  = tts("일", "il")
gu  = tts("구", "gu")
i2  = tts("이", "i2")
jo  = tts("죠", "jo")
tail119 = tts("친구가 다쳤어요 여기는 이태원이에요", "t119")
tail112 = tts("가방을 잃어버렸어요 도와주세요", "t112")

sil = os.path.join(TMP, "sil.wav")
subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono",
                "-t", str(GAP), sil], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def concat(pieces, outname):
    """조각들(mp3/wav)을 24k mono로 리샘플해 이어붙여 outname(.mp3)로 저장."""
    out = os.path.join(JD, outname + ".mp3")
    if os.path.exists(out):
        os.remove(out)
    inputs, filt = [], ""
    for i, p in enumerate(pieces):
        inputs += ["-i", p]
        filt += f"[{i}:a]aresample=24000,aformat=sample_fmts=fltp:channel_layouts=mono[a{i}];"
    filt += "".join(f"[a{i}]" for i in range(len(pieces))) + f"concat=n={len(pieces)}:v=0:a=1[o]"
    subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex", filt, "-map", "[o]",
                    "-ar", "24000", "-ac", "1", out],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"  {outname}.mp3  <= {len(pieces)}조각")
    return out

# 표준번호(단독): 일·일·구 / 일·일·이
concat([il, sil, il, sil, gu], "119")
concat([il, sil, il, sil, i2], "112")
# 통화문장: 일·일·구·죠 + 문장 / 일·일·이·죠 + 문장
concat([il, sil, il, sil, gu, sil, jo, sil, tail119], "119죠 친구가 다쳤어요 여기는 이태원이에요")
concat([il, sil, il, sil, i2, sil, jo, sil, tail112], "112죠 가방을 잃어버렸어요 도와주세요")
print("완료: 4개 클립 (일·일·구·죠 0.1초 간격, 선희)")
