# Seithi Infrastructure

This repository contains Docker and orchestration configuration for the Seithi multi-service application.

## Purpose

- Docker Compose files for local development
- Container configurations for all services
- Orchestration and deployment scripts
- Infrastructure as Code (IaC) configurations

## Services

The infrastructure manages the following services:
- **seithi-backend**: Go API server
- **seithi-web**: SvelteKit frontend
- **seithi-brain**: Python ML worker
- **Database**: PostgreSQL
- **Cache**: Redis (if needed)

## Getting Started

(To be added)



Manually create a superuser

`docker exec -it seithi-postgres psql -U postgres -c "CREATE USER admin_user WITH SUPERUSER PASSWORD 'your_secure_password';"`