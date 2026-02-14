
# Project Seithi (செய்தி)

**The Signal-First News Engine**

**Version:** 1.0

**Status:** Ready for Development

## 1. Executive Summary

**Seithi** is a personal intelligence engine designed to filter out "rage bait" and emotional manipulation while promoting high-nuance, deep-dive journalism. Unlike standard aggregators that optimize for engagement, Seithi optimizes for **Cognitive ROI** using a "Human-in-the-Loop" machine learning flywheel.

## 2. Core Philosophy (The 3 Axes)

Seithi scores every article on three distinct dimensions to determine its value:

1. **Epistemic (Truth):** Speculation (0) $\to$ Mixed (1) $\to$ Verified Fact (2).
    
2. **Emotive (Tone):** Triggering/Rage (0) $\to$ Edgy (1) $\to$ Calm/Neutral (2).
    
3. **Density (Depth):** Fluff/Snippet (0) $\to$ Standard (1) $\to$ Deep Dive (2).
    

---

## 3. System Architecture

The system consists of four Dockerized containers:

1. **Store (PostgreSQL):** Relational DB holding articles and user feedback.
    
2. **API (Go):** High-performance backend serving the feed and handling feedback.
    
3. **Client (Svelte):** Reactive frontend for reading and rapid grading.
    
4. **Brain (Python):** Background worker for RSS ingestion, zero-shot scoring, and model retraining.
    

---

## 4. Database Schema (PostgreSQL)

**Database Name:** `seithi_db`

### Table: `articles`

_Stores the content and the current "best guess" scores._

SQL

```
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    domain TEXT NOT NULL,
    content TEXT, -- Scraped via newspaper3k
    summary TEXT,
    published_at TIMESTAMP,
    
    -- Scoring Columns (0, 1, or 2)
    score_factual INT DEFAULT 0,
    score_emotive INT DEFAULT 0,
    score_density INT DEFAULT 0,
    
    -- Metadata
    is_user_corrected BOOLEAN DEFAULT FALSE, -- True if you touched it
    created_at TIMESTAMP DEFAULT NOW()
);

-- Optimized for the "Seithi Sort" (High Depth + High Calm)
CREATE INDEX idx_seithi_sort ON articles (score_density DESC, score_emotive DESC, published_at DESC);
```

### Table: `feedback_log`

_The training dataset. Every row here is a labeled data point._

SQL

```
CREATE TABLE feedback_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id),
    
    -- The specific axis corrected
    axis VARCHAR(20) NOT NULL, -- 'factual', 'emotive', 'density'
    
    -- The Label
    user_score INT NOT NULL, -- The "True" value provided by you
    
    timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## 5. Backend Service (Go)

**Module Name:** `seithi-backend`

**Framework:** `Chi` or `Gin`

### API Endpoints

1. **`GET /api/feed`**
    
    - **Logic:** Returns top 50 articles.
        
    - **Sorting:** Prioritizes `(Density * 2) + (Factual) + (Emotive)`.
        
    - **Response:** JSON list of articles including current scores.
        
2. **`POST /api/feedback`**
    
    - **Payload:** `{ "article_id": "uuid", "axis": "emotive", "value": 0 }`
        
    - **Logic:**
        
        1. Insert row into `feedback_log`.
            
        2. Update `articles` table immediately (Optimistic Update).
            
        3. Mark `articles.is_user_corrected = TRUE`.
            

---

## 6. Frontend Application (Svelte)

**Project Name:** `seithi-web`

**Framework:** SvelteKit

### UI Components

- **The Feed:** A clean, single-column list of cards.
    
- **The Control Bar:** Located at the bottom of every card. Contains 3 toggle groups.
    
    - _Visuals:_ The active score is highlighted. If the AI guessed "Rage (0)", the "Rage" button is lit up.
        
    - _Interaction:_ Clicking a different button (e.g., changing "Rage" to "Calm") triggers the `/api/feedback` endpoint and visually updates the state instantly.
        
- **The "Seithi" Badge:** A small indicator showing how many articles you have corrected today (e.g., "5 corrections submitted").
    

---

## 7. The Intelligence Layer (Python)

**Service Name:** `seithi-brain`

**Libraries:** `newspaper3k`, `feedparser`, `setfit`, `sentence-transformers`, `scikit-learn`.

### Worker A: The Ingestor (Runs Hourly)

1. **Fetch:** Polls RSS feeds.
    
2. **Parse:** Extracts text using `newspaper3k`.
    
3. **Deduplicate:** Checks `url` against `seithi_db`.
    
4. **Predict (Cold Start):**
    
    - If `model_v1` exists: Run inference.
        
    - If no model exists: Use a **Zero-Shot Pipeline** to guess the 3 scores.
        
5. **Save:** Writes new articles to Postgres.
    

### Worker B: The Trainer (Runs Weekly)

1. **Extract:** Pulls all text + labels from `feedback_log`.
    
2. **Train:** Fine-tunes `sentence-transformers/all-MiniLM-L6-v2` using **SetFit**.
    
    - _Why SetFit?_ It works with small data (only need ~50 examples per class).
        
3. **Save:** Exports 3 binary models (`factual_model.pt`, `emotive_model.pt`, `density_model.pt`).
    
4. **Deploy:** The Ingestor automatically loads these new models for the next batch.
