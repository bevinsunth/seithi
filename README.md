# Seithi

News aggregator with some smarts.

## Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd seithi
   ```

2. **Set up a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Database Setup**:
   Ensure you have a PostgreSQL server running locally on port 5432.
   
   Start the service:
   ```bash
   brew services start postgresql@17
   ```

   Create the database:
   ```bash
   createdb seithi
   ```

2. **Run the Aggregator**:
   ```bash
   python aggregator.py
   ```
   This will fetch news from RSS feeds, apply filters, and generate an `index.html` report.

3. **View the Report**:
   Open `index.html` in your browser to see the aggregated and filtered news.