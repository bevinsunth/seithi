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

# 3. Create Tables (in seithi schema)
echo "Creating tables..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SET search_path TO seithi, public;

    CREATE TABLE IF NOT EXISTS articles (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        title TEXT NOT NULL,
        link TEXT UNIQUE NOT NULL,
        summary TEXT,
        published_date TIMESTAMP,
        source TEXT,
        filter_status TEXT DEFAULT 'clean',
        filter_reason TEXT,
        word_count INTEGER,
        full_content TEXT,
        crawl_status TEXT DEFAULT 'pending',
        crawler_method TEXT DEFAULT 'none',
        crawled_at TIMESTAMP,
        ml_classification TEXT,
        ml_confidence FLOAT,
        ml_ragebait_score FLOAT,
        ml_nuanced_score FLOAT,
        ml_topic TEXT,
        ml_region TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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