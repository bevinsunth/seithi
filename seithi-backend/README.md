# Seithi Backend

Go-based REST API server for the Seithi news aggregation platform.

## Tech Stack

- **Language**: Go 1.21+
- **Router**: Chi (lightweight and idiomatic)
- **Database**: PostgreSQL with pgx driver
- **CORS**: go-chi/cors middleware

## Setup

1. **Install dependencies**:
```bash
go mod download
```

2. **Configure environment**:
The backend reads from `../seithi-infra/.env` or uses these defaults:
- `POSTGRES_HOST=localhost`
- `POSTGRES_PORT=5433`
- `POSTGRES_USER=admin`
- `POSTGRES_PASSWORD=123456`
- `POSTGRES_DB=seithi`

3. **Run the server**:
```bash
go run .
```

Server starts on `http://localhost:8080`

## API Endpoints

### GET /api/articles
Fetch articles with optional filtering.

**Query Parameters**:
- `limit` (default: 20, max: 100)
- `offset` (default: 0)
- `min_facts` (0-1, default: 0)
- `min_calm` (0-1, default: 0)
- `min_deep` (0-1, default: 0)

**Response**:
```json
{
  "articles": [...],
  "total": 93,
  "limit": 20,
  "offset": 0
}
```

### GET /api/articles/:id
Get a single article by ID.

### POST /api/feedback
Submit user feedback on article scores.

**Body**:
```json
{
  "article_id": "uuid",
  "axis": "epistemic|emotive|density",
  "user_score": 0|1|2
}
```

### GET /api/stats
Get overall statistics.

