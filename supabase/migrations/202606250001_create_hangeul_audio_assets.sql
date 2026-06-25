-- Migration: Create hangeul_audio_assets table (2026-06-25)
CREATE TABLE IF NOT EXISTS hangeul_audio_assets (
    id SERIAL PRIMARY KEY,
    text VARCHAR(100) UNIQUE NOT NULL,
    filepath VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
