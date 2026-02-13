from newspaper import Article
import json

urls = [
    "https://www.abc.net.au/news/2026-02-12/interest-rates-rba-governor-michele-bullock-inflation/104928236",
    "https://www.theguardian.com/australia-news/2024/feb/12/labor-reshuffle-fills-cabinet-vacancy", 
    "https://www.thehindu.com/news/national/farmers-protest-live-updates-delhi-chalo-march-february-13/article67840134.ece",
    "https://www.bbc.com/news/world-asia-india-68276135"
]

for url in urls:
    print(f"\n{'='*80}\nAnalyzing: {url}\n{'='*80}")
    try:
        article = Article(url)
        article.download()
        article.parse()
        try:
            article.nlp()
        except:
            print("NLP failed")
        
        print(f"Title: {article.title}")
        
        print("\n--- TAGS ---")
        print(article.tags)
        
        print("\n--- KEYWORDS (NLP) ---")
        print(article.keywords)
        
        print("\n--- META DATA (Filtered) ---")
        # Filter for interesting keys
        interesting_keys = ['section', 'category', 'tag', 'keywords', 'article:section', 'og:type', 'og:site_name']
        for k, v in article.meta_data.items():
            if any(x in k.lower() for x in interesting_keys):
                print(f"{k}: {v}")
                
    except Exception as e:
        print(f"Error: {e}")
