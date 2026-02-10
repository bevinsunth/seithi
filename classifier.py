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
    - Embedding dimension: 384
    - Classification method: Zero-shot semantic similarity
    - Categories: ragebait, nuanced
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


def classify_article(title: str, text: str) -> Tuple[str, float, Dict[str, float]]:
    """
    Classify a news article as 'ragebait' or 'nuanced' using semantic similarity.
    
    The classifier combines the article title and content, generates embeddings,
    and compares them to predefined category descriptions using cosine similarity.
    The category with the highest similarity score is selected.
    
    Args:
        title (str): The article title/headline
        text (str): The article content (summary or full text)
    
    Returns:
        Tuple containing:
            - classification (str): 'ragebait' or 'nuanced'
            - confidence (float): Confidence score 0.0-1.0 (normalized similarity)
            - scores (dict): Raw similarity scores for both categories
                {'ragebait': float, 'nuanced': float}
    
    Example:
        >>> classification, confidence, scores = classify_article(
        ...     "SHOCKING: You Won't Believe This!",
        ...     "This will make you so angry..."
        ... )
        >>> classification
        'ragebait'
        >>> confidence > 0.7
        True
    """
    try:
        # Combine title and text for classification
        combined_text = f"{title}. {text}"
        
        # Limit text length to avoid memory issues (first 1000 chars should be sufficient)
        if len(combined_text) > 1000:
            combined_text = combined_text[:1000]
        
        logger.info(f"Classifying article: {title[:60]}...")
        
        # Load model
        model = get_model()
        
        # Generate embeddings
        article_embedding = model.encode(combined_text)
        category_embeddings = {
            category: model.encode(description)
            for category, description in CATEGORY_DESCRIPTIONS.items()
        }
        
        # Calculate similarity scores
        scores = {
            category: float(cosine_similarity(article_embedding, cat_embedding))
            for category, cat_embedding in category_embeddings.items()
        }
        
        # Determine classification (highest similarity)
        classification = max(scores.items(), key=lambda x: x[1])[0]
        
        # Calculate confidence (normalized to 0-1 range)
        # Cosine similarity ranges from -1 to 1, so we normalize it
        raw_confidence = scores[classification]
        confidence = float((raw_confidence + 1) / 2)  # Map [-1, 1] to [0, 1]
        
        logger.info(
            f"Classification: {classification} "
            f"(confidence: {confidence:.2f}, "
            f"ragebait: {scores['ragebait']:.2f}, "
            f"nuanced: {scores['nuanced']:.2f})"
        )
        
        return classification, confidence, scores
        
    except Exception as e:
        logger.error(f"Error classifying article: {str(e)}")
        # Return default classification on error
        return 'nuanced', 0.5, {'ragebait': 0.0, 'nuanced': 0.0}


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
        classification, confidence, scores = classify_article(
            article.get('title', ''),
            article.get('text', '')
        )
        results.append((classification, confidence, scores))
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
