"""
News Article Classifier Module

This module provides ML-based classification for news articles using the
all-MiniLM-L6-v2 sentence transformer model. It classifies articles as either
"ragebait" (emotionally manipulative, outrage-inducing) or "nuanced" 
(balanced, thoughtful) based on semantic similarity.

Usage:
    from classifier import classify_article
    
    classification, confidence, scores = classify_article(
        title="Breaking News: Major Event",
        text="Full article content here..."
    )
    
    print(f"Classification: {classification}")
    print(f"Confidence: {confidence:.2f}")
    print(f"Ragebait score: {scores['ragebait']:.2f}")
    print(f"Nuanced score: {scores['nuanced']:.2f}")

Model Details:
    - Model: sentence-transformers/all-MiniLM-L6-v2
    - Classification method: Zero-shot semantic similarity
    - Categories: 
        - Style: ragebait, nuanced
        - Topic: politics, tech, business, science, health
        - Region: world, india, australia
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Category definitions for zero-shot classification
CATEGORY_DESCRIPTIONS = {
    'ragebait': """Emotionally manipulative article designed to provoke outrage, 
    anger, or strong emotional reactions. Uses inflammatory language, exaggeration, 
    divisive framing, sensationalism, and clickbait tactics. Often presents one-sided 
    views without nuance or context. May use all-caps, excessive punctuation, or 
    loaded language to trigger emotional responses.""",
    
    'nuanced': """Balanced, thoughtful article that presents multiple perspectives 
    and provides context and evidence. Uses measured, professional language. 
    Acknowledges complexity and avoids sensationalism. Cites sources and data. 
    Aims to inform rather than provoke. Shows journalistic integrity and 
    objectivity."""
}

TOPIC_CATEGORIES = {
    'politics': 'Government, elections, policy, laws, diplomacy, international relations, political parties, politicians, parliament, user, democracy.',
    'tech': 'Technology, software, hardware, AI, artificial intelligence, internet, startups, gadgets, cybersecurity, coding, silicon valley, digital.',
    'business': 'Economy, finance, markets, stock market, inflation, corporate news, companies, trade, jobs, unemployment, banking, investment.',
    'science': 'Scientific discovery, research, space, astronomy, biology, physics, chemistry, environment, climate change, nature, medical research.',
    'health': 'Medicine, wellness, fitness, nutrition, diseases, public health, hospitals, doctors, mental health, psychology, diet.',
    'sport': 'Sports, cricket, football, soccer, tennis, athletics, rugby, afl, nrl, olympics, games, matches, scores.',
    'entertainment': 'Movies, film, cinema, television, tv shows, music, celebrities, hollywood, bollywood, actors, art, culture.'
}

REGION_CATEGORIES = {
    'world': 'Global news, international events, foreign affairs, United Nations, global conflict, cross-border issues.',
    'india': 'India, Indian government, Delhi, Mumbai, Bangalore, Chennai, Kolkata, Indian politics, Bollywood, cricket, Indian economy.',
    'australia': 'Australia, Australian government, Sydney, Melbourne, Brisbane, Australian politics, AFL, rugby, Australian economy, Albanese, Dutton.'
}

# Global model instance (loaded once on first use)
_model = None

def get_model() -> SentenceTransformer:
    """
    Load or retrieve the sentence transformer model.
    
    The model is loaded once and cached for subsequent calls to improve performance.
    
    Returns:
        SentenceTransformer: The all-MiniLM-L6-v2 model instance
    """
    global _model
    if _model is None:
        logger.info("Loading all-MiniLM-L6-v2 model...")
        _model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        logger.info("Model loaded successfully")
    return _model


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First embedding vector
        vec2: Second embedding vector
    
    Returns:
        float: Cosine similarity score between -1 and 1
    """
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def _classify(title: str, text: str, categories: Dict[str, str], log_prefix: str = "Classifying") -> Tuple[str, float, Dict[str, float]]:
    """
    Generic classification function using semantic similarity.
    """
    try:
        # Combine title and text for classification
        combined_text = f"{title}. {text}"
        
        # Limit text length to avoid memory issues
        if len(combined_text) > 1000:
            combined_text = combined_text[:1000]
            
        logger.info(f"{log_prefix}: {title[:60]}...")
        
        # Load model
        model = get_model()
        
        # Generate embeddings
        article_embedding = model.encode(combined_text)
        category_embeddings = {
            category: model.encode(description)
            for category, description in categories.items()
        }
        
        # Calculate similarity scores
        scores = {
            category: float(cosine_similarity(article_embedding, cat_embedding))
            for category, cat_embedding in category_embeddings.items()
        }
        
        # Determine classification (highest similarity)
        classification = max(scores.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence
        raw_confidence = scores[classification]
        confidence = float((raw_confidence + 1) / 2)  # Map [-1, 1] to [0, 1]
        
        logger.info(f"{log_prefix} Result: {classification} (conf: {confidence:.2f})")
        
        return classification, confidence, scores
        
    except Exception as e:
        logger.error(f"Error in {log_prefix}: {str(e)}")
        # Return first category as default on error
        default_cat = list(categories.keys())[0]
        return default_cat, 0.0, {k: 0.0 for k in categories}


def classify_article(title: str, text: str) -> Tuple[str, float, Dict[str, float]]:
    """Classify article style (ragebait vs nuanced)."""
    return _classify(title, text, CATEGORY_DESCRIPTIONS, "Classifying Style")


def classify_topic(title: str, text: str) -> Tuple[str, float, Dict[str, float]]:
    """Classify article topic."""
    return _classify(title, text, TOPIC_CATEGORIES, "Classifying Topic")


def classify_region(title: str, text: str) -> Tuple[str, float, Dict[str, float]]:
    """Classify article region."""
    return _classify(title, text, REGION_CATEGORIES, "Classifying Region")


def map_tags(tags: list, mapping: Dict[str, str]) -> str:
    """Check if any tag matches a mapping."""
    if not tags:
        return None
    
    # Normalize tags
    norm_tags = [str(t).lower() for t in tags]
    
    for tag in norm_tags:
        # Check direct mapping
        if tag in mapping:
            return mapping[tag]
        
        # Check partial match (e.g. "indian politics" -> "india")
        for key, value in mapping.items():
            if key in tag:
                return value
    return None

import re

def check_url_keywords(url: str, mapping: Dict[str, str]) -> str:
    """Check if URL contains keywords using regex for whole words/segments."""
    if not url:
        return None
        
    url = url.lower()
    for key, value in mapping.items():
        # Match matches if key is surrounded by non-alphanumeric chars (buffers, /, -, etc)
        # Escaping key just in case, though keys are simple strings here
        pattern = r'[\b\-_/]' + re.escape(key) + r'[\b\-_/]'
        if re.search(pattern, url) or url.startswith(key + '-') or url.endswith('-' + key):
             return value
             
        # simpler word boundary check
        if re.search(r'\b' + re.escape(key) + r'\b', url):
            return value
            
    return None

# Mappings for Hybrid Classification
TOPIC_MAPPING = {
    'politics': 'politics', 'election': 'politics', 'government': 'politics', 'parliament': 'politics',
    'business': 'business', 'finance': 'business', 'economy': 'business', 'market': 'business',
    'tech': 'tech', 'technology': 'tech', 'science': 'science', 'health': 'health',
    'sport': 'sport', 'cricket': 'sport', 'football': 'sport', 'tennis': 'sport', 'rugby': 'sport', 'afl': 'sport', 'nrl': 'sport', 'olympics': 'sport',
    'entertainment': 'entertainment', 'movie': 'entertainment', 'music': 'entertainment', 'film': 'entertainment', 'tv': 'entertainment', 'television': 'entertainment', 'celebrity': 'entertainment', 'arts': 'entertainment', 'culture': 'entertainment',
    'lifestyle': 'entertainment' # Map lifestyle to entertainment for now
}

REGION_MAPPING = {
    'australia': 'australia', 'sydney': 'australia', 'melbourne': 'australia', 'brisbane': 'australia', 'nsw': 'australia', 'victoria': 'australia', 'queensland': 'australia',
    'india': 'india', 'delhi': 'india', 'mumbai': 'india', 'bangalore': 'india', 'chennai': 'india', 'kolkata': 'india',
    'world': 'world', 'international': 'world', 'global': 'world', 'us': 'world', 'uk': 'world', 'europe': 'world', 'asia': 'world'
}

def classify_hybrid_topic(title: str, text: str, url: str = None, tags: list = None) -> Tuple[str, float, Dict[str, float]]:
    """
    Hybrid topic classification: Tags > URL > ML
    """
    # 1. Try Tags
    topic = map_tags(tags, TOPIC_MAPPING)
    if topic:
        return topic, 1.0, {topic: 1.0}
        
    # 2. Try URL
    topic = check_url_keywords(url, TOPIC_MAPPING)
    if topic:
        return topic, 0.9, {topic: 0.9}
        
    # 3. Fallback to ML
    return classify_topic(title, text)

def classify_hybrid_region(title: str, text: str, url: str = None, tags: list = None) -> Tuple[str, float, Dict[str, float]]:
    """
    Hybrid region classification: Tags > URL > ML
    """
    # 1. Try Tags
    region = map_tags(tags, REGION_MAPPING)
    if region:
        return region, 1.0, {region: 1.0}
        
    # 2. Try URL
    region = check_url_keywords(url, REGION_MAPPING)
    if region:
        return region, 0.9, {region: 0.9}
        
    # 3. Fallback to ML
    return classify_region(title, text)





def batch_classify(articles: list) -> list:
    """
    Classify multiple articles in batch for better performance.
    
    Args:
        articles: List of dicts with 'title' and 'text' keys
        
    Returns:
        List of tuples (classification, confidence, scores) for each article
        
    Example:
        >>> articles = [
        ...     {'title': 'News 1', 'text': 'Content 1'},
        ...     {'title': 'News 2', 'text': 'Content 2'}
        ... ]
        >>> results = batch_classify(articles)
    """
    results = []
    for article in articles:
        style_res = classify_article(article.get('title', ''), article.get('text', ''))
        topic_res = classify_topic(article.get('title', ''), article.get('text', ''))
        region_res = classify_region(article.get('title', ''), article.get('text', ''))
        results.append({
            'style': style_res,
            'topic': topic_res,
            'region': region_res
        })
    return results


if __name__ == "__main__":
    # Test the classifier with sample articles
    print("Testing News Article Classifier\n" + "="*50)
    
    # Test case 1: Obvious ragebait
    test1_title = "SHOCKING: Politicians DESTROYED by This One Simple Trick!"
    test1_text = "You won't believe what happened next. This will make you furious!"
    
    classification, confidence, scores = classify_article(test1_title, test1_text)
    print(f"\nTest 1 (Expected: ragebait)")
    print(f"Title: {test1_title}")
    print(f"Classification: {classification}")
    print(f"Confidence: {confidence:.2f}")
    print(f"Scores: {scores}")
    
    # Test case 2: Nuanced article
    test2_title = "New Study Examines Climate Policy Trade-offs"
    test2_text = """Researchers at MIT have published a comprehensive analysis 
    of various climate policy approaches, weighing the economic costs against 
    environmental benefits. The study presents multiple perspectives from 
    industry stakeholders and environmental groups."""
    
    classification, confidence, scores = classify_article(test2_title, test2_text)
    print(f"\nTest 2 (Expected: nuanced)")
    print(f"Title: {test2_title}")
    print(f"Classification: {classification}")
    print(f"Confidence: {confidence:.2f}")
    print(f"Scores: {scores}")
    print(f"Classification: {classification}")
    print(f"Confidence: {confidence:.2f}")
    
    # Test 3: Topic/Region
    test3_title = "RBA holds interest rates steady as inflation cools in Australia"
    test3_text = "The Reserve Bank of Australia decided to keep the cash rate targets unchanged at 4.35%."
    
    topic, topic_conf, _ = classify_topic(test3_title, test3_text)
    region, region_conf, _ = classify_region(test3_title, test3_text)
    
    print(f"\nTest 3 (Expected: business + australia)")
    print(f"Title: {test3_title}")
    print(f"Topic: {topic} ({topic_conf:.2f})")
    print(f"Region: {region} ({region_conf:.2f})")
