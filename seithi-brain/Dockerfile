FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (for building psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the ML model to bake it into the image
# This prevents downloading 1GB+ on every startup
RUN python -c "from transformers import pipeline; pipeline('zero-shot-classification', model='valhalla/distilbart-mnli-12-3')"
RUN python -c "import nltk; nltk.download('punkt')"

# Copy source code
COPY . .

# Run the worker
CMD ["python", "-m", "src.main"]
