import psycopg2
from psycopg2 import sql
import os

import getpass

# Database connection configuration
# Defaulting to common local Postgres settings, can be overridden by env vars
DB_NAME = os.getenv("DB_NAME", "seithi")
DB_USER = os.getenv("DB_USER", getpass.getuser())
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    
    # Create articles table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            summary TEXT,
            published_date TIMESTAMP,
            source TEXT,
            filter_status TEXT DEFAULT 'clean',
            filter_reason TEXT,
            word_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def save_article(article_data):
    conn = get_connection()
    cur = conn.cursor()
    
    insert_query = """
        INSERT INTO articles (title, link, summary, published_date, source, filter_status, filter_reason, word_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (link) DO NOTHING
    """
    
    cur.execute(insert_query, (
        article_data['title'],
        article_data['link'],
        article_data['summary'],
        article_data.get('published_date'),
        article_data['source'],
        article_data['filter_status'],
        article_data.get('filter_reason'),
        article_data.get('word_count')
    ))
    
    conn.commit()
    cur.close()
    conn.close()

def get_articles(status='clean'):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT title, link, summary, source, filter_reason FROM articles WHERE filter_status = %s ORDER BY published_date DESC", (status,))
    articles = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return [
        {
            'title': a[0],
            'link': a[1],
            'summary': a[2],
            'source': a[3],
            'filter_reason': a[4]
        } for a in articles
    ]
