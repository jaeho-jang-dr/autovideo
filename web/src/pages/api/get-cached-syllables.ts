import type { APIRoute } from 'astro';
import fs from 'fs';
import path from 'path';

export const GET: APIRoute = async () => {
  try {
    const publicJamoDir = path.resolve(process.cwd(), 'public', 'audio', 'jamo');
    if (!fs.existsSync(publicJamoDir)) {
      return new Response(JSON.stringify({ success: true, cached: [] }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const files = fs.readdirSync(publicJamoDir);
    // .mp3 파일들의 이름에서 확장자를 뺀 글자 리스트를 추출합니다.
    const cached = files
      .filter(file => file.endsWith('.mp3'))
      .map(file => path.basename(file, '.mp3'));

    return new Response(JSON.stringify({ success: true, cached }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (err: any) {
    console.error("get-cached-syllables error:", err);
    return new Response(JSON.stringify({ error: err.message || "Failed to read cached files" }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
