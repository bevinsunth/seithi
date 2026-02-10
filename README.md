# Seithi

News aggregator with ML-powered content classification.

## Features

- **RSS Feed Aggregation**: Fetches news from multiple trusted sources (NYT, BBC, Reuters, Quanta, The Verge)
- **Full Article Crawling**: Uses newspaper4k to extract full article content
- **Heuristic Filtering**: Removes obvious spam and low-quality content
- **ML Classification**: Uses sentence-transformers (all-MiniLM-L6-v2) to classify articles as:
  - **Nuanced**: Balanced, thoughtful articles with multiple perspectives
  - **Ragebait**: Emotionally manipulative content designed to provoke outrage
- **Semantic Scoring**: Provides confidence scores and similarity metrics for transparency
- **Clean HTML Reports**: Visual dashboard showing classified articles

## Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd seithi
   ```

2. **Set up a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Database Setup**:
   Ensure you have a PostgreSQL server running locally on port 5432.
   
   Start the service:
   ```bash
   brew services start postgresql@17
   ```

   Create the database:
   ```bash
   createdb seithi
   ```

2. **Run the Aggregator**:
   ```bash
   python aggregator.py
   ```
   This will:
   - Fetch news from RSS feeds
   - Crawl full article content
   - Apply heuristic filters
   - Classify articles using ML (ragebait vs nuanced)
   - Store results in PostgreSQL
   - Generate an `index.html` report

3. **View the Report**:
   Open `index.html` in your browser to see the classified news articles.

## Testing the Classifier

You can test the ML classifier standalone:

```bash
python classifier.py
```

This runs test cases to verify the classification is working correctly.

## How Classification Works

The classifier uses **zero-shot semantic similarity**:
1. Combines article title + content into a single text
2. Generates 384-dimensional embeddings using all-MiniLM-L6-v2
3. Compares article embedding to predefined category descriptions
4. Returns classification with confidence score (0-1) and raw similarity scores

Categories are defined based on linguistic and journalistic patterns:
- **Ragebait**: Inflammatory language, exaggeration, divisive framing, sensationalism
- **Nuanced**: Multiple perspectives, measured language, evidence-based, contextual