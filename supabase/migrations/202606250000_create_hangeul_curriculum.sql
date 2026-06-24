-- 202606250000_create_hangeul_curriculum.sql
-- Hangeul 36-week (3 levels x 12 weeks) bilingual curriculum table.
-- Daily 1-hour structure per week: Concept (20m) + Interactive Practice (20m) + Real-life Application (20m).
-- Source plan: scratch/found_curriculum_073ae673-b8ee-4586-b9c2-f4f12e7276a1.md

CREATE TABLE IF NOT EXISTS hangeul_curriculum (
    id SERIAL PRIMARY KEY,
    level VARCHAR(20) NOT NULL,          -- 'beginner' | 'intermediate' | 'advanced'
    week INT NOT NULL,                   -- 1..12 within each level
    title_ko VARCHAR(255) NOT NULL,
    title_en VARCHAR(255) NOT NULL,
    concept_ko TEXT NOT NULL,            -- Step 1: 개념 이해 (20m)
    concept_en TEXT NOT NULL,
    practice_ko TEXT NOT NULL,           -- Step 2: 시청각/놀이 연습 (20m)
    practice_en TEXT NOT NULL,
    application_ko TEXT NOT NULL,        -- Step 3: 실생활 적용 (20m)
    application_en TEXT NOT NULL,
    target_letters VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- One row per (level, week); re-seeding upserts on this pair.
CREATE UNIQUE INDEX IF NOT EXISTS hangeul_curriculum_level_week_uidx
    ON hangeul_curriculum (level, week);

-- Read path for the public website (anon select). Tighten later if needed.
ALTER TABLE hangeul_curriculum ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'public'
          AND tablename = 'hangeul_curriculum'
          AND policyname = 'hangeul_curriculum_read_all'
    ) THEN
        CREATE POLICY hangeul_curriculum_read_all
            ON hangeul_curriculum
            FOR SELECT
            USING (true);
    END IF;
END $$;
