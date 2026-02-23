-- 0001_axes_simplification.sql
-- Simplified 3-axis scoring schema for Seithi on Cloudflare D1

CREATE TABLE articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    domain TEXT NOT NULL,
    content TEXT,
    image_url TEXT,
    published_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Objectivity Axis: 0.0 (Opinionated) → 1.0 (Factual)
    objectivity_score REAL DEFAULT 0.5,

    -- Calm Axis: 0.0 (Triggering / Rage-bait) → 1.0 (Calm)
    calm_score REAL DEFAULT 0.5,

    -- Depth Axis: 0.0 (Fluff) → 1.0 (Deep Dive)
    depth_score REAL DEFAULT 0.5
);

-- Indexes for fast API sorting and filtering
CREATE INDEX idx_seithi_sort ON articles (
    depth_score DESC,
    calm_score DESC,
    published_at DESC
);

CREATE INDEX idx_objectivity ON articles (objectivity_score DESC);
CREATE INDEX idx_calm ON articles (calm_score DESC);
CREATE INDEX idx_depth ON articles (depth_score DESC);

-- Feedback Log Table
CREATE TABLE feedback_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT NOT NULL,
    axis TEXT NOT NULL, -- 'objectivity', 'calm', or 'depth'
    user_score REAL NOT NULL, -- 0.0 – 1.0
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(article_id) REFERENCES articles(id) ON DELETE CASCADE
);

CREATE INDEX idx_feedback_article ON feedback_log (article_id);
