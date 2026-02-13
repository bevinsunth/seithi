import re

urls = [
    "https://www.abc.net.au/news/2026-02-12/interest-rates-rba-governor-michele-bullock-inflation/104928236",
    "https://www.theguardian.com/australia-news/2024/feb/12/labor-reshuffle-fills-cabinet-vacancy",
    "https://www.thehindu.com/news/national/farmers-protest-live-updates-delhi-chalo-march-february-13/article67840134.ece",
    "https://www.bbc.com/news/world-asia-india-68276135",
    "https://www.reuters.com/business/finance/global-markets-view-2024-02-12/",
    "https://www.abc.net.au/news/politics/2024-02-12/some-politics-story"
]

def classify_url(url):
    url = url.lower()
    topic = None
    region = None
    
    # Topic Heuristics
    if '/politics/' in url or 'labor-reshuffle' in url: # simplistic for test
        topic = 'politics'
    elif '/business/' in url or '/finance/' in url or 'interest-rates' in url:
        topic = 'business'
    elif '/sport/' in url:
        topic = 'sport'
    elif '/technology/' in url or '/tech/' in url:
        topic = 'tech'
        
    # Region Heuristics
    if 'australia' in url or '.au/' in url:
        region = 'australia'
    elif 'india' in url or 'time-of-india' in url:
        region = 'india'
    elif '/world/' in url:
        region = 'world'
        
    return topic, region

print(f"{'URL':<80} | {'TOPIC':<10} | {'REGION':<10}")
print("-" * 105)
for url in urls:
    topic, region = classify_url(url)
    print(f"{url:<80} | {str(topic):<10} | {str(region):<10}")
