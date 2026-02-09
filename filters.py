import re

TRIGGER_WORDS = ["Destroyed", "Humiliated", "Shocking", "Panic", "You Won't Believe"]

def scream_check(title):
    """Calculate the ratio of UPPERCASE letters to lowercase. If > 30%, discard."""
    uppers = sum(1 for c in title if c.isupper())
    lowers = sum(1 for c in title if c.islower())
    total = uppers + lowers
    if total == 0:
        return False
    ratio = uppers / total
    return ratio > 0.3

def punctuation_spam(title):
    """If the title contains !!, ??, or ?!, discard."""
    return "!!" in title or "??" in title or "?!" in title

def trigger_word_check(title):
    """Immediate penalty for words like Destroyed, Humiliated, Shocking, Panic, You Won't Believe."""
    for word in TRIGGER_WORDS:
        if word.lower() in title.lower():
            return True, word
    return False, None

def length_heuristic(body_text):
    """If the article body word count < 20 words, flag as 'Snippet/Low Depth'."""
    if not body_text:
        return True, 0
    words = re.findall(r'\w+', body_text)
    count = len(words)
    return count < 20, count

def apply_filters(article):
    title = article.get('title', '')
    summary = article.get('summary', '') or ''
    
    if scream_check(title):
        return 'filtered', 'Scream Check (>30% CAPS)'
    
    if punctuation_spam(title):
        return 'filtered', 'Punctuation Spam (!!, ??, ?!)'
    
    has_trigger, word = trigger_word_check(title)
    if has_trigger:
        return 'filtered', f'Trigger Word: {word}'
    
    is_short, count = length_heuristic(summary)
    article['word_count'] = count
    if is_short:
        return 'snippet', 'Snippet/Low Depth (< 300 words)'
    
    return 'clean', None
