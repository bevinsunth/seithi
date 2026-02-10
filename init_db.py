"""Initialize database with ML classification columns"""
import database

if __name__ == "__main__":
    print("Initializing database and applying migrations...")
    database.init_db()
    print("Database initialized successfully!")
