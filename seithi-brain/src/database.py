import psycopg2
from psycopg2.extras import execute_values
from .config import DATABASE_URL
import datetime

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.autocommit = True
        
    def article_exists(self, url):
        """
        Checks if an article URL already exists in the database.
        """
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM seithi.articles WHERE url = %s", (url,))
            return cur.fetchone() is not None

    def save_article(self, article_data):
        """
        Saves a classified article to the database using official Seithi schema.
        Expects article_data to contain probability score arrays.
        """
        query = """
            INSERT INTO seithi.articles (
                title, url, domain, content, summary, published_at,
                epistemic_opinion_score, epistemic_mixed_score, epistemic_facts_score,
                emotive_triggering_score, emotive_mixed_score, emotive_calm_score,
                density_fluff_score, density_standard_score, density_deep_score,
                is_user_corrected, created_at
            ) VALUES (
                %(title)s, %(url)s, %(domain)s, %(content)s, %(summary)s, %(published_at)s,
                %(epistemic_opinion_score)s, %(epistemic_mixed_score)s, %(epistemic_facts_score)s,
                %(emotive_triggering_score)s, %(emotive_mixed_score)s, %(emotive_calm_score)s,
                %(density_fluff_score)s, %(density_standard_score)s, %(density_deep_score)s,
                FALSE, NOW()
            )
            ON CONFLICT (url) DO NOTHING
            RETURNING id;
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, article_data)
                return cur.fetchone()
        except Exception as e:
            print(f"Error saving article {article_data.get('url')}: {e}")
            return None
    
    def get_feedback_for_axis(self, axis_name):
        """
        Retrieve all feedback for a specific axis with article content for training.
        """
        query = """
            SELECT a.content, f.user_score
            FROM seithi.feedback_log f
            JOIN seithi.articles a ON f.article_id = a.id
            WHERE f.axis = %s AND a.content IS NOT NULL
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (axis_name,))
            return [{"text": row[0], "user_score": row[1]} for row in cur.fetchall()]

    
    def get_filtered_articles(self, epistemic_facts_min=0.0, emotive_calm_min=0.0, density_deep_min=0.0, limit=100):
        """
        Query articles based on probability thresholds.
        Returns articles that meet ALL specified minimum scores.
        """
        query = """
            SELECT id, title, url, domain, published_at,
                   epistemic_facts_score, emotive_calm_score, density_deep_score
            FROM seithi.articles
            WHERE epistemic_facts_score >= %s
              AND emotive_calm_score >= %s
              AND density_deep_score >= %s
            ORDER BY density_deep_score DESC, emotive_calm_score DESC, published_at DESC
            LIMIT %s
        """
        with self.conn.cursor() as cur:
            cur.execute(query, (epistemic_facts_min, emotive_calm_min, density_deep_min, limit))
            columns = ['id', 'title', 'url', 'domain', 'published_at', 
                      'epistemic_facts_score', 'emotive_calm_score', 'density_deep_score']
            return [dict(zip(columns, row)) for row in cur.fetchall()]

    def close(self):
        if self.conn:
            self.conn.close()
