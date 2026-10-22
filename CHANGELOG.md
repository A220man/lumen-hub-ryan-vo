# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-22

### Added
- Initial project skeleton with FastAPI backend and React frontend
- Health check endpoints (`/health`, `/health/ready`, `/health/live`)
- Docker Compose with PostgreSQL, Keycloak, backend, frontend
- Keycloak realm configuration with roles and clients
- GitHub Actions CI workflow for backend/frontend tests and Docker builds
- Basic frontend with login page, dashboard, and protected routes
- Authentication context and hook (demo mode)
- TypeScript configuration with strict mode
- ESLint and Vitest setup

### Security
- Non-root Docker users
- Health checks on all services
- CORS configuration
- Environment-based secrets management