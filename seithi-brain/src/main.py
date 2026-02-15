import time
import schedule
from .ingestor import Ingestor
from .decision_wheel import DecisionWheel
from .database import Database
from .config import FILTER_ENABLED, FILTER_THRESHOLDS
import os

# Configuration
RSS_FEEDS = [
    "https://www.theguardian.com/world/india/rss",
    "https://www.sbs.com.au/news/feed"
]

def run_ingestion_cycle():
    print(f"--- Starting Ingestion Cycle at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")

    # Initialize components
    ingestor = Ingestor()
    db = Database()

    # Only load the heavy ML model if we have new articles to process
    # But for simplicity in V1, we load it once at startup or inside the loop
    # Let's load it inside the loop for now to be safe, or optimize later
    wheel = DecisionWheel()

    total_new = 0

    for feed_url in RSS_FEEDS:
        entries = ingestor.fetch_feed(feed_url)

        for entry in entries:
            url = entry.link

            # 1. Deduplication
            if db.article_exists(url):
                print(f"Skipping existing: {url}")
                continue

            # 2. Parse Content
            article_data = ingestor.process_article(url)
            if not article_data:
                continue

            # 3. Apply The Decision Wheel (3-Axis Scoring)
            print(f"Scoring: {article_data['title']}")
            scores = wheel.score_article(article_data['title'], article_data['text'])

            # 3.5. Apply Filtering (if enabled)
            if FILTER_ENABLED:
                # Check if article meets all threshold requirements
                passes_filter = True
                filter_reasons = []

                if scores['epistemic_scores'][2] < FILTER_THRESHOLDS['epistemic_facts_min']:
                    passes_filter = False
                    filter_reasons.append(f"Facts score {scores['epistemic_scores'][2]:.2f} < {FILTER_THRESHOLDS['epistemic_facts_min']}")

                if scores['emotive_scores'][2] < FILTER_THRESHOLDS['emotive_calm_min']:
                    passes_filter = False
                    filter_reasons.append(f"Calm score {scores['emotive_scores'][2]:.2f} < {FILTER_THRESHOLDS['emotive_calm_min']}")

                if scores['density_scores'][2] < FILTER_THRESHOLDS['density_deep_min']:
                    passes_filter = False
                    filter_reasons.append(f"Deep score {scores['density_scores'][2]:.2f} < {FILTER_THRESHOLDS['density_deep_min']}")

                if not passes_filter:
                    print(f"🚫 Filtered out: {article_data['title']}")
                    print(f"   Reasons: {', '.join(filter_reasons)}")
                    continue

            # 4. Save to DB
            # Map probability arrays to individual database columns
            full_record = {
                "title": article_data['title'],
                "url": url,
                "domain": article_data['domain'],
                "content": article_data['text'],
                "summary": article_data.get('summary', ''),
                "published_at": article_data['publish_date'],
                # Epistemic scores
                "epistemic_opinion_score": scores['epistemic_scores'][0],
                "epistemic_mixed_score": scores['epistemic_scores'][1],
                "epistemic_facts_score": scores['epistemic_scores'][2],
                # Emotive scores
                "emotive_triggering_score": scores['emotive_scores'][0],
                "emotive_mixed_score": scores['emotive_scores'][1],
                "emotive_calm_score": scores['emotive_scores'][2],
                # Density scores
                "density_fluff_score": scores['density_scores'][0],
                "density_standard_score": scores['density_scores'][1],
                "density_deep_score": scores['density_scores'][2]
            }

            if db.save_article(full_record):
                # Log with probability scores (showing highest confidence class)
                epistemic_label = ["Opinion", "Mixed", "Facts"][scores['epistemic_scores'].index(max(scores['epistemic_scores']))]
                emotive_label = ["Triggering", "Mixed", "Calm"][scores['emotive_scores'].index(max(scores['emotive_scores']))]
                density_label = ["Fluff", "Standard", "Deep"][scores['density_scores'].index(max(scores['density_scores']))]

                print(f"✅ Saved: {article_data['title']}")
                print(f"   Epistemic: {epistemic_label} ({max(scores['epistemic_scores']):.2f})")
                print(f"   Emotive: {emotive_label} ({max(scores['emotive_scores']):.2f})")
                print(f"   Density: {density_label} ({max(scores['density_scores']):.2f})")
                total_new += 1
            else:
                print(f"❌ Failed to save: {article_data['title']}")

    print(f"--- Cycle Complete. New Articles: {total_new} ---")
    db.close()

if __name__ == "__main__":
    # Run once immediately on startup
    run_ingestion_cycle()

    # Then schedule hourly
    schedule.every(1).hours.do(run_ingestion_cycle)

    print("Scheduler active. Waiting for next cycle...")
    while True:
        schedule.run_pending()
        time.sleep(60)
