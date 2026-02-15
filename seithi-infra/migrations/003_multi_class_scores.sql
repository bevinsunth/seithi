-- Migration: Convert from discrete scores to probability distributions
-- This migration updates the articles table to store probability scores for all classes on each axis

BEGIN;

-- Drop old score columns and index
DROP INDEX IF EXISTS seithi.idx_seithi_sort;
ALTER TABLE seithi.articles DROP COLUMN IF EXISTS score_factual;
ALTER TABLE seithi.articles DROP COLUMN IF EXISTS score_emotive;
ALTER TABLE seithi.articles DROP COLUMN IF EXISTS score_density;

-- Add new probability score columns (9 total: 3 per axis)
-- Set defaults to equal distribution (0.333) so they sum to ~1.0
-- Epistemic Axis: Opinion (0) -> Mixed (1) -> Facts (2)
ALTER TABLE seithi.articles ADD COLUMN epistemic_opinion_score REAL DEFAULT 0.333;
ALTER TABLE seithi.articles ADD COLUMN epistemic_mixed_score REAL DEFAULT 0.333;
ALTER TABLE seithi.articles ADD COLUMN epistemic_facts_score REAL DEFAULT 0.334;

-- Emotive Axis: Triggering (0) -> Mixed (1) -> Calm (2)
ALTER TABLE seithi.articles ADD COLUMN emotive_triggering_score REAL DEFAULT 0.333;
ALTER TABLE seithi.articles ADD COLUMN emotive_mixed_score REAL DEFAULT 0.333;
ALTER TABLE seithi.articles ADD COLUMN emotive_calm_score REAL DEFAULT 0.334;

-- Density Axis: Fluff (0) -> Standard (1) -> Deep (2)
ALTER TABLE seithi.articles ADD COLUMN density_fluff_score REAL DEFAULT 0.333;
ALTER TABLE seithi.articles ADD COLUMN density_standard_score REAL DEFAULT 0.333;
ALTER TABLE seithi.articles ADD COLUMN density_deep_score REAL DEFAULT 0.334;

-- Update any existing rows to have valid default values (equal distribution)
UPDATE seithi.articles SET
    epistemic_opinion_score = 0.333,
    epistemic_mixed_score = 0.333,
    epistemic_facts_score = 0.334,
    emotive_triggering_score = 0.333,
    emotive_mixed_score = 0.333,
    emotive_calm_score = 0.334,
    density_fluff_score = 0.333,
    density_standard_score = 0.333,
    density_deep_score = 0.334;

-- Add constraints to ensure scores are valid probabilities (0-1)
ALTER TABLE seithi.articles ADD CONSTRAINT epistemic_opinion_valid CHECK (epistemic_opinion_score >= 0 AND epistemic_opinion_score <= 1);
ALTER TABLE seithi.articles ADD CONSTRAINT epistemic_mixed_valid CHECK (epistemic_mixed_score >= 0 AND epistemic_mixed_score <= 1);
ALTER TABLE seithi.articles ADD CONSTRAINT epistemic_facts_valid CHECK (epistemic_facts_score >= 0 AND epistemic_facts_score <= 1);

ALTER TABLE seithi.articles ADD CONSTRAINT emotive_triggering_valid CHECK (emotive_triggering_score >= 0 AND emotive_triggering_score <= 1);
ALTER TABLE seithi.articles ADD CONSTRAINT emotive_mixed_valid CHECK (emotive_mixed_score >= 0 AND emotive_mixed_score <= 1);
ALTER TABLE seithi.articles ADD CONSTRAINT emotive_calm_valid CHECK (emotive_calm_score >= 0 AND emotive_calm_score <= 1);

ALTER TABLE seithi.articles ADD CONSTRAINT density_fluff_valid CHECK (density_fluff_score >= 0 AND density_fluff_score <= 1);
ALTER TABLE seithi.articles ADD CONSTRAINT density_standard_valid CHECK (density_standard_score >= 0 AND density_standard_score <= 1);
ALTER TABLE seithi.articles ADD CONSTRAINT density_deep_valid CHECK (density_deep_score >= 0 AND density_deep_score <= 1);

-- Add constraints to ensure each axis sums to approximately 1.0 (allowing for floating point precision)
ALTER TABLE seithi.articles ADD CONSTRAINT epistemic_sum_valid 
    CHECK (ABS((epistemic_opinion_score + epistemic_mixed_score + epistemic_facts_score) - 1.0) < 0.01);

ALTER TABLE seithi.articles ADD CONSTRAINT emotive_sum_valid 
    CHECK (ABS((emotive_triggering_score + emotive_mixed_score + emotive_calm_score) - 1.0) < 0.01);

ALTER TABLE seithi.articles ADD CONSTRAINT density_sum_valid 
    CHECK (ABS((density_fluff_score + density_standard_score + density_deep_score) - 1.0) < 0.01);

-- Create new index optimized for "Seithi Sort" (High Depth + High Calm)
-- Now using probability scores instead of discrete values
CREATE INDEX idx_seithi_sort ON seithi.articles (
    density_deep_score DESC,
    emotive_calm_score DESC,
    published_at DESC
);

-- Create additional indexes for common filtering patterns
CREATE INDEX idx_epistemic_facts ON seithi.articles (epistemic_facts_score DESC);
CREATE INDEX idx_emotive_calm ON seithi.articles (emotive_calm_score DESC);
CREATE INDEX idx_density_deep ON seithi.articles (density_deep_score DESC);

COMMIT;

