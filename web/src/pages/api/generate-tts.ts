import type { APIRoute } from 'astro';
import fs from 'fs';
import path from 'path';
import { execFile } from 'child_process';
import { promisify } from 'util';

const execFileAsync = promisify(execFile);

export const GET: APIRoute = async () => {
  return new Response(JSON.stringify({ message: "Sori Hangeul TTS API (Static Build Dummy)" }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  });
};

export const POST: APIRoute = async ({ request }) => {
  try {
    const body = await request.json();
    const { text } = body;

    if (!text || typeof text !== 'string') {
      return new Response(JSON.stringify({ error: "Invalid text parameter" }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // 한글 음절 및 낱자 검증 (한 글자 또는 자모 매핑 명칭)
    const isKoreanSyllableOrJamo = /^[가-힣ㄱ-ㅎㅏ-ㅣ•]+$/.test(text) || [
      '기역', '쌍기역', '키읔', '니은', '디귿', '쌍디귿', '티읔', '리을',
      '미음', '비읍', '쌍비읍', '피읔', '시옷', '쌍시옷', '지읒', '쌍지읒',
      '치읓', '이응', '히읗', '아래아'
    ].includes(text);
    
    if (!isKoreanSyllableOrJamo) {
      return new Response(JSON.stringify({ error: "Text must be Korean syllables or jamo names" }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // 저장할 경로 지정 (프로젝트 루트 기준 public/audio/jamo/)
    const publicJamoDir = path.resolve(process.cwd(), 'public', 'audio', 'jamo');
    if (!fs.existsSync(publicJamoDir)) {
      fs.mkdirSync(publicJamoDir, { recursive: true });
    }

    const filename = `${text}.mp3`;
    const filepath = path.join(publicJamoDir, filename);

    // 이미 존재하면 생성 건너뜀 (캐시 유지)
    if (fs.existsSync(filepath) && fs.statSync(filepath).size > 0) {
      return new Response(JSON.stringify({ success: true, text, status: "cached", filename }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // gTTS를 호출하여 mp3 파일 저장
    const pythonScript = "import sys; from gtts import gTTS; tts = gTTS(text=sys.argv[1], lang='ko'); tts.save(sys.argv[2]); print('OK')";
    
    await execFileAsync('python', ['-c', pythonScript, text, filepath]);

    if (fs.existsSync(filepath) && fs.statSync(filepath).size > 0) {
      return new Response(JSON.stringify({ success: true, text, status: "generated", filename }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    } else {
      throw new Error("File was not created or is empty.");
    }
  } catch (err: any) {
    console.error("gTTS generation error:", err);
    return new Response(JSON.stringify({ error: err.message || "Failed to generate TTS file" }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
