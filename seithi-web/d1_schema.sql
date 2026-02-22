-- 0000_initial.sql
-- Initial SQLite schema for Seithi Database on Cloudflare D1

CREATE TABLE articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    domain TEXT NOT NULL,
    content TEXT,
    published_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Epistemic Axis: Opinion (0) -> Mixed (1) -> Facts (2)
    epistemic_opinion_score REAL DEFAULT 0.333,
    epistemic_mixed_score REAL DEFAULT 0.333,
    epistemic_facts_score REAL DEFAULT 0.334,

    -- Emotive Axis: Triggering (0) -> Mixed (1) -> Calm (2)
    emotive_triggering_score REAL DEFAULT 0.333,
    emotive_mixed_score REAL DEFAULT 0.333,
    emotive_calm_score REAL DEFAULT 0.334,

    -- Density Axis: Fluff (0) -> Standard (1) -> Deep (2)
    density_fluff_score REAL DEFAULT 0.333,
    density_standard_score REAL DEFAULT 0.333,
    density_deep_score REAL DEFAULT 0.334
);

-- Indexes for fast API sorting and filtering
CREATE INDEX idx_seithi_sort ON articles (
    density_deep_score DESC,
    emotive_calm_score DESC,
    published_at DESC
);

CREATE INDEX idx_epistemic_facts ON articles (epistemic_facts_score DESC);
CREATE INDEX idx_emotive_calm ON articles (emotive_calm_score DESC);
CREATE INDEX idx_density_deep ON articles (density_deep_score DESC);

-- Feedback Log Table
CREATE TABLE feedback_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT NOT NULL,
    axis TEXT NOT NULL, -- 'epistemic', 'emotive', or 'density'
    user_score INTEGER NOT NULL, -- 0, 1, or 2
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(article_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE INDEX idx_feedback_article ON feedback_log (article_id);
