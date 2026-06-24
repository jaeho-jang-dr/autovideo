import type { Lang } from './content';

// UI 라벨 사전. 콘텐츠(제목/대본)는 DB에서, 인터페이스 문구는 여기서 온다.
export const ui = {
  ko: {
    nav_home: '홈',
    nav_lessons: '레슨',
    tagline: '의사의 메스로 세상을 해부하고, 만화가의 상상력으로 꿰매다.',
    stat_episodes: '에피소드',
    stat_published: '발행',
    stat_categories: '카테고리',
    explore: '레슨 둘러보기',
    all_lessons: '전체 레슨',
    lens: '의학 렌즈',
    watch: '영상 보기',
    coming_soon: '영상 준비 중',
    coming_soon_desc: '이 레슨의 영상은 곧 공개됩니다.',
    script_title: '한 · 영 대조 학습',
    script_desc: '같은 장면을 한국어와 영어로 나란히 읽으며 학습하세요.',
    col_kr: '한국어',
    col_en: 'English',
    no_script: '대본이 아직 준비되지 않았습니다.',
    runtime: '러닝타임',
    back: '목록으로',
    lessons_in: '레슨',
    published_badge: '발행됨',
    upcoming_badge: '예정',
    footer: '교육은 즐거워야 합니다.',
    nav_groove: '소리한글',
    groove_title: '소리한글 (Sori Hangeul)',
    groove_sub: '자모를 두드려 한글을 만들고, AI 코치와 발음을 맞춰보세요',
    groove_mic: '발음 코치 🎤',
    groove_play: '테마송 재생',
  },
  en: {
    nav_home: 'Home',
    nav_lessons: 'Lessons',
    tagline: "Dissecting the world with a doctor's scalpel, suturing it with a cartoonist's imagination.",
    stat_episodes: 'Episodes',
    stat_published: 'Published',
    stat_categories: 'Categories',
    explore: 'Explore lessons',
    all_lessons: 'All lessons',
    lens: 'Medical lens',
    watch: 'Watch',
    coming_soon: 'Coming soon',
    coming_soon_desc: 'The video for this lesson will be available soon.',
    script_title: 'KR · EN Side-by-Side',
    script_desc: 'Study the same scene in Korean and English, side by side.',
    col_kr: '한국어',
    col_en: 'English',
    no_script: 'The script is not ready yet.',
    runtime: 'Runtime',
    back: 'Back to list',
    lessons_in: 'lessons',
    published_badge: 'Published',
    upcoming_badge: 'Upcoming',
    footer: 'Learning should be a joy.',
    nav_groove: 'Sori Hangeul',
    groove_title: 'Sori Hangeul (소리한글)',
    groove_sub: 'Tap the jamo, build Hangeul, and match your pronunciation with the AI coach',
    groove_mic: 'Pronunciation Coach 🎤',
    groove_play: 'Play theme',
  },
} as const;

export type UI = (typeof ui)['ko'];

export function t(lang: Lang): UI {
  return ui[lang];
}

export function fmtRuntime(sec: number | null | undefined, lang: Lang): string {
  if (!sec || sec <= 0) return '—';
  const m = Math.floor(sec / 60);
  const s = sec % 60;
  if (lang === 'en') return m > 0 ? `${m}m ${s}s` : `${s}s`;
  return m > 0 ? `${m}분 ${s}초` : `${s}초`;
}
