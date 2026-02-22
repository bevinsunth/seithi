import os
import requests
import datetime
import json
from .config import DATABASE_URL # We might repurpose this or use a new INGEST_URL

INGEST_URL = os.getenv("INGEST_URL", "http://localhost:5173/api/ingest")
INGEST_SECRET = os.getenv("INGEST_SECRET", "dev-secret-key-123")

class Database:
    def __init__(self):
        # We no longer maintain a persistent TCP connection to a DB
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {INGEST_SECRET}",
            "Content-Type": "application/json"
        })
        
    def article_exists(self, url):
        """
        Since the new SvelteKit endpoint handles 'ON CONFLICT DO NOTHING',
        we can technically skip this pre-check to reduce network calls.
        However, for backward compatibility with the brain's logic, we'd need
        a new endpoint to check existence, or just rely on the insert failing gracefully.
        For now, we will return False and let the insert handle duplicates.
        """
        return False

    def save_article(self, article_data):
        """
        Saves a classified article by sending it to the SvelteKit D1 ingestion API.
        """
        try:
            # Format datetime if it's an object
            if 'published_at' in article_data and isinstance(article_data['published_at'], datetime.datetime):
                article_data['published_at'] = article_data['published_at'].isoformat()
                
            response = self.session.post(INGEST_URL, json=article_data)
            response.raise_for_status() # Raise exception for 4xx/5xx errors
            
            result = response.json()
            if result.get("status") == "ignored":
                print(f"Article ignored (duplicate): {article_data.get('url')}")
                return None
                
            return result.get("id")
            
        except requests.exceptions.RequestException as e:
            print(f"Error saving article {article_data.get('url')}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def get_feedback_for_axis(self, axis_name):
        """
        Currently not implemented via API.
        Training scripts will need a dedicated endpoint or direct DB access later.
        """
        print("Warning: get_feedback_for_axis is not yet supported via the HTTP API.")
        return []
    
    def get_filtered_articles(self, epistemic_facts_min=0.0, emotive_calm_min=0.0, density_deep_min=0.0, limit=100):
        """
        Currently not implemented via API in the Brain as it only ingests.
        """
        print("Warning: get_filtered_articles is not supported in the ingestor client.")
        return []

    def close(self):
        self.session.close()

