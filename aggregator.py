import feedparser
import database
import filters
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime
import time

RSS_FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "http://feeds.bbci.co.uk/news/rss.xml",
    "https://www.reutersagency.com/feed/",
    "https://api.quantamagazine.org/feed/",
    "https://www.theverge.com/rss/index.xml"
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
            
            status, reason = filters.apply_filters(article_data)
            article_data['filter_status'] = status
            article_data['filter_reason'] = reason
            
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
