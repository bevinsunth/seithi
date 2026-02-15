#!/bin/sh
set -e

# Psql execution function
psql_exec() {
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "$1"
}

echo "Starting initialization script..."

# 1. Create App Users (Idempotent)
echo "Creating users..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$APP_USER') THEN
            CREATE USER $APP_USER WITH LOGIN PASSWORD '$APP_PASSWORD';
        END IF;
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$READONLY_USER') THEN
            CREATE USER $READONLY_USER WITH LOGIN PASSWORD '$READONLY_PASSWORD';
        END IF;
    END
    \$\$;
EOSQL

# 2. Setup Extensions & Schema in correct DB
echo "Setting up schema..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    CREATE SCHEMA IF NOT EXISTS seithi;
    
    -- Grant Usage on Schema
    GRANT USAGE ON SCHEMA seithi TO $APP_USER;
    GRANT USAGE ON SCHEMA seithi TO $READONLY_USER;
EOSQL

# 3. Create Tables (in seithi schema) - Official Seithi Specification
echo "Creating tables..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SET search_path TO seithi, public;

    -- Articles Table (Official Schema)
    CREATE TABLE IF NOT EXISTS articles (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        title TEXT NOT NULL,
        url TEXT UNIQUE NOT NULL,
        domain TEXT NOT NULL,
        content TEXT,
        summary TEXT,
        published_at TIMESTAMP,
        
        -- Scoring Columns (0, 1, or 2)
        score_factual INT DEFAULT 0,
        score_emotive INT DEFAULT 0,
        score_density INT DEFAULT 0,
        
        -- Metadata
        is_user_corrected BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW()
    );

    -- Optimized for the "Seithi Sort" (High Depth + High Calm)
    CREATE INDEX IF NOT EXISTS idx_seithi_sort ON articles (
        score_density DESC, 
        score_emotive DESC, 
        published_at DESC
    );

    -- Feedback Log Table (Training Data)
    CREATE TABLE IF NOT EXISTS feedback_log (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        article_id UUID REFERENCES articles(id),
        axis VARCHAR(20) NOT NULL,  -- 'factual', 'emotive', 'density'
        user_score INT NOT NULL,    -- 0, 1, or 2
        timestamp TIMESTAMP DEFAULT NOW()
    );
EOSQL

# 4. Grant Permissions
echo "Granting permissions..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- App User (Write/Read)
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA seithi TO $APP_USER;
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA seithi TO $APP_USER;
    ALTER DEFAULT PRIVILEGES IN SCHEMA seithi GRANT ALL ON TABLES TO $APP_USER;
    ALTER DEFAULT PRIVILEGES IN SCHEMA seithi GRANT ALL ON SEQUENCES TO $APP_USER;

    -- Readonly User (Select Only)
    GRANT SELECT ON ALL TABLES IN SCHEMA seithi TO $READONLY_USER;
    ALTER DEFAULT PRIVILEGES IN SCHEMA seithi GRANT SELECT ON TABLES TO $READONLY_USER;
EOSQL

echo "Initialization complete."