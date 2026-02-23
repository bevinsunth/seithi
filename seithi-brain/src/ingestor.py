import feedparser
import newspaper
from newspaper import Article
from datetime import datetime
from typing import Optional
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

    def _extract_rss_image(self, entry) -> Optional[str]:
        """
        Tries to extract an image URL from the RSS entry metadata.
        Checks (in order): media:thumbnail, media:content, enclosures.
        Returns None if none found.
        """
        if entry is None:
            return None

        # media:thumbnail (common in many feeds)
        media_thumbnails = getattr(entry, 'media_thumbnail', [])
        if media_thumbnails:
            return media_thumbnails[0].get('url')

        # media:content (images embedded as media)
        media_content = getattr(entry, 'media_content', [])
        for media in media_content:
            mime = media.get('type', '')
            if 'image' in mime or not mime:
                url = media.get('url')
                if url:
                    return url

        # RSS enclosures (e.g. podcasts and image-rich feeds)
        enclosures = getattr(entry, 'enclosures', [])
        for enc in enclosures:
            mime = enc.get('type', '')
            if 'image' in mime:
                return enc.get('href') or enc.get('url')

        return None

    def process_article(self, url, rss_entry=None):
        """
        Downloads and parses a single article using newspaper4k.
        Returns a dict with title, text, authors, publish_date, domain, image_url.
        Image priority: RSS metadata → article.top_image → None.
        """
        print(f"Parsing article: {url}")

        try:
            article = Article(url)
            article.download()
            article.parse()

            # Determine best image: RSS feed → article top image → None
            image_url = self._extract_rss_image(rss_entry) or (article.top_image or None)

            return {
                "title": article.title,
                "text": article.text,
                "authors": article.authors,
                "publish_date": article.publish_date,
                "top_image": image_url,
                "image_url": image_url,
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
        data = ingestor.process_article(entries[0].link, entries[0])
        if data:
            print(f"Title: {data['title']}")
            print(f"Image: {data['image_url']}")
            print(f"Text length: {len(data['text'])}")
