import psycopg2
import os

# Database connection configuration
DB_NAME = os.getenv("DB_NAME", "seithi")
DB_USER = os.getenv("DB_USER", "bevin")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def check_schema():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()
    
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'articles'
        ORDER BY ordinal_position
    """)
    
    columns = cur.fetchall()
    
    print("Articles table schema:")
    print("-" * 50)
    for col_name, col_type in columns:
        print(f"{col_name:<25} {col_type}")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    check_schema()
