"""
Web crawler module for fetching full article content from URLs.
Uses newspaper4k library to extract article text from news pages.
"""

from newspaper import Article
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_article_content(url, timeout=10):
    """
    Fetch and extract article content from a URL using newspaper4k.
    
    Args:
        url (str): The article URL to fetch
        timeout (int): Request timeout in seconds (default: 10)
    
    Returns:
        tuple: (content, status, method)
            - content (str): Extracted article text, or empty string on failure
            - status (str): 'success' or 'failed'
            - method (str): 'newspaper' or 'none'
    """
    try:
        logger.info(f"Fetching article: {url}")
        
        # Create Article instance and configure
        article = Article(url)
        article.config.request_timeout = timeout
        article.config.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        
        # Download and parse the article
        article.download()
        article.parse()
        
        # Extract the main text
        content = article.text
        
        if content and len(content.strip()) > 0:
            logger.info(f"Successfully extracted {len(content)} characters from {url}")
            return (content, 'success', 'newspaper')
        else:
            logger.warning(f"No content extracted from {url}")
            return ('', 'failed', 'none')
            
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {str(e)}")
        return ('', 'failed', 'none')
