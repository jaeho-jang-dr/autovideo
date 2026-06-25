import type { APIRoute } from 'astro';
import fallback from '../../data/character_assets.json';

// /api/character-assets — 캐릭터(졸라맨/지은이/인준이 등) 에셋 데이터를 제공하는 엔드포인트.
//
// 동작 순서:
//   1) PUBLIC_SUPABASE_URL/ANON_KEY 가 실제로 설정돼 있으면 Supabase 의
//      assets 테이블에서 type='character' 데이터를 읽는다.
//   2) 자격증명이 없거나 조회가 실패하면 빌드 시점에 생성된 정적 덤프(character_assets.json)로 폴백한다.

function isRealCreds(url: string | undefined, key: string | undefined): boolean {
  return Boolean(
    url && key &&
    url.startsWith('https://') &&
    !url.includes('placeholder')
  );
}

export const GET: APIRoute = async () => {
  const url = import.meta.env.PUBLIC_SUPABASE_URL;
  const key = import.meta.env.PUBLIC_SUPABASE_ANON_KEY;

  // 1) Supabase 라이브 시도 (자격증명이 실제일 때만)
  if (isRealCreds(url, key)) {
    try {
      const { createClient } = await import('@supabase/supabase-js');
      const supabase = createClient(url!, key!);
      const { data, error } = await supabase
        .from('assets')
        .select('id,name_kr,name_en,type,file_path,flow_prompt')
        .eq('type', 'character')
        .order('id', { ascending: true });
      if (!error && data && data.length > 0) {
        return json({ source: 'supabase', count: data.length, characters: data });
      }
    } catch (err) {
      console.warn('[api/character-assets] Supabase fetch failed, using static fallback:', (err as Error)?.message);
    }
  }

  // 2) 정적 JSON 폴백
  return json({
    source: 'static',
    count: fallback.length,
    characters: fallback,
  });
};

function json(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, max-age=300',
      'Access-Control-Allow-Origin': '*', // Canva App에서 로컬 백엔드를 원활하게 패칭할 수 있도록 CORS 허용
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
    },
  });
}
