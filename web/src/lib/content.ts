// content.db -> export_web.py 가 만든 단일 데이터 파일을 읽어 타입과 헬퍼를 제공한다.
import raw from '../data/content.json';

export type Lang = 'ko' | 'en';
export const LOCALES: Lang[] = ['ko', 'en'];

export interface Scene {
  seq: number;
  script_kr: string | null;
  script_en: string | null;
  duration_sec: number | null;
}

export interface Episode {
  code: string;
  category: string;
  title_kr: string;
  title_en: string;
  hook_kr: string | null;
  logline_kr: string | null;
  status: string;
  priority: number;
  runtime_sec: number | null;
  youtube_kr: string | null;
  youtube_en: string | null;
  publish_date: string | null;
  scenes: Scene[];
}

export interface Category {
  code: string;
  name_kr: string;
  name_en: string;
  medical_lens: string | null;
  priority: number;
  count: number;
}

export interface Counts {
  episodes: number;
  published: number;
  categories: number;
}

const data = raw as unknown as {
  channel: Record<string, string>;
  categories: Category[];
  episodes: Episode[];
  counts: Counts;
};

export const channel = data.channel;
export const categories = data.categories;
export const episodes = data.episodes;
export const counts = data.counts;

export function getCategory(code: string): Category | undefined {
  return categories.find((c) => c.code === code);
}

export function getEpisode(code: string): Episode | undefined {
  return episodes.find((e) => e.code === code);
}

export function episodesByCategory(code: string): Episode[] {
  return episodes.filter((e) => e.category === code);
}

// --- 언어별 표기 헬퍼 ---
export function epTitle(e: Episode, lang: Lang): string {
  return lang === 'en' ? e.title_en : e.title_kr;
}

export function catName(c: Category, lang: Lang): string {
  return lang === 'en' ? c.name_en : c.name_kr;
}

export function epYoutube(e: Episode, lang: Lang): string | null {
  return lang === 'en' ? e.youtube_en : e.youtube_kr;
}

// --- prefixDefaultLocale:false 기준 URL 빌더 (ko는 접두사 없음) ---
export function homeUrl(lang: Lang): string {
  return lang === 'en' ? '/en/' : '/';
}
export function categoryUrl(code: string, lang: Lang): string {
  return lang === 'en' ? `/en/category/${code}/` : `/category/${code}/`;
}
export function lessonUrl(code: string, lang: Lang): string {
  return lang === 'en' ? `/en/lesson/${code}/` : `/lesson/${code}/`;
}

// 유튜브 임베드 ID 추출: 순수 ID, 일반 URL, 단축/embed/shorts 모두 허용.
export function youtubeId(rawValue: string | null | undefined): string | null {
  if (!rawValue) return null;
  const s = String(rawValue).trim();
  if (!s) return null;
  if (/^[\w-]{11}$/.test(s)) return s;
  const m = s.match(/(?:v=|\/embed\/|youtu\.be\/|\/shorts\/)([\w-]{11})/);
  return m ? m[1] : null;
}
