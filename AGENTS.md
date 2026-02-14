# Agent Guidelines for Seithi Project

## Project Overview

Seithi is a multi-service news aggregation platform with ML-based classification and quality analysis. The project uses a multi-repo architecture with separate services for infrastructure, backend, frontend, and ML processing.

## Architecture

### Multi-Repo Structure

```
seithi/
├── seithi-infra/    # Docker & Orchestration
├── seithi-backend/  # Go API Server
├── seithi-web/      # SvelteKit Frontend
└── seithi-brain/    # Python ML Worker
    └── poc-backup/  # Original POC implementation (reference only)
```

### Service Responsibilities

- **seithi-infra**: Docker Compose, container configs, deployment scripts
- **seithi-backend**: RESTful API, business logic, database access, authentication
- **seithi-web**: User interface, article browsing, filtering, responsive design
- **seithi-brain**: ML classification, hybrid categorization, background processing

## Tech Stack Guidelines

### seithi-backend (Go)
- **Language**: Go 1.21+
- **Framework**: Use Gin or Echo for REST API
- **Database**: PostgreSQL with GORM or sqlx
- **Structure**: Follow clean architecture (handler → service → repository)
- **Error Handling**: Use structured error types with context
- **Logging**: Use structured logging (e.g., zap, zerolog)
- **Testing**: Table-driven tests, mocks for external dependencies

### seithi-web (SvelteKit)
- **Framework**: SvelteKit with TypeScript
- **Styling**: Tailwind CSS preferred
- **State Management**: SvelteKit stores, avoid unnecessary complexity
- **API Calls**: Use SvelteKit's load functions for SSR data
- **Components**: Keep components small and reusable
- **Accessibility**: Don't bother for now
- **Testing**: Vitest for unit tests, Playwright for e2e

### seithi-brain (Python)
- **Language**: Python 3.9+
- **ML Framework**: Sentence Transformers (all-MiniLM-L6-v2 model)
- **Task Queue**: Celery or RQ for background jobs
- **Type Hints**: Always use type hints (enforce with mypy)
- **Code Style**: Follow PEP 8, use black for formatting
- **Dependencies**: Use requirements.txt or Poetry
- **Testing**: pytest with fixtures, mock external services

### seithi-infra (Docker)
- **Base Images**: Use official, minimal images (alpine where possible)
- **Multi-stage Builds**: Use for production images
- **Networks**: Define custom networks for service isolation
- **Volumes**: Use named volumes for persistent data
- **Environment**: Use .env files, never hardcode secrets

## Development Practices

### Code Quality
- Write self-documenting code with clear variable/function names
- Add comments only when the "why" isn't obvious from the code
- Keep functions small and focused (single responsibility)
- Avoid premature optimization; prioritize readability

### Git Workflow
- Each service is a separate git repository
- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Branch naming: `feature/`, `bugfix/`, `hotfix/`
- Always include meaningful commit messages

### API Design
- RESTful conventions: proper HTTP verbs and status codes
- Versioned endpoints: `/api/v1/...`
- Consistent error response format
- Pagination for list endpoints
- Include OpenAPI/Swagger documentation

### Database
- Use migrations for schema changes (never manual SQL)
- Add indexes for frequently queried fields
- Use transactions for multi-step operations
- Soft delete for user-facing data (add `deleted_at` column)

### Security
- Never commit secrets or API keys
- Use environment variables for configuration
- Validate all user input
- Use parameterized queries (prevent SQL injection)
- Implement rate limiting on API endpoints
- CORS configuration for frontend-backend communication

## ML/AI Specific Guidelines

### Model Usage
- Current model: `all-MiniLM-L6-v2` for zero-shot classification
- Classification types: "ragebait" vs "nuanced"
- Hybrid approach: RSS tags → URL heuristics → ML classifier
- Cache model embeddings to avoid recomputation

### Data Processing
- Preprocess text: remove HTML, normalize whitespace
- Handle missing/malformed data gracefully
- Log classification decisions with confidence scores
- Store raw article data separately from processed data

## Testing Requirements

### Unit Tests
- Aim for 70%+ code coverage
- Test edge cases and error conditions
- Mock external dependencies (databases, APIs, ML models)
- Keep tests fast (< 1 second per test)

### Integration Tests
- Test service-to-service communication
- Use test databases (Docker containers)
- Verify API contracts between services

### End-to-End Tests
- Critical user flows only (reading articles, filtering)
- Run in CI/CD pipeline
- Keep suite small and maintainable

## Documentation Standards

### Code Documentation
- Go: Use godoc comments for exported functions/types
- Python: Use docstrings (Google style)
- TypeScript: Use JSDoc for complex functions

### README Files
- Each service must have a README with:
  - Purpose and responsibilities
  - Setup instructions
  - Environment variables
  - Running tests
  - Common tasks/commands

### API Documentation
- Maintain OpenAPI/Swagger spec for backend
- Include request/response examples
- Document authentication requirements
- Version all API changes

## Common Patterns

### Error Handling
```go
// Go: Return errors, don't panic
func ProcessArticle(id string) (*Article, error) {
    if id == "" {
        return nil, fmt.Errorf("article ID cannot be empty")
    }
    // ...
}
```

```python
# Python: Use exceptions for exceptional cases
def classify_article(text: str) -> ClassificationResult:
    if not text:
        raise ValueError("Article text cannot be empty")
    # ...
```

### Configuration
- Use environment variables for deployment-specific config
- Provide sensible defaults
- Validate configuration on startup
- Document all required environment variables

### Logging
- Use structured logging with context
- Log levels: DEBUG (dev), INFO (important events), WARN (recoverable), ERROR (failures)
- Include request IDs for tracing
- Never log sensitive data (passwords, tokens)

## Phase-Specific Guidelines

### Current Phase: Phase 1 - Infrastructure & Orchestration
- Focus on Docker setup and service orchestration
- Define service dependencies and networking
- Create development environment setup scripts
- Document local development workflow

### Upcoming Phases
- **Phase 2**: Backend API development (database schema, endpoints)
- **Phase 3**: ML worker integration (task queue, classification service)
- **Phase 4**: Frontend development (UI/UX, API integration)
- **Phase 5**: Testing & production deployment

## Working with the POC

The `seithi-brain/poc-backup/` directory contains the original proof-of-concept:
- **DO NOT modify** files in poc-backup
- **DO reference** it for understanding the ML classification logic
- **DO extract** reusable components and improve them in the new structure
- Key files to reference:
  - `classifier.py`: ML classification implementation
  - `aggregator.py`: RSS feed processing
  - `database.py`: Database schema and queries

## Agent Behavior Expectations

### When Making Changes
1. Understand the full context before modifying code
2. Maintain consistency with existing patterns
3. Test changes locally when possible
4. Update documentation if behavior changes
5. Consider impact on other services

### When Stuck
1. Check the POC backup for reference implementations
2. Search for similar patterns in the codebase
3. Ask clarifying questions rather than making assumptions
4. Document uncertainties in comments

### Communication
- Be explicit about assumptions
- Highlight breaking changes or important decisions
- Provide context for non-obvious choices
- Use markdown formatting for clarity

## File Naming Conventions

- **Go**: `snake_case.go` for files, `PascalCase` for types
- **Python**: `snake_case.py` for everything
- **TypeScript**: `PascalCase.svelte` for components, `camelCase.ts` for utilities
- **Config**: `kebab-case.yml` or specific conventions (Dockerfile, docker-compose.yml)

## Environment Variables Format

Use this naming convention across all services:
```
SERVICE_NAME_FEATURE_SETTING

Examples:
SEITHI_DB_HOST=localhost
SEITHI_DB_PORT=5432
SEITHI_BRAIN_MODEL_PATH=/models
SEITHI_API_JWT_SECRET=xxx
```

## Summary

Follow these principles when working on Seithi:
1. **Clarity over cleverness** - write code that's easy to understand
2. **Consistency** - follow established patterns in each service
3. **Documentation** - explain the why, not just the what
4. **Testing** - write tests that give confidence
5. **Security** - never compromise on security basics
6. **Performance** - optimize when needed, not prematurely
7. **Maintainability** - think about the next developer who will read this code
8. **Readme** - any major decision should be documented in readme.md
  
