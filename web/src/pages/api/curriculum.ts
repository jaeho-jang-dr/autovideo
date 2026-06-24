import type { APIRoute } from 'astro';
import fallback from '../../data/curriculum_fallback.json';

// /api/curriculum — 한글 36주 커리큘럼 데이터 제공 엔드포인트.
//
// 동작 순서:
//   1) PUBLIC_SUPABASE_URL/ANON_KEY 가 실제로 설정돼 있으면 Supabase 의
//      hangeul_curriculum 에서 라이브 데이터를 읽는다.
//   2) 자격증명이 없거나(=정적 빌드 기본) 조회가 실패하면 빌드 시점에 함께 생성된
//      정적 덤프(web/src/data/curriculum_fallback.json)로 폴백한다.
//      (이 덤프는 scripts/seed_curriculum.py 가 SQLite/Supabase 시드와 동시에 만든다.)
//
// 정적 빌드(어댑터 없음)에서도 안전하도록 prerender=false 를 쓰지 않는다 → 빌드 시
// 한 번 실행되어 정적 응답으로 떨어진다. 네트워크 행을 막기 위해 자격증명이 없으면
// 곧바로 폴백을 사용한다.

const FIELDS = [
  'level', 'week', 'title_ko', 'title_en',
  'concept_ko', 'concept_en', 'practice_ko', 'practice_en',
  'application_ko', 'application_en', 'target_letters',
] as const;

function isRealCreds(url: string | undefined, key: string | undefined): boolean {
  return Boolean(
    url && key &&
    url.startsWith('https://') &&
    !url.includes('placeholder')
  );
}

function group(weeks: any[]) {
  const byLevel: Record<string, any[]> = { beginner: [], intermediate: [], advanced: [] };
  for (const w of weeks) {
    if (byLevel[w.level]) byLevel[w.level].push(w);
  }
  for (const lv of Object.keys(byLevel)) {
    byLevel[lv].sort((a, b) => a.week - b.week);
  }
  return byLevel;
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
        .from('hangeul_curriculum')
        .select(FIELDS.join(','))
        .order('level', { ascending: true })
        .order('week', { ascending: true });
      if (!error && data && data.length > 0) {
        return json({ source: 'supabase', count: data.length, levels: group(data as any[]), weeks: data });
      }
    } catch (err) {
      // 폴백으로 진행
      console.warn('[api/curriculum] Supabase fetch failed, using static fallback:', (err as Error)?.message);
    }
  }

  // 2) 정적 JSON 폴백
  const weeks = (fallback as any).weeks ?? [];
  return json({
    source: 'static',
    count: weeks.length,
    levels: group(weeks),
    weeks,
    rewards: (fallback as any).rewards,
  });
};

function json(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Cache-Control': 'public, max-age=300',
    },
  });
}
