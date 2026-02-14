import time
import schedule
from .ingestor import Ingestor
from .decision_wheel import DecisionWheel
from .database import Database
import os

# Configuration
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://www.theguardian.com/world/rss",
    "https://feeds.npr.org/1001/rss.xml"
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
            
            # 4. Save to DB
            full_record = {
                "title": article_data['title'],
                "url": url,
                "domain": article_data['domain'],
                "content": article_data['text'],
                "summary": article_data.get('summary', ''), # TODO: Generate summary if needed
                "published_at": article_data['publish_date'],
                "score_factual": scores['score_factual'],
                "score_emotive": scores['score_emotive'],
                "score_density": scores['score_density']
            }
            
            if db.save_article(full_record):
                print(f"✅ Saved: {article_data['title']} [F:{scores['score_factual']} E:{scores['score_emotive']} D:{scores['score_density']}]")
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
