// curriculum_fallback.json -> 타입과 헬퍼 제공.
// scripts/seed_curriculum.py 가 DB 시드와 함께 생성하는 정적 덤프를 빌드 시점에 읽는다.
// (content.ts 가 content.json 을 읽는 패턴과 동일 — 정적 빌드에서 항상 렌더 보장)
import raw from '../data/curriculum_fallback.json';
import type { Lang } from './content';

export type Level = 'beginner' | 'intermediate' | 'advanced';
export const LEVELS: Level[] = ['beginner', 'intermediate', 'advanced'];

export interface CurriculumWeek {
  level: Level;
  week: number;
  title_ko: string;
  title_en: string;
  concept_ko: string;
  concept_en: string;
  practice_ko: string;
  practice_en: string;
  application_ko: string;
  application_en: string;
  target_letters: string;
}

interface RewardText { ko: string; en: string; }

const data = raw as unknown as {
  generated_from: string;
  structure: string;
  levels: Level[];
  level_ko: Record<Level, string>;
  rewards: Record<Level, RewardText>;
  counts: Record<Level, number>;
  weeks: CurriculumWeek[];
};

export const weeks = data.weeks;
export const levelKo = data.level_ko;
export const rewards = data.rewards;
export const counts = data.counts;

export function weeksByLevel(level: Level): CurriculumWeek[] {
  return weeks.filter((w) => w.level === level).sort((a, b) => a.week - b.week);
}

// --- 언어별 표기 헬퍼 ---
export function levelName(level: Level, lang: Lang): string {
  if (lang === 'en') {
    return level.charAt(0).toUpperCase() + level.slice(1);
  }
  return levelKo[level];
}

export function weekTitle(w: CurriculumWeek, lang: Lang): string {
  return lang === 'en' ? w.title_en : w.title_ko;
}
export function weekConcept(w: CurriculumWeek, lang: Lang): string {
  return lang === 'en' ? w.concept_en : w.concept_ko;
}
export function weekPractice(w: CurriculumWeek, lang: Lang): string {
  return lang === 'en' ? w.practice_en : w.practice_ko;
}
export function weekApplication(w: CurriculumWeek, lang: Lang): string {
  return lang === 'en' ? w.application_en : w.application_ko;
}
export function rewardText(level: Level, lang: Lang): string {
  return lang === 'en' ? rewards[level].en : rewards[level].ko;
}
