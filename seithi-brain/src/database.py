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
            cur.execute("SELECT 1 FROM articles WHERE url = %s", (url,))
            return cur.fetchone() is not None

    def save_article(self, article_data):
        """
        Saves a classified article to the database.
        """
        query = """
            INSERT INTO articles (
                title, url, domain, content, summary, published_at,
                score_factual, score_emotive, score_density,
                is_user_corrected, created_at
            ) VALUES (
                %(title)s, %(url)s, %(domain)s, %(content)s, %(summary)s, %(published_at)s,
                %(score_factual)s, %(score_emotive)s, %(score_density)s,
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

    def close(self):
        if self.conn:
            self.conn.close()
