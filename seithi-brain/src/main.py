import time
import schedule
from .ingestor import Ingestor
from .decision_wheel import DecisionWheel
from .database import Database
from .config import FILTER_ENABLED, FILTER_THRESHOLDS
import os
import uuid

# Configuration
RSS_FEEDS = [
    "https://www.theguardian.com/world/india/rss",
    "https://www.sbs.com.au/news/feed",
    "https://feeds.bbci.co.uk/news/world/asia/india/rss.xml"
]

def run_ingestion_cycle():
    print(f"--- Starting Ingestion Cycle at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")

    ingestor = Ingestor()
    db = Database()
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

            # 2. Parse content + extract image
            article_data = ingestor.process_article(url, entry)
            if not article_data:
                continue

            # 3. Apply The Decision Wheel (3-Axis Scoring)
            print(f"Scoring: {article_data['title']}")
            scores = wheel.score_article(article_data['title'], article_data['text'])

            # 3.5. Apply Filtering (if enabled)
            if FILTER_ENABLED:
                passes_filter = True
                filter_reasons = []

                if scores['objectivity_score'] < FILTER_THRESHOLDS['objectivity_min']:
                    passes_filter = False
                    filter_reasons.append(f"Objectivity {scores['objectivity_score']:.2f} < {FILTER_THRESHOLDS['objectivity_min']}")

                if scores['calm_score'] < FILTER_THRESHOLDS['calm_min']:
                    passes_filter = False
                    filter_reasons.append(f"Calm {scores['calm_score']:.2f} < {FILTER_THRESHOLDS['calm_min']}")

                if scores['depth_score'] < FILTER_THRESHOLDS['depth_min']:
                    passes_filter = False
                    filter_reasons.append(f"Depth {scores['depth_score']:.2f} < {FILTER_THRESHOLDS['depth_min']}")

                if not passes_filter:
                    print(f"🚫 Filtered out: {article_data['title']}")
                    print(f"   Reasons: {', '.join(filter_reasons)}")
                    continue

            # 4. Save to DB
            full_record = {
                "id": str(uuid.uuid4()),
                "title": article_data['title'],
                "url": url,
                "domain": article_data['domain'],
                "content": article_data['text'],
                "summary": article_data.get('summary', ''),
                "published_at": article_data['publish_date'],
                "image_url": article_data.get('image_url'),
                "objectivity_score": scores['objectivity_score'],
                "calm_score":        scores['calm_score'],
                "depth_score":       scores['depth_score'],
            }

            if db.save_article(full_record):
                print(f"✅ Saved: {article_data['title']}")
                print(f"   Objectivity: {scores['objectivity_score']:.2f}  |  "
                      f"Calm: {scores['calm_score']:.2f}  |  "
                      f"Depth: {scores['depth_score']:.2f}")
                total_new += 1

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
