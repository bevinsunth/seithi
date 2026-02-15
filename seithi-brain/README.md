# Seithi Brain

Python-based ML worker for news classification and analysis.

## Purpose

- ML-based article classification (ragebait vs. nuanced)
- Hybrid categorization using RSS tags, URL heuristics, and ML
- Background processing of news articles
- Model training and evaluation

## Tech Stack

- **Language**: Python
- **ML Framework**: Sentence Transformers (all-MiniLM-L6-v2)
- **Task Queue**: TBD (e.g., Celery, RQ)
- **Message Broker**: TBD (e.g., Redis, RabbitMQ)

## POC Backup

The initial proof-of-concept implementation is preserved in the `poc-backup/` directory for reference.

## Getting Started

### Local Development Setup

To run Seithi Brain locally in a virtual environment:

1.  **Navigate to the directory**:
    ```bash
    cd seithi-brain
    ```

2.  **Create a virtual environment**:
    ```bash
    python3 -m venv .venv
    ```

3.  **Activate the virtual environment**:
    ```bash
    source .venv/bin/activate
    ```

4.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Environment Variables**:
    Create a `.env` file or export the following variables:
    ```bash
    POSTGRES_DB=seithi
    POSTGRES_USER=app_user
    POSTGRES_PASSWORD=your_password
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5433
    ```

6.  **Run the service**:
    ```bash
    python3 -m src.main
    ```

## Development

- Follow PEP 8 and use type hints as specified in `AGENTS.md`.
- Run tests using `pytest`.
