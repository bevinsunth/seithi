import feedparser
import newspaper
from newspaper import Article
from datetime import datetime
import time
import requests
from urllib.parse import urlparse

class Ingestor:
    def __init__(self):
        """Initialize the ingestor."""
        # Use a proper User-Agent to avoid 403s
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    def fetch_feed(self, rss_url):
        """
        Fetches and parses an RSS feed.
        Returns a list of entry objects.
        """
        print(f"Fetching RSS: {rss_url}")
        try:
            feed = feedparser.parse(rss_url)
            if feed.bozo:
                print(f"Warning: Feed {rss_url} has malformed XML, but trying anyway.")
            return feed.entries
        except Exception as e:
            print(f"Error fetching feed {rss_url}: {e}")
            return []

    def process_article(self, url):
        """
        Downloads and parses a single article using newspaper3k.
        Returns an object with title, text, summary, authors, etc.
        """
        print(f"Parsing article: {url}")
        
        try:
            # Newspaper3k setup
            article = Article(url)
            # Some sites block default newspaper user-agent, so we download manually if needed
            # But Article.download() is usually robust. Let's try standard way first.
            article.download()
            article.parse()
            
            # Optional: NLP for keyword extraction / summary if we want it later
            # article.nlp() 

            return {
                "title": article.title,
                "text": article.text,
                "authors": article.authors,
                "publish_date": article.publish_date,
                "top_image": article.top_image,
                "domain": urlparse(url).netloc
            }
        except Exception as e:
            print(f"Failed to parse {url}: {e}")
            return None

if __name__ == "__main__":
    # Quick sanity check
    ingestor = Ingestor()
    entries = ingestor.fetch_feed("http://feeds.bbci.co.uk/news/rss.xml")
    if entries:
        print(f"Found {len(entries)} entries. Processing first one...")
        data = ingestor.process_article(entries[0].link)
        if data:
            print(f"Title: {data['title']}")
            print(f"Text length: {len(data['text'])}")
