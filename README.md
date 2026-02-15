# Seithi - Multi-Repo Workspace

Seithi is a news aggregation platform with ML-based classification and quality analysis.

## Architecture

This workspace contains 4 separate repositories:

### [seithi-infra](./seithi-infra)
Docker and orchestration configuration for the entire stack.

### [seithi-backend](./seithi-backend)
Go-based API server handling business logic and data access.

### [seithi-web](./seithi-web)
SvelteKit frontend providing the user interface.

### [seithi-brain](./seithi-brain)
Python ML worker for article classification and analysis.

## Development Setup

Seithi uses a hybrid development model:
- **Infrastructure**: Core services like PostgreSQL run in **Docker** via `seithi-infra`.
- **Worker Services**: Services like `seithi-brain` run in **Local Virtual Environments** for easier debugging and iteration.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.9+
- Go 1.21+
- Node.js 20+

### Step-by-Step Setup

1.  **Start the Database**:
    ```bash
    cd seithi-infra
    docker-compose up -d
    ```

2.  **Setup Seithi Brain**:
    See [seithi-brain/README.md](./seithi-brain/README.md) for local setup instructions.

## Deployment

## Project Phases

- **Phase 1**: Infrastructure & Orchestration ← Current Phase
- **Phase 2**: Backend API Development
- **Phase 3**: ML Worker Integration
- **Phase 4**: Frontend Development
- **Phase 5**: Testing & Production Deployment
