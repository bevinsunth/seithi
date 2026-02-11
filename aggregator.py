import feedparser
import database
import filters
import crawler
import classifier
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime
import time

RSS_FEEDS = [
    "https://www.abc.net.au/news/feed/1948/rss.xml",
    "https://www.theguardian.com/au/rss",
    "https://www.thehindu.com/feeder/default.rss",
    "https://feeds.feedburner.com/ndtvnews-top-stories",
    "https://indianexpress.com/feed/",
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.reutersagency.com/feed/"
]

def fetch_and_process():
    database.init_db()
    
    for url in RSS_FEEDS:
        print(f"Fetching {url}...")
        feed = feedparser.parse(url)
        source = feed.feed.get('title', url)
        
        for entry in feed.entries:
            published = None
            if hasattr(entry, 'published_parsed'):
                published = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            
            article_data = {
                'title': entry.get('title', 'No Title'),
                'link': entry.get('link', ''),
                'summary': entry.get('summary', entry.get('description', '')),
                'published_date': published,
                'source': source
            }
            
            # Fetch full article content
            print(f"  Crawling: {article_data['title'][:60]}...")
            full_content, crawl_status, crawler_method = crawler.fetch_article_content(article_data['link'])
            article_data['full_content'] = full_content
            article_data['crawl_status'] = crawl_status
            article_data['crawler_method'] = crawler_method
            article_data['crawled_at'] = datetime.now() if crawl_status == 'success' else None
            
            # Apply filters using full content if available, otherwise use summary
            content_for_filtering = full_content if full_content else article_data['summary']
            status, reason = filters.apply_filters(article_data, content_for_filtering)
            article_data['filter_status'] = status
            article_data['filter_reason'] = reason
            
            # Apply ML classification
            print(f"  Classifying: {article_data['title'][:60]}...")
            classification, confidence, scores = classifier.classify_article(
                title=article_data['title'],
                text=content_for_filtering
            )
            article_data['ml_classification'] = classification
            article_data['ml_confidence'] = confidence
            article_data['ml_ragebait_score'] = scores.get('ragebait', 0.0)
            article_data['ml_nuanced_score'] = scores.get('nuanced', 0.0)
            
            database.save_article(article_data)

def generate_report():
    clean = database.get_articles('clean')
    filtered = database.get_articles('filtered')
    snippets = database.get_articles('snippet')
    
    # Group snippet with filtered for now, or highlight them
    all_filtered = filtered + snippets
    
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('index.html')
    
    output = template.render(
        clean_articles=clean,
        filtered_articles=all_filtered
    )
    
    with open('index.html', 'w') as f:
        f.write(output)
    print("Report generated: index.html")

if __name__ == "__main__":
    fetch_and_process()
    generate_report()
